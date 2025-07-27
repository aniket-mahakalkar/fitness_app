import socketio
from flask import Flask
from db import db
from flask_socketio import SocketIO
from routes.classes import bp as classes_bp
from routes.bookings import bp as bookings_bp
from routes.customers import bp as customer_bp
from routes.rag_support import bp as rag_support_bp, init_socket_events
from seed.seed_classess import seed_data

socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger= True)

def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)



    with app.app_context():
        db.create_all()
        seed_data()

    app.register_blueprint(classes_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(customer_bp)

    app.register_blueprint(rag_support_bp,url_prefix='/rag')

    init_socket_events(socketio)

    return app

if __name__ == '__main__':
    
    app = create_app()
    socketio.init_app(app)
    socketio.run(app ,debug=True, allow_unsafe_werkzeug=True)