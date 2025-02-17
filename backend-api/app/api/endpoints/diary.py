import os
import json
from flask import Blueprint, request, jsonify
from app import db
from app.models import Snippet, SnippetSession, DiaryEntry
from app.auth.auth import token_required
from langchain_community.embeddings import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
from app.rag.diaryCreate import update_or_create_diary_entry
from app.tasks import update_diary_entry_task


load_dotenv()

diary = Blueprint("diary", __name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

MAX_QUESTIONS = 3


def get_follow_up_question(responses):
    """Generate a concise, first-person follow-up question based on the current diary responses."""
    prompt = f"""
    You are my personal diary assistant, and we are having a conversation about my day. I have shared the following details: {responses}.
    In your reply, ask me one clear, concise follow-up question in the first person that encourages me to elaborate on my feelings, experiences, and any important details that may be missing for a complete diary entry.
    Do not include any extra commentary or explanation.
    If I have already provided all the necessary details for a well-structured diary entry, simply return the word "DONE".
    """
    response = openai_client.chat.completions.create(
        model="gpt-4", messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def finalize_snippet(responses, date):
    """Generate a structured snippet from the collected responses and create its embedding.
    Return the snippet as a JSON object."""
    structure_prompt = f"""
    Given the following responses: {responses} and the date: {date}, generate a well-structured diary snippet.
    The snippet must be formatted as a valid JSON object with exactly these keys:
      "Date": The date of the entry (string),
      "Mood": The user's mood (string),
      "Events": A description of the day's events (string),
      "Reflections": The user's reflections (string).
    Output ONLY the JSON object. Do not include any additional text, markdown, or commentary.
    For example, a valid response would be:
    {{"Date": "2025-02-05", "Mood": "Happy", "Events": "I got promoted at work.", "Reflections": "I feel excited and optimistic about the future."}}
    """
    structured_response = openai_client.chat.completions.create(
        model="gpt-4", messages=[{"role": "system", "content": structure_prompt}]
    )
    structured_entry = structured_response.choices[0].message.content.strip()

    try:
        structured_entry_json = json.loads(structured_entry)
    except Exception as e:
        print("Error parsing structured entry to JSON:", e)
        structured_entry_json = structured_entry

    embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
    embedding = embedding_model.embed_query(structured_entry)
    return structured_entry_json, embedding


@diary.route("/diary", methods=["POST"])
@token_required
def interactive_snippet_entry(current_user):
    data = request.get_json()
    user_id = current_user.id
    content = data.get("content")
    print(content)
    if not content:
        return jsonify({"error": "No content provided"}), 400

    snippet_session = SnippetSession.query.filter_by(
        user_id=user_id, active=True
    ).first()
    if not snippet_session:
        snippet_session = SnippetSession(
            user_id=user_id, responses=[], question_count=0, active=True
        )
        db.session.add(snippet_session)
        db.session.commit()

    snippet_session.responses.append(content)
    snippet_session.question_count += 1
    db.session.commit()  # Save changes

    if snippet_session.question_count >= MAX_QUESTIONS:
        structured_entry, embedding = finalize_snippet(
            snippet_session.responses, data.get("date", "Unknown")
        )
        new_entry = Snippet(
            user_id=user_id,
            content=structured_entry,
            embedding=embedding,
            date=data.get("date", "Unknown"),
        )

        update_diary_entry_task.delay(user_id,data.get("date"),structured_entry)

        db.session.add(new_entry)
        # Mark the session as inactive
        snippet_session.active = False
        db.session.commit()
        return jsonify({"message": "Snippet saved successfully!"}), 201

    print(snippet_session.responses)
    next_question = get_follow_up_question(snippet_session.responses)
    if next_question.strip().upper() == "DONE":
        structured_entry, embedding = finalize_snippet(
            snippet_session.responses, data.get("date", "Unknown")
        )
        new_entry = Snippet(
            user_id=user_id,
            content=structured_entry,
            embedding=embedding,
            date=data.get("date", "Unknown"),
        )
        update_diary_entry_task.delay(user_id,data.get("date"),structured_entry)
        db.session.add(new_entry)
        snippet_session.active = False
        db.session.commit()
        return jsonify({"message": "Snippet saved successfully!"}), 201

    return jsonify({"question": next_question})


@diary.route("/getdiary", methods=["POST"])
@token_required
def get_diary(current_user):
    data = request.get_json()
    user_id = current_user.id
    date = data.get("date")
    diary_entry = DiaryEntry.query.filter_by(user_id=user_id, date=date).first()
    return jsonify({"diary_entry": diary_entry})
