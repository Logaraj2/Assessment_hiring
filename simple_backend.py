from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse

def call_openrouter_api(api_key, prompt):
    """Call OpenRouter API to get AI response"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    data = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
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
            print(f"API Response Status: {response.getcode()}")
            return result['choices'][0]['message']['content']
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None
    except Exception as e:
        print(f"API call failed: {type(e).__name__}: {e}")
        return None

class SimpleHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if 'assess' in self.path:
            try:
                # Use the provided API key directly
                api_key = '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'
                print(f"API Key found: {'Yes' if api_key else 'No'}")
                
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
                    conversation_text = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation[-4:]])
                    user_prompt = f"""Continue the skill assessment conversation.

RECENT CONVERSATION:
{conversation_text}

CANDIDATE RESUME:
{resume}

JOB DESCRIPTION:
{job_desc}

Ask the next relevant question to assess the candidate's skills. If you have enough information (after 5-6 exchanges), provide a summary assessment."""
                
                # Call OpenRouter API
                ai_response = call_openrouter_api(api_key, f"[Instructions: {system_prompt}]\\n\\n{user_prompt}")
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
                    # Fallback if API fails - provide contextual questions
                    fallback_questions = [
                        "I see you have Python experience. Can you describe a challenging Python project you've worked on?",
                        "Tell me about your experience with React and any complex components you've built.",
                        "How have you used AWS or cloud services in your previous projects?",
                        "Describe your experience with database design and SQL optimization.",
                        "What's your approach to testing and code quality in your development process?",
                        "Can you explain a time you had to optimize application performance?",
                        "How do you handle version control and team collaboration using Git?",
                        "Tell me about your experience with RESTful API design and implementation."
                    ]
                    
                    # Use conversation length to pick different fallback questions
                    question_index = len(conversation) // 2
                    fallback_question = fallback_questions[min(question_index, len(fallback_questions) - 1)]
                    
                    response = {
                        "message": fallback_question,
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
                            "title": "Advanced React Development",
                            "duration_weeks": 8,
                            "skills": ["React Hooks", "State Management", "Performance Optimization"],
                            "resources": [
                                {"title": "React Advanced Patterns", "type": "course", "estimated_hours": 40},
                                {"title": "Build a Production App", "type": "project", "estimated_hours": 60}
                            ],
                            "project": "Build a full-stack React application with TypeScript"
                        }
                    ],
                    "total_duration_weeks": 8,
                    "success_metrics": ["Complete advanced React course", "Deploy production app"]
                }
            }
        else:
            response = {"error": "Endpoint not found"}
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHandler)
    print('Simple backend running on http://localhost:8000')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
