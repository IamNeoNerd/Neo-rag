import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def get_openai_embeddings():
    """
    Initializes and returns an OpenAIEmbeddings instance.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    
    return OpenAIEmbeddings(api_key=api_key)

# Placeholder for other embedding providers
def get_cohere_embeddings():
    """
    (Placeholder) Initializes and returns a CohereEmbeddings instance.
    """
    pass
