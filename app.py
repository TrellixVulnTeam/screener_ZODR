from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.dbstock

# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')

# API
@app.route('/result', methods=['GET','POST'])
def show_result():
    criteria = request.get_json()

    filter = {}
    for key in criteria:
        filter[criteria[key][0]] = {"$"+criteria[key][1] : criteria[key][2] }

    result = db.financials.find(filter)
    print(list(result))

    return jsonify({'result':'success'})

if __name__ =='__main__':
    app.run('0.0.0.0', port=5000, debug=True)

