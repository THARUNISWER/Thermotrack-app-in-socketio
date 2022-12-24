from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit
import requests
import core_predict

async_mode = None

weight = 30

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread():
    """Example of how to send server generated events to clients."""
    print('in background')
    while True:
        # --------------------------------------------
        params = core_predict.start(int(weight))
        print(weight)
        print(params)
        socketio.emit('updater',
                      {'weight_py': weight, 'core_temp': params[0], 'skin_temp' : params[1], 'max_HS' : params[2], 'Stor_body' : params[3], 'kcal_value' : params[4], 'recovery' : params[5], 'time_value' : params[6], 'flags' : params[7]})
        socketio.sleep(1)

@app.route('/')
def index():
    return render_template("Prototype3.html", async_mode=socketio.async_mode)

@socketio.event
def my_event(data):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data':"HI"})

@socketio.on('test_message')
def handle_message(weight_value):
    global weight
    print(weight_value)
    weight = float(weight_value['weight'])
    print('weight updated to: ' + str(weight))

@app.route('/', methods = ['POST'])
def getvalue():
    global weight
    weight = request.form.get('weight')
    # params = core_predict.start(int(weight))
    connect()
    return render_template("Prototype3.html", weight_py = weight)
                           # weight_py = weight, core_temp = params[0], skin_temp = params[1], max_HS = params[2], Stor_body = params[3], kcal_value = params[4], recovery = params[5], time_value = params[6], flags = params[7])

@socketio.on('test_message')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    #emit('my_response', {'data': 'Connected'})
    print("connected")

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
