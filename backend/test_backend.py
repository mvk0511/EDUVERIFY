import requests
import json
import os

base_url = "http://127.0.0.1:8000"

def check(name, resp):
    print(f"{name:40} | Status: {resp.status_code}")
    if resp.status_code not in (200, 201):
        print(f"Error detail: {resp.text}")

def test_api():
    try:
        check("GET /submissions", requests.get(f"{base_url}/submissions"))
        check("GET /detect", requests.get(f"{base_url}/detect"))
        check("GET /api/submissions/detect-plagiar...", requests.get(f"{base_url}/api/submissions/detect-plagiarism"))
        
        # Make dummy file for upload
        with open("dummy3.pdf", "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n")
            
        with open("dummy3.pdf", "rb") as f:
            resp = requests.post(f"{base_url}/upload", files={"file": ("dummy3.pdf", f, "application/pdf")})
        check("POST /upload", resp)
        
        with open("dummy3.pdf", "rb") as f:
            resp = requests.post(f"{base_url}/api/assignments/upload?student_id=1&assignment_id=2", files={"file": ("dummy3.pdf", f, "application/pdf")})
        check("POST /api/assignments/upload", resp)
        
        # Test Auth
        check("POST /api/auth/register/student", requests.post(f"{base_url}/api/auth/register/student", json={"name": "A", "email": "a@a.com", "password": "b", "department": "CS", "semester": "1"}))
        check("POST /api/auth/register/teacher", requests.post(f"{base_url}/api/auth/register/teacher", json={"name": "A", "email": "a@a.com", "password": "b", "department": "CS", "subject": "Math"}))
        check("POST /api/auth/login", requests.post(f"{base_url}/api/auth/login", json={"email": "a@a.com", "password": "b", "role": "student"}))
        
        # Test Assignments
        check("GET /api/assignments", requests.get(f"{base_url}/api/assignments"))
        check("POST /api/assignments", requests.post(f"{base_url}/api/assignments", json={"teacher_id": 1, "title": "A", "description": "B", "subject": "CS", "deadline": "2026-01-01T00:00:00Z"}))
        
        # Test Tasks
        check("GET /api/tasks/student/1", requests.get(f"{base_url}/api/tasks/student/1"))
        check("POST /api/tasks", requests.post(f"{base_url}/api/tasks", json={"student_id":1, "task_name": "Read", "task_date": "2026-01-01T00:00:00Z"}))
        check("PUT /api/tasks/1/toggle", requests.put(f"{base_url}/api/tasks/1/toggle"))
        
        # Test General
        check("GET /api/students", requests.get(f"{base_url}/api/students"))
        check("GET /api/submissions", requests.get(f"{base_url}/api/submissions"))
        
        # Test chatbot
        check("POST /api/chatbot/ask", requests.post(f"{base_url}/api/chatbot/ask", json={"user_id":1, "role": "student", "message": "hello"}))
        
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_api()
