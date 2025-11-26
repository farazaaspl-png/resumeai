# FastAPI Server with File Upload

## Installation

The dependencies are already installed in the virtual environment. If you need to install them manually:

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
cd backend
python -m uvicorn main:app --reload
```

The server will start at: http://127.0.0.1:8000

## API Endpoints

### 1. Root Endpoint
- **URL**: `GET /`
- **Response**: Server status message

### 2. Upload Form with File
- **URL**: `POST /upload`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `name` (string, required): User's name
  - `email` (string, required): User's email
  - `message` (string, optional): Optional message
  - `file` (file, required): File to upload

### 3. Health Check
- **URL**: `GET /health`
- **Response**: Health status

## Testing the API

### Using curl:
```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "message=Test message" \
  -F "file=@path/to/your/file.pdf"
```

### Using Python requests:
```python
import requests

url = "http://127.0.0.1:8000/upload"
files = {"file": open("document.pdf", "rb")}
data = {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Test message"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Interactive API Documentation
Visit http://127.0.0.1:8000/docs for Swagger UI to test the API interactively.

## Features

- ✅ FastAPI server with CORS enabled
- ✅ File upload endpoint accepting multipart form data
- ✅ Form validation
- ✅ Uploaded files saved to `uploads/` directory
- ✅ Detailed response with file information
- ✅ Auto-reload during development
