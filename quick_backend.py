from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

# Load environment variables from .env file
try:
    with open('backend/.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    print("Warning: backend/.env file not found")

def call_openrouter_api(api_key, prompt):
    """Call OpenRouter API to get AI response"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    data = {
        "model": "google/gemma-3-12b-it:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://skill-assessment-agent.app',
        'X-Title': 'Skill Assessment Agent'
    }
    
    try:
        req = urllib.request.Request(url, json.dumps(data).encode('utf-8'), headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"API call failed: {e}")
        return None

class SimpleHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()

    def do_POST(self):
        if self.path.startswith('/api/'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if 'assess' in self.path:
                try:
                    # Load API key from environment
                    api_key = os.getenv('OPENROUTER_API_KEY', '')
                    print(f"API Key found: {'Yes' if api_key else 'No'}")
                    if not api_key:
                        response = {
                            "message": "Error: OpenRouter API key not configured. Please set OPENROUTER_API_KEY environment variable.",
                            "is_complete": False,
                            "assessment_data": None
                        }
                    else:
                        data = json.loads(post_data.decode('utf-8'))
                        job_desc = data.get('job_description', '')
                        resume = data.get('resume', '')
                        conversation = data.get('conversation_history', [])
                        
                        # Build the AI prompt
                        system_prompt = """You are an expert technical interviewer conducting a skill assessment. Your task is to:

1. Assess the candidate's proficiency level for each required skill based on their resume
2. Ask targeted questions to verify their real proficiency level
3. Keep conversations focused and efficient (maximum 5-6 total exchanges)
4. Provide evidence-based assessments
5. Identify skill gaps and adjacent skills

For each skill, assess proficiency as: Beginner, Intermediate, Advanced, or Expert
Always provide specific evidence from their responses to justify your assessment.

Be conversational but professional. Ask one question at a time and wait for the candidate's response before proceeding."""
                        
                        if len(conversation) == 0:
                            # Start new assessment
                            user_prompt = f"""CANDIDATE RESUME:
{resume}

JOB DESCRIPTION:
{job_desc}

Please assess the candidate's proficiency in the required skills based on their resume.
Ask targeted questions to verify their real proficiency level.

Start the skill assessment by introducing yourself and explaining the process. Then ask about the first relevant skill."""
                        else:
                            # Continue conversation
                            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation[-4:]])
                            user_prompt = f"""Continue the skill assessment conversation.

RECENT CONVERSATION:
{conversation_text}

CANDIDATE RESUME:
{resume}

JOB DESCRIPTION:
{job_desc}

Ask the next relevant question to assess the candidate's skills. If you have enough information (after 5-6 exchanges), provide a summary assessment."""
                        
                        # Call OpenRouter API
                        ai_response = call_openrouter_api(api_key, f"[Instructions: {system_prompt}]\n\n{user_prompt}")
                        print(f"AI Response: {ai_response[:100] if ai_response else 'None'}")
                        
                        if ai_response:
                            # Check if assessment is complete
                            is_complete = len(conversation) >= 10 or "assessment complete" in ai_response.lower() or "thank you" in ai_response.lower()
                            
                            if is_complete:
                                response = {
                                    "message": ai_response,
                                    "is_complete": True,
                                    "assessment_data": {
                                        "skills_assessed": [
                                            {"skill": "Communication", "proficiency_level": "Intermediate", "evidence": "Clear responses during assessment"},
                                            {"skill": "Technical Knowledge", "proficiency_level": "Advanced", "evidence": "Demonstrated understanding of concepts"}
                                        ],
                                        "recommended_focus_areas": ["Continue skill development"],
                                        "adjacent_skills": ["Problem solving", "Team collaboration"]
                                    }
                                }
                            else:
                                response = {
                                    "message": ai_response,
                                    "is_complete": False,
                                    "assessment_data": None
                                }
                        else:
                            # Fallback if API fails
                            response = {
                                "message": "I'm having trouble connecting to the AI service. Let me ask a follow-up question: Could you tell me more about your most recent project experience?",
                                "is_complete": False,
                                "assessment_data": None
                            }
                        
                except Exception as e:
                    response = {
                        "message": f"Error processing request: {str(e)}",
                        "is_complete": False,
                        "assessment_data": None
                    }
            elif 'quick-assessment' in self.path:
                response = {
                    "skills_assessed": [
                        {"skill": "Python", "proficiency_level": "Advanced", "evidence": "5 years experience mentioned in resume"},
                        {"skill": "React", "proficiency_level": "Intermediate", "evidence": "React projects listed"}
                    ],
                    "recommended_focus_areas": ["Advanced React patterns", "System design"],
                    "adjacent_skills": ["TypeScript", "Node.js"]
                }
            elif 'generate-plan' in self.path:
                response = {
                    "learning_plan": {
                        "learning_path": [
                            {
                                "title": "Advanced React Patterns",
                                "duration_weeks": 4,
                                "skills": ["React Hooks", "State Management"],
                                "resources": [
                                    {"title": "React Advanced Patterns", "type": "course", "estimated_hours": 20}
                                ],
                                "project": "Build a complex React application"
                            }
                        ],
                        "total_duration_weeks": 4,
                        "success_metrics": ["Complete advanced React course", "Build complex app"]
                    }
                }
            else:
                response = {"error": "Unknown endpoint"}
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), SimpleHandler)
    print("Quick backend running on http://localhost:8000")
    server.serve_forever()
