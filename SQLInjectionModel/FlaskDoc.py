from flask import Flask, render_template, request
from DatabaseDoc import MyDB

app = Flask(__name__)


@app.route('/', methods={'GET'})
def index():
    id = request.args.get('id')
    name = request.args.get('name')
    if name:
        mydb = MyDB()
        infos = [item for item in mydb.search(id=id, name=name)]
        return render_template("PageDoc.html", infos=infos)
    else:
        return render_template("PageDoc.html")


app.run()
