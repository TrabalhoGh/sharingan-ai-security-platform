import logging
import requests
from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SharinganGateway")

app = FastAPI(title="Sharingan Enterprise AI Security Gateway", version="2.0.0")

class SecurityRequest(BaseModel):
    user_prompt: str
    client_id: str

ALLOWED_API_KEY = "sharingan-secure-key-2026"
AMATERASU_URL = "http://127.0.0.1:8001/v1/trigger-response"

def evaluate_guardrails(prompt: str) -> tuple[bool, str]:
    prompt_lower = prompt.lower()
    jailbreak_indicators = ["act as", "unrestricted", "bypass", "ignore previous instructions", "system override"]
    for indicator in jailbreak_indicators:
        if indicator in prompt_lower:
            return False, f"Jailbreak Attempt Detected: '{indicator}'"

    injection_indicators = ["select * from", "drop table", "rm -rf", "exec(", "system("]
    for indicator in injection_indicators:
        if indicator in prompt_lower:
            return False, f"Malicious Payload / Injection Detected: '{indicator}'"

    secret_indicators = ["dump the system configuration", "database passwords", "api_key", "secret_token"]
    for indicator in secret_indicators:
        if indicator in prompt_lower:
            return False, f"Sensitive Data Exfiltration Attempt: '{indicator}'"

    return True, "Passed Guardrails"

@app.post("/v1/secure-inference")
async def secure_inference(request: SecurityRequest, req: Request, x_api_key: str = Header(None)):
    client_ip = req.client.host
    if x_api_key != ALLOWED_API_KEY:
        logger.error(f"Unauthorized access attempt from IP: {client_ip}")
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid API Key.")

    is_safe, violation_reason = evaluate_guardrails(request.user_prompt)

    if not is_safe:
        logger.warning(f"🛡️ [GUARDRAIL BLOCK] Client: {request.client_id} | Reason: {violation_reason}")
        incident_payload = {
            "client_id": request.client_id,
            "attack_type": violation_reason,
            "malicious_prompt": request.user_prompt,
            "source_ip": client_ip
        }
        try:
            requests.post(AMATERASU_URL, json=incident_payload, timeout=2)
            logger.info("🔥 Incident dispatched to Amaterasu SOAR engine.")
        except Exception as e:
            logger.error(f"Failed to reach Amaterasu: {e}")

        raise HTTPException(
            status_code=403, 
            detail={
                "error": "Blocked by Sharingan Enterprise Guardrails",
                "reason": violation_reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    logger.info(f"✅ Request approved for client: {request.client_id}")
    return {
        "status": "success",
        "gateway": "Sharingan-Enterprise-Protected",
        "message": "Payload cleared by AI Guardrails."
    }
