from flask import Flask, request, abort,jsonify
from neo4j import GraphDatabase, basic_auth
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import re
import cv2
import numpy as np
from linebot import LineBotApi
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import requests
import re
import json
from flask import abort
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.models import *
from PIL import Image, ImageDraw, ImageFont
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
import ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.llms import Ollama
import os
app = Flask(__name__)

uri = "neo4j:172.30.81.113:7687"
user = "neo4j"
password= "password"
line_bot_api = LineBotApi('odz7P1Pu4YPBKfC2UaRJGzhP671gKFSR7DWrCKkBLCZaMUL4vRs62JDF9sfliaulr3C18QMazzHCXAZPBofFrBjs3schUsCWY9LoIbz0AH3PmGYb0COtKTDDwfqtlgJJ7W3mCN4YnYRwr41BTq6sKgdB04t89/1O/w1cDnyilFU=')
configuration = Configuration(access_token='odz7P1Pu4YPBKfC2UaRJGzhP671gKFSR7DWrCKkBLCZaMUL4vRs62JDF9sfliaulr3C18QMazzHCXAZPBofFrBjs3schUsCWY9LoIbz0AH3PmGYb0COtKTDDwfqtlgJJ7W3mCN4YnYRwr41BTq6sKgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('29e4dc7397d37e92d3a17cf5f459364b')

driver = GraphDatabase.driver(
        "neo4j://172.30.81.113:7687",
        auth=basic_auth("neo4j", "password"))

CHANNEL_ACCESS_TOKEN = 'odz7P1Pu4YPBKfC2UaRJGzhP671gKFSR7DWrCKkBLCZaMUL4vRs62JDF9sfliaulr3C18QMazzHCXAZPBofFrBjs3schUsCWY9LoIbz0AH3PmGYb0COtKTDDwfqtlgJJ7W3mCN4YnYRwr41BTq6sKgdB04t89/1O/w1cDnyilFU='

CACHE_FILE = "cached_data.json"
#@app.route("/callback", methods=['POST'])
#def callback():
    # get X-Line-Signature header value
    #signature = request.headers['X-Line-Signature']

    # get request body as text
    #body = request.get_data(as_text=True)
    #app.logger.info("Request body: " + body)

    # handle webhook body
    #try:
        #handler.handle(body, signature)
    #except InvalidSignatureError:
        #app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        #abort(400)

    #return 'OK'


#@handler.add(MessageEvent, message=TextMessageContent)
#def handle_message(event):
    #with ApiClient(configuration) as api_client:
        #line_bot_api = MessagingApi(api_client)
        #line_bot_api.reply_message_with_http_info(
           # ReplyMessageRequest(
             #   reply_token=event.reply_token,
              #  messages=[TextMessage(text=event.message.text)]
            #)
       # )


def fetch_questions_from_neo4j():
    query = """
        MATCH (n:QAM)-[r:ANSWER]->(m:QAM)
        RETURN n.answer AS answer,n.pic AS pic, m
        """
    results = []
    conn = Neo4jConnection(uri, user, password)
    """with conn._driver.session() as session:
        result = session.run(query)
        for record in result:
            answer = record["answer"]
            pic = record.get("pic", "default_value")
 #n_properties = dict(record["n"].items())
            m_properties = dict(record["m"].items()) # Convert properties to dictionary
            results.append({
            "answer": answer,
            "pic": pic,
            "questions": m_properties
            })

    return results"""
    with conn._driver.session() as session:
        result = session.run(query)
    # Save data to JSON file
        data = [record.data() for record in result]
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return data

def load_cached_data():
    """Load data from cache file if available."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def get_questions(use_cache=True):
    if use_cache:
        data = load_cached_data()
        if data:
            print("🔹 Loading data from cache...")
            return data
    print("🔹 Querying data from Neo4j...")
    return fetch_questions_from_neo4j()

def upload_to_google_drive(file_path, file_name):
    credentials = Credentials.from_service_account_file('path/to/credentials.json')
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {'name': file_name, 'parents': ['your_folder_id']}
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    file_id = file.get('id')
    service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
            ).execute()

    return f"https://drive.google.com/uc?id={file_id}&export=download"



class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))            
                        
    def close(self):
        self._driver.close()

    def query(self,query,parameters=None,single=False):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            if single:
                return result.single()
            return result
            
    def check_property(self, label, property_name, value):
        query = f'''
        MATCH (n:{label})
        WHERE n.{property_name} = $value
        RETURN n
        '''
        record = self.query(query, parameters={'value': value}, single=True)
        return record is not None

    

    @staticmethod
    def _check_property_query(tx, label, property_name, variable_value):
        query = (
                f"MATCH (n:{label}) "
                f"WHERE n.{property_name} = $variable_value "
            f"RETURN count(n) > 0 as exists"          
        )
        result = tx.run(query, variable_value=variable_value)
        return result.single()["exists"]

    def is_connected(self):
        try:
            with self._driver.session() as session:
                result = session.run("RETURN 1")
                if result.single()[0] == 1:
                    return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

results = []
questions = get_questions(use_cache=True)
conn = Neo4jConnection(uri, user, password)
for record in questions:
    answer = record["answer"]
    pic = record.get("pic", "default_value")
    m_properties = dict(record["m"].items())
    results.append({
        "answer": answer,
        "pic": pic,
        "questions": m_properties
        })


merged_results = []
#print(results)
for item in results:
 # Extract the answer
    answer_text = item['answer']
    pic_url = item.get('pic', None)
 # Combine all question values into a single string
 #questions_combined = item.get('question', '')
    for question_key, question_text in item['questions'].items():
        merged_results.append({
            'question': question_text,
            'answer': answer_text,
            'pic': pic_url
            })
flattened_data = []
for item in merged_results:
    if item['answer'] == "":
        answer = item['pic']
    else:
        answer = item['answer']
    question = item['question']
    flattened_data.append({'question': str(question), 'answer': str(answer)})
print("Flattened Data:")
print(flattened_data)

df = pd.DataFrame(flattened_data, columns=['question', 'answer'])
# Step 2: Create vectors from the text
text = df['question']
#print(text)
encoder = SentenceTransformer('kornwtp/SCT-model-wangchanberta')
vectors = encoder.encode(text)

# Step 3: Build a FAISS index from the vectors
vector_dimension = vectors.shape[1]
index = faiss.IndexFlatL2(vector_dimension)
faiss.normalize_L2(vectors)
index.add(vectors) 

def push_line_message(conn,user_id, message_text,line_bot_api):
    line_api_url = 'https://api.line.me/v2/bot/message/push'
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
            }
    payload = {
            'to': user_id,
            'messages': [
                {
                    'type': 'text',
                    'text': message_text
                }
            ]
        }
    #node_data = fetch_user_node_data(conn, user_id)
    #node_id = node_data['nodeID']
    #isEnd = check_end_node(conn, node_id)
    #phase = checkPhase(line_bot_api, conn, user_id)
    #boolean = check_confirm(line_bot_api,  conn, user_id, msg)
    isConfirm = read_confirm(line_bot_api,  conn, user_id)
    if isConfirm == True:
     #   fetch_next_day(conn,user_id)
        response = requests.post(line_api_url, headers=headers, json=payload)
        fetch_next_day(conn,user_id)
    #    updateCheckConfirm(line_bot_api, conn, user_id,False)
        return response.status_code, response.text
    else:
        return 204, "No message sent (isConfirm is False)" 

def push_flex_message(to, alt_text, flex_content):
    flex_message = FlexSendMessage(
        alt_text=alt_text,
        contents=flex_content
    )
    line_bot_api.push_message(to, flex_message)

flex_content = {
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "Hello, this is a Flex Message!",
                "weight": "bold",
                "size": "xl"
            },
            {
                "type": "box",
                "layout": "baseline",
                "margin": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "More details here",
                        "size": "sm",
                        "color": "#999999"
                    }
                ]
            }
        ]
    }
}

@app.route('/push_message_with_id', methods=['POST'])
def push_message_with_id():
    conn = Neo4jConnection(uri, user, password)
    data = request.get_json()
    user_id = data.get('user_id')
    #msg = "ไม่ใช่"
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    #boolean = check_confirm(line_bot_api, tk, conn, user_id, msg)
    message_text = "โปรดส่งข้อความเพื่อดำเนินการวันถัดไป"
    status_code, response_text = push_line_message(conn,user_id, message_text,line_bot_api)
     
    if status_code == 200:
        print('Message sent successfully!')
        return jsonify({'message': 'Message sent successfully!'}), 200
    else:
        print(f'Failed to send message: {response_text}')
        return jsonify({'error': f'Failed to send message: {response_text}'}), 500

def fetch_next_day(conn, user_id,boolean = True):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.fetchNext = true
    """
    query2 = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.fetchNext = false
    '''
    if boolean:
        conn.query(query, parameters={'user_id': user_id})
    else:
        conn.query(query2, parameters={'user_id': user_id})

@app.route("/send_flex_message", methods=['GET'])
def send_flex_message():
    user_id = 'U941269aa045b31f401009f8a369f2198'  # Replace with the actual user ID
    alt_text = 'This is a Flex Message'
    push_flex_message(user_id, alt_text, flex_content)
    return 'Flex Message sent!'



@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        access_token = 'odz7P1Pu4YPBKfC2UaRJGzhP671gKFSR7DWrCKkBLCZaMUL4vRs62JDF9sfliaulr3C18QMazzHCXAZPBofFrBjs3schUsCWY9LoIbz0AH3PmGYb0COtKTDDwfqtlgJJ7W3mCN4YnYRwr41BTq6sKgdB04t89/1O/w1cDnyilFU='
        secret = '29e4dc7397d37e92d3a17cf5f459364b'
        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(secret)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        msg_type = json_data['events'][0]['message']['type']
        #if msg_type == 'text':
        #msg = json_data['events'][0]['message']['text']
    
        tk = json_data['events'][0]['replyToken']
        user_id = json_data['events'][0]['source']['userId']
        if msg_type == 'text':
            msg = json_data['events'][0]['message']['text']
            reply_msg(line_bot_api, tk, user_id, msg)
        elif msg_type == 'image':
            message_id = json_data['events'][0]['message']['id']
            reply_msg(line_bot_api, tk, user_id, message_id)
            f'''message_id = json_data['events'][0]['message']['id']
            content = line_bot_api.get_message_content(message_id)
            file_path = f"static/image_{message_id}.jpg"
            with open(file_path, "wb") as f:
                for chunk in content.iter_content():
                    f.write(chunk)
            image_path = f"output/image_{message_id}.jpg"
            #image_path2 = f"output2/image_{message_id}.jpg"
            crop_image(file_path, image_path, expand_x=40, expand_y=60)
            overlay_images_resized(image_path, '/home/ecoadmin/workspace/chatbot/Info962.png', file_path, position=(0, 0))
            #image_url = f"https://10e9-2001-3c8-9009-151-5054-ff-feff-2355.ngrok-free.app/{file_path}"
            image_url = f"https://10e9-2001-3c8-9009-151-5054-ff-feff-2355.ngrok-free.app/{file_path}"
            image_message = ImageSendMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
            )
            line_bot_api.reply_message(tk, image_message)'''
        else:
            line_bot_api.reply_message(tk, TextSendMessage(text="ข้อความนี้ยังไม่รองรับ"))
        #msg_reply = reply_msg(msg,user_id)
        #line_bot_api.reply_message(tk,TextSendMessage(text=msg_reply[0],quick_reply=msg_reply[1]))                             
        #reply_msg(line_bot_api,tk,user_id,msg)

      #  print(msg, tk)
        print("user_id",user_id)
    except Exception as e:
        print(e) 
    return 'OK'

def crop_image(image_path, output_path, expand_x=20, expand_y=20):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        x = max(0, x - expand_x)
        y = max(0, y - expand_y)
        w = min(image.shape[1] - x, w + 2 * expand_x)
        h = min(image.shape[0] - y, h + 2 * expand_y)
        cropped_face = image[y:y + h, x:x + w]
        mask = np.zeros((h, w), dtype=np.uint8)
        center = (w // 2, h // 2)
        radius = min(w, h) // 2
        cv2.circle(mask, center, radius, 255, -1)
        circular_cropped = cv2.bitwise_and(cropped_face, cropped_face, mask=mask)
        circular_cropped_with_alpha = cv2.cvtColor(circular_cropped, cv2.COLOR_BGR2BGRA)
        circular_cropped_with_alpha[:, :, 3] = mask
        cv2.imwrite(output_path, circular_cropped_with_alpha)

        f'''image_with_face = image.copy()
        cv2.rectangle(image_with_face, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite(output_path, circular_cropped_with_alphacropped_face = image[y:y + h, x:x + w]
        cv2.imwrite(output_path, cropped_face)
        cv2.imwrite(output_path, cropped_face)'''
    else:
        print("No faces detected.")

    

def overlay_images_resized(name,background_path, overlay_path, output_path, position=(0, 0)):
    image_path = overlay_path
    target_image = cv2.imread(image_path)
    replacement_image = cv2.imread(background_path)
    hsv_image = cv2.cvtColor(target_image, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    mask = cv2.inRange(hsv_image, lower_white, upper_white)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        resized_image = cv2.resize(replacement_image, (w, h))
        mask_circle = np.zeros((h, w), dtype=np.uint8)
        center = (w // 2, h // 2)
        radius = min(w, h) // 2
        cv2.circle(mask_circle, center, radius, 255, -1)
        mask_inverse = cv2.bitwise_not(mask_circle)
        background = cv2.bitwise_and(target_image[y:y+h, x:x+w], target_image[y:y+h, x:x+w], mask=mask_inverse)
        foreground = cv2.bitwise_and(resized_image, resized_image, mask=mask_circle)
        combined = cv2.add(background, foreground)
        target_image[y:y+h, x:x+w] = combined
        image_pil = Image.fromarray(cv2.cvtColor(target_image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        font_path = "/home/ecoadmin/workspace/chatbot/THSarabun.ttf"
        font = ImageFont.truetype(font_path, size=100)
        text = f"น้องง{name}"
        position = (600, 1085)
        color = (0, 0, 0)
        draw.text(position, text, font=font, fill=color)
        final_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, final_image)
    
        f"""  background = Image.open(background_path).convert("RGBA")
    bg_width, bg_height = background.size
    overlay = Image.open(overlay_path).convert("RGBA")
    overlay_width, overlay_height = overlay.size
    scale = min(bg_width / overlay_width, bg_height / overlay_height)
    new_width = int(overlay_width * scale)
    new_height = int(overlay_height * scale)
    overlay_resized = overlay.resize((new_width, new_height), Image.Resampling.LANCZOS)
    position = ((bg_width - new_width) // 2, (bg_height - new_height) // 2)
    background.paste(overlay_resized, position, overlay_resized)
    background = background.convert("RGB")
    background.save(output_path)"""


def reply_msg(line_bot_api,tk,user_id,msg):
    #result = check_user_id(msg,user_id,line_bot_api,tk)
    #check_user_id(line_bot_api,tk,user_id,msg)
    #text_msg = result[0]
    #response = TextSendMessage(text=f"Hellom {msg}")
    #line_bot_api.reply_message(tk,response)
    check_user_id(line_bot_api,tk,user_id,msg)
    #quick_reply_dic = result[1]
    #text_result2 = result[2]
   # if (result[2]==2):
     #   text_msg = text_msg
    #    return text_msg,quick_reply_dic
   # else:
      #  return result,""

def check_user_id(line_bot_api,tk,user_id,msg):
    #if (msg == "Hello"):
        #return_message(line_bot_api,tk,user_id,msg)
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    conn = Neo4jConnection(uri, user, password)
    #getDisplayName(conn, user_id)
    node_label = "user"
    property_name = "userID"
    variable_value = user_id
    if (msg == "Hello"):
        #check if the property userID exits
        exists = conn.check_property(node_label, property_name, variable_value)
        if exists:
            #print("User ID exit in neo4j")i
            
            display_node(line_bot_api,tk,user_id,msg)
        else:
            create_user_node(driver,variable_value)
            getDisplayName(conn, user_id)
            display_node(line_bot_api,tk,user_id,msg)
    else:
        exists = conn.check_property(node_label, property_name, variable_value)
        if exists:
            
            display_node(line_bot_api,tk,user_id,msg)
        else:
            create_user_node(driver,variable_value)
            getDisplayName(conn, user_id)
            display_node(line_bot_api,tk,user_id,msg)

def create_user_node(driver,variable_value):
    query = '''
        CREATE (n:user {nodeID:0,dayStep:1,userID : $userID,questionCount:0,
        phase:false,fetchNext:false,confirm:false,pushTime:3})
    '''
    parameters = {"userID": variable_value}
    with driver.session() as session:
        session.run(query, parameters)

def return_message(line_bot_api,tk,user_id,msg):
    if(msg == "Hello"):
        flex = response_flex()
        line_bot_api.reply_message(tk,fkex)

def display_node(line_bot_api, tk, user_id, msg):
    video_url = "https://d2tu913n5i22kj.cloudfront.net/VDOwDay1.mp4"
    thumbnail_url = "https://www.example.com/thumbnail.jpg"
    title = "Sample Video Title"
    description = "This is a description of the video."

    
    conn = Neo4jConnection(uri, user, password)
     
    node_data = fetch_user_node_data(conn, user_id)
     
    if node_data:
        node_id, day_step, node_step = node_data['nodeID'], node_data['dayStep'], node_data['nodeStep'] 
        node_var = fetch_node_variable(conn, node_id)
        node_rel_var = fetch_rel_node_variable(conn, node_id)
        node_image = fetch_node_image(conn, node_id)
        question_tag = fetch_question_rel(conn, node_id)
        print(f"questiontag is {question_tag}")
        final_score = fetch_show_score_rel(conn,user_id, node_id, question_tag,day_step)
        showAnswer = False 
        wrongAnswers = fetch_answer(conn,user_id, node_id,question_tag,day_step)
       # isEnd = False
       # phase = False i

        phase = checkPhase(line_bot_api, conn, user_id)
        count = checkCount(line_bot_api, tk, conn, user_id)
        isEnd = check_end_node(conn, node_id)
        print(f"count is {count}")
       # if count == 3 or msg == "Yes":
            #resetCount(conn,line_bot_api, tk, user_id, count)
        #    count = checkCount(line_bot_api, tk, conn, user_id)
         #   phase = False
        #isAnswerRel = fetch_answer_rel(conn, node_id)
        #if wrongAnswers:
         #   showAnswer = traverse_nodes(line_bot_api,tk,conn,wrongAnswers,node_id,user_id)
        #print(wrongAnswers)
        #print(f"final score1 is {final_score}")
        #isFetch = False
        
        #    fetch_next_day(conn, user_id,False)
        isFetch = check_Is_Fetch(line_bot_api, tk, conn, user_id)
        update_confirm(line_bot_api,  conn, user_id, msg)
        isConfirm = read_confirm(line_bot_api,  conn, user_id)
        print(f'isConfirm: {isConfirm}')
        if isConfirm == True and isFetch == True:
            resetCount(conn,line_bot_api, tk, user_id, count)
            update_phase(line_bot_api, tk, conn, user_id,count,isConfirm)
            phase = checkPhase(line_bot_api, conn, user_id)
            count = checkCount(line_bot_api, tk, conn, user_id)
            updateCheckConfirm(line_bot_api,  conn, user_id,False)
            updateFetchNext(line_bot_api,  conn, user_id,False)
       #     updateCheckConfirm(line_bot_api, tk, conn, user_id)
           # fetch_next_day(conn, user_id,False)
        if msg != "Hello" and phase == False and isConfirm == False:
            updateisFetch(line_bot_api, tk, conn, user_id,count)
            if node_var:
                update_user_variable(conn,user_id,node_var,msg)
            if node_rel_var:
                update_user_rel_variable(conn, user_id, node_rel_var , node_id, msg)
            if node_image:
                message_id = msg
                manage_image(conn,tk,user_id,message_id)
                #update_user_image(conn,user_id, image_url)
                
            if question_tag:
                update_user_score(conn,user_id, node_id, msg, question_tag)
                
            print(f"""showAnser is {showAnswer}""")
            if final_score:
                node_id = final_score
            elif showAnswer:
                node_id = showAnswer
            else:
                #isEnd = check_end_node(conn, node_id)
                node_id = fetch_next_node(tk,conn, node_id, msg,day_step,user_id) or node_id
        isEnd = check_end_node(conn, node_id)

        isAnswerRel = fetch_answer_rel(conn, node_id)
        update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag,isEnd,count,msg,tk,phase)
        

        #if showAnswer == False:
        if phase == False:
            send_node_info(line_bot_api, tk, conn, node_id, node_step, day_step,user_id)
            resetCount(conn,line_bot_api, tk, user_id, count)
        print(f'isEnd2:{isEnd}')
        if isEnd:
            phase = True
            update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag,isEnd,count,msg,tk,phase)
        #if count > 3:
            #phase = False
           # update_count(conn,line_bot_api, tk, user_id, count)
        print(f'phase2:{phase}')
        if phase == True:
            #if count > 0:
            #is_question = check_question(conn,line_bot_api, tk, user_id ,msg)
            is_question = False
            #if count >= 1:
               # start_question(line_bot_api, tk, conn, user_id, checkConfirm)
               # checkConfirm = check_confirm(line_bot_api, tk, conn, user_id, msg)
                #start_question(line_bot_api, tk, conn, user_id)
                #start_question(line_bot_api, tk, conn, user_id, False)
                #is_question = check_question(conn,line_bot_api, tk, user_id ,msg)

           # if count == 0:
            #    start_question(line_bot_api, tk, conn, user_id)
             #   update_count(conn,line_bot_api, tk, user_id, count)
            #if is_question or count == 0 :
            if count > 0 :
                update_phase(line_bot_api, tk, conn, user_id,count,isFetch)
                update_count(conn,line_bot_api, tk, user_id, count)
                count = checkCount(line_bot_api, tk, conn, user_id)
                #update_phase(line_bot_api, tk, conn, user_id,count,isFetch)
            #    start_question(line_bot_api, tk, conn, user_id)
                if msg != "ไม่ใช่":
                    if msg != "ใช่":
                        return_message(line_bot_api, tk, user_id, msg)
                        start_question(line_bot_api, tk, conn, user_id)
            #else:
            #    repeat_question(line_bot_api, tk, conn, user_id)
            #update_count(conn,line_bot_api, tk, user_id, count)
            if count == 0:
                start_question(line_bot_api, tk, conn, user_id)
                update_count(conn,line_bot_api, tk, user_id, count)
                update_phase(line_bot_api, tk, conn, user_id,count,isFetch)

        if isAnswerRel :
            x = traverse_nodes(line_bot_api,tk,conn,wrongAnswers,node_id,user_id)
            node_id = x
            print(f"x nodeid is {x}")
            update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag)
            print(x)
            #node_id = x
            #update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag)
            #send_node_info(line_bot_api, tk, conn, node_id, node_step, day_step,user_id)
        
    else:
        print("No node data found")

def read_confirm(line_bot_api,  conn, user_id):
    query = f"""
    MATCH (n:user)
    WHERE n.userID = $user_id
    RETURN n.confirm as confirm
    """
    with conn._driver.session() as session:
        result = session.run(query, parameters={'user_id': user_id})
        record = result.single()
        return record["confirm"] if record else False

def updateFetchNext(line_bot_api,  conn, user_id,boolean=False):
    query = f"""
    MATCH (n:user)
    WHERE n.userID = $user_id
    SET n.fetchNext = false
    """
    conn.query(query, parameters={'user_id': user_id})

def updateCheckConfirm(line_bot_api,  conn, user_id,boolean=False):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.confirm = false
    """
    conn.query(query, parameters={'user_id': user_id})


def update_confirm(line_bot_api,  conn, user_id, msg):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.confirm = false
    """
    query2 = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.confirm = true
    """
    boolean = False
    if msg == "ใช่":
        conn.query(query, parameters={'user_id': user_id})
        boolean = False
    elif msg == "ไม่ใช่":
        conn.query(query2, parameters={'user_id': user_id})
        boolean = True
    #return boolean
    
def updateisFetch(line_bot_api, tk, conn, user_id,count):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.fetchNext = false
    """
    conn.query(query, parameters={'user_id': user_id})

def check_Is_Fetch(line_bot_api, tk, conn, user_id):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.fetchNext as fetchNext
    """
    with conn._driver.session() as session:
        result = session.run(query, parameters={'user_id': user_id})
        record = result.single()
        return record["fetchNext"] if record else False

def repeat_question(line_bot_api, tk, conn, user_id):
    message = "ขออภัย โปรดพิมพ์คำถามเกี่ยวกับสุขภาพช่องปาก"
    try:
        line_bot_api.push_message(
                user_id,
                TextSendMessage(text=message)
            )
        print(f"Message sent to user {user_id}: {message}")
    except Exception as e:
        print(f"Error occurred: {e}")

def get_ollama_response(prompt):
    try:
        response = ollama.chat(
            model='deepseek-r1:1.5b',
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

def answer_sentence(sentence):
    memory = ConversationBufferMemory()
    memory.clear()
    chat_model = ChatOllama(
            model="llama3.2:1b",
            temperature=0.2,
            max_tokens=30
        )
    prompt_template = PromptTemplate(
            input_variables=[],
            template=f"กล่าวก่อนตอบคำถาม เป็นวลี ก่อนตอบคำถามให้ลูกค้า 1 วลี/ประโยค ห้อมซ้อนข้อความ ที่มีเนื้อหาเดียวกับ {sentence}")
    #llm = Ollama(model="llama3.2:1b",temperature=0)
    #prompt_template = PromptTemplate(
     #   input_variables=[],
      #  template=f"กล่าวก่อนตอบคำถาม เป็นวลี ก่อนตอบคำถามให้ลูกค้า 1 วลี/ประโยค ห้อมซ้อนข้อความ ที่มีเนื้อหาเดียวกับ {sentence}"
    #)
    intro_chain = LLMChain(llm=chat_model, prompt=prompt_template)
    intro_response = intro_chain.run({})
    final_response = f"{intro_response} {sentence}"
    #print(final_response)
    return final_response


def classify_sentence(sentence):
 #   prompt = f'''
#ช่วยวิเคราะห์ว่าประโยคนี้เป็น "คำถาม" หรือ "บอกเล่า" และตอบโดยบอกว่าประโยคนี้เป็นคำถามหรือบอกเล่า:"{sentence}"
 #   '''
    prompt = f'''
    Answer only, not explain:
    โปรดวิเคราะห์ประโยคที่ให้มาว่าเป็นประโยคคำถามหรือประโยคบอกเล่า โดยตอบกลับเพียงแค่ 'คำถาม' หรือ 'บอกเล่า' เท่านั้น:
ประโยค: "{sentence}" คำตอบ:
'''
    response = get_ollama_response(prompt)
    response = response.strip()
    
    print(f"llm response is :{response}")
    if "คำถาม" in response and "คำตอบ" not in response:
        return True # เป็นคำถาม
    elif "คำตอบ" in response and "คำถาม" not in response:
        return False # เป็นคำตอบ
    elif "บอกเล่า" in response and "คำถาม" not in response:
        return False
    elif "บอกเลา" in response and "คำถาม"  in response:
        if "ไม่ใช่คำถาม" in response:
            return False
        else:
            return True
    elif "คำถาม" in response and "คำตอบ" in response:
 # หากมีทั้งสองคำ ให้พิจารณาข้อความเพิ่มเติม
        if "ไม่ใช่คำถาม" in response:
            return False
        else:
            return True
    else:
        return False #กรณีที่ไม่มีคำที่ต้องการ

def check_question(conn,line_bot_api, tk, user_id ,msg):
    is_question = answer_sentence(msg)
    if is_question:
        return True
    else:
        return False

def resetCount(conn,line_bot_api, tk, user_id, count):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.questionCount = 0
    """
    conn.query(query, parameters={'user_id': user_id})

def update_phase(line_bot_api, tk, conn, user_id,count,isConfirm):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.phase = true
    """
    query2 = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.phase = false
    """
    if isConfirm:
        conn.query(query2, parameters={'user_id': user_id})
    elif count < 6:
        conn.query(query, parameters={'user_id': user_id})
    else:
        conn.query(query2, parameters={'user_id': user_id})

def update_count(conn,line_bot_api, tk, user_id, count):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.questionCount = $count
    """
    count = checkCount(line_bot_api, tk, conn, user_id)
    if count < 10:
        count = count + 1
    else:
        count = 0
    conn.query(query, parameters={'user_id': user_id, 'count': count})


def checkCount(line_bot_api, tk, conn, user_id):
    query = f"""
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.questionCount as count
    """
    with conn._driver.session() as session:
        result = session.run(query, parameters={'user_id': user_id})
        record = result.single()
        return record["count"] if record else False

def checkPhase(line_bot_api,  conn, user_id):
    query = f"""
    MATCH (n:user)
    WHERE n.userID = $user_id
    RETURN n.phase as phase
    """
    with conn._driver.session() as session:
        result = session.run(query, parameters={'user_id': user_id})
        record = result.single()
        return record["phase"] if record else False

def start_question(line_bot_api, tk, conn, user_id,boolean = True):
    query = f'''
        MATCH (a:Question)
        WHERE id(a) = 597
        RETURN a.name AS name
    '''
    query2 = f'''
        MATCH (a:Question)-[r:NEXT]->(b:Question)
        WHERE id(a) =  620 AND id(b) = 597
        RETURN a.name as name ,r.choice as choice,b.name as name2
    '''
    with conn._driver.session() as session:
        result = session.run(query2)
        entity = {"name":None,"name2":None,"choices":[]}
        for record in result:
            entity["name"] = record.get("name", entity["name"]).strip() if record.get("name") else entity["name"]
            entity["name2"] = record.get("name2", entity["name2"]).strip() if record.get("name2") else entity["name2"]
            if record.get("choice") is not None:
                entity["choices"].append(record["choice"])
        #record = result.single()
       # name = record["name"]
       # entity = {"name":None}
       # entity["name"] = record.get("name", entity["name"]).strip() if record.get("name") else entity["name"]
    
    messages = []
    if boolean:
        if entity["name"]:
            messages.append(TextSendMessage(text=entity["name"]))
    else:
        if entity["name2"]:
             messages.append(TextSendMessage(text=entity["name2"]))
    if boolean:
        if entity["choices"] is not None:
            quick_reply_buttons = [QuickReplyButton(action=MessageAction(label=c, text=c)) for c in entity["choices"]
            if c.strip()]
            if quick_reply_buttons:
                quick_reply = QuickReply(items=quick_reply_buttons)
                messages.append(TextSendMessage(text="โปรดเลือกอย่างใดอย่างหนึ่ง", quick_reply=quick_reply))
    if messages:
        line_bot_api.push_message(user_id, messages)
    else:
        print("No valid messages to send111")

def return_message(line_bot_api, tk, user_id, msg):
    chk_msg = check_sentence(msg)
   # response =  answer_sentence(chk_msg[1])
    response = f"{chk_msg[1]}"
 
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, response)
    if urls:
        image_url = urls[0]
        image_message = ImageSendMessage(
            original_content_url=image_url, 
            preview_image_url=image_url
            )
        line_bot_api.reply_message(tk, [TextSendMessage(text=response), image_message])
    else:
        line_bot_api.reply_message(tk, TextSendMessage(text=response))

def check_sentence(msg):
    search_text = msg
    search_vector = encoder.encode(search_text)
    _vector = np.array([search_vector])
    faiss.normalize_L2(_vector)
    k = index.ntotal  # Number of nearest neighbors to retrieve
    distances, ann = index.search(_vector, k=k)
    results = pd.DataFrame({'distances': distances[0], 'ann': ann[0]})
    labels = df['answer']
    Ques = df['question']
    Sentence = labels[ann[0][0]]
    if distances[0][0] <= 0.5:
        answer = labels[ann[0][0]]
        Sentence = Ques[ann[0][0]]
    else:
        Sentence = msg
        answer = "ขออภัยไม่มีข้อมูลคำตอบของคำถามในฐานข้อมูล"

    return [Sentence, answer]



def manage_image(conn,tk,user_id,message_id):
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.name AS name
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'user_id': user_id})
        name_record = result.single()
        name = name_record["name"]
    content = line_bot_api.get_message_content(message_id)
    file_path = f"static/image_{message_id}.jpg"
    with open(file_path, "wb") as f:
        for chunk in content.iter_content():
            f.write(chunk)
    image_path = f"output/image_{message_id}.jpg"
    crop_image(file_path, image_path, expand_x=40, expand_y=60)
    overlay_images_resized(name,image_path, '/home/ecoadmin/workspace/chatbot/Info964.png', file_path, position=(0, 0))
    image_url = f"https://10e9-2001-3c8-9009-151-5054-ff-feff-2355.ngrok-free.app/{file_path}"
    image_message = ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
    )
    line_bot_api.reply_message(tk, image_message)
    



