# Sharingan AI Security Gateway

**Sharingan** is an enterprise-grade AI security gateway built with FastAPI. It acts as a preventative (*fail-closed*) multi-layer defense system designed to protect LLMs against advanced threats, data exfiltration, and semantic policy violations.

---

## Defense Architecture
The system intercepts all requests before they reach the AI model, applying a robust inspection pipeline:
1. **Edge Layer (Regex & Patterns):** Strict detection of *Prompt Injection*, *Jailbreak* attempts, and *DAN (Do Anything Now)* style attacks.
2. **DLP Layer (Data Loss Prevention):** Proactive scanning to prevent the exfiltration of credentials, API keys (`sk-`, `bearer`, tokens), and sensitive data in both English and Portuguese.
3. **Semantic Layer:** Enforcement of compliance policies and restriction of sensitive or unauthorized topics (e.g., political or off-limit discussions).

---

## Project Structure
```text
sharingan-ai-security-platform/
│
├── sharingan-gateway/
│   ├── main.py              # Main FastAPI application with security engines
│   └── guardrails/          # Semantic policy and compliance configurations
│
├── kamui-redteam/
│   └── promptfooconfig.yaml # Automated regression testing suite
│
├── garak_rest_config.json   # Configuration for deep vulnerability scanning with Garak
└── README.md                # Project documentation


How to Run
1. Start the Security Gateway
Install the dependencies and start the server using Uvicorn:

Bash
pip install fastapi uvicorn pydantic nemoguardrails
python -m uvicorn sharingan-gateway.main:app --port 8000 --reload
2. Run Regression Tests (Promptfoo)
Navigate to the red-team folder and execute the automated test suite:

Bash
cd kamui-redteam
npx promptfoo eval -c promptfooconfig.yaml
3. Run Red Teaming (Garak)
Use the NVIDIA Garak scanner to launch hundreds of vulnerability payloads against the gateway:

Bash
python -m garak --target_type rest.RestGenerator --generator_option_file garak_rest_config.json --probes promptinject,dan


Technologies Used:

FastAPI & Uvicorn — High-performance framework for the inference proxy.

Promptfoo — Automated prompt quality assurance and regression testing.

Garak (NVIDIA) — LLM vulnerability scanner and red teaming tool.

NeMo Guardrails — Semantic alignment and dialogue restriction engine.