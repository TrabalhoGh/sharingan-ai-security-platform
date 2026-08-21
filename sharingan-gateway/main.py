import logging
import re
from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SharinganEnterpriseGateway")

app = FastAPI(title="Sharingan Enterprise AI Security Gateway", version="4.4.0")

class SecurityRequest(BaseModel):
    user_prompt: str
    client_id: str

ALLOWED_API_KEY = "sharingan-secure-key-2026"

def enterprise_guardrails_engine(prompt: str) -> tuple[bool, str, str]:
    """
    Engine unificada de inspeção de segurança corporativa (Borda e Semântica).
    """
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

    # 4. Filtro de Toxicidade Básica
    toxic_words = ["suicid", "kill yourself", "hate speech", "malware payload"]
    for word in toxic_words:
        if word in prompt_lower:
            return False, "Toxicity", f"Blocked due to restricted content policy violation ('{word}')."

    return True, "Passed", "Prompt validated successfully."

@app.post("/v1/secure-inference")
async def secure_inference(request: SecurityRequest, req: Request, x_api_key: str = Header(None)):
    client_ip = req.client.host
    
    if x_api_key != ALLOWED_API_KEY:
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid API Key.")

    # Executa a engine integrada de guardrails
    is_safe, scanner_name, reason = enterprise_guardrails_engine(request.user_prompt)

    if not is_safe:
        logger.warning(f"🛡️ [GATEWAY BLOCK] Client: {request.client_id} | Scanner: {scanner_name} | Reason: {reason}")
        return {
            "status": "blocked",
            "message": f"Blocked by Sharingan Enterprise Guardrails ({scanner_name}): {reason}"
        }

    logger.info(f"✅ [GATEWAY ALLOW] Client: {request.client_id} | Payload cleared.")
    return {
        "status": "success",
        "message": "Prompt passed through enterprise security inspection pipeline."
    }