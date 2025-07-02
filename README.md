# G.R.O.S.S.O.
**Gemini Recon & Orchestration System for Secure Operations**

<img src="https://github.com/SirAlex01/GROSSO/blob/main/logo/grosso_logo.jpg" alt="GROSSO Auto Prompter" width="300"/>

This project automates LLM prompting for all files in a challenge directory, enabling fast vulnerability analysis and exploit generation in Attack-Defense CTFs.

> A `.env` file containing valid Gemini API keys is required to run this tool.

---

## 🔧 Usage

```bash
pip install -r requirements.txt
python3 auto_prompter.py -p PATH [-ms MAXSIZE] [-t TIMEOUT]
```

### Parameters

- **PATH**: The path of the directory that contains the challenge's files (required)
- **MAXSIZE**: Maximum size (in kilobytes) allowed for a single file to be included in the prompt (optional, default: 30 KB)  
- **TIMEOUT**: Maximum time (in seconds) to wait for the first response. If timeout expires, script switches to another model (optional, default: 300 seconds)

### Useful shortcuts for interactive chat:
- **Esc + Enter**: Insert a newline in the prompt
- **Ctrl + X**: Copy the code of the last generated exploit