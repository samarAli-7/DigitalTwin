from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import sys

def query_digital_twin(query_text):
    # 1. Initialize embeddings (must be the same as used for creation)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 2. Load the persisted vector store
    persist_directory = "./chroma_db"
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    # 3. Perform similarity search
    results = vector_db.similarity_search(query_text, k=3)

    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Ask Isaac Newton a question: ")
    
    print(f"\nSearching for: {query}\n")
    results = query_digital_twin(query)
    
    print("Relevant information from Newton's life and work:\n")
    for i, res in enumerate(results):
        print(f"--- Result {i+1} (Source: {res.metadata.get('source', 'Unknown')}) ---")
        print(res.page_content)
        print("\n")
