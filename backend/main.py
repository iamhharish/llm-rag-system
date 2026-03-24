import sys
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Add the ai folder to path so we can import the pipeline
ai_path = os.path.join(os.path.dirname(__file__), '..', 'ai')
sys.path.insert(0, ai_path)

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import re
import time
import requests
from urllib.parse import quote

# Import the AI pipeline while ai is in path
from pipeline import get_answer
from online_retrieval import get_online_data

# Remove ai from path to avoid import conflicts
sys.path.remove(ai_path)

# Now import database functions from local backend
from database import (
    init_db,
    create_chat_session,
    save_message,
    get_chat_session,
    get_chat_messages,
    get_user_chat_sessions,
    delete_chat_session,
)
from database_auth import (
    create_user,
    get_user_by_username_or_email,
    user_exists,
    init_auth_tables,
)


app = Flask(__name__)

print(f"\n\n=== MAIN.PY LOADED ===", file=sys.stderr, flush=True)
print(f"create_chat_session: {create_chat_session}", file=sys.stderr, flush=True)
print(f"create_chat_session module: {create_chat_session.__module__}", file=sys.stderr, flush=True)
print(f"=== END LOAD ===\n\n", file=sys.stderr, flush=True)

# Enable CORS for frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


@app.before_request
def startup():
    """Initialize database on first request."""
    import sys
    if not hasattr(app, 'db_initialized'):
        print("=== DB INIT START ===", file=sys.stderr, flush=True)
        try:
            init_db()
            init_auth_tables()
            app.db_initialized = True
            print("=== DB INIT COMPLETE ===", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"DB INIT ERROR: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)


def validate_email(email):
    """Simple email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Username must be 3-20 chars, alphanumeric and underscore."""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None


def build_online_fallback_answer(query):
    """
    Build a direct answer from online snippets when the RAG guard blocks output.
    This keeps UI responses useful without changing the AI pipeline code.
    """
    snippets = []
    max_retries = 3
    for attempt in range(max_retries):
        try:
            snippets = get_online_data(query)
            if snippets:
                break
        except Exception as e:
            print(f"Online fallback error (attempt {attempt + 1}/{max_retries}): {e}")
        time.sleep(0.6)

    if not snippets:
        wiki_summary = get_wikipedia_summary(query)
        if wiki_summary:
            return (
                f"{wiki_summary}\n\n📌 Source: Wikipedia | Marks: General"
            )
        return (
            "I could not find enough reliable online context right now. "
            "Please try rephrasing your question."
        )

    concise_snippets = [s.strip() for s in snippets if s and s.strip()][:3]
    return (
        "Here is what I found online:\n\n- "
        + "\n- ".join(concise_snippets)
        + "\n\n📌 Source: Online Search | Marks: General"
    )


def extract_topic_from_query(query):
    """Extract likely topic from common question forms."""
    q = query.strip().rstrip("?.! ")
    lower_q = q.lower()
    prefixes = [
        "what is ",
        "who is ",
        "define ",
        "explain ",
        "tell me about ",
    ]
    for prefix in prefixes:
        if lower_q.startswith(prefix):
            return q[len(prefix):].strip()
    return q


def get_wikipedia_summary(query):
    """
    Fallback source for consistent responses when search snippets are empty.
    Uses Wikipedia REST summary API with simple retries.
    """
    topic = extract_topic_from_query(query)
    if not topic:
        return None

    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(topic)}"
    headers = {"User-Agent": "llm-rag-system/1.0 (educational project)"}

    for attempt in range(2):
        try:
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get("extract", "").strip()
                if extract:
                    return extract
            # If exact title fails, try query search endpoint once.
            search_url = (
                "https://en.wikipedia.org/w/api.php"
                f"?action=query&list=search&srsearch={quote(topic)}&format=json&srlimit=1"
            )
            s_resp = requests.get(search_url, headers=headers, timeout=6)
            if s_resp.status_code == 200:
                s_data = s_resp.json()
                search_hits = s_data.get("query", {}).get("search", [])
                if search_hits:
                    page_title = search_hits[0].get("title", "")
                    if page_title:
                        summary_url = (
                            "https://en.wikipedia.org/api/rest_v1/page/summary/"
                            + quote(page_title)
                        )
                        p_resp = requests.get(summary_url, headers=headers, timeout=6)
                        if p_resp.status_code == 200:
                            p_data = p_resp.json()
                            extract = p_data.get("extract", "").strip()
                            if extract:
                                return extract
        except Exception as e:
            print(f"Wikipedia fallback error (attempt {attempt + 1}/2): {e}")
        time.sleep(0.4)

    return None


