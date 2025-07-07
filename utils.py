from file_info import File
from dotenv import load_dotenv
import os
import re

def isExecutableFile(file: File) -> bool:
    return file.type in {
        'application/x-executable',
        'application/x-pie-executable',
        'application/x-sharedlib',
        'application/x-mach-binary',
        'application/x-dosexec'
    }

def shouldCollect(file: File, max_size: int) -> bool:
    if file.kind == 'directory':
        return False
    if file.size > max_size:
        return False
    if "/.git/" in file.name or "/.vscode/" in file.name:
        return False
    if file.kind == 'text':
        return True
    if file.kind == 'binary' and isExecutableFile(file):
        return True
    return False

def collectApiKeys(num_api_keys):
    load_dotenv()
    prefix = "GOOGLE_API_KEY_"
    api_keys = []
    for i in range(1, num_api_keys+1):
        api_key_name = prefix + str(i)
        api_key = os.getenv(api_key_name)
        if api_key:
            api_keys.append(api_key)
    return api_keys

def extractExploitCode(gemini_response):
    matches = re.findall(r"```python\s*(.*?)\s*```", gemini_response.text, re.DOTALL)
    if matches:
        exploit_code = matches[-1].strip()  # use the last match
    else:
        exploit_code = gemini_response.text.strip()  # fallback
    return exploit_code
