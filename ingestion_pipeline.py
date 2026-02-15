import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import time
import random

load_dotenv()

def load_documents(docs_path="docs"):
    """Load all the document files from the docs directory"""
    print(f"Loading documents form {docs_path}...")
    
    #Check if docs directory is present or not
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The directory {docs_path} does not exist. Please create it and add your requied files")

    #Load all .txt files from the docs directory
    loader = DirectoryLoader(
        path = docs_path,
        glob = "**/*.txt", # Pattern: load all .txt files (including subfolders)
        loader_cls = TextLoader, 
        loader_kwargs={
            "encoding":"utf-8",  #force UTF-8 encoding (prevents Windos cp1252 errors)
            "autodetect_encoding":True   #Automatically detcet encoding if UTF-8 fails
        }
    )
    
    documents = loader.load() #load all the documents and displays 
    
    if len(documents) == 0:
        raise FileNotFoundError(f"No .txt files are found at the path {docs_path}. Please add the required files.")
    
    #show info about first 2 docs
    for i,doc in enumerate(documents[:2]):
        print(f"\nDocument {i+1}:")
        print(f" Source: {doc.metadata['source']}") #prints whatever is paired with key named as source
        print(f" Content length : {len(doc.page_content)} characters")
        print(f" Content preview: {doc.page_content[:100]}...")
        print(f" metadata: {doc.metadata}")

    return documents
    
    
    
def split_documents(documents, chunk_size=1000, chunk_overlap=0):
    """Split documents to smaller chunks"""
    print("Splittin the given documents into chunks...")
    
    text_splitter = CharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )
    
    chunks = text_splitter.split_documents(documents)
    
    if chunks:
        
        for i, chunk in enumerate(chunks[:5]):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Source: {chunk.metadata['source']}")
            print(f"Length: {len(chunk.page_content)} characters")
            print(f"Content:")
            print(chunk.page_content)
            print(f"-" * 50)
        
        if len(chunks)>5:
            print(f"\n and {len(chunks)-5} more chunks")
            
        return chunks



def create_vector_store(chunks, persist_directory="db/chroma_db"):
    print("Creating embeddings and storing in ChromaDB")

    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    # Create (or load) the DB WITHOUT embedding everything at once
    vectorstore = Chroma(
        collection_name="rag",
        embedding_function=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )

    MAX_REQUESTS_PER_MINUTE = 100
    request_count = 0
    minute_start = time.time()

    total = len(chunks)
    i = 0

    while i < total:
        # reset each minute
        elapsed = time.time() - minute_start
        if elapsed >= 60:
            request_count = 0
            minute_start = time.time()
            elapsed = 0

        # if hit 100 requests, wait for next minute window
        if request_count >= MAX_REQUESTS_PER_MINUTE:
            sleep_for = 60 - elapsed
            print(f"⏳ 100/min hit. Sleeping {sleep_for:.1f}s...")
            time.sleep(max(0, sleep_for))
            request_count = 0
            minute_start = time.time()

        chunk = chunks[i]

        try:
            # 1 chunk = 1 request (safe, slower)
            vectorstore.add_texts(
                texts=[chunk.page_content],
                metadatas=[chunk.metadata],
            )
            request_count += 1
            i += 1

            if i % 25 == 0 or i == total:
                print(f"✅ Embedded {i}/{total}")

        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                # obey server hint: it says retryDelay ~37s
                wait = 40 + random.uniform(0, 5)
                print(f"⚠️ 429 rate limited. Sleeping {wait:.1f}s then retry...")
                time.sleep(wait)
            else:
                raise

    vectorstore.persist()
    print(f"✅ Done. Saved to {persist_directory}")
    return vectorstore
    
        
def main():
    print("Main Function is woking")
    
    docs_path = "docs"
    
    #1. Loading the files
    documents = load_documents(docs_path)
    
    #2. Chunking the files
    
    chunks = split_documents(documents)
    #3. Embedding and Storing in Vector DB
    
    vectorstore = create_vector_store(chunks,persist_directory="db/chroma_db")
    



if __name__ == "__main__":
    main()