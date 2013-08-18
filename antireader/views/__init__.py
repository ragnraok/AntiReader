from views import app as views_app
from user import init_login

def init_views(app):
    login_manager = init_login(app)
    login_manager.login_view="web.login"
    app.register_blueprint(views_app, url_prefix="")
