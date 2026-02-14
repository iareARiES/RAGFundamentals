import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Main Function is woking")
    
    #1. Loading the files
    
    #2. Chunking the files
    
    #3. Embedding and Storing in Vector DB



if __name__ == "__main__":
    main()