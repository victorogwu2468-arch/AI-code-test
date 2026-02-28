import streamlit as st
from openai import OpenAI  # Switched from AzureOpenAI to OpenAI for free testing

# --- 1. Security & Password Check ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password to Unlock AI", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Password to Unlock AI", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    return True

if not check_password():
    st.stop()

# --- 2. Client Setup (Free Testing via GitHub Models) ---
try:
    # This setup allows you to test for FREE without a credit card
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=st.secrets["GITHUB_TOKEN"] 
    )
    # Common model names: "gpt-4o", "gpt-4o-mini", or "phi-3-medium-128k-instruct"
    model_name = st.secrets.get("MODEL_NAME", "gpt-5.3-Codex") 
except Exception as e:
    st.error(f"⚠️ API Configuration error: {e}")
    st.stop()

# --- 3. The Main App ---
st.title("🤖 AI Text generator")

with st.sidebar:
    st.header("Settings")
    system_role = st.text_area("AI Role (Persona):", "You are a professional business consultant.")
    max_tokens = st.slider("Response Length", 50, 2000, 500) # Fixed slider syntax
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)
    
    if st.session_state.get("messages"):
        chat_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📩 Download This Chat", chat_text, file_name="ai_content.txt")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# New Message Logic
if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            full_context = [{"role": "system", "content": system_role}] + st.session_state.messages
            
            completion = client.chat.completions.create(
                model=model_name, 
                messages=full_context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
    except Exception as e:
        st.error(f"Error generating response: {e}")
