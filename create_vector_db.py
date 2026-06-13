from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import shutil

# 1. Load documents
print("Loading documents from ./data/...")
loader = DirectoryLoader(
    path="./data/",         
    glob="**/*.txt",                
    loader_cls=TextLoader,
    loader_kwargs={"autodetect_encoding": True}
)
documents = loader.load()
print(f"Loaded {len(documents)} documents.")

# 2. Split documents
print("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
chunks = text_splitter.split_documents(documents)
print(f"Total chunks created: {len(chunks)}")

# 3. Create embeddings
print("Initializing embeddings (sentence-transformers/all-MiniLM-L6-v2)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. Create and persist vector store
persist_directory = "./chroma_db"
if os.path.exists(persist_directory):
    print(f"Removing existing vector store at {persist_directory}...")
    shutil.rmtree(persist_directory)

print("Creating new vector store...")
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=persist_directory
)

print(f"Vector store successfully created and persisted to {persist_directory}")
