from flask import  Blueprint, request
from flask_socketio import emit
from services.rag_service import answer_user_query


bp = Blueprint('rag_chat', __name__)
socketio = None



@bp.route('/status')
def status():
    return "RAG ONLINE"

def init_socket_events(socketio_instance):

    global socketio
    socketio = socketio_instance


    @socketio.on('user_message')
    def handle_user_message(data):
        query = data.get("query", "").strip()

        if not  query:
            emit("bot-response", {"status": "error", "message" : "Please ask something"})
            return
        try:
            emit("bot-response", {"status": "in_progress", "message": ""})

            final_response = "".join(answer_user_query(query))

            emit("bot-response", {"status": "success", "message": final_response})

        except Exception as e:
            emit(f"Failed to get response: {str(e)}")