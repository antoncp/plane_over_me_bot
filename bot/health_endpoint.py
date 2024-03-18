from threading import Event, Thread

from flask import Flask

from .planes import AirCraft, User

# Flask health check endpoint
app = Flask(__name__)
shutdown_event = Event()


@app.route("/", methods=["GET"])
def webhook() -> str:
    """Launches Flask on port 1300 as an health check endpoint with a list
    of airplane's objects  in a current memory.
    """
    if not shutdown_event.is_set():
        title = "Planes bot is up"
        num_planes = len(AirCraft.aircrafts)
        num_users = len(User.users.keys())
        reg_list = " no dedicated planes "
        if num_planes:
            reg_planes = []
            for plane in AirCraft.aircrafts:
                reg_planes.append(plane.reg)
            reg_list = ", ".join(set(reg_planes))
        info_1 = f"There are <b>{num_planes} planes</b> in system now:"
        info_2 = f"Active users in system: <b>{num_users}</b>"
        message = [title, info_1, f"<i>[{reg_list}]</i>", info_2]
        return "<br><br>".join(message)


def run_flask_app():
    app.run(host="0.0.0.0", port=1300)


flask_thread = Thread(target=run_flask_app)
