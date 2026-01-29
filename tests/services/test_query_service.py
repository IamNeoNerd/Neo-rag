import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized

from backend.app.services.query_service import QueryService
from backend.app.models.api_models import QueryResponse

class TestQueryService(unittest.TestCase):

    @parameterized.expand([
        (0.0,),
        (0.25,),
        (0.5,),
        (0.75,),
        (1.0,),
    ])
    @patch('backend.app.services.query_service.QueryService.__init__', lambda self: None)
    @patch('backend.app.services.query_service.QueryService._get_graph_context')
    @patch('backend.app.services.query_service.QueryService._get_vector_context')
    @patch('backend.app.services.query_service.QueryService._synthesize_answer')
    def test_query_orchestration_with_alpha(self, alpha_value, mock_synthesize, mock_vector, mock_graph):
        # Arrange
        mock_graph.return_value = "Mocked graph context"
        mock_vector.return_value = "Mocked vector context"
        mock_synthesize.return_value = "Mocked synthesized answer"

        service = QueryService()
        query_text = "Test query"

        # Act
        response = service.query(query_text, alpha=alpha_value)

        # Assert
        mock_graph.assert_called_once_with(query_text)
        mock_vector.assert_called_once_with(query_text)
        mock_synthesize.assert_called_once_with(
            query_text,
            "Mocked graph context",
            "Mocked vector context",
            alpha_value
        )
        
        self.assertIsInstance(response, QueryResponse)
        self.assertEqual(response.answer, "Mocked synthesized answer")
        self.assertEqual(response.graph_context, "Mocked graph context")
        self.assertEqual(response.vector_context, "Mocked vector context")

if __name__ == '__main__':
    unittest.main()