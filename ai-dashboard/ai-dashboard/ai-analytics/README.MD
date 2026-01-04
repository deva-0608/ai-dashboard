
========================
FILE: README.md
========================

# AI Reports Dashboard (FastAPI + LangGraph + Gemini)

This project implements a **chat-driven analytics dashboard** similar to
Autodesk ACC / Power BI Copilot.

Users can:
- Select a report
- View Excel data
- Ask natural language questions
- Get dynamic dashboards (charts + KPIs)

---

## 📁 Project Structure

ai-reports-platform/
│
├── backend/
│ ├── main.py
│ ├── config.py
│ ├── excel_loader.py
│ ├── state.py
│ │
│ ├── langgraph/
│ │ ├── runner.py
│ │ └── agents/
│ │ ├── schema_agent.py
│ │ ├── intent_agent.py
│ │ ├── query_agent.py
│ │ ├── viz_agent.py
│ │ ├── kpi_agent.py
│ │ └── insight_agent.py
│ │
│ ├── utils/
│ │ ├── dataframe_utils.py
│ │ ├── schema_utils.py
│ │ ├── chart_utils.py
│ │ ├── kpi_utils.py
│ │ └── prompt_utils.py
│ │
│ ├── requirements.txt
│ └── .env
│
├── frontend/
│ ├── reports.html
│ ├── report-list.html
│ ├── report-detail.html
│ ├── css/
│ └── js/
│
└── data/
└── projects/
├── custom-report/
├── project-report/
└── document-report/

yaml
Copy code

---

## 📊 Data Rules (IMPORTANT)

data/projects/{report_type}/{report_id}/{project_name}.xlsx

yaml
Copy code

Rules:
- Exactly **ONE Excel file per report folder**
- Excel filename = **project name**
- Folder name = **report_id**
- Excel content = source of truth

Supported report types:
- `custom-report`
- `project-report`
- `document-report`

---

## 🔑 Gemini API Key Setup

### 1️⃣ Create `.env` file

**backend/.env**
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY

csharp
Copy code

### 2️⃣ Load environment variables

At the **very top of `backend/main.py`**:
```python
from dotenv import load_dotenv
load_dotenv()
⚠️ This must be done before importing LangGraph agents.

▶️ How to Run Backend
bash
Copy code
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Backend URL:

arduino
Copy code
http://localhost:8000
Health check:

bash
Copy code
GET http://localhost:8000/health
🌐 Frontend Usage
Open directly in browser:

bash
Copy code
frontend/reports.html
Flow:

Choose report type

Select report ID

Excel table is displayed

Click chatbot icon

Enter prompt

Dashboard updates dynamically

Frontend uses:

HTML / CSS / JavaScript

Fetch API

ECharts for interactive charts

🔁 Runtime Flow
graphql
Copy code
User Prompt
   ↓
FastAPI /chat endpoint
   ↓
Excel loaded into pandas DataFrame
   ↓
LangGraph pipeline:
   schema → intent → query → viz → kpi → insight
   ↓
Charts + KPIs returned
   ↓
Frontend renders dashboard
🧠 Query Agent Design
LLM generates query plan (JSON)

Backend executes plan using pandas

No SQL

No eval

No dynamic code execution

Safe, deterministic, enterprise-grade.

🧪 Common Issues
API key is None
Ensure .env exists

Ensure load_dotenv() is called

Restart terminal

Start backend from backend/ directory

Charts not rendering
Check browser console

Verify backend /chat response

Ensure ECharts is loaded

✅ Status
✔ Backend complete
✔ LangGraph agents wired
✔ Excel-driven analytics
✔ Frontend-ready APIs

🚀 Optional Enhancements
Follow-up conversation memory

Date intelligence (month / quarter / year)

Auto chart selection

Auth & roles

Caching

👨‍💻 Notes
This project is designed to be:

-Modular
-Deterministic
-Safe (LLM plans, code executes)
-Easy to extend