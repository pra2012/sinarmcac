import subprocess
import sys

if __name__ == "__main__":
    # Executar a aplicação Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
