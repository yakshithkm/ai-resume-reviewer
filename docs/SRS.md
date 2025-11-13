# Software Requirements Specification (SRS)
## AI Resume Reviewer System

### 1. Introduction
#### 1.1 Purpose
This document outlines the software requirements for an AI-powered Resume Review System that analyzes resumes against job descriptions, providing automated feedback and scoring.

#### 1.2 Scope
The system will provide a web interface for resume uploads, perform NLP-based analysis, and generate detailed feedback reports.

### 2. System Requirements

#### 2.1 Functional Requirements

##### 2.1.1 File Upload and Processing
- FR1: System shall accept PDF and DOCX resume uploads
- FR2: System shall accept job description text input or file upload
- FR3: System shall extract text content from uploaded documents
- FR4: System shall identify and parse resume sections (contact, education, experience, skills)

##### 2.1.2 Analysis and Scoring
- FR5: System shall extract keywords and skills from both resume and job description
- FR6: System shall compute similarity scores using TF-IDF and cosine similarity
- FR7: System shall identify missing skills and keywords
- FR8: System shall generate specific improvement suggestions

##### 2.1.3 User Interface
- FR9: System shall provide a web interface for file upload
- FR10: System shall display analysis results in a structured format
- FR11: System shall allow downloading of feedback reports
- FR12: System shall show processing status and error messages

#### 2.2 Non-Functional Requirements

##### 2.2.1 Performance
- NFR1: File upload processing shall complete within 30 seconds
- NFR2: Analysis and scoring shall complete within 15 seconds
- NFR3: System shall handle files up to 10MB in size

##### 2.2.2 Security
- NFR4: Uploaded files shall be securely stored
- NFR5: User data shall be deleted after processing
- NFR6: System shall validate file types and content

##### 2.2.3 Usability
- NFR7: Interface shall be responsive and mobile-friendly
- NFR8: Error messages shall be clear and actionable
- NFR9: Results shall be presented in an easy-to-understand format

### 3. Technical Requirements

#### 3.1 Development Stack
- Python 3.8 or higher
- Flask web framework
- spaCy for NLP processing
- scikit-learn for TF-IDF and similarity scoring
- SQLite for metadata storage
- HTML5/CSS3/JavaScript for frontend

#### 3.2 Development Tools
- VS Code IDE
- Git for version control
- pytest for testing
- Python virtual environment

### 4. Constraints and Assumptions
- System will be developed and tested on Windows
- Initial release will support English language only
- Local deployment only (no cloud hosting required)
- Maximum concurrent users: 5 (development environment)

### 5. Timeline
- Development: October 29 - November 8, 2025
- Testing and Documentation: November 8-10, 2025
- Final Submission: November 10, 2025