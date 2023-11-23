# Step-by-Step Tutorial
Here: [Tutorial: Building an Exciting Journey for Your GenAI Application with Llama 2, AnalyticDB, PAI-EAS](https://www.alibabacloud.com/blog/600283)
## Demo demonstration combining LLM, LangChain, ADB

- Upload the user's local knowledge base file and generate embedding based on the SGPT-125M model
- Generate embedding and store it in AnalyticDB, and use it for subsequent vector retrieval
- Input the user question, output the prompt of the question, and use it to generate the answer in the subsequent LLM part
- Send the generated prompt to the chatglm2 service deployed on eas, get the answer to the question in real time, and complete the link

### Step 1: Development Environment

1. Pull the existing docker environment to prevent unavailability caused by environment installation failure
```bash
docker pull mybigpai-registry.cn-beijing.cr.aliyuncs.com/mybigpai/chatglm_webui_test:2.2
```

2. Clone the project
```bash
git clone git@gitlab.alibaba-inc.com:pai_biz_arch/LLM_Solution.git
cd LLM_Solution
```

3. Mount the local project to docker and start it
```bash
sudo docker run -t -d --network host --name llm_demo -v $(pwd):/home/LLM_Solution --gpus all mybigpai-registry.cn-beijing.cr.aliyuncs.com/mybigpai/chatglm_webui_test:2.2
docker exec -it llm_demo bash
cd /home/LLM_Solution
```

### Step 2: Configure config.json

- embedding: The path of the embedding model, which can be customized by the user. By default, /code/SGPT-125M-weightedmean-nli-bitfit in docker is used.
- EASCfg: The configuration has been deployed on the EAS LLM model service, which can be customized by the user
- ADBCfg: AnalyticDB related environment configuration
- create_docs: knowledge base path and related file configuration, all files under /docs are used by default
- query_topk: the number of relevant results returned by the query
- prompt_template: User-defined prompt

### Step 3: Run main.py
1. Upload and index the user-specified knowledge base
```bash
python main.py --config config.json --upload true
```

2. User request query
```bash
python main.py --config config.json --query "user question"
```

### Show results:
```bash
python main.py --config myconfig.json --query What is Machine Learning PAI?

Output:
The answer is: Sorry, this question cannot be answered based on known information.
```

```bash
python main.py --config myconfig.json --upload true

Output:
Insert into AnalyticDB Success.
```

```bash
python main.py --config myconfig.json --query What is Machine Learning PAI?

Output:
The answer is: Machine learning PAI is Alibaba Cloud's artificial intelligence platform, which provides one-stop machine learning solutions, including supervised learning, unsupervised learning, and enhanced learning. It can provide users with a mapping from input feature vectors to target values, and help users solve various machine learning problems, such as product recommendations, user group portraits, and accurate advertising placement.
```