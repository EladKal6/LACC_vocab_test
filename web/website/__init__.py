from flask import Flask

def create_app():
    app = Flask(__name__)
    # Secret key to secure sessions and cookies. 
    # It can be any random string, but it must be kept secret.
    app.config['SECRET_KEY'] = 'jfdnosandg fsghaajsfgas'

    from .views import views
    from .models import UserAnswerLog

    # Register the blueprints with the Flask app
    # You can specify a URL prefix for each blueprint if you want.
    app.register_blueprint(views, url_prefix='/')

    app.quiz_answers = UserAnswerLog(
        mongo_uri="mongodb://db:27017/db",
        db_name='quiz_app',
        collection_name='user_answers'
    )

    return app


