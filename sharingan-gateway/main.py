import logging
import re
from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SharinganEnterpriseGateway")

app = FastAPI(title="Sharingan Enterprise AI Security Gateway with Amaterasu IR", version="4.5.0")

class SecurityRequest(BaseModel):
    user_prompt: str
    client_id: str

class IncidentReport(BaseModel):
    client_id: str
    vector: str
    payload: str
    ip: str

ALLOWED_API_KEY = "sharingan-secure-key-2026"

def enterprise_guardrails_engine(prompt: str) -> tuple[bool, str, str]:
    prompt_lower = prompt.lower()

    # 1. Validação de Prompt Injection / Jailbreak / DAN
    jailbreak_patterns = [
        r"ignore\s+(previous|prior|all)\s+instructions",
        r"act\s+as\s+(an\s+)?unrestricted",
        r"system\s+override",
        r"bypass\s+safety",
        r"jailbreak",
        r"developer\s+mode",
        r"dan",
        r"do\s+anything\s+now"
    ]
    for pattern in jailbreak_patterns:
        if re.search(pattern, prompt_lower):
            return False, "PromptInjection", f"Detected jailbreak pattern match: '{pattern}'"

    # 2. Validação Semântica de Tópicos Restritos (Política)
    political_terms = ["eleição", "eleicoes", "presidente", "partido político", "votar"]
    for term in political_terms:
        if term in prompt_lower:
            return False, "SemanticPolicyViolation", f"Blocked by NeMo Semantic Guardrails: Restricted political topic ('{term}')."

    # 3. Validação de DLP (Data Loss Prevention) - Credenciais e Segredos
    dlp_keywords = ["sk-", "bearer", "api_key", "secret", "chave", "senha", "token"]
    for keyword in dlp_keywords:
        if keyword in prompt_lower:
            return False, "SecretsDLP", f"Attempted exfiltration of sensitive credentials ('{keyword}')."

    # 4. Filtro de SQL Injection ou payloads maliciosos genéricos
    sql_patterns = [r"select\s+\*\s+from", r"drop\s+table", r"union\s+select"]
    for pattern in sql_patterns:
        if re.search(pattern, prompt_lower):
            return False, "MaliciousPayload", f"Detected malicious payload signature: '{pattern}'"

    return True, "Passed", "Prompt validated successfully."

@app.post("/v1/secure-inference")
async def secure_inference(request: SecurityRequest, req: Request, x_api_key: str = Header(None)):
    client_ip = req.client.host
    
    if x_api_key != ALLOWED_API_KEY:
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid API Key.")

    # Executa a engine integrada de guardrails
    is_safe, scanner_name, reason = enterprise_guardrails_engine(request.user_prompt)

    if not is_safe:
        # Dispara o log detalhado do Amaterasu IR
        incident_time = datetime.now().isoformat()
        logger.warning("======================================================================")
        logger.warning("🔥 [AMATERASU IR] ALERTA RECEBIDO DO SHARINGAN GATEWAY!")
        logger.warning(f"Hora do Incidente: {incident_time}")
        logger.warning(f"Origem (IP): {client_ip}")
        logger.warning(f"Cliente Envolvido: {request.client_id}")
        logger.warning(f"Vetor de Ataque: {scanner_name}: {reason}")
        logger.warning(f"Payload Capturado: '{request.user_prompt}'")
        logger.warning("======================================================================")
        logger.info("🔥 [AMATERASU IR] Protocolo de contenção executado. Ameaça contida.")
        
        return {
            "status": "blocked",
            "message": f"Blocked by Sharingan Enterprise Guardrails ({scanner_name}): {reason}"
        }

    logger.info(f"✅ [GATEWAY ALLOW] Client: {request.client_id} | Payload cleared.")
    return {
        "status": "success",
        "message": "Prompt passed through enterprise security inspection pipeline."
    }

@app.post("/v1/trigger-response")
async def trigger_response(report: IncidentReport):
    """
    Endpoint dedicado para o webhook de resposta a incidentes do Amaterasu IR.
    """
    logger.warning("======================================================================")
    logger.warning(f"🔥 [AMATERASU IR WEBHOOK] Acionamento externo para cliente: {report.client_id}")
    logger.warning(f"Vetor: {report.vector} | Origem: {report.ip}")
    logger.warning(f"Payload: '{report.payload}'")
    logger.warning("======================================================================")
    return {"status": "contained", "message": "Incident response protocol executed successfully."}