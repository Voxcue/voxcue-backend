from supabase import create_client
from langchain.embeddings.openai import OpenAIEmbeddings
import os

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Custom Supabase Retriever
class SupabaseRetriever:
    def __init__(self, supabase_client, user_id: str, embedding_model):
        self.supabase_client = supabase_client
        self.user_id = user_id
        self.embedding_model = embedding_model

    def retrieve(self, query: str, k: int = 3):
        query_embedding = self.embedding_model.embed_query(query)
        response = self.supabase_client.rpc(
            "match_embeddings",  # Ensure this function is created in Supabase
            {"query_embedding": query_embedding.tolist(), "user_id": self.user_id, "top_k": k}
        ).execute()

        if response.error:
            raise ValueError(f"Retrieval error: {response.error}")
        
        return [
            {
                "content": result["content"],
                "metadata": {"id": result["id"], "similarity": result["similarity"]}
            }
            for result in response.data
        ]
