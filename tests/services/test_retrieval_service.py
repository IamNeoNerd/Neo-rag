import unittest
from unittest.mock import patch, MagicMock
from backend.app.services import retrieval_service

class TestRetrievalService(unittest.TestCase):

    @patch('backend.app.services.retrieval_service.embedding_service.get_openai_embeddings')
    @patch('backend.app.services.retrieval_service.neon_db.connect_to_neon')
    def test_vector_search(self, mock_connect_neon, mock_get_embeddings):
        """
        Test the vector search functionality.
        """
        # Mock database connection
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect_neon.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur
        mock_cur.fetchall.return_value = [
            ('doc1', 'content1', {'source': 'file1'}),
        ]

        # Mock embedding service
        mock_embedding_model = MagicMock()
        mock_embedding_model.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_get_embeddings.return_value = mock_embedding_model

        results = retrieval_service._vector_search("test query", 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 'doc1')
        mock_cur.execute.assert_called_once()

    @patch('backend.app.services.retrieval_service.ChatOpenAI')
    def test_synthesize_answer(self, mock_chat_openai):
        """
        Test the answer synthesis functionality.
        """
        mock_model_instance = MagicMock()
        mock_model_instance.invoke.return_value.content = "This is a synthesized answer."
        mock_chat_openai.return_value = mock_model_instance

        answer = retrieval_service._synthesize_answer("test query", [{"content": "context"}])
        
        self.assertEqual(answer, "This is a synthesized answer.")
        mock_model_instance.invoke.assert_called_once()

    @patch('backend.app.services.retrieval_service._route_query')
    @patch('backend.app.services.retrieval_service._vector_search')
    @patch('backend.app.services.retrieval_service._graph_search')
    @patch('backend.app.services.retrieval_service._synthesize_answer')
    def test_hybrid_retrieval_routes_to_vector(self, mock_synthesize, mock_graph_search, mock_vector_search, mock_route_query):
        """
        Test that the hybrid retrieval correctly routes to vector search.
        """
        mock_route_query.return_value = {"tool": "vector_search", "tool_input": "test query"}
        mock_vector_search.return_value = [{"id": "doc1", "content": "vector content"}]
        mock_synthesize.return_value = "Final answer."

        result = retrieval_service.hybrid_retrieval("test query")
        
        self.assertEqual(result['synthesized_answer'], "Final answer.")
        self.assertEqual(len(result['vector_results']), 1)
        mock_route_query.assert_called_once_with("test query")
        mock_vector_search.assert_called_once_with("test query", 5)
        mock_graph_search.assert_not_called()
        mock_synthesize.assert_called_once()

    @patch('backend.app.services.retrieval_service._route_query')
    @patch('backend.app.services.retrieval_service._vector_search')
    @patch('backend.app.services.retrieval_service._graph_search')
    @patch('backend.app.services.retrieval_service._synthesize_answer')
    def test_hybrid_retrieval_routes_to_graph(self, mock_synthesize, mock_graph_search, mock_vector_search, mock_route_query):
        """
        Test that the hybrid retrieval correctly routes to graph search.
        """
        mock_route_query.return_value = {"tool": "graph_search", "tool_input": "test query"}
        mock_graph_search.return_value = [{"node": "test"}]
        mock_synthesize.return_value = "Final answer."

        result = retrieval_service.hybrid_retrieval("test query")
        
        self.assertEqual(result['synthesized_answer'], "Final answer.")
        self.assertEqual(len(result['graph_results']), 1)
        mock_route_query.assert_called_once_with("test query")
        mock_vector_search.assert_not_called()
        mock_graph_search.assert_called_once_with("test query")
        mock_synthesize.assert_called_once()

if __name__ == '__main__':
    unittest.main()

    @patch('backend.app.services.retrieval_service.AgentExecutor')
    def test_route_query(self, mock_agent_executor):
        """
        Test the query routing functionality.
        """
        mock_executor_instance = MagicMock()
        mock_executor_instance.invoke.return_value = {"tool": "vector_search", "output": "some results"}
        mock_agent_executor.return_value = mock_executor_instance

        result = retrieval_service._route_query("summarize the document")

        self.assertEqual(result['tool'], 'vector_search')
        mock_executor_instance.invoke.assert_called_once_with({"input": "summarize the document"})
