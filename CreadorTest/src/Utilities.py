
import re

class Utilities():
    
    @staticmethod
    def extract_code(text: str) -> str:
        pattern = r"```(.*?)```"
        result = re.search(pattern, text, re.DOTALL)
        if result:
            result = result.group(1).strip()
            return result[result.find('@isTest'):]
        return text
    
    @staticmethod
    def read_file(path: str) -> str:
        with open(path, 'r', encoding="utf-8") as file:
            return file.read()
        
    @staticmethod
    def write_file(path: str, content: str) -> None:
        with open(path, 'w', encoding="utf-8") as file:
            file.write(content)
            
    @staticmethod
    def separate_dependendencies_resume(result):
        result = result.split("-----")
        return result[0].strip().split('-'), result[1].strip() if len(result) > 1 else ""
    