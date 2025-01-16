from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '반갑습니다 (main에서 생성)'

if __name__ == '__main__':
    app.run(debug=True)