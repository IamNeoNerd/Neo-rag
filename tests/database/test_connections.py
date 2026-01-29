import unittest
from unittest.mock import patch, MagicMock
import psycopg2
from backend.app.database import neon_db, neo4j_db

class TestDatabaseConnections(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_neon_db_connection_success(self, mock_connect):
        """
        Test successful connection to Neon DB.
        """
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        conn = neon_db.connect_to_neon()
        self.assertIsNotNone(conn)
        mock_connect.assert_called_once()

    @patch('psycopg2.connect', side_effect=psycopg2.OperationalError("Connection Error"))
    def test_neon_db_connection_failure(self, mock_connect):
        """
        Test failed connection to Neon DB.
        """
        conn = neon_db.connect_to_neon()
        self.assertIsNone(conn)
        mock_connect.assert_called_once()

    @patch('neo4j.GraphDatabase.driver')
    def test_neo4j_db_connection_success(self, mock_driver):
        """
        Test successful connection to Neo4j AuraDB.
        """
        mock_instance = MagicMock()
        mock_driver.return_value = mock_instance
        driver = neo4j_db.connect_to_neo4j()
        self.assertIsNotNone(driver)
        mock_driver.assert_called_once()
        mock_instance.verify_connectivity.assert_called_once()

    @patch('backend.app.database.neo4j_db.GraphDatabase.driver', side_effect=Exception("Connection Error"))
    def test_neo4j_db_connection_failure(self, mock_driver):
        """
        Test failed connection to Neo4j AuraDB.
        """
        driver = neo4j_db.connect_to_neo4j()
        self.assertIsNone(driver)
        mock_driver.assert_called_once()

if __name__ == '__main__':
    unittest.main()