def getDisplayName(conn, user_id):
    query = '''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.p_display_name = $p_display_name
    '''
    profile = line_bot_api.get_profile(user_id)
    p_display_name = profile.display_name
    #print(f"User's display name: {p_display_name}")
    conn.query(query, parameters={'user_id': user_id, 'p_display_name': p_display_name})

def fetch_user_node_data(conn, user_id):
    query = '''
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.nodeStep as nodeStep, n.dayStep as dayStep, n.nodeID as nodeID,
        COALESCE(n.isEnd, false) as isEnd
    '''
    
    record = conn.query(query, parameters={'user_id':user_id}, single=True)
    if record:
        return {"nodeStep": record["nodeStep"], "dayStep": record["dayStep"], "nodeID": record["nodeID"],"isEnd":record["isEnd"]}
    return None

def fetch_node_variable(conn, current_node_id):
    query = '''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id
        RETURN a.parameter AS node_var
    '''
    
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id})
        record = result.single() 
        return record["node_var"] if record else None

def fetch_rel_node_variable(conn, node_id):
    query = '''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id
        RETURN a.rel_parameter AS node_var
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': node_id})
        record = result.single()
        return record["node_var"] if record else None

def fetch_node_image(conn, current_node_id):
    query = '''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id
        RETURN a.playerimage AS node_image
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id})
        record = result.single()
        return record["node_image"] if record else None

