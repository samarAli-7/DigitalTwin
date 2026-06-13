import streamlit as st
import os
import re
import io
import subprocess
import tempfile
import numpy as np
from dotenv import load_dotenv
from agent import get_agent, get_hooke
from memory_manager import LongTermMemoryManager
from voice_engine import speak, listen
from langchain_community.chat_message_histories import ChatMessageHistory

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Sir Isaac Newton: Digital Twin", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .newton-msg {
        background-color: #f1f5f9;
        color: #0f172a !important;
        padding: 15px;
        border-radius: 15px 15px 15px 0px;
        margin-bottom: 12px;
        border: 1px solid #cbd5e1;
        font-family: sans-serif;
    }
    .hooke-msg {
        background-color: #e0e7ff;
        color: #1e1b4b !important;
        padding: 15px;
        border-radius: 15px 15px 0px 15px;
        margin-bottom: 12px;
        border: 1px solid #c7d2fe;
    }
    .debate-header {
        text-align: center;
        font-family: 'Georgia', serif;
        color: #1e293b;
        background: #f8fafc;
        padding: 10px;
        border-radius: 10px;
        border: 2px solid #1e293b;
        margin-bottom: 25px;
    }
    .manuscript-box {
        background-color: #fffaf0;
        padding: 30px;
        border: 5px double #8b4513;
        font-family: 'Times New Roman', serif;
        color: #2c1810;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "debate_active" not in st.session_state:
    st.session_state.debate_active = False
if "debate_history" not in st.session_state:
    st.session_state.debate_history = []
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

def run_simulation(code):
    """Runs Pygame code in a separate process."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(code.encode())
        temp_file = f.name
    
    # Run in background to not block Streamlit
    subprocess.Popen(["python3", temp_file])

# Initialize Memory Manager
memory_manager = LongTermMemoryManager()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Newton Digital Twin")
    st.write("---")
    
    if not st.session_state.debate_active:
        st.session_state.voice_enabled = st.checkbox("Enable Voice Response", value=st.session_state.voice_enabled)
        
        if st.button("Speak to Newton"):
            with st.spinner("Newton is listening..."):
                voice_input = listen()
                if voice_input and "Newton hearing only silence" not in voice_input:
                    st.session_state.voice_prompt = voice_input
                    st.rerun() # Force rerun to process voice prompt
                elif voice_input:
                    st.warning(voice_input)
        
        st.write("---")
        if st.button("Publish Manuscript"):
            if st.session_state.chat_history.messages:
                with st.spinner("Newton is drafting the official manuscript..."):
                    agent = get_agent()
                    manuscript = agent.generate_manuscript(st.session_state.chat_history.messages)
                    st.session_state.current_manuscript = manuscript
            else:
                st.info("No discoveries yet to publish.")

        if st.button("End Conversation"):
            if st.session_state.messages:
                with st.spinner("Newton is documenting our discourse..."):
                    agent = get_agent()
                    conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                    memory_manager.extract_facts_and_save(conversation_text, agent)
                    st.info("Discourse documented. Newton bids thee farewell.")
                    import time
                    time.sleep(2)
                    os._exit(0)
            else:
                os._exit(0)

        st.write("---")
        st.subheader("Long-Term Memory")
        data = memory_manager.load_memory()
        if data["user_facts"]:
            st.success("Memory Active")
        else:
            st.info("No Memory Found")
        
        if st.button("Clear All Memory"):
            if os.path.exists("long_term_memory.json"):
                os.remove("long_term_memory.json")
            st.rerun()

    st.write("---")
    st.subheader("Rivalries")
    enable_rival = st.checkbox("Engage in Philosophical Dispute (Debate)", value=st.session_state.debate_active)
    
    if enable_rival and not st.session_state.debate_active:
        topic = st.text_input("Dispute Topic (e.g., Optics, Gravity):")
        if st.button("Begin Dispute"):
            if topic:
                st.session_state.debate_active = True
                st.session_state.debate_topic = topic
                st.session_state.debate_history = []
                st.rerun()
    
    if not enable_rival and st.session_state.debate_active:
        st.session_state.debate_active = False
        st.rerun()

# --- MANUSCRIPT DISPLAY ---
if "current_manuscript" in st.session_state:
    st.markdown("<div class='manuscript-box'>", unsafe_allow_html=True)
    st.subheader("Philosophical Transactions of the Royal Society")
    st.markdown(st.session_state.current_manuscript)
    if st.button("Close Manuscript"):
        del st.session_state.current_manuscript
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("---")

# --- DEBATE MODE UI ---
if st.session_state.debate_active:
    st.markdown(f"<h1 class='debate-header'>A Philosophical Dispute: {st.session_state.debate_topic}</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sir Isaac Newton")
        for msg in st.session_state.debate_history:
            if msg["role"] == "newton":
                st.markdown(f"<div class='newton-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    with col2:
        st.subheader("Robert Hooke")
        for msg in st.session_state.debate_history:
            if msg["role"] == "hooke":
                st.markdown(f"<div class='hooke-msg'>{msg['content']}</div>", unsafe_allow_html=True)

    st.write("---")
    c1, c2, c3 = st.columns([1, 1, 1])
    if c2.button("Continue Discourse"):
        agent = get_agent()
        hooke = get_hooke()
        last_hooke_msg = next((m["content"] for m in reversed(st.session_state.debate_history) if m["role"] == "hooke"), "Start the debate.")
        newton_response = agent.get_newton_response(f"Dispute with Hooke: {st.session_state.debate_topic}. Last claim: {last_hooke_msg}", st.session_state.session_id, "", [])
        st.session_state.debate_history.append({"role": "newton", "content": newton_response})
        st.rerun()

    if st.session_state.debate_history and st.session_state.debate_history[-1]["role"] == "newton":
        with st.spinner("Robert Hooke is drafting a rebuttal..."):
            import time
            time.sleep(1)
            hooke = get_hooke()
            hooke_response = hooke.get_rebuttal(st.session_state.debate_history[-1]["content"])
            st.session_state.debate_history.append({"role": "hooke", "content": hooke_response})
            st.rerun()

    if c3.button("End Dispute"):
        if st.session_state.debate_history:
            agent = get_agent()
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.debate_history])
            messages = [
                ("system", "Summarize the following scientific dispute."),
                ("user", history_text)
            ]
            response = agent.llm.invoke(messages)
            summary = response.content
            memory_manager.save_fact(f"Dispute on {st.session_state.debate_topic}: {summary}", agent=agent)
        st.session_state.debate_active = False
        st.rerun()

# --- NORMAL MODE UI ---
else:
    st.title("Sir Isaac Newton Digital Twin")
    st.write("*'To every action there is always opposed an equal reaction...'*")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Persistent Chat Input
    prompt = st.chat_input("Inquire of Sir Isaac...")

    # Check for voice prompt from session state (overrides text input)
    if "voice_prompt" in st.session_state:
        prompt = st.session_state.pop("voice_prompt")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Newton is reflecting..."):
                try:
                    agent = get_agent()
                    response_text = agent.get_newton_response(prompt, st.session_state.session_id, "", st.session_state.chat_history.messages)
                    
                    # Handle Illustration Logic
                    if "[ILLUSTRATION:" in response_text:
                        match = re.search(r"\[ILLUSTRATION: (.*?)\]", response_text)
                        if match:
                            sim_type = match.group(1)
                            sim_code = agent.get_illustration_code(sim_type)
                            if sim_code:
                                run_simulation(sim_code)
                                response_text = re.sub(r"\[ILLUSTRATION: .*?\]", f"\n\n*Newton has provided an illustration of {sim_type} in a new window.*", response_text)

                    message_placeholder.markdown(response_text)
                    if st.session_state.voice_enabled:
                        speak(response_text)
                    st.session_state.chat_history.add_user_message(prompt)
                    st.session_state.chat_history.add_ai_message(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"Error: {e}")
