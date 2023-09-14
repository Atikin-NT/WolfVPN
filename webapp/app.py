from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def start():
    return render_template('start.html')


@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html')


@app.route('/add_peer', methods=['GET'])
def add_peer():
    return render_template('add_peer.html')


@app.route('/bill/<int:host_id>', methods=['GET'])
def bill(host_id: int):
    return render_template('bill.html')


@app.route('/qrcode/<int:host_id>', methods=['GET'])
def qrcode(host_id: int):
    return render_template('qrcode.html')
 

if __name__ == '__main__':
    app.run()
