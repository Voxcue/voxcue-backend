import os 
from flask import Blueprint, request, jsonify
from app import db
from app.models import DiaryEntry
from app.auth.auth import token_required
from langchain.embeddings.openai import OpenAIEmbeddings
from app.rag.retriever import SupabaseRetriever

from dotenv import load_dotenv
load_dotenv()

diary = Blueprint('diary', __name__)

# Add a new diary entry
@diary.route('/diary', methods=['POST'])
@token_required
def add_diary_entry(current_user):
    data = request.get_json()
    content = data.get("content")
    date = data.get("date")
    
    embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    embedding = embedding_model.embed_text(content)
    
    new_entry = DiaryEntry(user_id=current_user.id, content=content, embedding=embedding, date=date)
    db.session.add(new_entry)
    db.session.commit()
    
    return jsonify({"message": "Diary entry added successfully!"}), 201