# ============= AUTHENTICATION ENDPOINTS =============

@app.post("/api/auth/register")
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip()

        # Validation
        if not username or not email or not password:
            return jsonify({"error": "Username, email, and password are required"}), 400

        if not validate_username(username):
            return jsonify({"error": "Username must be 3-20 characters and contain only letters, numbers, and underscores"}), 400

        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        # Check if user exists
        if user_exists(username, email):
            return jsonify({"error": "Username or email already exists"}), 409

        # Create user
        user_id = create_user(username, email, password, phone)

        return jsonify({
            "message": "Registration successful",
            "data": {
                "id": user_id,
                "username": username,
                "email": email
            }
        }), 201

    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({"error": "Registration failed"}), 500


@app.post("/api/auth/login")
def login():
    """Login user."""
    try:
        data = request.get_json()
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '').strip()

        if not username_or_email or not password:
            return jsonify({"error": "Username/email and password are required"}), 400

        # Get user
        user = get_user_by_username_or_email(username_or_email)

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({"error": "Invalid username/email or password"}), 401

        return jsonify({
            "id": user['id'],
            "username": user['username'],
            "email": user['email']
        }), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


# ============= TEST ENDPOINT =============

@app.post("/test")
def test_endpoint():
    """Test if basic functionality works."""
    result = {
        "status": "ok",
        "create_chat_session_type": str(type(create_chat_session)),
        "test": "success"
    }
    return jsonify(result), 200


# ============= CHAT ENDPOINTS =============

