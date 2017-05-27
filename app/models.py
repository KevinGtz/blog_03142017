# HERE ARE THE DEFINED MODELS

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')  # THIS MODEL GONNA BE A RELATION

    def __repr__(self):  # THESE METHOD IS TO REPRESENT THE MODEL IN A STRING
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    def generation_confirmed_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):  # THIS METHOD IS USING TO GENERATE THE HASH OF THE PASSWORD
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  # THIS METHOD IS TO VALIDATE THAT THE PASSWORD HASH
        #  IS A REFERENCE OF THE PASSWORD
        return check_password_hash(self.password_hash, password)



    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):  # THIS METHOD SEARCH A USER IN THE DB
    return User.query.get(int(user_id))