import os
from flask import Blueprint, request, jsonify
from app import db
from app.models import DiaryEntry
from app.auth.auth import token_required
from langchain.embeddings.openai import OpenAIEmbeddings
from app.rag.retriever import SupabaseRetriever
from dotenv import load_dotenv

load_dotenv()

diary = Blueprint("diary", __name__)

# Add a new diary entry
@diary.route("/diary", methods=["POST"])
@token_required
def add_diary_entry(current_user):
    data = request.get_json()

    # Input validation
    content = data.get("content")
    date = data.get("date")

    if not content or not date:
        return jsonify({"error": "Content and date are required"}), 400

    try:
        # Generate embedding
        embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        embedding = embedding_model.embed_query(content)  

        # Save diary entry
        new_entry = DiaryEntry(user_id=current_user.id, content=content, embedding=embedding, date=date)
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Diary entry added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": f"Failed to process diary entry: {str(e)}"}), 500
