import subprocess
import os

frontend_dir = "./edi-app"
backend_dir = "./backend"

subprocess.run("npm install", shell=True, cwd=frontend_dir)

subprocess.run("pip install -r requirements.txt", shell=True, cwd=backend_dir)

npm_start_command = "npm start"
subprocess.Popen(npm_start_command, shell=True, cwd=frontend_dir)

uvicorn_command = "uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
subprocess.Popen(uvicorn_command, shell=True, cwd=backend_dir)

# Aguarde a execução dos processos em segundo plano (ou simplesmente deixe o script rodando)
try:
    input("Pressione Enter para encerrar...")
except KeyboardInterrupt:
    pass