def fetch_question_rel(conn, current_node_id):
    query= '''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id AND r.isCorrect IS NOT NULL
        RETURN HEAD(labels(a)) AS label
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id})
        record = result.single()
        return record["label"] if record else None

def fetch_answer_rel(conn, node_id):
    query = f'''
        MATCH (a)-[r:ANSWER]->(b)
        WHERE id(a) = $node_id 
        RETURN r.number AS number
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': node_id})
        record = result.single()
        element = record["number"] if record else None
        return element
        
    

def traverse_nodes(line_bot_api,tk,conn,wrongAnswers, node_id, user_id,index=0,messages= None):
    if messages is None:
        messages = []
    query2 = f'''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id
        RETURN id(b) as node_id,b.name as name,r.choice as choice,r.name as quickreply
    '''
    entity = {"name": None, "name2": None, "photo": None,"quickreply":None, "choices": []}
    if index >= len(wrongAnswers):
        print(f'''messages are {messages}''')
        with conn._driver.session() as session:
            result = session.run(query2, parameters={'node_id': node_id})
            record = result.single()
            if record:
                ##node_id = record["node_id"]
                entity["name"] = record.get("name", entity["name"]).strip() if record.get("name") else entity["name"]
                if record.get("quickreply") is not None:
                    entity["quickreply"] = record.get("quickreply", entity["quickreply"]).strip()
                if record.get("choice") is not None:
                    entity["choices"].append(record["choice"])
                entity["photo"] = record.get("photo", entity["photo"]).strip() if record.get("photo") else entity["photo"]
                #if entity["photo"]:
                 #   messages.append(ImageSendMessage(original_content_url=entity["photo"], preview_image_url=entity["photo"]))
                #if entity["name"]:
                 #   messages.append(TextSendMessage(text=entity["name"]))
                if entity["quickreply"] is not None:
                    quick_reply_buttons = [QuickReplyButton(action=MessageAction(label=c, text=c)) for c in entity["choices"] if c.strip()]
                    if quick_reply_buttons:
                        quick_reply = QuickReply(items=quick_reply_buttons)
                        messages.append(TextSendMessage(text=entity["quickreply"], quick_reply=quick_reply))

                 
            if messages:
                #for i in range(0, len(messages), 5):
                 #   batch = messages[i:i + 5]
                line_bot_api.reply_message(tk, messages)
        return node_id 
        
    if wrongAnswers[index] == 0:
        isFalse = True
    if wrongAnswers[index] == 1:
        isFalse = False
    #print(f'''isFalse is {isFalse}''')
    query = f'''
        MATCH (a)-[r:ANSWER]->(b)
        WHERE id(a) = $node_id and r.isFalse = $isFalse and r.number = $number
        RETURN id(b) as node_id, b.photo as photo
        ORDER BY r.number ASC
        LIMIT 1
    '''
    query2 = f'''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id
        RETURN id(b) as node_id
    '''
    
    with conn._driver.session() as session:
        #if index >= len(wrongAnswers):
         #   result = session.run(query2, parameters={'node_id': node_id})
          #  if messages:
           #     line_bot_api.reply_message(tk, messages)
            
        #else:
        result = session.run(query, parameters={'node_id': node_id, 'isFalse': isFalse, 'number':index+1})
        record = result.single()
        if record:
            print(f"Current Node: {node_id}, Next Node: {record['node_id']}")
            node_id = record["node_id"]
            photo = record["photo"]
            
            if photo:
                messages.append(ImageSendMessage(original_content_url=photo, preview_image_url=photo))
       # if index >= len(wrongAnswers):
         #   return node_id
            
    return traverse_nodes(line_bot_api,tk,conn,wrongAnswers, node_id, user_id, index + 1,messages)

    #traverse_nodes(conn,wrongAnswers,node_id, index +1)

