from cli import parseArgs
from collector import *
from utils import collectApiKeys
from gemini import *
# === Main ===
args = parseArgs() 
PATH = args.path
MAX_SIZE = args.maxsize * 1024  # Convert KB to bytes
TIMEOUT = args.timeout 

NUM_KEYS = 13

files, layout = readDirectoryRecursively(PATH, MAX_SIZE)
file_data = collectFileContents(files)

api_keys = collectApiKeys(NUM_KEYS)
hist = prepareHistory(file_data)
chat = makePrompts(api_keys, hist, TIMEOUT)
interactiveChat(chat)