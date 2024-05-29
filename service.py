# import pyscreenshot as ImageGrab
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

client = Client(host='http://localhost:11434')

def screenshot():
    "Take screenshot and save it in the directory"
    dtime = time.strftime('%Y-%m-%d %H:%M:%S')
    # make directory if not exists
    if not os.path.exists("/home/rachit/.recall_Screenshots"):
        os.makedirs("/home/rachit/.recall_Screenshots")
    os.system("spectacle -f -b -n -o /home/rachit/.recall_Screenshots/'screenshot"+dtime+".png'")
    print("Screenshot taken")
    return "/home/rachit/.recall_Screenshots/screenshot"+dtime+".png"


def get_description_from_ollama_AI(img_path):
    "Get description from ollama AI"
    desc = client.generate(model='moondream', prompt="This is a screenshot now describe everything you see on the computer screen.", images =[img_path])
    desc = desc['response']
    return desc

def OCR_text(img_path):
    "Get OCR text from image"
    text = pytesseract.image_to_string(Image.open(img_path))
    return text


def get_window_info():
    "Get active window info"
    window_id = str(subprocess.check_output(['kdotool', 'getactivewindow']))[2:-3]
    window_name = str(subprocess.check_output(['kdotool', 'getwindowname', window_id]))[2:-3]
    window_process_id  = str(subprocess.check_output(['kdotool', 'getwindowpid', window_id]))[2:-3]
    return window_id, window_name, window_process_id


def files_opened_by_process(process_id):
    "Testing ..."
    files = subprocess.check_output(['lsof', '-p', process_id]).decode('utf-8')
    return files

def generate_embeddings(ocr_text, description):
    "Generate embeddings"
    ocr_text_embedding = client.embeddings(prompt=ocr_text, model='mxbai-embed-large')['embedding']
    description_embedding = client.embeddings(prompt=description, model='mxbai-embed-large')['embedding']
    return ocr_text_embedding, description_embedding


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
    "Save data to database"
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''INSERT INTO snapshots (time, ocr_text, description, window_id, window_name, window_process_id, img_path) VALUES (?,?,?,?,?,?,?)''', (time, ocr_text, description, window_id, window_name, window_process_id, img_path))
    doc_id = c.lastrowid
    conn.commit()
    conn.close()
    print("Data saved to database")
    return doc_id

def save_embeddings(time, document_id, ocr_text_embedding, description_embedding, window_name_embedding, window_id_embedding, window_process_id_embedding):
    "Save embeddings to qdrant database"
    qdrant = QdrantClient()
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
            ]
    )

    print("Embeddings saved")


while True:
    img_path = screenshot()
    description = get_description_from_ollama_AI(img_path)
    ocr_text = OCR_text(img_path)
    window_id, window_name, window_process_id = get_window_info()
    description = f"Window: {window_name} \n {description}"
    ocr_text_embedding, description_embedding, window_name_embedding, window_id_embedding, window_process_id_embedding = generate_embeddings(ocr_text, description, img_path, window_id, window_name, window_process_id)
    ntime = time.strftime('%Y-%m-%d %H:%M:%S')
    doc_id = save_to_db(ntime, ocr_text, description, window_id, window_name, window_process_id, img_path)
    save_embeddings(ntime, doc_id, ocr_text_embedding, description_embedding, window_name_embedding, window_id_embedding, window_process_id_embedding)
    time.sleep(180) # sleep for 3 minutes


