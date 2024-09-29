from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import join_room, leave_room, SocketIO, send
import os
import random
from string import ascii_uppercase



app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkye1234"
chatapp = SocketIO(app,cors_allowed_origins="*")


rooms = {}
def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code
    

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")

        if not name:
            return render_template("homev1.html", error="Please enter a name.")
        session["displayName"] = name
        salt = generate_unique_code(4)

        session["name"] = name + salt
        return redirect(url_for("join"))

    return render_template("homev1.html")


@app.route("/join", methods=["POST", "GET"])
def join():
    name = session.get("name")
    if not name:
        return redirect(url_for("home"))
    if request.method == "POST":
        code = request.form.get("code")
        code = code.lstrip()
        code = code.rstrip()
        code = code.upper()
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if join != False and not code:
                return render_template("join.html", error="Please enter a room code.", code=code, name=session.get("displayName"))
        room = code
        
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("join.html", error="Room does not exist.", code=code, name=session.get("displayName"))
        session["room"] = room
        return redirect(url_for("room"))

    return render_template("join.html", name=session.get("displayName"))


@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template('roomv1.html', code=room, messages=rooms[room]["messages"], fullName=session.get("name"))


@chatapp.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("displayName"),
        "fullName": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@chatapp.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("displayName")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({'name': name, "message": "has entered the room", "fullName": session.get("name")}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} has joinned the room {room}")

@chatapp.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("displayName")
    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <1:
            del rooms[room]
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
