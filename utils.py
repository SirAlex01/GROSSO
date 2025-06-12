from file_info import File
from dotenv import load_dotenv
import os

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
        api_keys.append(os.getenv(api_key_name))
    return api_keys