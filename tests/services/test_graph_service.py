import unittest
from unittest.mock import patch, MagicMock
from backend.app.services import graph_service

class TestGraphService(unittest.TestCase):

    @patch('backend.app.database.neo4j_db.connect_to_neo4j')
    def test_get_neo4j_driver(self, mock_connect_neo4j):
        """
        Test that the graph service correctly calls the database connection logic.
        """
        mock_driver = MagicMock()
        mock_connect_neo4j.return_value = mock_driver

        driver = graph_service.get_neo4j_driver()

        self.assertEqual(driver, mock_driver)
        mock_connect_neo4j.assert_called_once()

if __name__ == '__main__':
    unittest.main()

    @patch('backend.app.services.graph_service.Neo4jGraph')
    @patch('backend.app.services.graph_service.GraphCypherQAChain')
    @patch('backend.app.services.graph_service.get_neo4j_driver')
    def test_query_graph(self, mock_get_driver, mock_qa_chain, mock_neo4j_graph):
        """
        Test the graph query functionality.
        """
        # Mock the Neo4j driver and graph
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver
        mock_graph_instance = MagicMock()
        mock_neo4j_graph.return_value = mock_graph_instance

        # Mock the QA chain
        mock_chain_instance = MagicMock()
        mock_chain_instance.invoke.return_value = {"result": [{"node": "test"}]}
        mock_qa_chain.from_llm.return_value = mock_chain_instance

        result = graph_service.query_graph("test query")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['node'], 'test')
        mock_get_driver.assert_called_once()
        mock_neo4j_graph.assert_called_once_with(mock_driver)
        mock_qa_chain.from_llm.assert_called_once()
        mock_chain_instance.invoke.assert_called_once_with({"query": "test query"})
