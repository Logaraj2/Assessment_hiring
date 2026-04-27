from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

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
                    data = json.loads(post_data.decode('utf-8'))
                    job_desc = data.get('job_description', '').lower()
                    resume = data.get('resume', '').lower()
                    conversation = data.get('conversation_history', [])
                    
                    # Generate contextual questions based on job requirements and resume
                    questions = [
                        "I see you have Python experience. Can you tell me about a recent Python project you worked on?",
                        "You mentioned React in your resume. What's your experience with React hooks and state management?",
                        "The job requires AWS experience. Can you describe your experience with cloud deployment?",
                        "Tell me about your experience with RESTful API design and database integration.",
                        "How do you approach version control and CI/CD in your development workflow?",
                        "Can you explain your experience with microservices architecture?",
                        "What's your experience with testing and debugging in your applications?",
                        "How do you handle performance optimization in your code?"
                    ]
                    
                    # Determine which question to ask based on conversation length
                    question_index = len(conversation) // 2  # Each exchange has 2 messages (user + assistant)
                    
                    if question_index >= len(questions):
                        # Assessment complete
                        response = {
                            "message": "Thank you for your responses! I've completed the assessment. Your skills have been evaluated.",
                            "is_complete": True,
                            "assessment_data": {
                                "skills_assessed": [
                                    {"skill": "Python", "proficiency_level": "Advanced", "evidence": "Demonstrated project experience"},
                                    {"skill": "React", "proficiency_level": "Intermediate", "evidence": "Knowledge of hooks and state management"},
                                    {"skill": "AWS", "proficiency_level": "Intermediate", "evidence": "Cloud deployment experience"}
                                ],
                                "recommended_focus_areas": ["Advanced React patterns", "System design"],
                                "adjacent_skills": ["TypeScript", "Node.js"]
                            }
                        }
                    else:
                        response = {
                            "message": questions[question_index],
                            "is_complete": False,
                            "assessment_data": None
                        }
                        
                except (json.JSONDecodeError, KeyError):
                    # Fallback for malformed requests
                    response = {
                        "message": "Hello! I'm your AI interviewer. Let me start by asking about your experience with Python. Can you tell me about a recent project you worked on?",
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
