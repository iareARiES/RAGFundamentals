import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load .env file
load_dotenv()

def test_gemini():
    try:
        print("Checking API Key...")
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("❌ API Key not found.")
            return
        
        print("✅ API Key detected.")

        # Initialize embedding model
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )

        print("Calling Gemini API...")

        # Test embedding
        vector = embeddings.embed_query("Hello Gemini")

        print("✅ Gemini API is working!")
        print(f"Embedding length: {len(vector)}")

    except Exception as e:
        print("❌ Error occurred:")
        print(e)


if __name__ == "__main__":
    test_gemini()
