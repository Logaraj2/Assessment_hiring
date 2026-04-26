# AI-Powered Skill Assessment & Personalized Learning Plan Agent

**Built for Deccan AI Catalyst Hackathon 2026**

An intelligent agent that assesses candidates' real proficiency against job requirements and generates personalized learning roadmaps with curated resources and realistic time estimates.

## Deployment on Netlify

### Prerequisites
- Netlify account
- GitHub repository
- OpenRouter API key (free models available)

### Setup Instructions

#### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Netlify deployment"
git push origin main
```

#### 2. Connect to Netlify
1. Go to [Netlify](https://netlify.com)
2. Click "New site from Git"
3. Connect your GitHub repository
4. Configure build settings:
   - **Build command**: (leave empty)
   - **Publish directory**: `frontend`
   - **Functions directory**: `netlify/functions`

#### 3. Set Environment Variables
In Netlify dashboard:
- Go to Site settings > Environment variables
- Add: `OPENROUTER_API_KEY` = your OpenRouter API key
- Add: `PYTHON_VERSION` = 3.9

#### 4. Deploy
- Click "Deploy site"
- Wait for build to complete
- Your site will be live at the provided URL

### Local Testing with Netlify CLI (Optional)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Set env vars locally
netlify env:set OPENROUTER_API_KEY your-api-key-here

# Test functions locally
netlify dev
```

### Local Development (Original)

#### Prerequisites
- Python 3.9+
- OpenRouter API key

#### Setup
```bash
git clone <your-repo-url>
cd resume-assessment

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variable
export OPENROUTER_API_KEY=your-api-key-here

# Run the app
python backend/main.py
```

Open http://localhost:8000 in your browser.

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp ../.env.example .env
# Edit .env and add your OPENROUTER_API_KEY (get from https://openrouter.ai/keys)
```

#### 3. Start Backend Server
```bash
python main.py
```
Server runs on `http://localhost:8000`

#### 4. Frontend (Browser)
```bash
# Open in browser (from project root)
cd frontend
# Serve the HTML file - can use any http server
# Python: python -m http.server 8080
# Or just open index.html directly in browser
```

Frontend connects to backend at `http://localhost:8000/api`

## Features

- **Resume Upload** - Upload PDF, DOCX, or TXT resume files for automatic text extraction
- **Skill Extraction** - Automatically extracts required skills from job descriptions
- **Conversational Assessment** - Multi-turn dialogue for realistic proficiency evaluation
- **Gap Analysis** - Identifies skill gaps and proficiency levels
- **Adjacent Skills** - Recommends complementary skills for efficient learning
- **Personalized Learning Plans** - Phase-based roadmaps with curated resources, time estimates, project suggestions, and success metrics
- **Confidence Scoring** - Tracks assessment confidence for each skill
- **Realistic Timelines** - 12-week achievable learning paths

## Project Structure

```
resume-assessment/
├── .env.example                    # Environment variable template
├── README.md
├── backend/
│   ├── main.py                     # Entrypoint (uvicorn target)
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (not in git)
│   └── app/
│       ├── __init__.py             # App factory (create_app)
│       ├── config.py               # Settings via pydantic-settings
│       ├── schemas.py              # Pydantic request/response models
│       ├── prompts.py              # AI system prompt constants
│       ├── ai_client.py            # OpenRouter API wrapper
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── health.py           # GET /, GET /health
│       │   ├── assessment.py       # POST /api/assess, /api/quick-assessment
│       │   ├── plan.py             # POST /api/generate-plan
│       │   └── upload.py           # POST /api/upload-resume
│       └── services/
│           ├── __init__.py
│           ├── assessment.py       # Assessment business logic
│           ├── plan.py             # Learning plan generation logic
│           └── file_parser.py      # Resume file parsing (PDF, DOCX, TXT)
└── frontend/
    ├── index.html                  # Web UI (HTML + JavaScript)
    └── styles.css                  # Stylesheet
```

## Architecture

```
Frontend (index.html + styles.css)
    │
    │ HTTP/JSON
    ▼
FastAPI Backend
  main.py (entrypoint)
    ├── app/__init__.py         App factory, CORS, router registration
    ├── app/routers/            Route definitions (thin controllers)
    ├── app/services/           Business logic (AI orchestration)
    ├── app/ai_client.py        OpenRouter API calls + JSON parsing
    ├── app/schemas.py          Request/response models
    ├── app/prompts.py          System prompt constants
    └── app/config.py           Settings from environment variables
    │
    ▼
OpenRouter API → Free AI Models (Google Gemma, Meta Llama, etc.)
```

### Data Flow

