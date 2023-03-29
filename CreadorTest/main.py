from src.GPTConnector import GPTConnector
from src.SalesforceConnector import SalesforceConnector
from src.Utilities import Utilities

def _retry_with_error(error, retry_type):
    print(f"Error: {error} - Retry type: {retry_type}")
    is_break = input('Do you want to break? (y/n)')
    if is_break == 'y':
        quit()
    print(f"Creating new version...")
    if is_mock['error_mock']:
        code = Utilities.read_file(f"../force-app/main/default/classes/{class_name}Test.cls")
    else:
        code = Utilities.extract_code(gpt.prompt_apex_test_with_error(error, retry_type))
    while 'STOP' in code:
        response_user = input(code)
        code = Utilities.extract_code(gpt.prompt_response_user(response_user))
    if retry_type == 'compilar':
        push_salesforce(code)
    if retry_type == 'ejecutar':
        push_salesforce(code)
        run_test()

def read_prompt():
    print("Reading prompt...")
    prompt = Utilities.read_file("data/prompt.txt")
    gpt.save_message('system', prompt)
    
def collect_dependencies():
    print("Collecting dependencies...")
    
    while len(list_class_to_visit) > 0:
        class_info = list_class_to_visit.pop(0)
        visit_class.append(class_info[0])
        if class_info[1] > max_level:
            continue
        response = sf.get_apex_class_code(class_info[0])
        if response['Error']:
            gpt.save_conversation_dependencies(class_info[0], response['Message'] )
            print(response['Message'])
            continue
        result = gpt.prompt_dependencies_apex_class(class_info[1],class_info[0],response['Body']) if not is_mock['generate_mock'] else Utilities.read_file(f"mock_data/{class_info[0]}.txt")
        if not is_mock['generate_mock']:
            Utilities.write_file(f"mock_data/{class_info[0]}.txt", result)
        depencies, resume = Utilities.separate_dependendencies_resume(result)
        gpt.save_conversation_dependencies(class_info[0], resume if resume != "" else response['Body'])
        map_code_class[class_info[0]] = response['Body']
        print(f"Class: {class_info[0]} - Level: {class_info[1]} - Depencies: {depencies}")
        for depency in depencies:
            if depency not in visit_class and depency not in to_visit_class and 'Listo' not in depency:
                list_class_to_visit.append((depency, class_info[1] + 1))
                to_visit_class.append(depency)


def generate_test_code():
    print("Generating test code...")
    if is_mock['use_mock']:
        code = Utilities.read_file(f"../force-app/main/default/classes/{class_name}Test.cls")
        return code
    class_code = map_code_class[class_name]
    return Utilities.extract_code(gpt.prompt_generate_apex_test_code(class_name, class_code))

def push_salesforce(code):
    sf.create_apex_file(code)
    result = sf.push_apex_class()
    if result['Error']:
        print('Error deploy.')
        if retry['retry_compilation'] > 0:
            print('Retry deploy: ' + str(retry['retry_compilation']))
            retry['retry_compilation'] -= 1
            _retry_with_error(result['Message'], 'compilar')
        else:
            print('Error deploy cannot retry.')
            quit()
    print('Success deploy')
    
    
def run_test():
    print("Running test...")
    result = sf.run_test_in_salesforce()
    if result['Error']:
        print('Error run test: ' + result['Message'])
        if retry['retry_run'] > 0:
            print('Retry run test: ' + str(retry['retry_run']))
            retry['retry_run'] -= 1
            _retry_with_error(result['Message'], 'ejecutar')
        else:
            print('Error run test cannot retry.')
            quit()
    print('Success run test with result: ' + result['Message'])
    
class_name = 'ChatGPT_CTRL'
modelo = 'gpt-4'
list_class_to_visit = [(class_name, 0)]
visit_class = []
to_visit_class = [class_name]
map_code_class = {}
gpt = GPTConnector(modelo)
sf = SalesforceConnector(class_name)  
max_level = 3
is_mock = {'generate_mock': True, 'use_mock': True, 'error_mock': True}
retry = {'retry_compilation': 3, 'retry_run': 3}
        
if __name__ == '__main__':
    read_prompt()
    collect_dependencies()
    code = generate_test_code()
    push_salesforce(code)
    run_test()