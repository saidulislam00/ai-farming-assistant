---
title: AI Farming Assistant Bangla
emoji: 🌾
sdk: docker
app_port: 7860
---

# AI Farming Assistant (Bangla) - Prototype

## Features
- Upload leaf image → PlantVillage disease detection (HF Transformers)
- OpenCV health score (yellowing + spots + heat stress)
- Bangla recommendations (rules + optional LLM)
- Bangla TTS (gTTS)
- Voice query endpoint (Google STT via SpeechRecognition)
- Dashboard with demo farms + chart

## Run
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

Open:
- http://localhost:8000/
- http://localhost:8000/dashboard/

