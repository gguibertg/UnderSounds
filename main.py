import os

# Determine the operating system and execute the appropriate shell command
if os.name == 'nt':  # Windows
    os.system("python -m uvicorn controller.controller:app --reload")
else:  # Linux/Unix/MacOS
    os.system("uvicorn controller.controller:app --reload")