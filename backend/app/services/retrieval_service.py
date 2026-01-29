"""
Retrieval Service

Provides agentic retrieval capabilities with intelligent query routing.
Uses LangChain agents to select the best retrieval strategy based on query type.
"""
import logging
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from ..database import neon_db
from . import embedding_service
from . import graph_service
from . import code_analysis_service
from . import graph_embedding_service

logger = logging.getLogger(__name__)


def _vector_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform similarity search in the Neon vector database.
    
    Args:
        query: The search query.
        top_k: Maximum number of results to return.
    
    Returns:
        List of documents with id, content, and metadata.
    """
    try:
        embedding_model = embedding_service.get_openai_embeddings()
        query_embedding = embedding_model.embed_query(query)
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        return []
    
    with neon_db.get_connection_context() as conn:
        if conn is None:
            logger.error("Failed to get Neon DB connection")
            return []
        
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, content, metadata FROM documents ORDER BY embedding <=> %s LIMIT %s",
                    (query_embedding, top_k)
                )
                results = cur.fetchall()
            
            return [
                {"id": str(row[0]), "content": row[1], "metadata": row[2] or {}}
                for row in results
            ]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []


def _graph_search(query: str) -> List[Dict[str, Any]]:
    """
    Perform graph search in Neo4j using the graph service.
    
    Args:
        query: The natural language query about relationships.
    
    Returns:
        List of results from the graph query.
    """
    try:
        result = graph_service.query_graph(query)
        # Ensure result is a list
        if isinstance(result, list):
            return result
        elif isinstance(result, str):
            return [{"content": result}]
        else:
            return [{"content": str(result)}]
    except Exception as e:
        logger.error(f"Graph search failed: {e}")
        return []


def _synthesize_answer(query: str, context: List[Dict[str, Any]]) -> str:
    """
    Generate a synthesized answer based on the retrieved context.
    
    Args:
        query: The original user query.
        context: List of retrieved documents/results.
    
    Returns:
        Synthesized answer string.
    """
    if not context:
        return "I couldn't find relevant information to answer your query."
    
    chat_model = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    
    # Build context string, handling different content structures
    context_parts = []
    for item in context:
        if isinstance(item, dict) and "content" in item:
            context_parts.append(item["content"])
        elif isinstance(item, str):
            context_parts.append(item)
        else:
            context_parts.append(str(item))
    
    context_str = "\n---\n".join(context_parts)
    
    prompt = f"""
    Answer the user's query based on the following context:

    Context:
    {context_str}

    Query:
    {query}
    
    Provide a comprehensive answer based on the context above. If the context doesn't 
    contain enough information to fully answer the query, acknowledge that.
    """
    
    try:
        response = chat_model.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"Answer synthesis failed: {e}")
        return f"Failed to synthesize answer: {str(e)}"


# Define tools for the agent
@tool
def vector_search(query: str) -> List[Dict[str, Any]]:
    """
    Use this tool for questions about summarizing content or finding general information.
    Best for semantic similarity searches and content retrieval.
    """
    return _vector_search(query, top_k=5)


@tool
def graph_search(query: str) -> List[Dict[str, Any]]:
    """
    Use this tool for questions about relationships between entities.
    Best for queries like "How is X related to Y?" or "What entities are connected to Z?"
    """
    return _graph_search(query)


@tool
def code_analysis(query: str) -> str:
    """
    Use this tool for questions about the codebase, such as how a specific function works or what a file contains.
    """
    return code_analysis_service.analyze_code(query)


@tool
def hybrid_graph_search(query: str) -> dict:
    """
    Use this tool when you need semantic similarity search combined with graph relationships.
    Best for finding concepts similar to the query AND their connected entities.
    Returns similar nodes by meaning plus their graph connections.
    """
    return graph_embedding_service.hybrid_graph_search(query, top_k=5, hop_depth=1)


def _route_query(query: str) -> dict:
    """
    Analyze the user query and route to the optimal retrieval strategy.
    
    Uses an LLM-based agent to intelligently select between vector search,
    graph search, or code analysis based on the query characteristics.
    
    Args:
        query: The user's natural language query.
    
    Returns:
        Dictionary containing the agent's output and routing decision.
    """
    tools = [vector_search, graph_search, code_analysis, hybrid_graph_search]
    
    system_message = """You are a helpful assistant that routes a user's query to the best tool.

Available tools:
- vector_search: For general content retrieval, summarization, finding specific information
- graph_search: For relationship queries, entity connections, "how is X related to Y"
- code_analysis: For questions about code, functions, implementations

