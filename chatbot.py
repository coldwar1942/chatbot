from flask import Flask, request, jsonify

from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np
import requests

import json
# faiss_init
data = [['ทำไมเราต้องแปรงฟันทั้งตอนเช้าและก่อนนอนวันละ 2 ครั้ง?', ' 1'], ['การแปรงฟันวันละ 2 ครั้ง ตอนเช้าและก่อน', ' 2'],  
['เพราะอะไรเราถึงต้องแปรงฟันตอนเช้าและก่อนนอนทุกวัน?', '3' ], ['ทำไมถึงแทำไมถึงแนะนำให้แปรงฟันวันละ 2 ครั้ง โดยเฉพาะตอนเช้าและก่อนนอน?', ' 4'], 
['ทำไมการแปรงฟันในตอนเช้าและก่อนนอนถึงสำคัญ?',' 5'],['เหตุผลที่ต้องแปรงฟันทั้งตอนเช้าและก่อนนอนคืออะไร?','6 '],
['ทำไมควรแปรงฟันวันละ 2 ครั้งในตอนเช้าและก่อนนอน?',' 7'],['ทำไมถึงต้องแปรงฟันก่อนนอนและตอนเช้าในทุก ๆ วัน?',' 8'],
['ทำไมการแปรงฟัน 2 ครั้งต่อวันจึงแนะนำ โดยเฉพาะตอนเช้าและก่อนนอน?',' 9'],['เพราะอะไรการแปรงฟันก่อนนอนและตอนเช้าถึงเป็นเรื่องจำเป็น?',' 10'],
['การแปรงฟันตอนเช้าและก่อนนอนสำคัญต่อสุขภาพฟันอย่างไร?',' 11'],['ทำไมแปรงฟันวันละ 2 ครั้งต้องทำตอนเช้าและก่อนเข้านอน?','12 '],
['เพราะเหตุใดต้องแปรงฟันตอนเช้าและก่อนนอนทุกวัน?','13 '],['การแปรงฟันวันละ 2 ครั้งในตอนเช้าและก่อนนอนมีประโยชน์อะไร?',' 14'],
['ทำไมการแปรงฟันในช่วงเช้าและก่อนนอนถึงมีความสำคัญมาก?',' 15'],['แปรงฟันตอนเช้าและก่อนนอนช่วยอะไร ทำไมต้องทำวันละ 2 ครั้ง?','16 '],
['เพราะอะไรการแปรงฟันวันละ 2 ครั้งถึงเน้นในช่วงเช้าและก่อนนอน?','17 '],['ทำไมต้องแปรงฟันในช่วงเช้าและก่อนนอนทุกวัน?',' 18'],
['การแปรงฟันตอนเช้าและก่อนนอนช่วยรักษาสุขภาพช่องปากอย่างไร?',' 19'],['ทำไมจึงควรแปรงฟันตอนเช้าและก่อนนอนวันละ 2 ครั้ง?','20 ']]
df = pd.DataFrame(data, columns = ['text', 'category'])
#Step 2: Create vectors from the text
text = df['text']
encoder = SentenceTransformer('kornwtp/SCT-model-wangchanberta')
vectors = encoder.encode(text)
#Step 3: Build a FAISS index from the vectors
vector_dimension = vectors.shape[1]
index = faiss.IndexFlatL2(vector_dimension)
faiss.normalize_L2(vectors)
index.add(vectors)

def check_sentent(msg):
    #Step 4: Create a search vector
    search_text = msg
    search_vector = encoder.encode(search_text)
    _vector = np.array([search_vector])
    faiss.normalize_L2(_vector)
    #Step 5: Search
    k = index.ntotal
    distances, ann = index.search(_vector, k=k)
    results = pd.DataFrame({'distances': distances[0], 'ann': ann[0]})
    #Step 6: Sort search results
    labels  = df['text']
    Sentence = labels[ann[0][0]]
    print(distances[0][0])
    if distances[0][0] <= 0.5:
        category = labels[ann[0][0]]
    else:
        category = msg
    print(category)
    
    return category

def return_message(line_bot_api,tk,user_id,msg):
    chk_msg = check_sentent(msg)
      
    line_bot_api.reply_message(tk,TextSendMessage(text=chk_msg))
    

app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                    
    try:
        json_data = json.loads(body)                         
        access_token = 'Sm250PXlleF0RD2zQnVaHoZEdvXAS2WIB/0oxHRbLHuIyNnLuybXqLlsfqZykrlFrp89895E8NMWRKWwOCNfRkGdIBeOqxDTVWu3F8a1ezoxMNhtTJNq15sXr8uVZuU3YUxxHj+9i0wup1UN8rMosgdB04t89/1O/w1cDnyilFU='
        secret = '345d9479db60500b905cdd0cebfc165c'
        line_bot_api = LineBotApi(access_token)              
        handler = WebhookHandler(secret)                     
        signature = request.headers['X-Line-Signature']      
        handler.handle(body, signature)                      
        msg = json_data['events'][0]['message']['text']      
        user_id = json_data['events'][0]['source']['userId']      
        tk = json_data['events'][0]['replyToken']       
        #line_bot_api.reply_message(tk,TextSendMessage(text=msg,quick_reply={"items": [{'type': 'action', 'imageUrl': '',  'action': {'type': 'message', 'label': msg ,  'text': 'MMM'}}]}))
        return_message(line_bot_api,tk,user_id,msg)
        print(msg, tk)                                      
    except:
        print(body)                                          
    return 'OK'                 

if __name__ == '__main__':
    app.run(port=8080)




