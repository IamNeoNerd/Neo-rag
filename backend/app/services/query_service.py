"""
Query Service

Handles hybrid query processing that combines both graph and vector context
with configurable alpha weighting for context prioritization.
"""
import json
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

from ..models.api_models import QueryResponse
from ..database import neon_db, neo4j_db
from . import embedding_service

logger = logging.getLogger(__name__)


class QueryService:
    """
    Service to handle the hybrid query process.
    
    Combines graph-based (structured relationships) and vector-based (semantic similarity)
    retrieval with configurable weighting via the alpha parameter.
    
    Attributes:
        llm: The language model for Cypher generation and answer synthesis.
        graph: Neo4j graph connection for Cypher queries.
        cypher_chain: LangChain chain for natural language to Cypher conversion.
    """

    def __init__(self, model: str = "gpt-4-turbo"):
        """
        Initialize the QueryService.
        
        Args:
            model: The OpenAI model to use for LLM operations.
        """
        self.llm = ChatOpenAI(model=model, temperature=0)
        
        driver = neo4j_db.get_driver()
        if driver is None:
            logger.warning("Neo4j driver not available, graph queries will fail")
            self.graph = None
            self.cypher_chain = None
        else:
            self.graph = Neo4jGraph(driver=driver)
            self.cypher_chain = GraphCypherQAChain.from_llm(
                graph=self.graph, llm=self.llm, verbose=True
            )

    def _get_graph_context(self, query: str) -> str:
        """
        Generate and execute a Cypher query to retrieve graph context.
        
        Args:
            query: The natural language query.
        
        Returns:
            JSON string of graph query results, or error message if failed.
        """
        if self.cypher_chain is None:
            logger.warning("Cypher chain not initialized, cannot get graph context")
            return "Graph database not available."
        
        try:
            result = self.cypher_chain.invoke({"query": query})
            return json.dumps(result.get('result', []), indent=2)
        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            return f"Graph query error: {str(e)}"

    def _get_vector_context(self, query: str, top_k: int = 5) -> str:
        """
        Perform vector similarity search to retrieve relevant document chunks.
        
        Args:
            query: The search query.
            top_k: Maximum number of results to return.
        
        Returns:
            Concatenated string of relevant document chunks.
        """
        try:
            embedding_model = embedding_service.get_openai_embeddings()
            query_embedding = embedding_model.embed_query(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return "Failed to generate query embedding."
        
        with neon_db.get_connection_context() as conn:
            if conn is None:
                logger.error("Failed to get Neon DB connection")
                return "Vector database not available."
            
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT content FROM documents ORDER BY embedding <=> %s::vector LIMIT %s",
                        (query_embedding, top_k)
                    )
                    results = [row[0] for row in cur.fetchall()]
                
                if not results:
                    return "No relevant documents found."
                
                return "\n---\n".join(results)
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                return f"Vector search error: {str(e)}"

    def _get_weighting_instruction(self, alpha: float) -> str:
        """
        Generate weighting instruction based on alpha value.
        
        Args:
            alpha: Weight factor (0.0 = vector only, 1.0 = graph only, 0.5 = equal).
        
        Returns:
            Instruction string for the LLM about how to weight contexts.
        """
        if alpha == 1.0:
            return "You must rely *exclusively* on the Graph Context. Ignore the Vector Context."
        elif alpha == 0.0:
            return "You must rely *exclusively* on the Vector Context. Ignore the Graph Context."
        elif alpha > 0.5:
            factor = alpha / (1 - alpha)
            return f"You should prioritize the Graph Context. The Graph Context is more important by a factor of {factor:.1f}."
        elif alpha < 0.5:
            factor = (1 - alpha) / alpha
            return f"You should prioritize the Vector Context. The Vector Context is more important by a factor of {factor:.1f}."
        else:  # alpha == 0.5
            return "You should give equal weight to both the Graph Context and the Vector Context."

    def _synthesize_answer(self, query: str, graph_context: str, 
                           vector_context: str, alpha: float) -> str:
        """
        Synthesize a final answer from the retrieved contexts.
        
        Args:
            query: The original user query.
            graph_context: Context retrieved from graph database.
            vector_context: Context retrieved from vector database.
            alpha: Weight factor for context prioritization.
        
        Returns:
            Synthesized answer string.
        """
        weighting_instruction = self._get_weighting_instruction(alpha)

        prompt_template = """
        You are an expert Q&A system that is trusted around the world.
        You are given a question and context from two sources: a knowledge graph and a vector store.
        Your task is to synthesize a comprehensive and coherent answer based on all available information.

        **Weighting Instructions**: {weighting_instruction}

        Question: {query}

        Graph Context:
        {graph_context}

        Vector Context:
        {vector_context}

        Answer:
        """
        
        prompt = PromptTemplate(
            input_variables=["query", "graph_context", "vector_context", "weighting_instruction"],
            template=prompt_template,
        )
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "query": query,
                "graph_context": graph_context,
                "vector_context": vector_context,
                "weighting_instruction": weighting_instruction
            })
            return result.content
        except Exception as e:
            logger.error(f"Answer synthesis failed: {e}")
            return f"Failed to synthesize answer: {str(e)}"

    def query(self, query: str, alpha: float = 0.5) -> QueryResponse:
        """
        Orchestrate the hybrid query process.
        
        Retrieves context from both graph and vector databases, then synthesizes
        a comprehensive answer using LLM with configurable weighting.
        
        Args:
            query: The user's natural language query.
            alpha: Weight factor between 0.0 and 1.0.
                   - 0.0 = Use only vector context (semantic search)
                   - 0.5 = Equal weight to both (default)
                   - 1.0 = Use only graph context (relationship queries)
        
        Returns:
            QueryResponse containing the synthesized answer and both contexts.
        """
        logger.info(f"Processing query with alpha={alpha}: {query[:100]}...")
        
        # Retrieve contexts in parallel (could be optimized with async)
        graph_context = self._get_graph_context(query)
        vector_context = self._get_vector_context(query)
        
        # Synthesize answer
        answer = self._synthesize_answer(query, graph_context, vector_context, alpha)
        
        logger.info("Query processing complete")
        
        return QueryResponse(
            answer=answer,
            graph_context=graph_context,
            vector_context=vector_context
        )