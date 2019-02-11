# import flask_loginsys
from flask_loginsys import app
from flask_loginsys import main

if __name__ == '__main__':
  app.run(host='localhost', port=8000, debug=True)