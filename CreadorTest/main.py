import os
import subprocess
from simple_salesforce import Salesforce
import requests
import openai
import re
import json


# Reemplaza con tus credenciales de Salesforce
SF_USERNAME = "jbrotonc@mindful-shark-jtq2qi.com"
SF_PASSWORD = "jbCandela22!"
SF_SECURITY_TOKEN = "RhmDbwU93BMRvMQxY1V1m98p"
openai.api_key = "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"

messages = []
class_name = 'ChatGPT_CTRL'
list_class_to_visit = [class_name]
visit_class = []
map_code_class = {}


sf = Salesforce(username=SF_USERNAME, password=SF_PASSWORD, security_token=SF_SECURITY_TOKEN)


def save_message(role, message):
        messages.append({"role": role, "content": message})

def get_apex_class_code(apex_class_name):
    query = f"SELECT Id, Name, Body FROM ApexClass WHERE Name = '{apex_class_name}'"
    apex_class = sf.query(query)

    if apex_class['totalSize'] == 0:
        return {'Error':True, 'Message':f'ApexClass not found: {apex_class_name}'}
    
    apex_class_code = apex_class['records'][0]['Body']
    return {'Error':False, 'Message':f'ApexClass found: {apex_class_name}', 'Body': apex_class_code}

def extract_code(text: str) -> str:
    pattern = r"```(.*?)```"
    result = re.search(pattern, text, re.DOTALL)
    if result:
        return result.group(1).strip()
    return ""

def chat_gpt(messages):
    return openai.ChatCompletion.create(model="gpt-4", messages=messages).choices[0].message.content

def generate_apex_test_code(apex_class_name, apex_class_code):
    prompt = f"Realiza la clase test de {apex_class_name}:\n '''{apex_class_code}'''\n---\n"
    save_message('user', prompt)
    response_test = chat_gpt(messages)
    save_message('assistant', response_test)
    return response_test

def generate_apex_test(apex_class_name, apex_class_code):
    prompt = f"{apex_class_name}:\n '''{apex_class_code}'''\n---\n"
    save_message('user', prompt)
    list_class_dependence = chat_gpt(messages)
    save_message('assistant', list_class_dependence)
    return list_class_dependence

def generate_not_apex_test(apex_class_name):
    prompt = f"{apex_class_name}: No es una clase APEX.\n"
    save_message('user', prompt)
    list_class_dependence = chat_gpt(messages)
    save_message('assistant', list_class_dependence)
    
def generate_apex_test_with_error(errores):
    prompt = f"Hemos encontrado los siguientes errores al ejecutar el test: {errores}. \n"
    save_message('user', prompt)
    list_class_dependence = chat_gpt(messages)
    response_test = save_message('assistant', list_class_dependence)
    return response_test

    
def create_and_push_test_file(apex_class_name, test_code):
    print("Creating test file...")
    path = "../force-app/main/default/classes/"
    file_name = f"{path}{apex_class_name}Test.cls"
    print(file_name)
    print(test_code)
    with open(file_name, 'w', encoding="utf-8") as file:
        file.write(test_code)
        
    print("Creating test metadata file...")
    
    file_name_meta = f"{path}{apex_class_name}Test.cls-meta.xml"
    
    with open("meta.txt", "r", encoding="utf-8") as f:
        meta = f.read()
    
    with open(file_name_meta, 'w', encoding="utf-8") as file_meta:
        file_meta.write(meta)
    
    print("Pushing test file to Salesforce...")
    push_command = f"sfdx force:source:deploy --sourcepath {file_name}"
    result = subprocess.run(push_command, shell=True, capture_output=True, text=True)
    print(result)
    if result.returncode != 0:
        raise Exception("Error pushing test file to Salesforce")
    
def generate_test(apex_class_name):
    while len(list_class_to_visit) != 0:
        apex_class_name = list_class_to_visit[0]
        if not apex_class_name:
            return "Error: No ApexClass name provided."
        visit_class.append(apex_class_name)
        list_class_to_visit.pop(0)
        apex_class_code = get_apex_class_code(apex_class_name)
        map_code_class.update({apex_class_name:apex_class_code.get('Body')})
        if apex_class_code.get('Error'):
            print (apex_class_code.get('Message'))
            generate_not_apex_test(apex_class_name)
        else:
            print (apex_class_code.get('Message'))
            dependencia_class = generate_apex_test(apex_class_name, apex_class_code.get('Body')).split('-')
            print('Dependencias encontradas: ', dependencia_class)
            for dependencia in dependencia_class:
                if dependencia not in visit_class and dependencia not in list_class_to_visit and  'Listo' not in dependencia:
                     list_class_to_visit.append(dependencia)
    print('Generando test de la clase: ', class_name)
    response = generate_apex_test_code(class_name, map_code_class.get(class_name))
    if extract_code(response) != '':
        response = extract_code(response)
    create_and_push_test_file(class_name,response)
    
def run_test_in_salesforce():
    test_class_name = f'{class_name}Test'
    print(f"Running test for {test_class_name}...")
    command = f"sfdx force:apex:test:run -n {test_class_name} -r json"
    
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout, stderr = process.communicate()
    print(stdout)

    result_json = json.loads(stdout)
    test_results = result_json['result']['summary']
    if test_results['failing'] > 0:
        error_message = ''
        print(f'Test Failing Results for {test_class_name}, recreating test...')
        for result in result_json['result']['tests']:
            if result['Outcome'] == 'Fail':
                error_message += result['Message'] + '\n'
        print('Generando test de la clase: ', class_name)
        response = generate_apex_test_with_error(error_message)
        if extract_code(response) != '':
            response = extract_code(response)
        create_and_push_test_file(class_name,response)
        run_test_in_salesforce()
    else:
        print('Test Success Results for {test_class_name}')
        
        
if __name__ == '__main__':
    with open("prompt.txt", "r", encoding="utf-8") as f:
        save_message('system', f.read())
    #generate_test(class_name)
    print('Realizando test de la clase: ', class_name)
    run_test_in_salesforce()