import json

from llm_service import LLMService



# Initialize the LLMService object with the configuration
with open('config.json') as f:
    cfg = json.load(f)
    solver = LLMService(cfg)


# Function for generating LLM response
def generate_response(prompt_input, email, passwd):
    # Hugging Face Login
    # sign = Login(email, passwd)
    # cookies = sign.login()
    # Create ChatBot                        
    # chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    # level = options
    user_query = prompt_input
    user_prompt_template = solver.create_user_query_prompt(user_query)
    answer = solver.user_query(user_query)
    return answer


prompt = "What was HSBC’s financial performance for 2022?"
hf_email = "asdf"
hf_pass = "asdf"

response = generate_response(prompt, hf_email, hf_pass)

answer = response

print(answer)            


# What was HSBC’s financial performance for 2022?

# What were the three focuses on HSBC's strength calls from FY 22? Focus on the transformation journey that the company is building. Include the ESG perspective as well