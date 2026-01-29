import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field
from backend.app.models.data_models import KnowledgeGraph

def get_extraction_chain():
    """
    Creates and returns a langchain chain configured for graph extraction.
    """
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    prompt = ChatPromptTemplate.from_messages(
        [(
            "system",
            """
            You are a top-tier algorithm designed for extracting information in structured formats.
            - Extract all entities and relationships from the text.
            - The 'id' of each node should be a meaningful, concise, and unique identifier.
            - The 'type' of each relationship should be a verb or a short phrase that describes the connection.
            - Do not add any nodes or relationships that are not explicitly mentioned in the text.
            """
        ),
        ("human", "{input}")
        ]
    )
    
    structured_llm = llm.with_structured_output(KnowledgeGraph)
    return prompt | structured_llm

def extract_entities_and_relationships(text: str) -> Dict[str, Any]:
    """
    Extracts entities and relationships from unstructured text using an LLM.

    Args:
        text (str): The unstructured text to process.

    Returns:
        Dict[str, Any]: A dictionary containing the extracted 'nodes' and 'relationships'.
    """
    chain = get_extraction_chain()
    graph = chain.invoke({"input": text})
    return graph.model_dump()