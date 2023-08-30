from flask import Flask, render_template

app = Flask(__name__)
 
@app.route('/')
def start():
    return render_template('start.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/bill')
def bill():
    return render_template('bill.html')

@app.route('/qrcode')
def qrcode():
    return render_template('qrcode.html')
 

if __name__ == '__main__':
    app.run()