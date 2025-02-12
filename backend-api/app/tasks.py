from celery import shared_task
from app import create_app ,db 
from app.rag.diaryCreate import update_or_create_diary_entry
from app.rag.todo import extract_todo_items
from app.models import TodoItem, Snippet
import json
app = create_app()

@shared_task(name="app.tasks.update_diary_entry_task")
def update_diary_entry_task(user_id, date, snippet_content):
    with app.app_context():
        diary_entry = update_or_create_diary_entry(user_id, date, snippet_content)
        return diary_entry.id



@shared_task(name="app.tasks.update_todo_list_task")
def update_todo_list_task(user_id, date):
    with app.app_context():
        snippets = Snippet.query.filter_by(user_id=user_id).all()
        snippet_texts = []
        for s in snippets:
            if isinstance(s.content, dict):
                snippet_texts.append(json.dumps(s.content))
            else:
                snippet_texts.append(s.content)
        
        todo_items = extract_todo_items(snippet_texts)
        
        existing_todos = TodoItem.query.filter_by(user_id=user_id).all()
        existing_descriptions = {todo.description.lower() for todo in existing_todos}
        
        for item in todo_items:
            if item.lower() not in existing_descriptions:
                new_todo = TodoItem(user_id=user_id, description=item, completed=False)
                db.session.add(new_todo)
            else:
                pass
        
        db.session.commit()
        return todo_items
