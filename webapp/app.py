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


@app.route('/bill', methods=['GET'])
def bill():
    return render_template('bill.html')


@app.route('/qrcode/<int:host_id>', methods=['GET'])
def qrcode(host_id: int):
    return render_template('qrcode.html')


@app.route('/coupon', methods=['GET'])
def coupon():
    return render_template('coupon.html')


@app.route('/pay', methods=['GET'])
def pay():
    return render_template('pay.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('./ssl.crt', './ssl.key'))
