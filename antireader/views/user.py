from werkzeug import generate_password_hash, check_password_hash
from flask.ext import login, wtf

class ReaderUser:
    def __init__(self, app):
        self.username = app.config['ADMIN_NAME']
        self.password = generate_password_hash(app.config['ADMIN_PASSWORD'])

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return True

    #def check_if_correct_user(self):
    #    if self.username != app.config['ADMIN_NAME']:
    #        return False
    #    if not check_password_hash(self.password, app.config['ADMIN_PASSWORD']):
    #        return False
    #    return True

    def verify(self, username, password):
        if username != self.username:
            return False
        if not check_password_hash(self.password, password):
            return False
        return True


def init_login(_app):
    login_manager = login.LoginManager()
    login_manager.setup_app(_app)
    reader_user = ReaderUser(_app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id != reader_user.get_id():
            return None
        else:
            return reader_user
    return login_manager
