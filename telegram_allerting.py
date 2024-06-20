import json
import requests
import os
import re
import threading
import time
import pandas as pd
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "{token}"
token=pd.read_csv('telegram/token.csv')
token=token['0'].tolist()
def tambah():
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates'
    response = requests.get(url)
    page_content = response.content
    data = json.loads(page_content)
    results = data.get('result', [])
    ids=[]
    for result in data['result']:
        if result['message'].get('text') == '{password}':
            ids.append(result['message']['from']['id'])
    for i in ids:
        if i not in token:
            token.append(i)
            send_tambah(i)
    token_write=pd.DataFrame(token)
    token_write.to_csv('telegram/token.csv', sep=',', index=False)
    return ids
def send_tambah(id):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': id,
        'text': "anda telah ditambahkan kedalam database untuk dikirim notifikasi"
    }
    response = requests.post(url, data=data)
def send_telegram_message(message):
    for i in token:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        data = {
            'chat_id': i,
            'text': message
        }
        response = requests.post(url, data=data)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    description_match = re.search(r'description = (.+)', data['message'])
    if description_match:
        description_match=description_match.group(0)
    else:
        description_match=" "
    summary_match = re.search(r'summary = (.+)', data['message'])
    if summary_match:
        summary_match=summary_match.group(0)
    else:
        summary_match=" "
    message = f"Peringatan\n{summary_match}\n{description_match}"
    send_telegram_message(message)
    return "Alert received!", 200
def background_task():
    while True:
        token=tambah()
        time.sleep(5)
if __name__ == '__main__':
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()
    app.run(host='0.0.0.0',port=2612,debug=False)
