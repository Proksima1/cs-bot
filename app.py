from multiprocessing import Process

from flask import Flask, render_template, request
from bot import dp, executor, is_pid_alive

app = Flask(__name__)


@app.route('/')
def main():
    print(request.remote_addr)
    return render_template('main.html', ip=request.remote_addr)


@app.route('/start_bot', methods=['GET'])
def start_bot():
    bot_process = Process(target=start_executor)
    bot_process.start()
    pid = bot_process.pid
    print(is_pid_alive(pid))
    return f'{pid}'


def start_executor():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    app.run('0.0.0.0', threaded=True, debug=True)
