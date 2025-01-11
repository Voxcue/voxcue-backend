import os
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Load Knowledge Base
def load_knowledge_base(file_path: str):
    """
    Load and process the text knowledge base from a file.
    """
    try:
        loader = TextLoader(file_path)
        documents = loader.load()
        
        # Split text into manageable chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
        docs = text_splitter.split_documents(documents)
        return docs
    except Exception as e:
        raise ValueError(f"Failed to load or process the knowledge base: {e}")

# Create Vector Store
def create_vector_store(docs, embedding_model):
    """
    Create a FAISS vector store using the provided documents and embedding model.
    """
    try:
        vector_store = FAISS.from_documents(docs, embedding_model)
        return vector_store
    except Exception as e:
        raise ValueError(f"Failed to create vector store: {e}")

def create_rag_pipeline(vector_store, retriever_k=3, retriever_score_threshold=None):
    """
    Create a RAG pipeline using LangChain with a custom query template.
    """
    try:
        # Define a custom prompt template
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a helpful daily assistant. Use the following context, derived from the user's previous diary entries, to answer the question."
                "\n\nContext (Diary Entries): {context}\n\nUser's Question: {question}\n\nYour Response:"
            )
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

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
    
    knowledge_base_path = os.getenv("FILE_PATH")
    if not knowledge_base_path:
        raise EnvironmentError("Knowledge base file path not found. Please set the 'FILE_PATH' environment variable.")
    
    print("Starting RAG Super Memory...")

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
        print("RAG pipeline created. Ready to answer questions!")
        
        # Step 4: Answer queries
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            result = qa_pipeline(query)
            response = result["result"]
            sources = result["source_documents"]
            
            print(f"\nASSISTANT: {response}")

    
    except Exception as e:
        print(f"Error: {e}")
