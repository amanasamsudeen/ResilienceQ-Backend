from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore

INDEX_NAME = "pdf-chatbot-index"

class ChatModel:
    def __init__(self):
        # 1. Embeddings: Added task_type and output_dimensionality
        # task_type="retrieval_query" optimizes the vector for searching
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            task_type="retrieval_query",
            output_dimensionality=768  # Crucial: Matches your Pinecone index size
        )

        # 2. Pinecone VectorStore
        self.vectorstore = PineconeVectorStore(
            index_name=INDEX_NAME,
            embedding=self.embeddings
        )

        self.k = 3

        # 3. LLM: Updated to the latest stable flash model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", # Use 1.5-flash unless you have access to experimental 2.0+
            temperature=0.3,
        )

    def ask(self, question: str):
        # The vectorstore will now use the 768-dim version of gemini-embedding-001
        docs = self.vectorstore.similarity_search(
            query=question,
            k=self.k
        )

        context = "\n\n".join(doc.page_content for doc in docs)

        prompt = f"""
You are an academic assistant. 
Answer ONLY from the context below. 
If the answer is not present, say "sorry, i can assist on ResilienceQ related queries".

Context:
{context}

Question:
{question}
"""

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "sources": list(
                {doc.metadata.get("source", "Unknown") for doc in docs}
            ),
        }