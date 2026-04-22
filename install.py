import subprocess
import sys
import os

def install_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("Success")
    except subprocess.CalledProcessError as e:
        print(f"Fail: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()