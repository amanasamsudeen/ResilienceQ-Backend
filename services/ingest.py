import os
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
# import core.config

# Use absolute paths to avoid "folder not found" errors

DATA_DIR = "../data" 

INDEX_NAME = "pdf-chatbot-index"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 1. SET ENVIRONMENT VARIABLES (This fixes the API Key error)
PINECONE_API_KEY = "pcsk_3L3cYv_7mwC2hcrRxVbuDeVXVUDfnSTyrKDyDRj2ru2vts9zBg2wY8FLz6H1oj9QqPzukR" # Your actual key
GOOGLE_API_KEY = "AIzaSyCidyWIVfn6wUZInxVuYV4cMOyj-HZ2w44"    # Your actual key

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def ingest_pdfs():
    print(f"📍 Checking path: {DATA_DIR}")
    
    # Step 1: Load PDFs
    print("📂 Loading PDFs...")
    documents = []
    if not os.path.exists(DATA_DIR):
        print(f"❌ Data folder '{DATA_DIR}' does not exist!")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
    if not files:
        print(f"❌ No PDF files found in {DATA_DIR}")
        return

    for file in files:
        print(f"➡️ Processing {file}...")
        loader = PyPDFLoader(os.path.join(DATA_DIR, file))
        documents.extend(loader.load())

    # Step 2: Split text
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)
    print(f"✂️ Created {len(chunks)} chunks.")

    # Step 3: Initialize Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        task_type="retrieval_document",
        output_dimensionality=768
    )

    # Step 4: Clear Pinecone Index
    print("⚡ Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists
    index_list = [i.name for i in pc.list_indexes()]
    if INDEX_NAME in index_list:
        print(f"🧹 Clearing old vectors from '{INDEX_NAME}'...")
        index = pc.Index(INDEX_NAME)
        try:
            # delete_all=True wipes the default namespace
            index.delete(delete_all=True)
            print("✅ Index cleared.")
            time.sleep(5) # Wait for Pinecone to settle
        except Exception as e:
            # This catches the 404 if the namespace is already empty
            print(f"ℹ️ Note: Index was likely already empty ({e})")
    else:
        print(f"🆕 Creating new index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        # Wait for the index to be ready
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)

    # Step 5: Upload
    print(f"🚀 Preparing to upload {len(chunks)} chunks...")
    
    batch_size = 30  # Smaller batches are safer for Free Tier
    i = 0
    while i < len(chunks):
        batch = chunks[i : i + batch_size]
        print(f"📤 Uploading chunks {i} to {min(i + batch_size, len(chunks))}...")
        
        try:
            PineconeVectorStore.from_documents(
                documents=batch,
                embedding=embeddings,
                index_name=INDEX_NAME
            )
            print(f"✅ Batch successful.")
            i += batch_size  # Move to the next batch
            time.sleep(5)    # Small breather between successful batches
            
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("🛑 Quota hit! Sleeping for 30 seconds to reset...")
                time.sleep(30) # Longer sleep to let the 1-minute quota window clear
                # We do NOT increment 'i' here, so it will retry the SAME batch
            else:
                print(f"❌ Unexpected Error: {e}")
                break # Stop if it's a real error (like an invalid API key)

    print("🏁 Finished! Check your Pinecone dashboard for the final count.")

if __name__ == "__main__":
    ingest_pdfs()