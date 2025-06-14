import google.generativeai as genai
import random
import logging
import time
import string
import re
import multiprocessing

# Setup error logging
logging.basicConfig(
    filename="gemini_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Supported fallback models (most capable first)
MODELS = [
    "models/gemini-2.5-flash-preview-05-20",
    "models/gemini-2.0-flash"
]

CONTEXT_PROMPT = """You are a cybersecurity expert analyzing code for an Attack-Defense CTF competition.
Your task is to identify vulnerabilities and create exploits.
Focus on common vulnerabilities like SQL injection, XSS, command injection, file inclusion, authentication bypasses, and logic flaws.
Be precise and practical in your analysis."""

VULNS_PROMPT = """Analyze all the provided files and list vulnerabilities found, ordered by easiness to exploit (easiest first).
For each vulnerability, provide:
1. File name and line number
2. Vulnerability type
3. Brief description of the flaw
4. Exploitation difficulty (Easy/Medium/Hard)
Focus on exploitable vulnerabilities that could lead to flag capture in a CTF environment."""

EXPLOIT_PROMPT = """Based on the vulnerabilities identified and the provided exploit template, create a working exploit for the easiest vulnerability.
The exploit should:
1. Be ready to run
2. Include necessary imports and setup
3. Have clear comments explaining the attack vector
4. Target the most straightforward vulnerability for quick flag capture, unless explicitly requested
5. Always USE THE PROVIDED TEMPLATES and adapt them for the current challenge
6. DO NOT USE ANY OTHER LIBS FOR CONNECTIONS/COMMUNICATIONS RATHER THAN requests and pwntools!
7. Insert the FULL python payload at the end of the response within ```python and ```. USE ONLY ONE SECTION WITH THE EXPLOIT CODE. NO OTHER python SECTION!
8. ALWAYS gather ALL available flags ITERATING ON flag_ids ONE BY ONE LIKE IN THE TEMPLATES. DO NOT STOP AFTER ONE FLAG! IN GENERAL DO NOT CHANGE THEIR STRUCTURE.
9. flag format is 32 printable characters, the last one is always =

Remember to use generate for any varying information which does not need to be fixed to obfuscate your exploit as much as possible.
If CLI interactive communication is needed in the exploit, use pwntools rather than requests. 
Remember that flush=True when printing the flag is necessary!

Template for requests:
"""
with open("templates/template.py", "r") as f:
    EXPLOIT_PROMPT += f.read()

EXPLOIT_PROMPT += "\n\nTemplate for pwntools:\n"
with open("templates/template_pwntools.py", "r") as f:
    EXPLOIT_PROMPT += f.read()

def prepareHistory(file_data):
    history = [
        {
            "role": "user",
            "parts": [{"text": CONTEXT_PROMPT}]
        },
        {
            "role": "model", 
            "parts": [{"text": "I understand. I'm ready to analyze code for CTF vulnerabilities and create exploits. Please provide the files you'd like me to examine."}]
        }
    ]
    
    # Add file contents to history with varied responses
    responses = [
        "Thank you for providing {}! I'm analyzing it for security issues.",
        "Received {}. Examining the code for potential weaknesses.",
        "Got {}. Scanning for exploitable flaws.",
        "File {} received. Analyzing for attack vectors.",
        "Perfect, {} loaded. Looking for security weaknesses now.",
        "Excellent! {} is now being reviewed for exploitable issues.",
        "File {} added to analysis. Checking for security problems.",
        "Great, {} received. Searching for potential attack points.",
        "Thanks for {}! Examining for security flaws.",
        "File {} loaded successfully. Reviewing for exploit opportunities.",
        "Analyzing {} now. Looking for security gaps.",
        "Got it! {} is being scanned for vulnerabilities.",
        "File {} received. Checking for security holes.",
        "Perfect! {} loaded. Examining for exploitable weaknesses.",
        "Thanks for providing {}. Analyzing for potential security issues."
    ]

    
    for i, (file_obj, content) in enumerate(file_data.items()):
        print(f"[INFO] {file_obj} added to history")
        history.extend([{
            "role": "user",
            "parts": [{"text": f"File: {file_obj.name}\n\n```\n{content}\n```"}]
        },
        {
            "role": "model", 
            "parts": [{"text": responses[i % len(responses)].format(file_obj.name)}]
        }
        ])
    
    return history


def makePrompts(api_keys, history, timeout=10):
    for idx, key in enumerate(api_keys):
        print(f"\n[INFO] Trying API key #{idx + 1}")

        try:
            genai.configure(api_key=key)
        except Exception as e:
            logging.error(f"Failed to configure API key #{idx + 1}: {str(e)}")
            continue

        for model_name in MODELS:
            print(f"[INFO] Trying model: {model_name} with API key #{idx + 1}")

            try:
                gemini_model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        top_p=1.0,
                        top_k=1
                    )
                )

                chat = gemini_model.start_chat(history=history)

                # === VULNERABILITIES with TIMEOUT ===
                try:
                    response_vulns = sendWithTimeout(chat, VULNS_PROMPT, timeout)
                    print("Gemini (vulnerabilities):", response_vulns.text.strip())
                except Exception as ve:
                    logging.error(f"Timeout/error on VULNS [{model_name}] key #{idx + 1}: {str(ve)}")
                    continue  # try next model

                # === EXPLOIT without timeout ===
                try:
                    response_exploit = chat.send_message(EXPLOIT_PROMPT)
                    exploit_code = response_exploit.text.strip()                    
                    print("Gemini (exploit):", exploit_code)

                    matches = re.findall(r"```python\s*(.*?)\s*```", response_exploit.text, re.DOTALL)
                    if matches:
                        exploit_code = matches[-1].strip()  # use the last match
                    else:
                        exploit_code = response_exploit.text.strip()  # fallback

                    rand_digits = ''.join(random.choices(string.digits, k=6))
                    filename = f"exploit_{rand_digits}.py"
                    with open(filename, "w") as f:
                        f.write(exploit_code)
                    print(f"Gemini (exploit) saved to: {filename}")

                except Exception as ee:
                    logging.error(f"Error on EXPLOIT [{model_name}] key #{idx + 1}: {str(ee)}")
                    continue  # try next model

                return chat  # success

            except Exception as e:
                logging.error(f"Model setup failed [{model_name}] key #{idx + 1}: {str(e)}")
                time.sleep(1)

    raise RuntimeError("All API keys and models failed. See gemini_errors.log for details.")

def sendMessageWorker(chat, message, return_dict):
    try:
        response = chat.send_message(message)
        return_dict["response"] = response
    except Exception as e:
        return_dict["error"] = str(e)


def sendWithTimeout(chat, message, timeout_seconds):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    process = multiprocessing.Process(target=sendMessageWorker, args=(chat, message, return_dict))
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError("send_message() timed out after {} seconds".format(timeout_seconds))

    if "error" in return_dict:
        raise RuntimeError(f"send_message() failed: {return_dict['error']}")

    return return_dict["response"]

def interactiveChat(chat):
    print("---- Enter interactive mode. Type 'exit' or 'quit' to leave. ----")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower().strip() in {"exit", "quit"}:
                print("-------------------------------------------------------------------")
                print("Exiting chat session. Goodbye!")
                break

            response = chat.send_message(user_input)
            print("Gemini:", response.text.strip() if response.text else "(No response text received)")
        except KeyboardInterrupt:
            print("\n[Interrupted] Exiting chat session.")
            break
        except Exception as e:
            logging.error(f"Error during chat: {str(e)}")
            print("An error occurred. Check the logs.")