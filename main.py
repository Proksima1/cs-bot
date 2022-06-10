from multiprocessing import Process

from flask import Flask, render_template, request
from bot import dp, executor, is_pid_alive

server = Flask(__name__)


@server.route('/')
def main():
    print(request.remote_addr)
    return render_template('main.html', ip=request.remote_addr)


@server.route('/start_bot', methods=['GET'])
def start_bot():
    bot_process = Process(target=before_server_startup)
    bot_process.start()
    pid = bot_process.pid
    print(is_pid_alive(pid))
    return f'{pid}'


def before_server_startup():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    server.run('0.0.0.0', debug=True)
