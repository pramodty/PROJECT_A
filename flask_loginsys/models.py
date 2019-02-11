from flask_login import UserMixin
from flask_loginsys import manager, db

class User1(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))

if __name__ == '__main__':
  manager.run()