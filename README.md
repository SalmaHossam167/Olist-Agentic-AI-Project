# 🤖 Olist Agentic AI

<div align="center">

### Ask business questions about 99,441 real e-commerce orders — in plain English, answered in seconds

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-7C3AED?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Free_LLM-F55036?style=for-the-badge)](https://console.groq.com)
[![Status](https://img.shields.io/badge/Status-Live-22C55E?style=for-the-badge)](#)

</div>

---

## What Is This?

A natural-language AI analyst built on top of the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

You type a business question. The agent writes the SQL, queries the database, and gives you a clear answer — no SQL knowledge needed, no dashboards to maintain.

![Olist AI Agent Demo](outputs/agent_demo.png)

---

## Why It Matters

Data teams are a bottleneck. A business question like *"which product categories drive the most revenue?"* normally takes hours — write a ticket, wait for a data analyst, get a static spreadsheet back.

This agent removes that bottleneck entirely:

| Old Way | With This Agent |
|---------|----------------|
| Write a ticket to the data team | Type your question directly |
| Wait hours or days | Get an answer in under 10 seconds |
| Receive a static report | Query live data anytime |
| Requires SQL knowledge | Requires nothing — just English |

---

## How It Works

The agent uses a 3-step LangGraph pipeline:

```
Your Question
      │
      ▼
┌─────────────┐
│   Planner   │  LLM reads your question and writes a SQLite SELECT query
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Executor   │  Runs the query against the live Olist SQLite database
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Synthesiser  │  LLM reads the raw rows and writes a clear, insightful answer
└──────┬───────┘
       │
       ▼
  Streamlit UI
```

No tool-calling API quirks. No JSON parsing hacks. Just a clean, reliable pipeline that works with any LLM provider.

---

## Example Questions You Can Ask

| Question | What You Get |
|----------|-------------|
| *What are the top 5 product categories by revenue?* | Ranked list with totals and % share |
| *Which states have the worst average delivery delay?* | State-by-state delay breakdown |
| *How many orders were placed each month in 2018?* | Monthly order volume trend |
| *What percentage of orders were delivered late?* | Count, percentage, and context |
| *Which sellers have the highest average review score?* | Seller ranking by customer rating |
| *What is the most common payment method?* | Payment type breakdown |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI orchestration | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| LLM | Groq `openai/gpt-oss-20b` (free tier) or OpenAI `gpt-4o-mini` |
| UI | [Streamlit](https://streamlit.io) |
| Database | SQLite (built from Olist CSVs via `db_setup.py`) |
| Language | Python 3.12 |

---

## Setup

### 1. Clone
```bash
git clone https://github.com/SalmaHossam167/Olist-Agentic-AI-Project.git
cd Olist-Agentic-AI-Project
```

### 2. Install dependencies
```bash
pip install -r olist_ai_agent/requirements.txt
```

### 3. Add your API key
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your-groq-key-here
```
> Get a free key at [console.groq.com](https://console.groq.com) — no credit card needed.

### 4. Build the database
Download the Olist CSVs from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) or [Google Drive](https://drive.google.com/drive/folders/159si9BxbBBRKrhgFc6h__nQ-OkqNCoCa?usp=drive_link), place them in `data/`, then run:
```bash
python olist_ai_agent/db_setup.py
```

### 5. Launch
```bash
streamlit run olist_ai_agent/app.py
```
Open [http://localhost:8501](http://localhost:8501), paste your API key in the sidebar, and start asking.

---

## Project Structure

```
Olist-Agentic-AI-Project/
│
├── olist_ai_agent/
│   ├── agent.py          # LangGraph pipeline (planner → executor → synthesiser)
│   ├── app.py            # Streamlit chat UI
│   ├── tools.py          # SQL execution tool
│   ├── db_setup.py       # Loads CSVs into SQLite
│   └── requirements.txt
│
├── data/                 # Olist CSV files (not committed — download separately)
├── outputs/              # Charts from the analysis pipeline
└── .env                  # API keys (never committed)
```

---

## The Data Behind It

The agent queries a SQLite database built from the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — **99,441 orders** across 9 tables covering customers, orders, products, sellers, payments, and reviews.

Key numbers surfaced during the initial analysis that motivated building this agent:

- **R$ 16M+** total revenue across the dataset
- **96.9% churn rate** — most customers buy exactly once
- **8.1% late delivery rate** — a major driver of 1-star reviews
- **Health & Beauty** is the top revenue category at R$1.26M

Instead of building static dashboards for these numbers, the agent lets the business keep asking new questions as they come up.

---

## 👩‍💻 Author

**Salma Hossam**  
[GitHub @SalmaHossam167](https://github.com/SalmaHossam167) · salmahoss666@gmail.com
 
