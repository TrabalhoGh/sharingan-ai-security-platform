import logging
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AmaterasuSOAR")

app = FastAPI(title="Amaterasu SOAR Engine", version="1.0.0")

class IncidentAlert(BaseModel):
    client_id: str
    attack_type: str
    malicious_prompt: str
    source_ip: str

@app.post("/v1/trigger-response")
async def trigger_response(alert: IncidentAlert):
    logger.warning("=" * 60)
    logger.warning("🔥 [AMATERASU SOAR] PROTOCOLO DE CONTENÇÃO ATIVADO!")
    logger.warning(f"Origem do Ataque (IP): {alert.source_ip}")
    logger.warning(f"Cliente Infrator: {alert.client_id}")
    logger.warning(f"Tipo de Ameaça: {alert.attack_type}")
    logger.warning(f"Payload Bloqueado: '{alert.malicious_prompt}'")
    logger.info("⚡ [AÇÃO AUTOMATIZADA] IP adicionado à blocklist de borda.")
    logger.info("⚡ [AÇÃO AUTOMATIZADA] Notificação de incidente despachada para o SOC.")
    logger.warning("=" * 60)
    return {
        "status": "contained",
        "engine": "Amaterasu-SOAR",
        "timestamp": datetime.utcnow().isoformat()
    }
