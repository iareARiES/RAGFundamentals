import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

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

def create_vector_store():
    
    continue
    
    
def main():
    print("Main Function is woking")
    
    docs_path = "docs"
    
    #1. Loading the files
    documents = load_documents(docs_path)
    
    #2. Chunking the files
    
    chunks = split_documents(documents)
    #3. Embedding and Storing in Vector DB



if __name__ == "__main__":
    main()