from flask.ext import wtf
from wtforms import TextField, PasswordField
from wtforms.validators import Required
from user import ReaderUser

class LoginForm(wtf.Form):

    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required()])

    def get_user(self, app):
        return ReaderUser(app)
