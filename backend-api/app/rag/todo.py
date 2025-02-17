import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

def extract_todo_items(snippet_texts):

    combined_text = "\n".join(snippet_texts)
    prompt = f"""
You are my personal assistant. I have the following diary snippet entries:
{combined_text}

Please extract any to-do items, tasks, or reminders mentioned in these snippets.
Return your answer as a JSON array of strings, for example:
["Buy groceries", "Call the doctor", "Finish the report"]
If there are no to-do items, return an empty JSON array.
"""
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    output = response.choices[0].message.content.strip()
    try:
        todo_items = json.loads(output)
    except Exception as e:
        print("Error parsing todo items from LLM response:", e)
        todo_items = []
    return todo_items
