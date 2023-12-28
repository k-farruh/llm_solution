import streamlit as st
import json

from PIL import Image

from llm_service import LLMService



# App title
st.set_page_config(page_title="🤗💬 Alibaba Cloud OpenSearch WebUI")
# Initialize the LLMService object with the configuration
with open('config.json') as f:
    cfg = json.load(f)
    solver = LLMService(cfg)

# Hugging Face Credentials
with st.sidebar:
    st.title('🤗💬 Alibaba Cloud OpenSearch WebUI')
    if ('username' in st.secrets) and ('password' in st.secrets):
        st.success('OpenSearch Login credentials already provided!', icon='✅')
        hf_email = st.secrets['username']
        hf_pass = st.secrets['password']
    else:
        hf_email = st.text_input('Enter E-mail:', type='password')
        hf_pass = st.text_input('Enter password:', type='password')
        if not (hf_email and hf_pass):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    st.markdown('📖 More detail about the OpenSearch LLM Intelligent Q&A Edition in this [Documentation](https://www.alibabacloud.com/help/en/open-search/llm-intelligent-q-a-version/)!')
    
    st.markdown('**Upload a file to the KBS**')

    # Upload a file
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        solver.upload_custom_knowledge()

        with open(uploaded_file.name, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.success('File saved successfully!')


    options = st.selectbox(
        'What is your role and permission',
        ['HR', 'Finance', 'Back-end', 'Front-end'])

    st.write('You selected:', options)



# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function for generating LLM response
def generate_response(prompt_input, email, passwd):
    # Hugging Face Login
    # sign = Login(email, passwd)
    # cookies = sign.login()
    # Create ChatBot                        
    # chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    level = options
    user_query = prompt_input
    answer = solver.content_query(user_query)
    return answer

# User-provided prompt
if prompt := st.chat_input(disabled=not (hf_email and hf_pass)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt, hf_email, hf_pass)
            # st.write(response)
            # category = response["body"]["result"]["data"][0]["reference"][0]["category"]
            answer = response

            print(answer)            
            st.write(answer)
            
    message = {"role": "assistant", "content": answer}
    st.session_state.messages.append(message)
