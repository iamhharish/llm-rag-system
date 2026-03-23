from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, Chat, Messages, ApiKey
from llm import ask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rag.db'
db.init_app(app)
CORS(app)


from routes.auth_bp import auth_bp
from routes.chat_bp import chat_bp

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)





@app.route('/api/ask', methods=['POST'])
def ask_route():
    data = request.get_json()
    user_input = data.get('query', '').strip()
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    response = ask(user_input)
    if response is None:
        return jsonify({'error': 'Failed to get response from LLM'}), 500

    return jsonify({'response': response})







@app.route('/db/users')
def db_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'password': user.password,
        'created_at': user.created_at.isoformat()
    } for user in users])
    
    
@app.route('/db/chats')
def db_chats():
    chats = Chat.query.all()
    return jsonify([{
        'id': chat.id,
        'user_id': chat.user_id,
        'created_at': chat.created_at.isoformat(),
        'mode': chat.mode
    } for chat in chats])
    
@app.route('/db/messages')
def db_messages():
    messages = Messages.query.all()
    return jsonify([{
        'id': message.id,
        'chat_id': message.chat_id,
        'sender': message.sender,
        'content': message.content,
        'timestamp': message.timestamp.isoformat()
    } for message in messages])
    

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        new_user = User(username='testuser',
                        password='testpass',
                        email='testuser@example.com',
                        phone='1234567890'
                        )
        db.session.add(new_user)
        db.session.commit()
        
        
    app.run(debug=True)