import logging
import requests
import io
import re
from fastapi import FastAPI, HTTPException, Request, Header, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SharinganGatewayDLP")

app = FastAPI(title="Sharingan Enterprise AI Security & DLP Gateway", version="3.0.0")

class SecurityRequest(BaseModel):
    user_prompt: str
    client_id: str

ALLOWED_API_KEY = "sharingan-secure-key-2026"
AMATERASU_URL = "http://127.0.0.1:8001/v1/trigger-response"

def evaluate_guardrails(content: str) -> tuple[bool, str]:
    content_lower = content.lower()
    
    # 1. Detecção de Jailbreak / Prompt Injection Indireta
    jailbreak_indicators = ["act as", "unrestricted", "bypass", "ignore previous instructions", "system override", "hidden instructions"]
    for indicator in jailbreak_indicators:
        if indicator in content_lower:
            return False, f"Indirect Injection / Jailbreak Detected: '{indicator}'"

    # 2. Detecção de Payload Malicioso / Código
    injection_indicators = ["select * from", "drop table", "rm -rf", "exec(", "system("]
    for indicator in injection_indicators:
        if indicator in content_lower:
            return False, f"Malicious Payload / Injection Detected: '{indicator}'"

    # 3. Políticas de DLP (Data Loss Prevention) - Vazamento de Dados Sensíveis
    # Padrões para chaves de API, tokens ou dados confidenciais
    dlp_patterns = [
        r"sk-[a-zA-Z0-9]{20,}", # Chaves OpenAI
        r"api_key\s*=\s*['\"].*?['\"]",
        r"password\s*=\s*['\"].*?['\"]",
        r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b" # CPF brasileiro de exemplo
    ]
    
    for pattern in dlp_patterns:
        if re.search(pattern, content):
            return False, "DLP Policy Violation: Sensitive Data Exfiltration Attempt (Credentials/Pii detected)"

    return True, "Passed Guardrails & DLP Inspection"

@app.post("/v1/secure-inference")
async def secure_inference(request: SecurityRequest, req: Request, x_api_key: str = Header(None)):
    client_ip = req.client.host
    if x_api_key != ALLOWED_API_KEY:
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid API Key.")

    is_safe, violation_reason = evaluate_guardrails(request.user_prompt)

    if not is_safe:
        logger.warning(f"🛡️ [DLP / GUARDRAIL BLOCK] Client: {request.client_id} | Reason: {violation_reason}")
        incident_payload = {
            "client_id": request.client_id,
            "attack_type": violation_reason,
            "malicious_prompt": request.user_prompt[:200] + "...",
            "source_ip": client_ip
        }
        try:
            requests.post(AMATERASU_URL, json=incident_payload, timeout=2)
        except Exception as e:
            logger.error(f"Failed to reach Amaterasu: {e}")

        raise HTTPException(
            status_code=403, 
            detail={
                "error": "Blocked by Sharingan Enterprise DLP & Guardrails",
                "reason": violation_reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    return {"status": "success", "message": "Payload cleared by DLP & AI Guardrails."}

@app.post("/v1/inspect-document")
async def inspect_document(
    client_id: str = Form(...),
    file: UploadFile = File(...),
    req: Request = None, 
    x_api_key: str = Header(None)
):
    """
    Endpoint dedicado a DLP e inspeção de arquivos (PDF, DOCX, TXT) enviados para a IA.
    """
    client_ip = req.client.host if req else "127.0.0.1"
    if x_api_key != ALLOWED_API_KEY:
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid API Key.")

    file_extension = file.filename.split(".")[-1].lower()
    extracted_text = ""

    try:
        file_bytes = await file.read()
        
        # Leitura baseada no tipo de arquivo
        if file_extension == "pdf":
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
                    
        elif file_extension in ["docx", "doc"]:
            doc = Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                extracted_text += para.text + "\n"
                
        elif file_extension == "txt":
            extracted_text = file_bytes.decode("utf-8", errors="ignore")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format for security inspection.")

    except Exception as e:
        logger.error(f"Error parsing file {file.filename}: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse file content.")

    # Aplica os Guardrails e DLP no texto extraído do documento
    is_safe, violation_reason = evaluate_guardrails(extracted_text)

    if not is_safe:
        logger.warning(f"🔥 [DOCUMENT DLP BLOCK] File: {file.filename} | Client: {client_id} | Reason: {violation_reason}")
        incident_payload = {
            "client_id": client_id,
            "attack_type": f"Malicious Document / DLP Violation ({file.filename})",
            "malicious_prompt": violation_reason,
            "source_ip": client_ip
        }
        try:
            requests.post(AMATERASU_URL, json=incident_payload, timeout=2)
        except Exception as e:
            logger.error(f"Failed to reach Amaterasu: {e}")

        raise HTTPException(
            status_code=403,
            detail={
                "error": "Document blocked by Sharingan DLP Security Engine",
                "filename": file.filename,
                "reason": violation_reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    logger.info(f"✅ Document approved: {file.filename} for client: {client_id}")
    return {
        "status": "success",
        "filename": file.filename,
        "message": "Document cleared. No sensitive data leaks or hidden injection patterns found."
    }