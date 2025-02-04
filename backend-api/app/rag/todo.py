import os
import json
from langchain_community.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# File to store the generated to-do list
TODO_LIST_FILE = "todo_list.json"

def initialize_todo_list_file():
    """
    Initialize the to-do list JSON file if it doesn't exist.
    """
    if not os.path.exists(TODO_LIST_FILE):
        with open(TODO_LIST_FILE, "w") as file:
            json.dump([], file)

def append_to_todo_list(new_items):
    """
    Append new to-do items to the JSON file.
    """
    try:
        with open(TODO_LIST_FILE, "r") as file:
            todo_list = json.load(file)
        todo_list.extend(new_items)
        with open(TODO_LIST_FILE, "w") as file:
            json.dump(todo_list, file, indent=4)
    except Exception as e:
        print(f"Error updating to-do list: {e}")

def generate_todo_list(entry, qa_pipeline):
    """
    Generate a to-do list from a diary entry using the RAG pipeline.
    """
    query = "What are the tasks or to-dos described in the above entry?"
    try:
        result = qa_pipeline.invoke(query)
        # Print the result for debugging
        print(f"Pipeline result: {result}")
        # Handle response format based on the return structure
        if isinstance(result, str):
            todo_items = result.strip().split("\n")
        elif isinstance(result, dict) and "result" in result:
            todo_items = result["result"].strip().split("\n")
        else:
            print(f"Unexpected result format: {result}")
            return []
        return [item for item in todo_items if item.strip()]
    except Exception as e:
        print(f"Error generating to-do list: {e}")
        return []


def load_knowledge_base(file_path: str):
    """
    Load and process the text knowledge base from a file.
    """
    loader = TextLoader(file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
    return text_splitter.split_documents(documents)

def create_vector_store(docs, embedding_model):
    """
    Create a FAISS vector store using the provided documents and embedding model.
    """
    return FAISS.from_documents(docs, embedding_model)

def create_rag_pipeline(vector_store, retriever_k=3, retriever_score_threshold=None):
    """
    Create a RAG pipeline using LangChain with a custom query template.
    """
    try:
        # Define a custom prompt template
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a helpful assistant. Based on the following context, extract actionable to-do items if and only if it is mentioned that the task is to be done in the future ignore all tasks that havce already occured :"
                "The response should be in a json format with the following elements : todo , date , description."
                "\n\nContext: {context}\n\nQuery: {question}\n\nResponse:"
        ),
        )
        
        # Initialize the retriever with custom parameters
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": retriever_k})
        
        # Adjust retriever filtering based on similarity scores (optional)
        if retriever_score_threshold:
            retriever.set_score_threshold(retriever_score_threshold)

        # Use the custom prompt template in the RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY")),
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template},  # Include the custom template
        )
        return qa_chain
    except Exception as e:
        raise ValueError(f"Failed to create RAG pipeline: {e}")


if __name__ == "__main__":
    # Initialize
    initialize_todo_list_file()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")

    knowledge_base_path = os.getenv("FILE_PATH")
    if not knowledge_base_path:
        raise EnvironmentError("Knowledge base file path not found. Please set the 'FILE_PATH' environment variable.")

    print("Starting RAG Super Memory with Automatic To-Do List Generator...")

    try:
        # Step 1: Load the knowledge base
        docs = load_knowledge_base(knowledge_base_path)
        print(f"Knowledge base loaded with {len(docs)} documents.")

        # Step 2: Create vector embeddings
        embedding_model = OpenAIEmbeddings(openai_api_key=api_key)
        vector_store = create_vector_store(docs, embedding_model)
        print("Vector store created.")

        # Step 3: Create RAG pipeline
        qa_pipeline = create_rag_pipeline(vector_store)
        print("RAG pipeline created.")

        # Step 4: Process new diary entries and generate to-do lists
        for doc in docs:
            entry_text = doc.page_content
            # Generate and append to-do list
            todo_items = generate_todo_list(entry_text, qa_pipeline)
            print(f"Generated To-Do Items: {todo_items}")
            append_to_todo_list(todo_items)

        print("All diary entries processed and to-do lists generated.")

    except Exception as e:
        print(f"Error: {e}")
