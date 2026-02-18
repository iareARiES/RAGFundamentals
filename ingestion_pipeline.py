import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import json

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
    
    if not chunks:
        raise ValueError("No chunks were produced. Check your documents.")    
    
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
        
    
    
    

#data loaded in the data as a list of diactionaries and then loading in the json file together

def save_chunks(chunks, filename="db/chunks"):
    os.makedirs(os.path.dirname(filename),exist_ok =True)
    
    data = [
        {
            "index":i,
            "content": chunk.page_content,
            "metadata": chunk.metadata
        }
        for i,chunk in enumerate(chunks,start=1)  #indexing start from 1
    ]
    with open(filename, "w", encoding ="utf-8") as f:
        json.dump(data,f,indent=4)
    
    print(f"Chunks successfully saved at {filename}")
    
    
    
def create_vector_store(chunksjson_dir = "db/chunks", persist_directory="db/chroma_db"):
    """
    Load chunks from JSON, add them to ChromaDB, and POP them from the JSON list,
    then save back the updated JSON (so next run continues).
    """
    
    print("Creating embeddings and storing in ChromaDB")
    
    with open(chunksjson_dir,"r",encoding="utf-8") as f:
        chunks = json.load(f)
        
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
    #better complexity O(1) from O(n2) better than pop(0)
    chunks.reverse()
    while chunks:
        chunk = chunks.pop()
        
        print(f"\n🔹 Processing Chunk Index: {chunk['index']}")
        print(f"   Remaining chunks after pop: {len(chunks)}")
        
        vectorstore.add_texts(
            texts=[chunk["content"]],
            metadatas=[chunk["metadata"]],
            ids=[f"chunks_{chunk['index']}"]
        )
    
        with open(chunksjson_dir,"w", encoding="utf-8") as f:
            json.dump(chunks,f,indent =4)
    
    vectorstore.persist()
    
    return vectorstore
    
        
        
               
def main():
    print("Main Function is woking")
    
    docs_path = "docs"
    chunksjson_dir= "db/chunks"
    os.makedirs("db",exist_ok = True)
    
    #if no json is created then its clear that you have to perform all the steps
    if not os.path.exists(chunksjson_dir):
        print(f"{chunksjson_dir} not found. Creating it from the docs...")
        docs_path = "docs"
        documents = load_documents(docs_path)
        chunks = split_documents(documents)
        save_chunks(chunks,filename="db/chunks")
        create_vector_store(chunksjson_dir="db/chunks",persist_directory="db/chroma_db")
        return

    #if file is present but is empty then also you have to do all the steps
    with open(chunksjson_dir,"r",encoding="utf-8") as f:
        tempchunk=json.load(f)
    
    if not tempchunk:   #meaning if list is empty
        #1. Loading the files
        documents = load_documents(docs_path)
        #2. Chunking the files
        chunks = split_documents(documents)
        #3 Saving the chunks in json format in another file
        save_chunks(chunks,filename="db/chunks")
        #4. Embedding and Storing in Vector DB from the jsonfile, also gives what needs to be chunked currently
        create_vector_store(chunksjson_dir="db/chunks",persist_directory="db/chroma_db")
    else :
        create_vector_store(chunksjson_dir="db/chunks",persist_directory="db/chroma_db")
        

if __name__ == "__main__":
    main()