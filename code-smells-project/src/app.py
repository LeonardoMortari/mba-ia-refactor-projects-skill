from flask import Flask
from flask_cors import CORS
from src.config.settings import Settings
from src.database import close_db, init_db
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import bp

def create_app():
    app = Flask(__name__); app.config.from_object(Settings); CORS(app); app.register_blueprint(bp); app.teardown_appcontext(close_db); register_error_handlers(app)
    with app.app_context(): init_db()
    return app

app = create_app()

if __name__ == "__main__": app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
