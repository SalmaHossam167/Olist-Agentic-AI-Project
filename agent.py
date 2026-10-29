import os
import sys
import re
from typing import Any, Dict, List, TypedDict

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from dotenv import load_dotenv

load_dotenv()

# Ensure the olist_ai_agent directory is on sys.path so local imports work
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from tools import SQLTool, pandas_summary as _pandas_summary

# ---- DB path ----
_DB_PATH = os.path.join(_THIS_DIR, 'olist.db')
_sql_tool = SQLTool(db_path=_DB_PATH)


def get_llm():
    """Return a plain LLM (no tool binding) — works with any provider."""
    if os.getenv('OPENAI_API_KEY'):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model='gpt-4o-mini', temperature=0)
    if os.getenv('GROQ_API_KEY'):
        from langchain_groq import ChatGroq
        # openai/gpt-oss-20b is fast and available on free tier
        return ChatGroq(model='openai/gpt-oss-20b', temperature=0)
    raise RuntimeError('No LLM API key found. Set OPENAI_API_KEY or GROQ_API_KEY.')


# ---- State ----

class OlistState(TypedDict, total=False):
    messages: List[BaseMessage]
    sql_query: str
    sql_result: str
    final_answer: str


# ---- Prompts ----

PLANNER_SYSTEM = """You are an expert SQL analyst for the Olist Brazilian e-commerce SQLite database.

Tables available:
- olist_customers (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
- olist_orders (order_id, customer_id, order_status, order_purchase_timestamp, order_delivered_customer_date, order_estimated_delivery_date)
- olist_order_items (order_id, order_item_id, product_id, seller_id, price, freight_value)
- olist_order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
- olist_order_reviews (review_id, order_id, review_score, review_comment_title, review_comment_message)
- olist_products (product_id, product_category_name, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
- olist_sellers (seller_id, seller_zip_code_prefix, seller_city, seller_state)
- olist_product_category_name_translation (product_category_name, product_category_name_english)

Given the user's question, write ONE valid SQLite SELECT query to answer it.
Respond with ONLY the raw SQL query — no markdown, no explanation, no code fences.
"""

# Escape all curly braces in PLANNER_SYSTEM so ChatPromptTemplate doesn't
# treat column names like {customer_id} as template variables.
PLANNER_SYSTEM = PLANNER_SYSTEM.replace('{', '{{').replace('}', '}}')

SYNTHESISER_SYSTEM = """You are a data analyst. Given the user's question and the raw SQL result below,
write a clear, concise, and insightful answer in plain English (or the same language as the question).
Do NOT show the SQL query itself. Focus on insights and key numbers.

SQL Result:
{sql_result}
"""
# Note: {sql_result} is intentionally left as a single-brace template variable
# — it will be filled via ChatPromptTemplate input, not via .format()


# ---- Nodes ----

def planner_node(state: OlistState) -> Dict[str, Any]:
    """Ask the LLM to generate a SQL query for the user's question."""
    messages = state.get('messages', [])
    user_question = ''
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            user_question = m.content
            break

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ('system', PLANNER_SYSTEM),
        ('human', '{question}'),
    ])
    response = (prompt | llm).invoke({'question': user_question})
    raw = response.content.strip()

    # Strip any accidental markdown fences
    raw = re.sub(r'^```[a-zA-Z]*\n?', '', raw)
    raw = re.sub(r'\n?```$', '', raw)
    sql = raw.strip()

    return {'sql_query': sql}


def executor_node(state: OlistState) -> Dict[str, Any]:
    """Execute the SQL query and store the result."""
    sql = state.get('sql_query', '').strip()
    if not sql:
        return {'sql_result': 'No SQL query was generated.'}
    try:
        rows = _sql_tool.execute_sql_query(sql)
        if not rows:
            result = 'The query returned no rows.'
        else:
            result = str(rows[:50])
    except Exception as e:
        result = f'SQL error: {e}'
    return {'sql_result': result}


def synthesiser_node(state: OlistState) -> Dict[str, Any]:
    """Ask the LLM to turn raw SQL results into a human-friendly answer."""
    messages = state.get('messages', [])
    user_question = ''
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            user_question = m.content
            break

    sql_result = state.get('sql_result', '')
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ('system', SYNTHESISER_SYSTEM),
        ('human', '{question}'),
    ])
    response = (prompt | llm).invoke({'question': user_question, 'sql_result': sql_result})
    answer = response.content.strip()

    new_messages = list(messages) + [AIMessage(content=answer)]
    return {'messages': new_messages, 'final_answer': answer}


# ---- Build graph ----

def build_agent():
    graph = StateGraph(OlistState)
    graph.add_node('planner', planner_node)
    graph.add_node('executor', executor_node)
    graph.add_node('synthesiser', synthesiser_node)

    graph.set_entry_point('planner')
    graph.add_edge('planner', 'executor')
    graph.add_edge('executor', 'synthesiser')
    graph.add_edge('synthesiser', END)

    return graph.compile()


agent = build_agent()

__all__ = ['agent', 'build_agent', 'OlistState']
