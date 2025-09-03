# Student Advisor Project

A comprehensive course recommendation system for Computer Science students at the University of Washington. This project uses AI to analyze job descriptions and student transcripts to provide personalized course recommendations.

## 🚀 Features

- **Job Description Analysis**: Parse and analyze job postings to extract key requirements
- **Transcript Processing**: Extract and structure student academic history from PDF transcripts
- **AI-Powered Recommendations**: Use OpenAI's GPT models to generate personalized course suggestions
- **Prerequisite Checking**: Verify course prerequisites against student's completed courses
- **Course Database**: Comprehensive database of UW CSE courses with descriptions and prerequisites
- **Web API**: RESTful API for frontend integration
- **Embedding-Based Matching**: Use semantic embeddings to match job requirements with course content

## 🏗️ Architecture

### Backend (Flask API)
- **`studentAdvisor_flaskapp.py`**: Main Flask application with REST endpoints
- **`model_Interactor.py`**: Core logic for generating prompts and interacting with OpenAI
- **`config.py`**: Configuration management for database paths and environment variables

### Data Processing
- **`jobDescriptionAnalyser.py`**: Parse job descriptions from PDF or text
- **`Transcript_Analyzer.py`**: Extract structured data from student transcripts
- **`prereq_checker.py`**: Check course prerequisites against student's academic history

### AI & Embeddings
- **`scripts/jd_processor.py`**: Process job descriptions and create embeddings
- **`utils/embedding_utils.py`**: Utilities for creating and managing course embeddings
- **`embedding_Creator.py`**: Generate embeddings for course descriptions

### Database
- **`CourseDatabase_HCDE.py`**: Database operations for course information
- **`CoursesDatabase.py`**: Course data management and normalization
- **`course_database.db`**: SQLite database containing course information

### Utilities
- **`utils/analysis_utils.py`**: Analysis utilities for course rankings
- **`ranking_tester.py`**: Testing utilities for recommendation algorithms

## 📁 Project Structure

```
studentAdvisorProject/
├── studentAdvisor_flaskapp.py    # Main Flask application
├── model_Interactor.py           # Core AI interaction logic
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── data/                       # Data files
│   └── course_database.db      # Course database
├── utils/                      # Utility modules
│   ├── embedding_utils.py      # Embedding utilities
│   └── analysis_utils.py       # Analysis utilities
├── scripts/                    # Processing scripts
│   └── jd_processor.py        # Job description processor
├── notebooks/                  # Jupyter notebooks for experimentation
└── frontend/                   # Frontend application (if applicable)
```

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- Git
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hbothra1/studentAdvisorProject.git
   cd studentAdvisorProject
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

5. **Run the application**
   ```bash
   gunicorn studentAdvisor_flaskapp:app
   ```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for GPT model access
- `DB_PATH`: Path to the course database (defaults to `data/course_database.db`)

### Database Setup
The application uses a SQLite database containing:
- Course information (codes, titles, descriptions)
- Prerequisites and course relationships
- Course embeddings for semantic matching

## 📡 API Endpoints

### Core Endpoints

#### `GET /`
- **Description**: Health check endpoint
- **Response**: `{"message": "Flask API is running!"}`

#### `GET /api/courses`
- **Description**: Retrieve all courses or search by term
- **Query Parameters**: 
  - `search` (optional): Search term for course code or title
- **Response**: Array of course objects with `course_code` and `course_name`

#### `POST /process_job_description_text`
- **Description**: Process job description text
- **Body**: `{"text": "job description text"}`
- **Response**: Confirmation message

#### `POST /process_transcript_json`
- **Description**: Process student transcript data
- **Body**: Transcript JSON data
- **Response**: Confirmation message

#### `POST /generate_recommendation`
- **Description**: Generate course recommendations
- **Prerequisites**: Job description and transcript must be processed first
- **Response**: `{"recommendation_text": "AI-generated recommendations"}`

#### `POST /check_prerequisites`
- **Description**: Check prerequisites for recommended courses
- **Body**: `{"response_text": "recommendations text"}`
- **Response**: Prerequisites analysis

## 🤖 How It Works

### 1. Job Description Processing
- Job descriptions are parsed and restructured using GPT
- Key requirements are extracted and converted to embeddings
- The system identifies technical skills, tools, and domain knowledge

### 2. Transcript Analysis
- PDF transcripts are processed to extract course history
- Student's academic background is structured for analysis
- Completed courses and grades are catalogued

### 3. Course Matching
- Course descriptions are converted to embeddings
- Semantic similarity is calculated between job requirements and courses
- Courses are ranked based on relevance to job requirements

### 4. AI Recommendation Generation
- A comprehensive prompt is generated combining:
  - Job description analysis
  - Student's academic history
  - Relevant course details
- GPT generates personalized course recommendations
- Recommendations include specific examples and justifications

### 5. Prerequisite Verification
- System checks if student meets prerequisites for recommended courses
- Identifies missing prerequisites
- Suggests prerequisite courses if needed

## 🚀 Deployment

### Local Development
```bash
gunicorn studentAdvisor_flaskapp:app
```

### Cloud Deployment (Render)
1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Configure build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn studentAdvisor_flaskapp:app`

## 🧪 Testing

### API Testing with Postman
1. Import the API endpoints into Postman
2. Use your Render URL: `https://your-app-name.onrender.com`
3. Test endpoints with sample data

### Local Testing
```bash
# Test the home endpoint
curl http://localhost:8000/

# Test course search
curl "http://localhost:8000/api/courses?search=math"
```

## 🔒 Security Considerations

- API keys are stored as environment variables
- CORS is configured for specific origins
- Input validation is implemented for all endpoints
- Database connections are properly managed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- University of Washington CSE Department for course data
- OpenAI for GPT model access
- Flask community for web framework
- Render for cloud hosting platform

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Note**: This project is designed specifically for UW CSE students and may need modifications for other institutions or departments. 