Choose the most appropriate tool based on the query type."""
    
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    
    try:
        # Create agent using langgraph's create_react_agent
        agent = create_react_agent(llm, tools, prompt=system_message)
        
        # Invoke the agent
        result = agent.invoke({"messages": [("user", query)]})
        
        # Extract the final message content
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            output = getattr(last_message, 'content', str(last_message))
        else:
            output = ""
        
        logger.info(f"Routing result: {str(output)[:100]}...")
        return {"output": output}
    except Exception as e:
        logger.error(f"Query routing failed: {e}")
        # Fallback to vector search
        return {"output": _vector_search(query, top_k=5)}


def hybrid_retrieval(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Perform agentic retrieval with transparency features.
    
    Uses an LLM agent to intelligently select between vector search, graph search,
    hybrid graph search, or code analysis. Returns routing decisions, confidence
    scores, and source citations.
    
    Args:
        query: The user's natural language query.
        top_k: Maximum number of results for vector search (default: 5).
    
    Returns:
        Dictionary containing:
        - vector_results: Results from vector search
        - graph_results: Results from graph search  
        - synthesized_answer: LLM-generated answer
        - routing_decision: Which tool(s) were used
        - confidence: Estimated confidence score
        - source_citations: Detailed source tracking
    """
    logger.info(f"Processing retrieval query: {query[:100]}...")
    
    # Route the query to the best tool
    routing_result = _route_query(query)
    
    # Extract the output from agent execution
    output = routing_result.get("output", "")
    
    # Perform vector search to get structured results for citations
    vector_results = _vector_search(query, top_k)
    
    # Also try hybrid graph search for additional context
    hybrid_graph_results = graph_embedding_service.hybrid_graph_search(query, top_k=3)
    
    # Build source citations
    source_citations = []
    
    # Add vector search citations
    for i, result in enumerate(vector_results):
        source_citations.append({
            "source_id": result.get("id", f"vector_{i}"),
            "source_type": "vector_chunk",
            "content_preview": result.get("content", "")[:200],
            "similarity_score": None  # pgvector returns ordered, score not exposed
        })
    
    # Add graph node citations
    for node in hybrid_graph_results.get("nodes", []):
        source_citations.append({
            "source_id": node.get("id", ""),
            "source_type": "graph_node",
            "content_preview": f"{node.get('label', 'Entity')}: {node.get('id', '')}",
            "similarity_score": node.get("similarity")
        })
    
    # Calculate confidence based on available context
    confidence = _calculate_confidence(vector_results, hybrid_graph_results)
    
    # Determine routing decision based on what returned results
    routing_decision = _determine_routing_decision(vector_results, hybrid_graph_results)
    
    # Build context from all available results
    context = vector_results if vector_results else []
    
    # Add graph context if available
    graph_context_str = hybrid_graph_results.get("context", "")
    if graph_context_str:
        context.append({"content": graph_context_str})
    
    # Generate synthesized answer
    if isinstance(output, str) and output:
        synthesized_answer = output
    else:
        synthesized_answer = _synthesize_answer(query, context)
    
    return {
        "vector_results": vector_results,
        "graph_results": hybrid_graph_results.get("nodes", []),
        "synthesized_answer": synthesized_answer,
        "routing_decision": routing_decision,
        "confidence": confidence,
        "source_citations": source_citations,
    }


def _calculate_confidence(vector_results: List, graph_results: Dict) -> float:
    """Calculate confidence score based on retrieval quality."""
    confidence = 0.5  # Base confidence
    
    # More vector results = higher confidence
    if vector_results:
        confidence += min(0.2, len(vector_results) * 0.04)
    
    # Graph nodes with high similarity boost confidence
    for node in graph_results.get("nodes", []):
        sim = node.get("similarity", 0)
        if sim and sim > 0.8:
            confidence += 0.1
            break
    
    # Having both sources = higher confidence
    if vector_results and graph_results.get("nodes"):
        confidence += 0.1
    
    return min(1.0, round(confidence, 2))


def _determine_routing_decision(vector_results: List, graph_results: Dict) -> str:
    """Determine which retrieval method contributed results."""
    has_vector = bool(vector_results)
    has_graph = bool(graph_results.get("nodes"))
    
    if has_vector and has_graph:
        return "hybrid"
    elif has_graph:
        return "graph"
    elif has_vector:
        return "vector"
    else:
        return "none"

