# 🎯 AI-Powered Skill Assessment & Personalized Learning Plan Agent

**Built for Deccan AI Catalyst Hackathon 2026**

An intelligent agent that assesses candidates' real proficiency against job requirements and generates personalized learning roadmaps with curated resources and realistic time estimates.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js (for local development)
- Anthropic API key

### Setup Instructions

#### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd resume-assessment
```

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
# Edit .env and add your ANTHROPIC_API_KEY
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

## 📋 Features

✅ **Skill Extraction** - Automatically extracts required skills from job descriptions
✅ **Conversational Assessment** - Multi-turn dialogue for realistic proficiency evaluation
✅ **Gap Analysis** - Identifies skill gaps and proficiency levels
✅ **Adjacent Skills** - Recommends complementary skills for efficient learning
✅ **Personalized Learning Plans** - Phase-based roadmaps with:
   - Curated resources (courses, books, tutorials, projects)
   - Time estimates per resource
   - Real-world project suggestions
   - Success metrics
✅ **Confidence Scoring** - Tracks assessment confidence for each skill
✅ **Realistic Timelines** - 12-week achievable learning paths

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│   Frontend UI   │  (HTML/CSS/JS)
│  (index.html)   │
└────────┬────────┘
         │
         │ HTTP/JSON
         ↓
┌─────────────────────────────┐
│    FastAPI Backend          │  (main.py)
├─────────────────────────────┤
│  ├─ /api/assess             │  Conversational assessment
│  ├─ /api/generate-plan      │  Learning plan generation
│  └─ /api/quick-assessment   │  End-to-end analysis
└────────┬────────────────────┘
         │
         │ API Calls
         ↓
┌─────────────────────────────┐
│    Claude AI (Opus 4.6)     │  Multi-turn reasoning
│    - Skill extraction       │  - Assessment logic
│    - Learning plan design   │  - Resource curation
└─────────────────────────────┘
```

### Data Flow

1. **Input**: Job description + Candidate resume
2. **Skill Extraction**: Parse JD to identify required skills
3. **Assessment**: 
   - Claude asks targeted questions
   - Evaluates proficiency (beginner→expert)
   - Tracks confidence scores
4. **Gap Analysis**: Compare candidate proficiency vs. requirements
5. **Learning Plan**: Generate phase-based roadmap with:
   - Adjacent skill recommendations
   - Curated resources
   - Time estimates
   - Success metrics

## 📡 API Endpoints

### POST `/api/quick-assessment`
End-to-end assessment without conversation.

**Request:**
```json
{
  "job_description": "Senior Python Engineer...",
  "resume": "John Doe\nSkills: Python, React...",
  "conversation_history": []  // optional
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
  "learning_plan": {...}
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
  "assessment_results": {...},
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

## 📊 Sample Use Case

### Input
**Job Description:**
```
Senior Full-Stack Engineer - 5+ years required
Skills: Python (Django/FastAPI), React, AWS, SQL, REST APIs, CI/CD
```

**Resume:**
```
John Doe - 5 years full-stack experience
Skills: Python, Django, FastAPI, JavaScript, React, PostgreSQL, AWS
Experience: Built REST APIs, React dashboards, AWS infrastructure
```

### Output
**Assessment Results:**
- Python: **Advanced** (0.95 confidence) - Evidence: 5 years Django/FastAPI
- React: **Advanced** (0.90 confidence) - Evidence: Built dashboards
- AWS: **Intermediate** (0.85 confidence) - Gap: Needs deeper microservices knowledge
- REST APIs: **Advanced** (0.95 confidence)
- Database Design: **Intermediate** (0.80 confidence) - Gap: Advanced optimization

**Learning Plan:**
- **Phase 1 (4 weeks)**: Microservices Architecture & Scalability
- **Phase 2 (4 weeks)**: Advanced Database Optimization & Sharding
- **Phase 3 (4 weeks)**: System Design & Production Patterns
- **Total Duration**: 12 weeks
- **Adjacent Skills**: Docker/Kubernetes, Event-driven architecture, CQRS

## 🔧 Technologies

- **Backend**: Python, FastAPI, Uvicorn
- **AI**: Claude Opus 4.6 (Anthropic)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **API**: RESTful with JSON
- **LLM Integration**: Multi-turn conversational reasoning

## 📝 How the Assessment Works

### Phase 1: Skill Extraction
- Parses job description
- Identifies technical and soft skills
- Ranks by importance

### Phase 2: Initial Proficiency Evaluation
- Reviews candidate resume
- Maps experience to required skills
- Assigns initial proficiency levels

### Phase 3: Conversational Deepdive
- Claude asks targeted technical questions
- Evaluates:
  - Theoretical knowledge
  - Practical hands-on experience
  - Project complexity
  - Problem-solving approach
  - Communication clarity

### Phase 4: Confidence Scoring
- Assigns confidence 0.0-1.0 for each assessment
- Higher confidence = more sure of proficiency level
- Lower confidence = need follow-up questions

### Phase 5: Learning Plan Generation
- Identifies skill gaps
- Recommends adjacent/complementary skills
- Creates phase-based learning path
- Curates resources (courses, books, projects)
- Provides time estimates
- Suggests success metrics

## 🎯 Scoring Logic

**Proficiency Levels:**
- **Beginner**: < 6 months hands-on experience
- **Intermediate**: 6 months - 2 years
- **Advanced**: 2+ years with diverse projects
- **Expert**: Deep specialization, mentoring others

**Confidence Score:**
- High (0.8-1.0): Clear evidence from resume/interview
- Medium (0.5-0.8): Some evidence, needs verification
- Low (<0.5): Unclear or contradictory signals

## 📦 Deployment

### Local Deployment
See "Quick Start" section above.

### Production Deployment

**Heroku/Railway/Render:**
```bash
# Backend environment variables
ANTHROPIC_API_KEY=sk-ant-...

# Deploy and serve both backend and frontend
```

**Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend:** Deploy `frontend/index.html` to any static hosting (GitHub Pages, Vercel, Netlify)

## 🔐 Environment Variables

Create `.env` in backend directory:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

## 📚 Resources Referenced

- **LLM Model**: Claude Opus 4.6 for complex reasoning
- **Assessment Framework**: Based on industry standard technical interview practices
- **Learning Design**: Spaced repetition, project-based learning principles

## 🧪 Testing the Application

1. Open `http://localhost:8000` (or served frontend)
2. Click "Load Sample" to populate sample JD and resume
3. Click "Start Assessment"
4. View results in "Assessment Chat" tab
5. View personalized learning plan in "Learning Plan" tab

## 🐛 Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (need 3.9+)
- Check API key: `echo $ANTHROPIC_API_KEY`
- Check port 8000 is free: `lsof -i :8000`

**Frontend can't connect to backend?**
- Ensure backend is running on `http://localhost:8000`
- Check CORS is enabled (it is by default)
- Check browser console for errors

**Assessment timeout?**
- Claude takes ~10-30 seconds per request
- Check internet connection
- Verify API key is valid

## 📄 License

MIT License - Built for Deccan AI Catalyst Hackathon 2026

## 👨‍💻 Author

Logaraj C  
Deccan AI Catalyst Hackathon 2026

---

**Questions?** Email: support@deccanexperts.ai  
**Discord**: https://discord.gg/aczDnqNR