1. **Input**: Job description + Candidate resume (paste or upload PDF/DOCX/TXT)
2. **Skill Extraction**: Parse JD to identify required skills
3. **Assessment**:
   - AI asks targeted questions
   - Evaluates proficiency (beginner → expert)
   - Tracks confidence scores
4. **Gap Analysis**: Compare candidate proficiency vs. requirements
5. **Learning Plan**: Generate phase-based roadmap with adjacent skill recommendations, curated resources, time estimates, and success metrics

## API Endpoints

### POST `/api/upload-resume`
Upload a resume file (PDF, DOCX, TXT) and extract text.

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "text": "Extracted resume text..."
}
```

### POST `/api/quick-assessment`
End-to-end assessment without conversation.

**Request:**
```json
{
  "job_description": "Senior Python Engineer...",
  "resume": "John Doe\nSkills: Python, React...",
  "conversation_history": []
}
```

**Response:**
```json
{
  "skills_assessed": [
    {
      "skill": "Python",
      "proficiency_level": "advanced",
      "evidence": "5 years Django/FastAPI experience",
      "confidence": 0.95,
      "gap_analysis": "Could strengthen async patterns"
    }
  ],
  "adjacent_skills": ["FastAPI", "SQLAlchemy", "Async patterns"],
  "recommended_focus_areas": ["Microservices", "System Design"],
  "learning_plan": {}
}
```

### POST `/api/assess`
Conversational assessment endpoint for multi-turn interactions.

**Request:**
```json
{
  "job_description": "...",
  "resume": "...",
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### POST `/api/generate-plan`
Generate learning plan from assessment results.

**Request:**
```json
{
  "assessment_results": {},
  "candidate_name": "John Doe"
}
```

**Response:**
```json
{
  "learning_plan": {
    "learning_path": [
      {
        "phase": 1,
        "title": "Microservices Foundations",
        "skills": ["Event-driven architecture", "Message queues"],
        "duration_weeks": 4,
        "resources": [
          {
            "title": "Building Microservices",
            "type": "book",
            "estimated_hours": 20
          }
        ],
        "project": "Build a multi-service order processing system"
      }
    ],
    "total_duration_weeks": 12,
    "success_metrics": [
      "Deploy a microservices app to production",
      "Understand service communication patterns"
    ]
  }
}
```

## Scoring Logic

**Proficiency Levels:**
- **Beginner**: < 6 months hands-on experience
- **Intermediate**: 6 months - 2 years
- **Advanced**: 2+ years with diverse projects
- **Expert**: Deep specialization, mentoring others

**Confidence Score:**
- High (0.8-1.0): Clear evidence from resume/interview
- Medium (0.5-0.8): Some evidence, needs verification
- Low (<0.5): Unclear or contradictory signals

## Free AI Models

The app uses OpenRouter with free AI models (no payment required):

| Model | ID |
|---|---|
| Google Gemma 3 12B | `google/gemma-3-12b-it:free` |
| Google Gemma 3 27B | `google/gemma-3-27b-it:free` |
| Meta Llama 3.3 70B | `meta-llama/llama-3.3-70b-instruct:free` |
| Qwen 3 Coder | `qwen/qwen3-coder:free` |

Change the model in `.env` by updating `AI_MODEL`.

## Deployment

### Local Deployment
See "Quick Start" section above.

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend:** Deploy `frontend/` to any static hosting (GitHub Pages, Vercel, Netlify)

## Environment Variables

Create `.env` in backend directory:
```
OPENROUTER_API_KEY=your-openrouter-api-key-here
AI_MODEL=google/gemma-3-12b-it:free
```

Get your API key from [openrouter.ai/keys](https://openrouter.ai/keys)

## Technologies

- **Backend**: Python, FastAPI, Uvicorn, Pydantic
- **AI**: Free models via OpenRouter (Google Gemma, Meta Llama)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **API**: RESTful with JSON

## Testing the Application

1. Open `http://localhost:8000/docs` for Swagger API docs
2. Open the frontend and click "Load Sample" to populate sample data
3. Click "Start Assessment"
4. View results in "Assessment Chat" tab
5. View personalized learning plan in "Learning Plan" tab

## Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (need 3.9+)
- Check API key in `.env`: `OPENROUTER_API_KEY=...`
- Check port 8000 is free

**Getting 429 rate limit errors?**
- Free models have rate limits — wait a minute and retry
- Try switching to a different free model in `.env`

**Frontend can't connect to backend?**
- Ensure backend is running on `http://localhost:8000`
- Check browser console for errors
- If serving frontend via file server, ensure CORS is working

**Assessment timeout?**
- AI requests take ~10-30 seconds
- Check internet connection
- Verify API key is valid

## License

MIT License - Built for Deccan AI Catalyst Hackathon 2026

## Author

Logaraj C
Deccan AI Catalyst Hackathon 2026
