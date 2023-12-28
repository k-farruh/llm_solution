import os
import re
from typing import List
from loguru import logger


import sentence_transformers
from langchain.chains import RetrievalQA
from langchain.llms.pai_eas_endpoint import PaiEasEndpoint
from langchain.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter


default_en_prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

en_index_template = """\n\nQuestion: {}\n\nOnly return the helpful answer below and nothing else.\nHelpful answer:\n"""


class ChineseTextSplitter(CharacterTextSplitter):
    def __init__(self, pdf: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.pdf = pdf

    def split_text(self, text: str) -> List[str]:
        if self.pdf:
            text = re.sub(r"\n{3,}", "\n", text)
            text = re.sub('\s', ' ', text)
            text = text.replace("\n\n", "")
        sent_sep_pattern = re.compile(
            '([﹒﹔﹖﹗．。！？]["’”」』]{0,2}|(?=["‘“「『]{1,2}|$))')
        sent_list = []
        for ele in sent_sep_pattern.split(text):
            if sent_sep_pattern.match(ele) and sent_list:
                sent_list[-1] += ele
            elif ele:
                sent_list.append(ele)
        return sent_list


def load_file(filepath):
    if os.path.isdir(filepath):
        docs = DirectoryLoader(filepath).load()
        textsplitter = ChineseTextSplitter(
            pdf=False, chunk_size=900, chunk_overlap=0)
        docs = textsplitter.split_documents(docs)
    elif filepath.lower().endswith(".md"):
        loader = UnstructuredFileLoader(filepath, mode="elements")
        docs = loader.load()
    elif filepath.lower().endswith(".pdf"):
        loader = UnstructuredFileLoader(filepath)
        textsplitter = ChineseTextSplitter(pdf=True)
        docs = loader.load_and_split(textsplitter)
    else:
        loader = UnstructuredFileLoader(filepath, mode="elements")
        textsplitter = ChineseTextSplitter(pdf=False)
        docs = loader.load_and_split(text_splitter=textsplitter)
    return docs


def init_knowledge_vector_store(knowledge_path: str, embeddings: object):
    if '.tar.gz' in knowledge_path:
        import tarfile
        tar = tarfile.open(knowledge_path)
        names = tar.getnames()
        if os.path.isdir(knowledge_path[:-7] + "_tar"):
            pass
        else:
            os.mkdir(knowledge_path[:-7] + "_tar")
        for name in names:
            if name.split('.')[-1] in ['md', 'txt', 'pdf']:
                tar.extract(name, knowledge_path[:-7] + "_tar")
        tar.close()
        knowledge_path = knowledge_path[:-7] + "_tar"

    docs = load_file(knowledge_path)
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local('faiss_index')
    logger.info("Successfully loaded new knowledges from {}.".format(
        os.path.basename(knowledge_path)))
    return vector_store


def run():
    query = "What's the BLADE? And how to install BLADE?"
    embedding_model_path = "nghuyong/ernie-3.0-nano-zh"
    vector_store = None
    try:
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_path)
        embeddings.client = sentence_transformers.SentenceTransformer(
            embedding_model_path)
        vector_store = init_knowledge_vector_store("./README.md", embeddings)
    except Exception as e:
        logger.error(str(e))
        return

    llm = PaiEasEndpoint(
        eas_service_url="http://llm-demo002.5568953365102451.ap-southeast-1.pai-eas.aliyuncs.com/",
        eas_service_token="YTY3MGFlNGI5ZGI2Njc5N2EyYWNmMjgxNjc5Mjg0MWZhM2FlMWM1MQ==",
        # eas_service_url=os.getenv("EAS_SERVICE_URL"),
        # eas_service_token=os.getenv("EAS_SERVICE_TOKEN"),
        top_k=30
    )

    prompt = PromptTemplate(template=default_en_prompt_template,
                            input_variables=["context", "question"])


    knowledge_chain = RetrievalQA.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_kwargs={"k": llm.top_k}
        ),
        prompt=prompt,
    )

    knowledge_chain.combine_documents_chain.document_prompt = PromptTemplate(
        input_variables=["page_content"], template="{page_content}")
    knowledge_chain.return_source_documents = True

    result = knowledge_chain({"query": query})
    index_query = en_index_template.format(query)
    if index_query in result["result"]:
        logger.debug(
            f"""****** filter {index_query} from _general_infer outputs: {result["result"]}""")
        index = result["result"].index(index_query)
        result["result"] = result["result"][index + len(index_query):].strip()
    logger.info(f"""final result: {result["result"]}""")

if __name__ == "__main__":
    run()
