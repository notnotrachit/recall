import pyscreenshot as ImageGrab
# import sqlite3
import subprocess
import os
from ollama import Client
import time
import pytesseract
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import sqlite3
import json
import uuid




# print current datetime
# print(time.strftime('%Y-%m-%d %H:%M:%S'))
client = Client(host='http://localhost:11434')

def screenshot():
    img = ImageGrab.grab()
    if not os.path.exists("./Screenshots"):
        os.makedirs("./Screenshots")
    dtime =     time.strftime('%Y-%m-%d %H:%M:%S')  
    img.save("./Screenshots/screenshot"+dtime+".png")
    print("Screenshot taken")
    return "./Screenshots/screenshot"+dtime+".png"

def get_description_from_ollama_AI(img_path):
    desc = client.generate(model='moondream', prompt="This is a screenshot now describe everything you see on the computer screen.", images =[img_path])
    # print(desc)
    desc = desc['response']
    return desc

def OCR_text(img_path):
    text = pytesseract.image_to_string(Image.open(img_path))
    # print(text)
    return text


def get_window_info():
    window_id = str(subprocess.check_output(['kdotool', 'getactivewindow']))[2:-3]
    window_name = str(subprocess.check_output(['kdotool', 'getwindowname', window_id]))[2:-3]
    window_process_id  = str(subprocess.check_output(['kdotool', 'getwindowpid', window_id]))[2:-3]
    return window_id, window_name, window_process_id

def generate_embeddings(ocr_text, description, img_path, window_id, window_name, window_process_id):
    ocr_text_embedding = client.embeddings(prompt=ocr_text, model='mxbai-embed-large')['embedding']
    description_embedding = client.embeddings(prompt=description, model='mxbai-embed-large')['embedding']
    window_name_embedding = client.embeddings(prompt=window_name, model='mxbai-embed-large')['embedding']
    window_id_embedding = client.embeddings(prompt=window_id, model='mxbai-embed-large')['embedding']
    window_process_id_embedding = client.embeddings(prompt=window_process_id, model='mxbai-embed-large')['embedding']
    # img_embedding = client.embeddings(images=[img_path], model='mxbai-embed-large')
    return ocr_text_embedding, description_embedding, window_name_embedding, window_id_embedding, window_process_id_embedding


def create_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE snapshots
                 (
                    id INTEGER, 
                    time TEXT, 
                    ocr_text TEXT,
                    description TEXT,
                    window_id TEXT,
                    window_name TEXT,
                    window_process_id TEXT,
                    img_path TEXT,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )
            ''')
    conn.commit()
    conn.close()
    print("Database created")

def save_to_db(time, ocr_text, description, window_id, window_name, window_process_id, img_path):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''INSERT INTO snapshots (time, ocr_text, description, window_id, window_name, window_process_id, img_path) VALUES (?,?,?,?,?,?,?)''', (time, ocr_text, description, window_id, window_name, window_process_id, img_path))
    doc_id = c.lastrowid
    conn.commit()
    conn.close()
    print("Data saved to database")
    return doc_id

def save_embeddings(time, document_id, ocr_text_embedding, description_embedding, window_name_embedding, window_id_embedding, window_process_id_embedding):
    qdrant = QdrantClient()
    # create collection if not exists
    # qdrant.create_collection(
    #     collection_name='snapshots',
    #     vectors_config={
    #         'size': 1024,
    #         'distance': 'Cosine'
    #     }
    # )
    print("Collection created")
    qdrant.upsert(
        collection_name='snapshots',
            wait=True,
            points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=ocr_text_embedding,
                payload={'document_id': document_id, 'type': 'ocr_text'}
            ),
            PointStruct(
                id=str(uuid.uuid4()),
                vector=description_embedding,
                payload={'document_id': document_id, 'type': 'description'}
            ),
            PointStruct(
                id=str(uuid.uuid4()),
                vector=window_name_embedding,
                payload={'document_id': document_id, 'type': 'window_name'}
            ),
            PointStruct(
                id=str(uuid.uuid4()),
                vector=window_id_embedding,
                payload={'document_id': document_id, 'type': 'window_id'}
            ),
            PointStruct(
                id=str(uuid.uuid4()),
                vector=window_process_id_embedding,
                payload={'document_id': document_id, 'type': 'window_process_id'}
            ),
            ]
    )

    print("Embeddings saved")


img_path = screenshot()
description = get_description_from_ollama_AI(img_path)
ocr_text = OCR_text(img_path)
window_id, window_name, window_process_id = get_window_info()
ocr_text_embedding, description_embedding, window_name_embedding, window_id_embedding, window_process_id_embedding = generate_embeddings(ocr_text, description, img_path, window_id, window_name, window_process_id)
time = time.strftime('%Y-%m-%d %H:%M:%S')
doc_id = save_to_db(time, ocr_text, description, window_id, window_name, window_process_id, img_path)
save_embeddings(time, doc_id, ocr_text_embedding, description_embedding, window_name_embedding, window_id_embedding, window_process_id_embedding)
print("Screenshot saved to database")


