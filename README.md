## Claim_Document_Processor

Backend utility to extract and process claim documents. This README covers setup on Windows, macOS, and Linux, including virtual environment creation, dependency installation, and environment configuration.

### Prerequisites
- Python 3.9+ installed and on PATH
- Git installed
- A Google API key (for services used by this project)

### Environment Variables (.env)
Create a file named `.env` in the project root with at least:

```
GOOGLE_API_KEY=your-google-api-key-here
```

Keep `.env` out of version control.

### Quick Start
1) Clone the repository
```bash
git clone <your-repo-url>
cd Claim_Document_Processor
```

2) Create and activate a Python virtual environment

- Windows (PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Windows (Command Prompt)
```cmd
py -3 -m venv .venv
.\.venv\Scripts\activate.bat
```

- macOS/Linux (bash/zsh)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies
```bash
pip install -r requirements.txt
```

4) Add your environment variables
- Create `.env` in the project root if you haven't already and set `GOOGLE_API_KEY`.

5) Run the application
```bash
python main.py
```

### Project Structure
```
agents/
  decision_agent.py
  extract_agent.py
  main_workflow_agents.py
  validation_agent.py
utilities/
  extract_text_from_pdf.py
main.py
requirements.txt
```

### OS-specific Notes
- Windows: If script execution is restricted, you may need to allow running the venv activation script in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
- macOS/Linux: Ensure you are using the same Python version for both creating and running the venv (`python3 --version`).

### Common Commands
- Freeze dependencies after changes:
```bash
pip freeze > requirements.txt
```
- Deactivate the virtual environment:
```bash
deactivate
```

### Troubleshooting
- Virtual environment not activating:
  - Confirm the venv path exists (`.venv/`) and you are using the right activation script for your shell/OS.
- Missing `GOOGLE_API_KEY` error:
  - Ensure `.env` exists in project root and contains a valid key.
  - Restart your shell or IDE after adding `.env` if variables are not detected.