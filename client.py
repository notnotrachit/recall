import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from ollama import AsyncClient
import sqlite3
from qdrant_client import QdrantClient
import asyncio
from qasync import QEventLoop

oclient = AsyncClient(host='http://localhost:11434')
client = QdrantClient()

def get_doc(doc_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM snapshots WHERE id=?", (doc_id,))
    doc = c.fetchone()
    conn.close()
    return doc

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setFixedSize(800, 900)

        self.layout = QVBoxLayout()

        self.text_field = QLineEdit()
        self.layout.addWidget(self.text_field)

        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.on_button_clicked)
        self.layout.addWidget(self.button)

        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        self.loader_label = QLabel("Loading...")
        self.loader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loader_label.hide()
        self.layout.addWidget(self.loader_label)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setAcceptRichText(True)
        self.layout.addWidget(self.result_area)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def on_button_clicked(self):
        self.loader_label.show()
        self.result_area.clear()
        asyncio.create_task(self.handle_query())

    async def handle_query(self):
        query = self.text_field.text()
        query_embedding = await oclient.embeddings(prompt=query, model='mxbai-embed-large')
        query_embedding = query_embedding['embedding']
        search_result = client.search(collection_name="snapshots", query_vector=query_embedding, limit=1)
        doc_id = search_result[0].payload['document_id']
        doc = get_doc(doc_id)
        img_path = doc[-1]
        pixmap = QPixmap(img_path)
        scaled_pixmap = pixmap.scaled(720, 405, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt = f"I am talking about a window that I had opened. The title of the window is {doc[5]}. The OCR text in the window is {doc[2]} (this may be very inaccurate). The description of the window is {doc[3]}. Now answer the following question: \n" + query

        response_stream = oclient.chat(
            model='phi3',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
        
        
        ## TODO - Fix the streaming markdown rendering

        # async for chunk in await response_stream:
        #     # print(chunk['message']['content'], end='', flush=True)
        #     if chunk['message']['content'] == '':
        #         continue
        #     prev_text = self.result_area.toMarkdown()
        #     if prev_text.endswith('\n'):
        #         prev_text = prev_text[:-2]
        #     new_text = chunk['message']['content'].replace('\n', '\n​')
        #     print(repr(new_text))
        #     self.result_area.setMarkdown(prev_text + new_text+'\n')
        #     # if chunk['message']['content'] == '\n':
        #     #     self.result_area.setMarkdown(prev_text + '\n')
        #     # else:
        #     #     self.result_area.setMarkdown(f"{prev_text}{chunk['message']['content']}")
        #     # i=input()
        #     # self.result_area.insertPlainText(chunk['message']['content'])
        #     # self.result_area.setMarkdown(prev_text + chunk['message']['content'].replace('\n', '<br>') + '\n')


        response = await oclient.generate(model='phi3', prompt="Hello, written a sample markdown response")
        self.result_area.setMarkdown(response['response'])
        self.loader_label.hide()

app = QApplication(sys.argv)

loop = QEventLoop(app)
asyncio.set_event_loop(loop)

window = MainWindow()
window.show()

with loop:
    loop.run_forever()
