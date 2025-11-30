"""Test upload endpoint to debug the error."""
import requests

url = 'http://127.0.0.1:5000/upload'

# Test 1: Upload very_long_resume.txt
print("Test 1: Upload very_long_resume.txt...")
try:
    with open('test_edge_cases/very_long_resume.txt', 'rb') as resume, \
         open('test_edge_cases/job_description.txt', 'rb') as job:
        files = {
            'resume': ('very_long_resume.txt', resume, 'text/plain'),
            'job_description': ('job_description.txt', job, 'text/plain')
        }
        response = requests.post(url, files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        print()
except Exception as e:
    print(f"Error: {e}\n")

# Test 2: Upload empty_resume.docx
print("Test 2: Upload empty_resume.docx...")
try:
    with open('test_edge_cases/empty_resume.docx', 'rb') as resume, \
         open('test_edge_cases/job_description.txt', 'rb') as job:
        files = {
            'resume': ('empty_resume.docx', resume, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            'job_description': ('job_description.txt', job, 'text/plain')
        }
        response = requests.post(url, files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        print()
except Exception as e:
    print(f"Error: {e}\n")

# Test 3: Upload minimal_resume.txt
print("Test 3: Upload minimal_resume.txt...")
try:
    with open('test_edge_cases/minimal_resume.txt', 'rb') as resume, \
         open('test_edge_cases/job_description.txt', 'rb') as job:
        files = {
            'resume': ('minimal_resume.txt', resume, 'text/plain'),
            'job_description': ('job_description.txt', job, 'text/plain')
        }
        response = requests.post(url, files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        print()
except Exception as e:
    print(f"Error: {e}\n")
