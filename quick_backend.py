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
