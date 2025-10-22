from newspaper import Article
from langchain.text_splitter import  RecursiveCharacterTextSplitter
import os
import time
from concurrent.futures import ThreadPoolExecutor
from langchain_core.documents import Document
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import shutil
from uuid import uuid4
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
import dotenv
from utils import reset_vectorstore
os.environ["USER_AGENT"] = "Mozilla/5.0"

OLLAMA_MODEL = "llama3.2:1b"
GROQ_MODEL = "llama-3.3-70b-versatile"
CHUNK_SIZE = 1000
# EMBEDDING_MODEL = 'Alibaba-NLP/gte-base-en-v1.5'
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = Path.cwd() / "resources/vectorstore"
COLLECTION_NAME = "real_estate"

#
dotenv.load_dotenv("./.env")
llm=None
vector_store=None


def initialize_component():
    global llm

    llm = ChatGroq(model=GROQ_MODEL,max_retries=2,max_tokens=None)



# get url-->article
def fetch_article(url):
    article = Article(url)
    article.download()
    article.parse()
    time.sleep(2)  # Delay to avoid hammering the server
    return {"title": article.title, "text": article.text, "source": url}

# url-->doc-->vector db
def process_urls(urls):
    global vector_store
    # reset vector db
    yield "Resetting vector store...✅"
    reset_vectorstore(VECTORSTORE_DIR)
    if llm==None:
        yield "Initializing Components"
        initialize_component()
    # url

    yield "Loading data...✅"
    # Use ThreadPoolExecutor to fetch articles in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_article, urls))
    # articles-->Documents

    docs = [
        Document(
            page_content=article["text"],
            metadata={"title": article["title"], "source": article["source"]}
        )
        for article in results]
    # split documents
    yield "Splitting text into chunks...✅"
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " "],  # Split on
                                                   chunk_size=200,  # Max characters per chunk
                                                   chunk_overlap=20  # Overlap between chunks

                                                   )

    # yield "Add chunks to vector database...✅"
    chunks = text_splitter.split_documents(docs)

    uuids=[str(uuid4())for _ in range(len(chunks))]



    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL,
                               model_kwargs={"trust_remote_code": True}
                               )

    # create chroma vector db and store documents/docs
    vector_store = Chroma.from_documents(
        collection_name=COLLECTION_NAME,
        documents=chunks,
        ids=uuids,

        embedding=embedding_function,
        persist_directory=str(VECTORSTORE_DIR)
    )
    yield "Done adding docs to vector database...✅"


def generate_answer(query):
    if llm==None:
        initialize_component()
    chat_history = []
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        return_source_documents=True,
        max_tokens_limit=4000
    )

    result = chain.invoke({"question": query, "chat_history": chat_history})
    answer = result["answer"]
    sources = result["source_documents"]
    return answer, sources
if __name__=="__main__":

    raw_urls = [
        "https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html"
        ]
    urls = [url.strip().replace(" ", "") for url in raw_urls]

    # vec=process_urls(urls)
    for p in process_urls(urls):
        print("")
    results = vector_store.similarity_search("What are  mortgage rates?", k=2)
    for doc in results:
        print(doc)
    print('////////////////////')
    answer,source=generate_answer("What affects mortgage rates?")
    print(answer)
    print(source)