@app.post("/chat")
def create_chat_endpoint():
    """
    Create a new chat session and get initial AI response.
    This is the main entry point from the frontend.
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        user_id = data.get('user_id', '')

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Create a new chat session
        import sys
        print(f"\n=== CREATE CHAT START ===", file=sys.stderr, flush=True)
        print(f"create_chat_session function: {create_chat_session}", file=sys.stderr, flush=True)
        try:
            chat_id = create_chat_session(
                user_id=user_id,
                title="New Chat"
            )
            print(f"create_chat_session returned: {chat_id}, type: {type(chat_id).__name__}", file=sys.stderr, flush=True)
            
            import inspect
            if inspect.iscoroutine(chat_id):
                print("ERROR: chat_id is a coroutine!", file=sys.stderr, flush=True)
            else:
                print("OK: chat_id is not a coroutine", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"Exception calling create_chat_session: {e}", file=sys.stderr, flush=True)
            raise
        
        # Get AI response using the RAG pipeline
        try:
            ai_response = get_answer(query)
            if not ai_response or not ai_response.strip():
                ai_response = build_online_fallback_answer(query)
            if "I don't have enough data to answer this" in ai_response:
                ai_response = build_online_fallback_answer(query)
        except Exception as e:
            print(f"Error getting AI response: {e}")
            ai_response = build_online_fallback_answer(query)

        # Extract source and marks from response
        source = "Hybrid (Docs + Online)"
        marks = 0

        # Parse marks from the response
        if "Marks:" in ai_response:
            try:
                marks_part = ai_response.split("Marks:")[-1].strip()
                marks = int(marks_part.split()[0]) if marks_part and marks_part[0].isdigit() else 0
            except:
                marks = 0

        # Parse source from the response
        if "Source:" in ai_response:
            try:
                source_part = ai_response.split("Source:")[-1].split("|")[0].strip()
                source = source_part
            except:
                pass

        # Save the message to database
        try:
            message_result = save_message(
                chat_id=chat_id,
                user_id=user_id,
                query=query,
                response=ai_response.split("\n\n")[0].strip() if "\n\n" in ai_response else ai_response,
                source=source,
                marks=marks
            )
            print(f"Message saved successfully: {message_result}")
        except Exception as save_err:
            print(f"Error saving message: {save_err}")
            import traceback
            traceback.print_exc()

        return jsonify({
            "chat_id": chat_id,
            "answer": ai_response,
            "source": source,
            "marks": marks,
            "timestamp": datetime.now().isoformat()
        }), 201

    except Exception as e:
        print(f"Error in create_chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.get("/chat/<chat_id>/<user_id>")
def get_chat_messages_endpoint(chat_id, user_id):
    """Get all messages for a chat session - formatted for frontend."""
    try:
        messages = get_chat_messages(chat_id)

        # Format for frontend expectation (user first, then bot)
        formatted = []
        for msg in messages:
            # User query first
            formatted.append({
                "id": msg["id"] + "_query",
                "content": msg["query"],
                "sender": "user"
            })
            # Bot response second
            formatted.append({
                "id": msg["id"],
                "content": msg["response"],
                "sender": "bot"
            })

        return jsonify(formatted), 200

    except Exception as e:
        print(f"Error in get_chat_messages: {e}")
        return jsonify({"error": str(e)}), 500


@app.get("/user/<user_id>/chats")
def get_user_chats(user_id):
    """Get all chat sessions for a user."""
    try:
        chats = get_user_chat_sessions(user_id)
        return jsonify(chats), 200
    except Exception as e:
        print(f"Error in get_user_chats: {e}")
        return jsonify({"error": str(e)}), 500


@app.post("/chat/<chat_id>/message")
def add_message(chat_id):
    """Add a new message to an existing chat session."""
    try:
        session = get_chat_session(chat_id)
        if not session:
            return jsonify({"error": "Chat session not found"}), 404

        data = request.get_json()
        query = data.get('query', '').strip()
        user_id = data.get('user_id', '')

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        # Get AI response
        try:
            ai_response = get_answer(query)
            if not ai_response or not ai_response.strip():
                ai_response = build_online_fallback_answer(query)
            if "I don't have enough data to answer this" in ai_response:
                ai_response = build_online_fallback_answer(query)
        except Exception as e:
            print(f"Error getting AI response: {e}")
            ai_response = build_online_fallback_answer(query)

        # Extract source and marks
        source = "Hybrid (Docs + Online)"
        marks = 0

        if "Marks:" in ai_response:
            try:
                marks_part = ai_response.split("Marks:")[-1].strip()
                marks = int(marks_part.split()[0]) if marks_part and marks_part[0].isdigit() else 0
            except:
                marks = 0

        if "Source:" in ai_response:
            try:
                source_part = ai_response.split("Source:")[-1].split("|")[0].strip()
                source = source_part
            except:
                pass

        # Save message
        message_id = save_message(
            chat_id=chat_id,
            user_id=user_id,
            query=query,
            response=ai_response.split("\n\n")[0].strip() if "\n\n" in ai_response else ai_response,
            source=source,
            marks=marks
        )

        return jsonify({
            "message_id": message_id,
            "query": query,
            "response": ai_response,
            "source": source,
            "marks": marks,
            "timestamp": datetime.now().isoformat()
        }), 201

    except Exception as e:
        print(f"Error in add_message: {e}")
        return jsonify({"error": str(e)}), 500


@app.delete("/chat/<chat_id>")
def delete_chat(chat_id):
    """Delete a chat session."""
    try:
        delete_chat_session(chat_id)
        return jsonify({"message": "Chat deleted successfully"}), 200
    except Exception as e:
        print(f"Error in delete_chat: {e}")
        return jsonify({"error": str(e)}), 500


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    print("Backend server started - RAG system ready")
    app.run(host="127.0.0.1", port=5000, debug=False)
