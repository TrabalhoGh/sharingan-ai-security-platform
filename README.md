# 👁️ Sharingan AI Security Platform

<p align="center">
  <img src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop" width="150" alt="Akatsuki Cloud">
</p>

> A modular, enterprise-grade AI Security Platform featuring an intelligent Edge Gateway, automated SOAR incident response, and an adversarial Red Teaming evaluation suite. Designed under an *Uchiha/Akatsuki* aesthetic framework.

---

## 🏛️ Architecture Overview

The platform is structured as a **Monorepo** consisting of three core microservices and an operational SOC dashboard:

1. **`sharingan-gateway/`**: The FastAPI Edge Gateway responsible for real-time request authentication (API Keys), payload inspection, and multi-layered AI Guardrails (detecting prompt injections, jailbreaks, and sensitive data exfiltration).
2. **`amaterasu-soar/`**: The Security Orchestration, Automation, and Response (SOAR) engine that instantly catches security violations triggered by the gateway, logs threat intelligence data, and simulates automated containment playbooks.
3. **`kamui-redteam/`**: The adversarial evaluation suite powered by **Promptfoo**, configured to audit model boundaries and test firewall resilience against sophisticated attack vectors.
4. **`dashboard-soc/`**: A real-time Security Operations Center (SOC) web interface built with **Streamlit**, providing visual metrics, threat analytics, and an interactive attack simulator.

---

## 📂 Repository Structure

```text
sharingan-ai-security-platform/
├── sharingan-gateway/      # FastAPI Guardrails & Edge Gateway
├── amaterasu-soar/         # Automated Incident Response Engine
├── kamui-redteam/          # Promptfoo AI Red Teaming Suite
├── dashboard-soc/          # Streamlit SOC Operations Dashboard
└── docker-compose.yml      # Multi-container orchestration blueprint
```