def fetch_answer(conn, user_id,node_id,question_tag,day_step):
    dayWrong = f"d{day_step}Wrong"
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.{dayWrong} AS wrong
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'user_id': user_id})
        wrong_answers_record = result.single()
        return wrong_answers_record["wrong"] if wrong_answers_record else False

def fetch_next_node(tk,conn, current_node_id, msg, day_step,user_id):
    isEnd = check_end_node(conn, current_node_id)
    count = checkCount(line_bot_api, tk, conn, user_id) 
    phase = checkPhase(line_bot_api, conn, user_id)
    if phase == False:
        node_label = f"d{day_step}"
        query = f'''
            MATCH (a:{node_label})
            WHERE id(a) = $node_id  
            OPTIONAL MATCH (a)-[r1:SCORE]->(b1:{node_label})
            OPTIONAL MATCH (a:{node_label})-[r2:NEXT]->(b2:{node_label})
            WHERE r2.choice = $msg OR r2.choice IS NULL OR r2.choice = ""
            RETURN 
                CASE
                    WHEN b1 IS NOT NULL THEN id(b1)
                    ELSE id(b2)
                END AS node_id
        '''
    #else:
        #day_step = day_step + 1
        #node_label = f"d{day_step}"
       # query = f'''
        #    MATCH (a:{node_label})
         #   WHERE a.step = 1
          #  OPTIONAL MATCH (a:{node_label})-[r:NEXT]->(b:{node_label})
           # WHERE a.step = 1 AND (r.choice = $msg OR r.choice IS NULL OR r.choice = "")
           # RETURN id(a) AS node_id
        #'''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id, 'msg': msg})
        record = result.single()  # Fetch the single record from the result
        return record["node_id"] if record else None

