# LLM RAG Backend

FastAPI backend connecting the frontend to the AI RAG pipeline.

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:5000`

## API Endpoints

- `POST /chat` - Create new chat session and get AI response
  - Body: `{ "query": "question", "user_id": "user-id" }`
  - Returns: `{ "chat_id": "...", "answer": "...", "source": "...", "marks": 0 }`

- `GET /chat/{chat_id}/{user_id}` - Get messages for a chat session

- `POST /chat/{chat_id}/message` - Add message to existing chat

- `GET /user/{user_id}/chats` - Get all chat sessions for a user

- `DELETE /chat/{chat_id}` - Delete a chat session

- `GET /health` - Health check

## Architecture

The backend:
1. Receives requests from the React frontend
2. Processes queries through the RAG pipeline (`ai/pipeline.py`)
3. Stores chat history in SQLite database
4. Returns structured responses to the frontend

## Database

Chat history is stored in `backend/chat_history.db` with two tables:
- `chat_sessions` - Chat session metadata
- `messages` - Individual messages with query/response pairs
