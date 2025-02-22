import os
from flask import Blueprint, request, jsonify
from app.auth.auth import token_required
from app.rag.retriever import SupabaseRetriever
from app.rag.pipeline import create_rag_pipeline
from langchain_community.embeddings import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

query = Blueprint('query', __name__)

@query.route('/query', methods=['POST'])
@token_required
def ask_question(current_user):
    data = request.get_json()
    question = data.get("question")
    
    embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    retriever = SupabaseRetriever(supabase, str(current_user.id), embedding_model)

    qa_pipeline = create_rag_pipeline(retriever)
    
    try:
        response = qa_pipeline.invoke(question)
        result_text = response.get("result", "No answer found")

        source_docs = [
            {
                "content":doc.page_content,
                "metadata": doc.metadata
            }
            for doc in response.get("source_documents", [])
        ]

        return jsonify({"answer": result_text, "sources": source_docs}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
