import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.app.main import app
from backend.app.services.query_service import QueryService

client = TestClient(app)

class TestQueryEndpoint:
    """Integration tests for the /api/v1/query endpoint."""

    @patch('backend.app.services.query_service.QueryService.__init__', lambda self: None)
    @patch('backend.app.services.query_service.QueryService.query')
    def test_valid_alpha_value(self, mock_query):
        """Test valid request with custom alpha value."""
        # Arrange
        mock_query.return_value = MagicMock(
            answer="Mocked answer",
            graph_context="Mocked graph context",
            vector_context="Mocked vector context"
        )
        
        # Act
        response = client.post("/api/v1/query", json={
            "query": "Test query",
            "alpha": 0.75
        })
        
        # Assert
        assert response.status_code == 200
        mock_query.assert_called_once_with("Test query", 0.75)

    @patch('backend.app.services.query_service.QueryService.__init__', lambda self: None)
    @patch('backend.app.services.query_service.QueryService.query')
    def test_alpha_boundary_0_0(self, mock_query):
        """Test alpha value at boundary 0.0."""
        # Arrange
        mock_query.return_value = MagicMock(
            answer="Mocked answer",
            graph_context="Mocked graph context",
            vector_context="Mocked vector context"
        )
        
        # Act
        response = client.post("/api/v1/query", json={
            "query": "Test query",
            "alpha": 0.0
        })
        
        # Assert
        assert response.status_code == 200
        mock_query.assert_called_once_with("Test query", 0.0)

    @patch('backend.app.services.query_service.QueryService.__init__', lambda self: None)
    @patch('backend.app.services.query_service.QueryService.query')
    def test_alpha_boundary_1_0(self, mock_query):
        """Test alpha value at boundary 1.0."""
        # Arrange
        mock_query.return_value = MagicMock(
            answer="Mocked answer",
            graph_context="Mocked graph context",
            vector_context="Mocked vector context"
        )
        
        # Act
        response = client.post("/api/v1/query", json={
            "query": "Test query",
            "alpha": 1.0
        })
        
        # Assert
        assert response.status_code == 200
        mock_query.assert_called_once_with("Test query", 1.0)

    @patch('backend.app.services.query_service.QueryService.__init__', lambda self: None)
    @patch('backend.app.services.query_service.QueryService.query')
    def test_alpha_default_value(self, mock_query):
        """Test alpha value with default value 0.5."""
        # Arrange
        mock_query.return_value = MagicMock(
            answer="Mocked answer",
            graph_context="Mocked graph context",
            vector_context="Mocked vector context"
        )
        
        # Act
        response = client.post("/api/v1/query", json={
            "query": "Test query"
        })
        
        # Assert
        assert response.status_code == 200
        mock_query.assert_called_once_with("Test query", 0.5)

    def test_out_of_range_alpha_value(self):
        """Test out-of-range alpha value should return 422."""
        # Act
        response = client.post("/api/v1/query", json={
            "query": "Test query",
            "alpha": 1.1
        })
        
        # Assert
        assert response.status_code == 422
        
        # Act
        response2 = client.post("/api/v1/query", json={
            "query": "Test query",
            "alpha": -0.1
        })
        
        # Assert
        assert response2.status_code == 422

    def test_non_float_alpha_value(self):
        """Test non-float alpha value should return 422."""
        # Act
        response = client.post("/api/v1/query", json={
            "query": "Test query",
            "alpha": "abc"
        })
        
        # Assert
        assert response.status_code == 422

    def test_missing_query_field(self):
        """Test missing query field should return 422."""
        # Act
        response = client.post("/api/v1/query", json={
            "alpha": 0.5
        })
        
        # Assert
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])