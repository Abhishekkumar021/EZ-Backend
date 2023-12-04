from app import db
from datetime import datetime, timedelta


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    token_timestamp = db.Column(db.DateTime, nullable=True)

    def is_token_expired(self):
        if self.token_timestamp is None:
            return True
        expiration_time = self.token_timestamp + timedelta(days=1)
        return datetime.utcnow() > expiration_time

    def check_password(self, password):
        return password == self.password


class OpUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    token_timestamp = db.Column(db.DateTime, nullable=True)

    def is_token_expired(self):
        if self.token_timestamp is None:
            return True
        expiration_time = self.token_timestamp + timedelta(days=1)
        return datetime.utcnow() > expiration_time

    def check_password(self, password):
        return password == self.password


class File(db.Model):
    file_id = db.Column(db.String(512), primary_key=True)
    filename = db.Column(db.String(512), nullable=False)
    filetype = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)


class downloadFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_token = db.Column(db.String(512), unique=True, nullable=True)
    file_url = db.Column(db.String(512), nullable=False)
    token_timestamp = db.Column(db.DateTime, nullable=True)

    def is_token_expired(self):
        if self.token_timestamp is None:
            return True
        expiration_time = self.token_timestamp + timedelta(hours=1)
        return datetime.utcnow() > expiration_time

    def expire_token(self):
        if self.is_token_expired():
            return False
        else:
            db.session.delete(self)
            db.session.commit()
            return True
