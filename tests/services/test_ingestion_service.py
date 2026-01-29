import unittest
from unittest.mock import patch, MagicMock
from backend.app.services import ingestion_service

class TestIngestionService(unittest.TestCase):

    def test_chunk_text(self):
        """
        Test that text is chunked correctly.
        """
        text = "This is a test sentence. " * 200
        chunks = ingestion_service.chunk_text(text)
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 1)
        self.assertIsInstance(chunks[0], str)

    @patch('backend.app.services.ingestion_service.neo4j_db.connect_to_neo4j')
    @patch('backend.app.services.ingestion_service.graph_extraction_service.extract_entities_and_relationships')
    @patch('backend.app.services.ingestion_service.embedding_service.get_openai_embeddings')
    @patch('backend.app.services.ingestion_service.neon_db.connect_to_neon')
    def test_ingest_text(self, mock_connect_neon, mock_get_embeddings, mock_extract_entities, mock_connect_to_neo4j):
        """
        Test the full text ingestion process.
        """
        # Mock database connection
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect_neon.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        # Mock embedding service
        mock_embedding_model = MagicMock()
        mock_embedding_model.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_get_embeddings.return_value = mock_embedding_model
        
        # Mock graph extraction service
        mock_extract_entities.return_value = {
            "nodes": [],
            "relationships": []
        }
        
        # Mock neo4j database connection
        mock_neo4j_driver = MagicMock()
        mock_connect_to_neo4j.return_value = mock_neo4j_driver
        mock_neo4j_session = MagicMock()
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_neo4j_session
        
        # Mock graph extraction service
        mock_extract_entities.return_value = {
            "nodes": [],
            "relationships": []
        }

        text = "This is a test."
        chunk_count = ingestion_service.ingest_text(text)

        self.assertEqual(chunk_count, 1)
        mock_connect_neon.assert_called_once()
        mock_get_embeddings.assert_called_once()
        mock_extract_entities.assert_called_once_with(text)
        mock_connect_to_neo4j.assert_called_once()
        mock_embedding_model.embed_documents.assert_called_once_with([text])
        mock_cur.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_neo4j_driver.session.assert_called_once()
        mock_neo4j_driver.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
