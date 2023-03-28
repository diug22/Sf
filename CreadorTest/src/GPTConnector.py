import openai
import os
from src.Utilities import Utilities
from dotenv import load_dotenv


class GPTConnector():
    
    def __init__(self,modelo):
        load_dotenv()
        openai.api_key = os.getenv('openai_api_key')
        self.messages = []
        self.modelo = modelo
        
    def _chat_gpt(self,messages):
        return openai.ChatCompletion.create(model=self.modelo, messages=messages).choices[0].message.content
        
    def save_message(self,role, message):
        self.messages.append({"role": role, "content": message})
        
    def save_conversation(self, prompt):
        self.save_message('user', prompt)
        response_gpt = self._chat_gpt(self.messages)
        self.save_message('assistant', response_gpt)
        return response_gpt
    
    def save_conversation_dependencies(self, class_name,response):
        self.save_message('user', class_name)
        self.save_message('assistant', response)
        
    
    
    def prompt_dependencies_apex_class(self,nivel,apex_class_name, apex_class_code):
        dependencies_messages = []
        context = Utilities.read_file("data/prompt_dependencies.txt")
        dependencies_messages.append({"role": 'system', "content": context})
        prompt = f"Nivel:{nivel}\n {apex_class_name}:\n '''{apex_class_code}'''\n---\n"
        dependencies_messages.append({"role": 'user', "content": prompt})
        return self._chat_gpt(dependencies_messages)
    
    
    def prompt_generate_apex_test_code(self,apex_class_name, apex_class_code):
        prompt = f"Realiza la clase test de {apex_class_name}:\n '''{apex_class_code}'''\n---\n"
        return self.save_conversation(prompt)

    def prompt_apex_test_with_error(self,errores,type_error):
        prompt = f"Hemos encontrado los siguientes errores al {type_error} el test: {errores}. \n" 
        return self.save_conversation(prompt)
    
  
   