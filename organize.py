import os
import shutil

# Caminho base atual onde o script está rodando
base_dir = os.getcwd()

# Estrutura de pastas que vamos criar
folders = [
    "sharingan-gateway",
    "amaterasu-soar",
    "kamui-redteam",
    "dashboard-soc"
]

for folder in folders:
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
    print(f"[+] Pasta criada: {folder}")

# Criando os arquivos de configuração essenciais na raiz
docker_compose_content = """version: '3.8'

services:
  sharingan-gateway:
    build: ./sharingan-gateway
    ports:
      - "8000:8000"

  amaterasu-soar:
    build: ./amaterasu-soar
    ports:
      - "8001:8001"

  dashboard-soc:
    build: ./dashboard-soc
    ports:
      - "8501:8501"
    depends_on:
      - sharingan-gateway
      - amaterasu-soar
"""

with open(os.path.join(base_dir, "docker-compose.yml"), "w", encoding="utf-8") as f:
    f.write(docker_compose_content)

print("[+] Arquivo docker-compose.yml criado com sucesso na raiz!")
print("\nEstrutura pronta! Agora basta copiar os seus códigos anteriores (.py e .yaml) para dentro de suas respectivas pastas.")