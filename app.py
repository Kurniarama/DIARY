from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import base64
import os
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

# Folder untuk menyimpan gambar yang diupload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET'])
def show_diary():
    articles = list(db.diary.find({}, {'_id': False}))
    return jsonify({'articles': articles})

@app.route('/diary', methods=['POST'])
def save_diary():
    # Mengambil data yang dikirim dari form
    title_receive = request.form.get('title_give')
    content_receive = request.form.get('content_give')
    image_receive = request.form.get('image_give')
    profile_image_receive = request.form.get('profile_image_give')

    # Buat nama file baru untuk profile image
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    profile_image_name = f"profile_{timestamp}.jpg"
    profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_name)

    # Simpan profile image
    if profile_image_receive:
        with open(profile_image_path, "wb") as f:
            f.write(base64.b64decode(profile_image_receive.split(",")[1]))

    # Simpan data ke MongoDB dengan menambahkan tanggal saat ini
    doc = {
        'title': title_receive,
        'content': content_receive,
        'image': image_receive,
        'profile_image': profile_image_path,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Tambahkan tanggal saat ini
    }
    db.diary.insert_one(doc)
    
    return jsonify({'msg': 'Data berhasil disimpan!'})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run('0.0.0.0', port=5002, debug=True)
