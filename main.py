from flask import Flask, redirect, render_template, request, session
from flask_socketio import join_room, leave_room, SocketIO, send

import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["secret_key"] = "secretkye"
chatapp = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    chatapp.run(app)
