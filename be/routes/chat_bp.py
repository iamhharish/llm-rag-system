from flask import Blueprint, jsonify, request
from models import db, User, Chat, Messages, ApiKey
from llm import ask

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/chat', methods=['POST'])
def index():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input provided'}), 400

        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        user_input = data.get('query', '').strip()
        if not user_input:
            return jsonify({'error': 'Empty query'}), 400

        mode = data.get('mode', 0)

        new_chat = Chat(
            user_id=user_id,
            mode=mode,
            title=user_input[:30]
        )
        db.session.add(new_chat)
        db.session.commit()

        # Save user message
        db.session.add(Messages(
            chat_id=new_chat.id,
            sender=0,
            content=user_input
        ))
        db.session.commit()

        response = ask(user_input)
        if not response:
            return jsonify({'error': 'LLM failed'}), 500

        # Save bot message
        db.session.add(Messages(
            chat_id=new_chat.id,
            sender=1,
            content=response
        ))
        db.session.commit()

        return jsonify({
            'chat_id': new_chat.id,
            'response': response
        }), 201

    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal server error'}), 500

@chat_bp.route('/chat/<int:chat_id>', methods=['POST'])
def continue_chat(chat_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input provided'}), 400

        user_input = data.get('query', '').strip()
        user_id = data.get('user_id')

        if not user_input:
            return jsonify({'error': 'Empty query'}), 400

        chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404

        db.session.add(Messages(
            chat_id=chat.id,
            sender=0,
            content=user_input
        ))
        db.session.commit()

        response = ask(user_input)
        if not response:
            return jsonify({'error': 'LLM failed'}), 500

        db.session.add(Messages(
            chat_id=chat.id,
            sender=1,
            content=response
        ))
        db.session.commit()

        return jsonify({'response': response}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal server error'}), 500
    
@chat_bp.route('/chat/<int:chat_id>/<int:user_id>', methods=['GET'])
def get_chat(chat_id, user_id):
    try:
        messages = Chat.query.filter_by(id=chat_id, user_id=user_id).first().messages
        return jsonify([{
            'sender': 'user' if msg.sender == 0 else 'bot',
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        } for msg in messages]), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal server error'}), 500
    
@chat_bp.route('/chat/history/<int:user_id>', methods=['GET'])
def get_chat_history(user_id):
    try:
        chats = Chat.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'chat_id': chat.id,
            'title': chat.title,
            'created_at': chat.created_at.isoformat(),
            'mode': chat.mode
        } for chat in chats]), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal server error'}), 500