def check_end_node(conn, current_node_id):
    query = f'''
        MATCH (a)
        WHERE id(a) = $node_id AND coalesce(a.isEnd, false) = true
        RETURN a.isEnd AS result
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id})
        record = result.single()  
        return record["result"] if record else False

def fetch_show_score_rel(conn, user_id,current_node_id, question_tag,day_step):
    dayScore = f"d{day_step}Score"
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.{dayScore} as score

    '''
    
    with conn._driver.session() as session:
        result = session.run(query, parameters={'user_id': user_id})
        score_record = result.single()
    score = score_record["score"] if score_record else None
    print(f"score is {score}")
    if score is not None:
        query = f'''
            MATCH (a)-[r:SCORE]->(b)
            WHERE id(a) = $current_node_id AND r.score = $score
            RETURN id(b) as node_id
        '''
        with conn._driver.session() as session:
            result = session.run(query, parameters={'current_node_id': current_node_id, 'score': score})
            record = result.single()
            return record["node_id"] if record else False
    else:
        return False

def update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag,isEnd,count,msg,tk,phase):
    isEnd = check_end_node(conn, node_id)
    count = checkCount(line_bot_api, tk, conn, user_id)
    #dayScore = f"{question_tag}Score"
    print(isEnd)
    #phase = False
    node_label = f"d{day_step}"
    if isEnd and count == 0 :
        day_step = day_step + 1
        node_step = 1
        node_label = f"d{day_step}"
    
    query1 = f'''
            MATCH (n:user)
            WHERE n.userID = $user_id
            SET n.dayStep = $day_step, n.nodeID = $node_id, n.nodeStep = $node_step
        '''
    
    query2 = f'''
            MATCH (a:{node_label})
            WHERE a.step = 1
            RETURN id(a) AS node_id
        '''
  #  if (isEnd and count >= 3) or msg == "Yes":
 #       day_step = day_step + 1
