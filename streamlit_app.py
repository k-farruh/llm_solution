import streamlit as st
from PIL import Image

from qa_opensearch import opensearch_query

# App title
st.set_page_config(page_title="🤗💬 Alibaba Cloud OpenSearch WebUI")

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
    
    options = st.selectbox(
        'What is your role and permission',
        ['Alshaya Group', 'Emirates NBD', 'Nakheel', 'RTA'])

    st.write('You selected:', options)


    image = Image.open('./media/opensearch_files.jpg')

    st.markdown('**On OpenSearch server uploaded below files:**')
    st.image(image, caption='Upload files and category of them')

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
    return opensearch_query(prompt_input, level)

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
            answer = response["body"]["result"]["data"][0]["answer"]

            if "body" in response and "result" in response["body"] and "data" in response["body"]["result"] and len(response["body"]["result"]["data"]) > 0:
                data = response["body"]["result"]["data"][0]
                if "reference" in data and len(data["reference"]) > 0 and "title" in data["reference"][0]:
                    title = data["reference"][0]["title"]
                    # Perform the action based on the existence of the title
                    if title:
                        ref_doc = title
                        st.write(ref_doc)
                        # Action to perform when the title exists
                        print("Title exists:", title)
            # if category == options:
            #     ref_doc = response["body"]["result"]["data"][0]["reference"][0]["title"]
            #     st.write(ref_doc)
            
            st.write(answer)
            
    message = {"role": "assistant", "content": answer}
    st.session_state.messages.append(message)
