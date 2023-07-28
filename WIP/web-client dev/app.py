from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Put the name of your HTML file here

if __name__ == '__main__':
    app.run(debug=True)