#        node_step = 1
        
    if phase == False:
      
        conn.query(query1, parameters={'user_id': user_id, 'day_step': day_step, 'node_id': node_id, 'node_step': node_step})
    if phase == True:
        with conn._driver.session() as session:
            print(f"node label is {node_label}")
            result = session.run(query2, parameters={'node_label': node_label})
            record = result.single()  # Fetch the single record from the result
            node_id = record["node_id"] if record else None
        if node_id != None:
            conn.query(query1, parameters={'user_id': user_id, 'day_step': day_step, 'node_id': node_id, 'node_step': node_step})

    #else:
     #   conn.query(query2, parameters={'user_id': user_id, 'day_step': day_step, 'node_id': node_id, 'node_step': node_step,'msg':msg})

def update_user_variable(conn, user_id, node_var, msg):
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.{node_var} = $msg
    '''
    conn.query(query, parameters={'user_id': user_id, 'node_var': node_var, 'msg':msg})

def update_user_rel_variable(conn, user_id, node_rel_var , node_id, msg):
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.{node_rel_var} = $variable
    '''
    query2 = f'''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id AND r.choice = $msg
        RETURN r.choice AS choice
    '''
    with conn._driver.session() as session:
        result = session.run(query2, parameters={'node_id': node_id, 'msg': msg})
        record = result.single()
        variable = record["choice"]
    conn.query(query, parameters={'user_id': user_id,  'variable':variable})

