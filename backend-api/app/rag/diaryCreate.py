import os
from datetime import datetime
from openai import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from app import db
from app.models import DiaryEntry
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

def update_or_create_diary_entry(user_id: int, date: str, new_snippet: str) -> DiaryEntry:
    diary_entry = DiaryEntry.query.filter_by(user_id=user_id, date=date).first()
    
    if diary_entry:
        prompt = f"""
You are my personal diary assistant. I already have a diary entry for today:
"{diary_entry.diary_content}"

I have just added a new snippet:
"{new_snippet}"

Please update my diary entry by merging the new snippet into the existing entry. 
The updated entry should be a natural, coherent summary of my day that highlights the main points.
Return only the updated diary entry text.Keep the diary to the point higlighting the main points only and it should not be very lengthy.
It should be to the point keeping only necessary and main points.
"""
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        updated_text = response.choices[0].message.content.strip()
        diary_entry.diary_content = updated_text
        db.session.commit()
        return diary_entry
    else:
        prompt = f"""
You are my personal diary assistant. I want to create a diary entry for today ({date}).
I have the following snippet:
"{new_snippet}"

Please generate a natural, coherent diary entry that captures the main points of my day, including my mood, key events, and reflections.
Return only the diary entry text.
"""
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        new_text = response.choices[0].message.content.strip()
        new_entry = DiaryEntry(
            user_id=user_id,
            diary_content=new_text,
            date=date
        )
        db.session.add(new_entry)
        db.session.commit()
        return new_entry
