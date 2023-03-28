from simple_salesforce import Salesforce
import os
import subprocess
import json
from dotenv import load_dotenv
from src.Utilities import Utilities



class SalesforceConnector():
        
    def __init__(self,apex_class_name):
        load_dotenv()
        self.sf = Salesforce(username=os.getenv('sf_username'), password=os.getenv('sf_password'), security_token=os.getenv('sf_security_token'))
        self.apex_class_name = apex_class_name
        self.path = "../force-app/main/default/classes/"
        
    def get_apex_class_code(self,apex_class_name):
        query = f"SELECT Id, Name, Body FROM ApexClass WHERE Name = '{apex_class_name}'"
        apex_class = self.sf.query(query)

        if apex_class['totalSize'] == 0:
            return {'Error':True, 'Message':f'ApexClass not found: {apex_class_name}'}
        
        apex_class_code = apex_class['records'][0]['Body']
        return {'Error':False, 'Message':f'ApexClass found: {apex_class_name}', 'Body': apex_class_code}
    
    def create_apex_file(self, apex_class_code):
        print("Creating test file...")
        file_name = f"{self.path}{self.apex_class_name}Test.cls"
        Utilities.write_file(file_name, apex_class_code)
        print("Creating test metadata file...")
        file_name_meta = f"{self.path}{self.apex_class_name}Test.cls-meta.xml"
        meta = Utilities.read_file("data/meta.txt")
        Utilities.write_file(file_name_meta, meta)

    
    def push_apex_class(self):
        print("Pushing test file to Salesforce...")
        file_name = f"{self.path}{self.apex_class_name}Test.cls"
        push_command = f"sfdx force:source:deploy --sourcepath {file_name}"
        result = subprocess.run(push_command, shell=True, capture_output=True, text=True)
        message_to_result = {}
        if result.returncode != 0:
            message_to_result['Error'] = True
            message_to_result['Message'] = ' '.join(result.stdout.split('Error')[1:])
            return message_to_result
        message_to_result['Error'] = False
        return message_to_result
        
    def run_test_in_salesforce(self):
        print(f"Running test for {self.apex_class_name}Test...")
        command = f"sfdx force:apex:test:run -n {self.apex_class_name}Test -r json"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        result_json = json.loads(stdout)
        message_to_result = {}
        if result_json['result']['summary']['outcome'] == 'Failed':
            message_to_result['Error'] = True
            message = ''
            for failure in result_json['result']['tests']:
                if failure['Outcome'] == 'Fail':
                    message += f"Error: {failure['Message']}\n"
            message_to_result['Message'] = message
            return message_to_result
        coverage = int(result_json['result']['summary']['passRate'].replace('%',''))
        if coverage < 75:
            message_to_result['Error'] = True
            message_to_result['Message'] = f"Test coverage is {coverage}%"
            return message_to_result
        message_to_result['Error'] = False
        message_to_result['Message'] = f"Test coverage is {coverage}%"
        return message_to_result