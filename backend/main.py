"""
AI-Powered Skill Assessment & Personalized Learning Plan Agent
Backend API with OpenRouter AI integration
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
