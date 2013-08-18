from flask.ext import wtf
from user import ReaderUser

class LoginForm(wtf.Form):

    username = wtf.TextField(validators=[wtf.required()])
    password = wtf.PasswordField(validators=[wtf.required()])

    def get_user(self, app):
        return ReaderUser(app)