def update_user_score(conn, user_id, node_id, msg, question_tag):
    dayScore = f"{question_tag}Score"
    wrongAnswer = f"{question_tag}Wrong"
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.{dayScore} = coalesce(n.{dayScore}, 0) + 1,
            n.{wrongAnswer} = coalesce(n.{wrongAnswer}, []) + [1]
    '''
    query2 = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.{dayScore} = coalesce(n.{dayScore}, 0) + 0,
            n.{wrongAnswer} = coalesce(n.{wrongAnswer}, []) + [0]
    '''
    isCorrect = check_is_correct(conn, node_id, msg)
    
    if isCorrect:
        conn.query(query, parameters={'user_id': user_id})
    else:
        conn.query(query2, parameters={'user_id': user_id})


def check_is_correct(conn,  node_id, msg):
    query = f'''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id AND r.choice = $msg
        RETURN r.isCorrect AS isCorrect
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': node_id, 'msg': msg})
        record = result.single()
        return record["isCorrect"] if record else None


def send_node_info(line_bot_api, tk, conn, node_id, node_step, day_step,user_id):
    entity_data = fetch_entity_data(conn, node_id, node_step,user_id)
    if entity_data:
        entity_data = replace_text_with_variable(conn,user_id,entity_data)
        send_messages(line_bot_api, tk, entity_data)
         

def fetch_entity_data(conn, node_id, node_step,user_id):
    query = '''
        MATCH (n)
        WHERE id(n) = $node_id
        OPTIONAL MATCH (n)-[r:NEXT]->(m)
        OPTIONAL MATCH (n)-[a:ANSWER]->(m)
        RETURN n.name as name, n.name2 as name2, n.photo as photo, r.choice as choice,r.name as quickreply, coalesce(n.video, '') as video,n.pic1 as pic1,n.pic2 as pic2,n.pic3 as pic3
    '''
    query2 = '''
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.relDay9 as relVar
    '''
    entity = {"name": None, "name2": None, "photo": None,"quickreply":None, "choices": [],
              "video":None,"relpic":None}
    
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': node_id})
        result2 = session.run(query2, parameters={'user_id': user_id})
        for record in result2:
            relVar = record["relVar"]
        records = list(result)
        print(f"relVar is {relVar}") 
        if not records:
            print(f"No records found for node_id: {node_id}")
            return None
        for record in records:
            if relVar == "รูปที่1":
                entity["relpic"] = record.get("pic1",entity["relpic"]).strip() if record.get("pic1") else entity["relpic"]
            elif relVar == "รูปที่2":
                entity["relpic"] = record.get("pic2",entity["relpic"]).strip() if record.get("pic2") else entity["relpic"]
            elif relVar == "รูปที่3":
                entity["relpic"] = record.get("pic3",entity["relpic"]).strip() if record.get("pic3") else entity["relpic"]
        #if not records:
         #   print(f"No records found for node_id: {node_id}")
        #    return None
        #for record in records:
            entity["name"] = record.get("name", entity["name"]).strip() if record.get("name") else entity["name"]
        
            entity["name2"] = record.get("name2", entity["name2"]).strip() if record.get("name2") else entity["name2"]

    
            entity["photo"] = record.get("photo", entity["photo"]).strip() if record.get("photo") else entity["photo"]

            entity["video"] = record.get("video", entity["video"]).strip() if record.get("video") else entity["video"]
            if record.get("quickreply") is not None:
                entity["quickreply"] = record.get("quickreply", entity["quickreply"]).strip()
            if record.get("choice") is not None:
                entity["choices"].append(record["choice"])
    
    return entity if any(value is not None for value in entity.values()) else None

def replace_text_with_variable(conn,user_id,entity_data):
    print(entity_data)
    pattern = r'<<\s*(.*?)\s*>>'
    for key, text in entity_data.items():
        if isinstance(text, str):
            matches = re.findall(pattern, text) 
            #print(f"Matches for {key}: {matches}")
            for match in matches:
                query = f'''
                    MATCH (n:user)
                    WHERE n.userID = $user_id
                    RETURN n.{match} AS node_var
                '''
                node_var = conn.query(query, parameters={'user_id': user_id}, single=True)
                if node_var:
                    
                    entity_data[key] = entity_data[key].replace(f"<<{match}>>", str(node_var[0]))
                else:
                    print(f"No value found for {match}, skipping replacement.")
 
    return entity_data

def send_messages(line_bot_api, tk, entity_data):
    print(entity_data["video"])
    messages = []
    if entity_data["relpic"]:
        messages.append(ImageSendMessage(original_content_url=entity_data["relpic"], preview_image_url=entity_data["relpic"]))
    if entity_data["name"]:
        messages.append(TextSendMessage(text=entity_data["name"]))
    if entity_data["name2"]:
        messages.append(TextSendMessage(text=entity_data["name2"]))
    if entity_data["photo"]:
        messages.append(ImageSendMessage(original_content_url=entity_data["photo"], preview_image_url=entity_data["photo"]))
    if entity_data["video"]:
        messages.append(VideoSendMessage(original_content_url=entity_data["video"],preview_image_url=entity_data["video"]))

    if entity_data["quickreply"] is not None:
        quick_reply_buttons = [QuickReplyButton(action=MessageAction(label=c, text=c)) for c in entity_data["choices"]
        if c.strip()]
        if quick_reply_buttons:
            quick_reply = QuickReply(items=quick_reply_buttons)
            messages.append(TextSendMessage(text=entity_data["quickreply"], quick_reply=quick_reply))
    

    if messages:
        
        line_bot_api.reply_message(tk, messages)
    else:
        print("No valid messages to send2222")

def send_video_message(user_id, video_url, thumbnail_url):
    video_message = VideoSendMessage(
            original_content_url=video_url,  # URL of the video
            preview_image_url=thumbnail_url  # URL of the thumbnail image
        )
    line_bot_api.push_message(user_id, video_message)

def create_video_flex_message(video_url, thumbnail_url, title, description):
    bubble = BubbleContainer(
        body=BoxComponent(
            layout="vertical",
            contents=[
                ImageComponent(
                    url=thumbnail_url,
                    size="full",
                    aspect_ratio="16:9",
                    aspect_mode="cover",
                    action=URIAction(uri=video_url, label="Play Video")
                ),
                BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(
                            text=title,
                            weight="bold",
                            size="lg",                                      
                            wrap=True
                        ),
                        TextComponent(
                            text=description,
                            size="sm",
                            wrap=True,
                            color="#666666"
                        )
                    ],
                    spacing ="sm",
                    margin="lg"
                )
            ]
        )
    )
    flex_message = FlexSendMessage(alt_text="Video Message", contents=bubble)
    return flex_message

if __name__ == "__main__":
    app.run(port=8080)
