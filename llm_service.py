import json
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import CSVLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import AnalyticDB
from langchain.llms.pai_eas_endpoint import PaiEasEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from loguru import logger



import os
import time
import argparse


class LLMService:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.vector_db = self.connect_adb()
        self.llm = self.activate_llm()
    
    def activate_llm(self):
        llm = PaiEasEndpoint(
            eas_service_url = self.cfg['EASCfg']['url'],
            eas_service_token = self.cfg['EASCfg']['token'],
            top_k=3
        )
        return llm
    
    def connect_adb(self):
        connection_string = AnalyticDB.connection_string_from_db_params(
            host=self.cfg['ADBCfg']['PG_HOST'],
            database=self.cfg['ADBCfg']['PG_DATABASE'],
            user=self.cfg['ADBCfg']['PG_USER'],
            password=self.cfg['ADBCfg']['PG_PASSWORD'],
            driver='psycopg2cffi',
            port=5432,
        )
        embedding_model = self.cfg['embedding']['embedding_model']
        model_dir = self.cfg['embedding']['model_dir']
        embed = HuggingFaceEmbeddings(model_name=os.path.join(model_dir, embedding_model), model_kwargs={'device': 'cpu'})
        
        vector_db = AnalyticDB(
            embedding_function=embed,
            embedding_dimension=self.cfg['embedding']['embedding_dimension'],
            connection_string=connection_string,
            # pre_delete_collection=self.is_delete,
        )
        return vector_db
    

    def upload_file_knowledge(self, file):
        """
        Check the file extension and call the respective function to handle the file.
        """
        # Call the appropriate function based on the file extension
        if file.lower().endswith('.csv'):
            # Load csv file
            documents = CSVLoader(file).load()
        elif file.lower().endswith('.md'):
            # Load markdown file
            documents = UnstructuredMarkdownLoader(file).load()
        elif file.lower().endswith('.txt'):
            # Load text file
            documents = TextLoader(file).load()
        elif file.lower().endswith('.pdf'):
            # Load PDF file
            documents = PyPDFLoader(file).load()
        elif file.lower().endswith('.html'):
            # Load HTML file
            documents = UnstructuredHTMLLoader(file).load()
        else:
            raise ValueError(f"Unsupported file extension: {file.lower()}")

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)
        start_time = time.time()
        self.vector_db.add_documents(docs)
        end_time = time.time()
        print("Insert into AnalyticDB Success. Cost time: {} s".format(end_time - start_time)) 

    def upload_directory(self, dir_path):
        docs = DirectoryLoader(dir_path, glob=self.cfg['create_docs']['glob'], show_progress=True).load()
        text_splitter = CharacterTextSplitter(chunk_size=int(self.cfg['create_docs']['chunk_size']), chunk_overlap=self.cfg['create_docs']['chunk_overlap'])
        docs = text_splitter.split_documents(docs)
        start_time = time.time()
        self.vector_db.add_documents(docs)
        end_time = time.time()
        print("Insert into AnalyticDB Success. Cost time: {} s".format(end_time - start_time))
    
    def content_query(self, question):
        docs = self.vector_db.similarity_search(question, k=int(self.cfg['result_topk']))
        context_docs = ""
        for idx, doc in enumerate(docs):
            context_docs += "-----\n\n"+str(idx+1)+".\n"+doc.page_content
        context_docs += "\n\n-----\n\n"

        template = self.cfg['prompt_template']

        prompt = PromptTemplate(template=template,
                        input_variables=["context", "question"])


        knowledge_chain = RetrievalQA.from_llm(
            llm=self.llm,
            retriever=self.vector_db.as_retriever(
                search_kwargs={"k": self.llm.top_k}
            ),
            prompt=prompt,
        )

        knowledge_chain.combine_documents_chain.document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}")
        knowledge_chain.return_source_documents = True

        result = knowledge_chain({"query": question})

        return result['result']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Command line argument parser')
    parser.add_argument('--config', type=str, help='json configuration file input', required=True)
    parser.add_argument('--upload_file', type=str, help='Path to file to upload knowledge from')
    parser.add_argument('--upload_dir', type=str, help='Path to directory to upload knowledge from')
    parser.add_argument('--question', help='User request question')  # Changed from --query to --question
    args = parser.parse_args()

    if not args.upload_file and not args.upload_dir and not args.question:  # Changed from args.query to args.question
        print('No operation specified. Use --upload_file, --upload_dir, or --question.')  # Changed message accordingly
    else:
        if os.path.exists(args.config):
            with open(args.config) as f:
                cfg = json.load(f)
            solver = LLMService(cfg)
            if args.upload_file:
                print('Uploading file to ADB.')
                solver.upload_file_knowledge(args.upload_file)
            if args.upload_dir:
                print('Uploading directory to ADB.')
                solver.upload_directory(args.upload_dir)
            if args.question:  # Changed from args.query to args.question
                answer = solver.content_query(args.question)  # Changed from args.query to args.question
                print("The answer is: ", answer)
        else:
            print(f"{args.config} does not exist.")

# python llm_service.py --config config.json --question "Tell me about Machine Learning PAI"