import os
import sys
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

# Ensure the olist_ai_agent directory is on sys.path so local imports work
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# Load .env if present (allows persisting keys across sessions if user creates a .env file)
load_dotenv()

st.set_page_config(page_title='Olist AI Agent', layout='wide')
st.title('📊 Olist AI Agent')
st.caption('Ask natural-language business questions about the Olist e-commerce dataset')

# ---------- Sidebar: LLM provider and API keys ----------
st.sidebar.header('🔑 API Configuration')
provider = st.sidebar.selectbox('LLM Provider', ['Groq', 'OpenAI'], index=0)
if provider == 'OpenAI':
    openai_key = st.sidebar.text_input('OpenAI API Key', type='password')
    if openai_key:
        os.environ['OPENAI_API_KEY'] = openai_key
        st.sidebar.success('OpenAI key set')
    os.environ.pop('GROQ_API_KEY', None)
else:
    groq_key = st.sidebar.text_input('Groq API Key', type='password')
    if groq_key:
        os.environ['GROQ_API_KEY'] = groq_key
        st.sidebar.success('Groq key set')
    os.environ.pop('OPENAI_API_KEY', None)

# ---------- Session state for conversation ----------
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ---------- Helper to get response from LangGraph agent ----------
def get_response(user_input: str) -> str:
    """Run the agent with the current conversation and return the AI answer."""
    from agent import build_agent

    agent = build_agent()

    # Add the new human message to history
    st.session_state.messages.append(HumanMessage(content=user_input))

    # Pass current message history as initial state
    initial_state = {"messages": list(st.session_state.messages)}

    # Invoke the graph — result is the final state dict
    result = agent.invoke(initial_state)

    if not result:
        return '(agent returned no result)'

    # Update conversation history from the result state
    updated_messages = result.get('messages', [])
    if updated_messages:
        st.session_state.messages = updated_messages

    # Extract the last AIMessage content as the answer
    for msg in reversed(updated_messages):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content

    # Fallback: check for a top-level 'final_answer' key in state
    fallback = result.get('final_answer', '')
    if fallback:
        return fallback

    return '(no response from agent)'


# ---------- Chat input form ----------
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input('Your question', placeholder='e.g., Total revenue by month for 2023')
    submitted = st.form_submit_button('Send')
    if submitted and user_input:
        with st.spinner('Thinking...'):
            try:
                answer = get_response(user_input)
            except Exception as e:
                answer = f"Error: {e}"
        st.success('Answer:')
        st.write(answer)

# ---------- Conversation history ----------
if st.session_state.messages:
    st.subheader('Conversation')
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            st.markdown(f"**You:** {msg.content}")
        elif isinstance(msg, AIMessage):
            st.markdown(f"**Agent:** {msg.content}")
