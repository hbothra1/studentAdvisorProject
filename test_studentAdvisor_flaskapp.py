import unittest
import json
from unittest.mock import patch, MagicMock
from studentAdvisor_flaskapp import app

class TestStudentAdvisorFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Flask API is running!')

    @patch('studentAdvisor_flaskapp.extract_transcript_data')
    @patch('studentAdvisor_flaskapp.save_transcript_to_json')
    def test_process_transcript(self, mock_save, mock_extract):
        mock_transcript = {'courses': []}
        mock_extract.return_value = mock_transcript
        
        with open('test_transcript.pdf', 'wb') as f:
            f.write(b'dummy pdf content')
            
        with open('test_transcript.pdf', 'rb') as f:
            response = self.app.post('/process_transcript',
                                   data={'file': (f, 'test_transcript.pdf')})
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['transcript_json'], mock_transcript)

    @patch('studentAdvisor_flaskapp.parse_job_description')
    @patch('studentAdvisor_flaskapp.save_job_description_to_json') 
    def test_process_job_description(self, mock_save, mock_parse):
        mock_job_desc = {'requirements': []}
        mock_parse.return_value = mock_job_desc
        
        with open('test_job.pdf', 'wb') as f:
            f.write(b'dummy job desc')
            
        with open('test_job.pdf', 'rb') as f:
            response = self.app.post('/process_job_description',
                                   data={'file': (f, 'test_job.pdf')})
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['job_description_json'], mock_job_desc)

    def test_get_job_description_json_no_data(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session.clear()
            response = client.get('/get_job_description_json')
            self.assertEqual(response.status_code, 400)

    def test_get_transcript_json_no_data(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session.clear()
            response = client.get('/get_transcript_json')
            self.assertEqual(response.status_code, 400)

    @patch('studentAdvisor_flaskapp.generate_advisory_prompt')
    @patch('studentAdvisor_flaskapp.send_prompt_to_openai')
    @patch('studentAdvisor_flaskapp.check_prerequisites')
    def test_generate_recommendation(self, mock_prereq, mock_openai, mock_prompt):
        mock_job = {'requirements': []}
        mock_transcript = {'courses': []}
        mock_recommendations = "Course recommendations"
        mock_prereqs = "Prerequisites"
        
        mock_prompt.return_value = "Test prompt"
        mock_openai.return_value = mock_recommendations
        mock_prereq.return_value = mock_prereqs
        
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['job_description_json'] = mock_job
                session['transcript_json'] = mock_transcript
            
            response = client.get('/generate_recommendation')
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertIn(mock_recommendations, data['combined_text'])
            self.assertIn(mock_prereqs, data['combined_text'])

    def test_check_prerequisites_no_transcript(self):
        test_data = {'response_text': 'Test response'}
        response = self.app.post('/check_prerequisites',
                               json=test_data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()