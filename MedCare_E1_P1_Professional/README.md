# MedCare Pharma — E1 + P1 Professional UI

A hackathon-ready Flask prototype combining:

## E1 — Smart Restock Inventory Alert System
- SKU-wise inventory monitoring
- Minimum stock and safety stock thresholds
- Low-stock alerts
- Expiry monitoring
- Replenishment recommendations
- Replenishment approval workflow

## P1 — Demand Sensing & Replenishment Planning
- Historical vs forecast demand
- Demand trend visualization
- Demand signal overview
- What-if demand simulation
- Shortage detection
- Recommended replenishment quantities

## Run in VS Code

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:
http://127.0.0.1:5000

SQLite is built into Python. No separate sqlite3 pip install is required.

## GitHub

```bash
git init
git add .
git commit -m "Initial MedCare E1 P1 prototype"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```
