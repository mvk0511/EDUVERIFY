import requests

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("--- Testing /login ---")
    login_data = {"roll_no": "22CS101", "email": "student@gmail.com"}
    res = requests.post(f"{BASE_URL}/login", json=login_data)
    print("Login status:", res.status_code, res.json())

    print("\n--- Testing /upload ---")
    with open("dummy.pdf", "wb") as f:
        f.write(b"%PDF-1.4 dummy pdf content")
    
    with open("dummy.pdf", "rb") as f:
        files = {"file": ("test_submission.pdf", f, "application/pdf")}
        data = {
            "roll_no": "22CS101",
            "email": "student@gmail.com",
            "student_id": 99,
            "assignment_id": 101
        }
        res = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        print("Upload status:", res.status_code, res.json())

    print("\n--- Testing /submissions (Success) ---")
    res = requests.get(f"{BASE_URL}/submissions?roll_no=22CS101&email=student@gmail.com")
    print("Submissions status:", res.status_code, res.json())

    print("\n--- Testing /submissions (Validation Failure) ---")
    res = requests.get(f"{BASE_URL}/submissions")
    print("Submissions failure status:", res.status_code, res.json())

if __name__ == "__main__":
    test_api()
