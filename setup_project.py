import os

print("🌀 [SETUP] Iniciando a estruturação automática do projeto...")

# 1. Criando as pastas
folders = ["sharingan-gateway", "amaterasu-soar", "kamui-redteam", "dashboard-soc"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"[+] Pasta criada: {folder}/")

# 2. Criando o docker-compose.yml na raiz
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
with open("docker-compose.yml", "w", encoding="utf-8") as f:
    f.write(docker_compose_content)

# 3. Criando os Dockerfiles básicos para cada microsserviço (padrão sênior)
base_dockerfile = """FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
"""

for folder in ["sharingan-gateway", "amaterasu-soar", "dashboard-soc"]:
    with open(os.path.join(folder, "Dockerfile"), "w", encoding="utf-8") as f:
      f.write(base_dockerfile)

# 4. Criando requirements.txt padrão
with open("sharingan-gateway/requirements.txt", "w", encoding="utf-8") as f:
  f.write("fastapi==0.110.0\nuvicorn==0.28.0\nrequests==2.31.0\npydantic==2.6.4")

with open("amaterasu-soar/requirements.txt", "w", encoding="utf-8") as f:
  f.write("fastapi==0.110.0\nuvicorn==0.28.0\nrequests==2.31.0")

with open("dashboard-soc/requirements.txt", "w", encoding="utf-8") as f:
  f.write("streamlit==1.32.0\nrequests==2.31.0\npandas==2.2.1")

print("\n✨ Estrutura corporativa e arquivos de configuração gerados com sucesso!")
print("Agora sua base está pronta para receber os códigos principais.")