import os
from flask import Blueprint, request, jsonify
from app.auth.auth import token_required
from app.rag.retriever import SupabaseRetriever
from app.rag.pipeline import create_rag_pipeline
from langchain.embeddings.openai import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
import os

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


query = Blueprint('query', __name__)

# Ask a question based on the diary entries
@query.route('/query', methods=['POST'])
@token_required
def ask_question(current_user):
    data = request.get_json()
    question = data.get("question")
    
    embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    retriever = SupabaseRetriever(supabase, current_user.id, embedding_model)
    qa_pipeline = create_rag_pipeline(retriever)
    
    try:
        result = qa_pipeline.run(question)
        return jsonify({"answer": result["result"], "sources": result["source_documents"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
