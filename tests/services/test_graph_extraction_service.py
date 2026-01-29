import unittest
from unittest.mock import patch, MagicMock

from backend.app.services.graph_extraction_service import extract_entities_and_relationships
from backend.app.models.data_models import KnowledgeGraph

class TestGraphExtractionService(unittest.TestCase):

    @patch('backend.app.services.graph_extraction_service.get_extraction_chain')
    def test_extract_entities_and_relationships_success(self, mock_get_chain):
        # Arrange
        mock_chain = MagicMock()
        mock_get_chain.return_value = mock_chain

        mock_graph = KnowledgeGraph(
            nodes=[
                {"id": "PersonA", "label": "Person"},
                {"id": "PersonB", "label": "Person"}
            ],
            relationships=[
                {"source_node_id": "PersonA", "target_node_id": "PersonB", "type": "KNOWS"}
            ]
        )
        mock_chain.invoke.return_value = mock_graph

        sample_text = "Person A knows Person B."

        # Act
        result = extract_entities_and_relationships(sample_text)

        # Assert
        mock_get_chain.assert_called_once()
        mock_chain.invoke.assert_called_once_with({"input": sample_text})
        self.assertEqual(result, mock_graph.model_dump())
        self.assertIn("nodes", result)
        self.assertIn("relationships", result)
        self.assertEqual(len(result["nodes"]), 2)
        self.assertEqual(len(result["relationships"]), 1)

if __name__ == '__main__':
    unittest.main()