from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create RAG pipeline
def create_rag_pipeline(retriever, retriever_k=3):
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are a helpful daily assistant. Use the following context, derived from the user's previous diary entries, to answer the question."
            "\n\nContext (Diary Entries): {context}\n\nUser's Question: {question}\n\nYour Response:"
        )
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(openai_api_key=OPENAI_API_KEY),
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template},
    )
    return qa_chain
