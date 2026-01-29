import unittest
from unittest.mock import patch, mock_open
from backend.app.services import code_analysis_service

class TestCodeAnalysisService(unittest.TestCase):

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="test content")
    def test_analyze_code_file_exists(self, mock_file, mock_exists):
        """
        Test that the code analysis service can read an existing file.
        """
        content = code_analysis_service.analyze_code("test_file.py")
        self.assertEqual(content, "test content")
        mock_exists.assert_called_once_with("test_file.py")
        mock_file.assert_called_once_with("test_file.py", 'r')

    @patch('os.path.exists', return_value=False)
    def test_analyze_code_file_not_found(self, mock_exists):
        """
        Test that the code analysis service handles a missing file.
        """
        content = code_analysis_service.analyze_code("non_existent_file.py")
        self.assertEqual(content, "File not found: non_existent_file.py")
        mock_exists.assert_called_once_with("non_existent_file.py")

if __name__ == '__main__':
    unittest.main()
