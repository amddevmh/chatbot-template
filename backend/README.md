# Nutrition Assistant Backend API

This is a FastAPI backend for the Nutrition Assistant application. It provides endpoints for chat message processing, nutrition information extraction, and nutrition tracking.

## Complete Setup Guide (From Step 0)

### Prerequisites

- Python 3.8+ installed on your system
- Basic knowledge of terminal/command line

### Step 1: Clone the Repository (if you haven't already)

```bash
git clone <repository-url>
cd chatbot-template
```

### Step 2: Set Up Python Virtual Environment

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip to the latest version
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# The .env file should already exist with default values
# Edit it if you need to change any settings
# Example: Add your OpenAI API key
```

The default `.env` file contains:
```
API_PORT=8000
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 5: Run the Server

```bash
# Make sure you're in the backend directory with activated virtual environment
python run.py
```

The server will start on port 8000 by default (configurable in .env file).
You should see output similar to:
```
INFO:     Will watch for changes in these directories: ['/path/to/chatbot-template/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Verify the Server is Running

Open your browser and navigate to:
```
http://localhost:8000/health
```

Or use curl from the terminal:
```bash
curl http://localhost:8000/health
```

You should see a response like:
```json
{"status":"healthy","message":"API is running"}
```

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /api/chat/message` - Process chat messages
- `POST /api/nutrition/extract` - Extract nutrition information from user messages
- `POST /api/nutrition/confirm/{nutrition_id}` - Confirm extracted nutrition information
- `POST /api/nutrition/reject/{nutrition_id}` - Reject extracted nutrition information

## Testing the API

### Using curl

```bash
# Test the chat endpoint
curl -X POST -H "Content-Type: application/json" -d '{"message": "I had a salad for lunch"}' http://localhost:8000/api/chat/message

# Test the nutrition extraction endpoint
curl -X POST -H "Content-Type: application/json" -d '{"message": "I had a salad with chicken, tomatoes, and olive oil"}' http://localhost:8000/api/nutrition/extract
```

## Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in the `.env` file
   - Check if another process is using port 8000

2. **Package installation errors**
   - Try updating pip: `pip install --upgrade pip`
   - Make sure you're using a compatible Python version

3. **Environment activation issues**
   - Ensure you've activated the virtual environment before running commands
   - The terminal prompt should show `(venv)` when activated

## Development

The server uses hot-reloading, so any changes you make to the code will automatically restart the server.
