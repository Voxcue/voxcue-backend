from langchain.schema import Document, BaseRetriever
from langchain.embeddings.openai import OpenAIEmbeddings
from typing import List, Any
import os
from supabase import create_client
from pydantic import Field, ConfigDict
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseRetriever(BaseRetriever):  
    supabase_client: Any = Field(...)
    user_id: int = Field(...)
    embedding_model: Any = Field(...)

    model_config = ConfigDict(arbitrary_types_allowed=True) 

    def __init__(self, supabase_client, user_id: str, embedding_model):

        user_id = int(user_id)
        super().__init__(
            supabase_client=supabase_client,
            user_id=user_id,
            embedding_model=embedding_model
        )

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Fetch relevant documents from Supabase using vector search."""
        query_embedding = self.embedding_model.embed_query(query)

        response = self.supabase_client.rpc(
    "match_embedding2",  
    {"input_user_id": self.user_id, "query_embedding": query_embedding, "top_k": 3}
).execute()


        if response:
            return [
            Document(
                page_content=result["content"],
                metadata={"id": result["id"], "similarity": result["similarity"]}
            )
            for result in response.data
        ]

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """Asynchronous version of getting relevant documents."""
        return self._get_relevant_documents(query)
