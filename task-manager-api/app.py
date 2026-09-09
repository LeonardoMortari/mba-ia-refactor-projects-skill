from datetime import datetime, timezone

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from database import db
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Settings)
    CORS(app)
    db.init_app(app)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled API error: %s", error)
        return {"error": "Erro interno do servidor"}, 500

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': datetime.now(timezone.utc).isoformat()}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    with app.app_context():
        db.create_all()
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=Settings.DEBUG, host='127.0.0.1', port=5000)
