from flask import (
    Flask, 
    request,
    make_response,
    send_from_directory,
    redirect,
)
from jinja2 import Environment, FileSystemLoader
import pymongo
import os
import base58
from time import time
from PIL import Image
from bson import json_util as json
from dotenv import load_dotenv
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

app = Flask("catnet")

env = Environment(loader=FileSystemLoader("templates/"))

mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/", username=DB_USER, password=DB_PASS)
mydb = mongodb_client["mydatabase"]
catsdb = mydb["cats"]

with open("templates/upload.html", "r") as upload:
    upload_page = upload.read()

with open("templates/feed.html") as feed_file:
    feedhtml = feed_file.read()

def resize_image(path:str):
    image = Image.open(path)
    if image.width < 300 or image.height < 300:
        os.unlink(path=path)
        return None
    if image.width > 1080:
        image = image.resize(size=(1080, int(image.height*(1080/image.width))))
    if image.height > 1080:
        image = image.resize(size=(int((image.width*(1080/image.height))), 1080))
    image.save(path)
    return 1

@app.route("/<id>")
def showcat(id):
    cat_profile = env.get_template("catpicture.html")
    catdata:dict = catsdb.find_one({"catid": str(id)})
    content = {
    "catname": "cat", 
    "cat_id": id, 
    "catdescription": catdata["description"]
    }
    return cat_profile.render(content)

@app.route('/upload', methods=['GET', 'POST'])
def upload_cat():
    if request.method == 'POST':
        error = env.get_template("error.html")
        id = int(time()) << 32 | catsdb.count_documents(filter={})
        coded_id = base58.b58encode(id.to_bytes(8)).decode("utf-8")
        catdesc = request.values['description']
        catfile = request.files['cat']
        catfile.save(f'static/images/{coded_id}.jpg')
        if not resize_image(f'static/images/{coded_id}.jpg'):
            return error.render({"error_text": "Ваш кот слишком маленьковый жестб, давай кота побольбше"})
        catsdb.insert_one({"catid": coded_id, "description": catdesc})
        return error.render({"error_text": f"Ваш кот забран, алах назвал его вот так {coded_id}"})
    return upload_page

@app.route('/feed-update/<int:pos>', methods=['GET'])
def feed_apdate(pos):
    catdata = list(catsdb.find().sort("_id", -1).skip(pos*5).limit(5))
    print(catdata)
    response = make_response(json.dumps(catdata))
    response.headers["Content-Type"] = "application/json; charset=UTF-8"
    return response

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static/icons", "favicon.ico")

@app.route('/feed')
def feed():
    return feedhtml

@app.route('/')
def redirect_to_feed():
    return redirect('/feed', code=302)