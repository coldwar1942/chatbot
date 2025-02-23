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

carousel_data = {
    1: [  # ✅ ข้อที่ 1 มี 3 ภาพ พร้อมข้อความตอบกลับ
        {"image_url": "https://drive.google.com/uc?export=view&id=1job8DnIdyX_090eR2MS8gNHsvgnV76L4","label":"ใช่" ,"text": "ใช่"},
        {"image_url": "https://drive.google.com/uc?export=view&id=1miIfR_GIQVRkNPqBCvgKhX98huzavgq8","label":"ใช่" ,"text": "ใช่"},
        {"image_url": "https://drive.google.com/uc?export=view&id=1DwywrPv27dtTDAGhTd2a2wPWKZ6SAzAb","label":"ไม่ใช่" ,"text": "ไม่ใช่"}
    ],
    2: [  # ✅ ข้อที่ 2 มี 2 ภาพ พร้อมข้อความตอบกลับ
        {"image_url": "https://drive.google.com/uc?export=view&id=1ELrAyLmQajhH1o_upkQhjJMseO5ioi6M", "label":"ใช่","text": "ใช่"},
        {"image_url": "https://drive.google.com/uc?export=view&id=1Ug3nmk5EOgnSQiL_fSvNPBtt4Jbwd9Fc", "label":"ใช่","text": "ใช่"},
        {"image_url": "https://drive.google.com/uc?export=view&id=10UFJUDCJewih1N3F9hLGcyqjfW11wU8O", "label":"ไม่ใช่","text": "ไม่ใช่"}
    ],
     3: [  # ✅ ข้อที่ 2 มี 2 ภาพ พร้อมข้อความตอบกลับ
         {"image_url": "https://drive.google.com/uc?export=view&id=1BSncdOg4b4EuJ_RSxZDyAH8v4TauNhBW", "label" : "ใช่" , "text" : "ใช่"},
        {"image_url": "https://drive.google.com/uc?export=view&id=1ntBAXBuH5OseyVYvVDKiZFgr4S2B6geV", "label":"ไม่ใช่","text": "ไม่ใช่"}
    ],
     4: [  # ✅ ข้อที่ 2 มี 2 ภาพ พร้อมข้อความตอบกลับ
        {"image_url": "https://drive.google.com/uc?export=view&id=1NJinUCFExDDF_9Dl2ZauH4vZaUIpwczs", "label":"ใช่","text": "ใช่"},
        {"image_url": "https://drive.google.com/uc?export=view&id=1KzTGiHkY0xHhwfRFp6amWqg96JGU8FnV", "label":"ไม่ใช่","text": "ไม่ใช่"}
    ],
     5: [  # ✅ ข้อที่ 2 มี 2 ภาพ พร้อมข้อความตอบกลับ
        {"image_url": "https://drive.google.com/uc?export=view&id=1h9eaIZbRFFkDrSSRqbHI81yX2sSMlFdl", "label":"ใช่","text": "ใช่"},
         {"image_url": "https://drive.google.com/uc?export=view&id=1NgsODwZvBUlwC7hEO9WKwJH33dxLg6EH", "label":"ไม่ถึง1ปี" , ""  "text" : "ไม่ใช่" },
        {"image_url": "https://drive.google.com/uc?export=view&id=19r7-hh9Gx41euZ4Lh_zJOj8pXQvPRA2C", "label":"ไม่ใช่","text": "ไม่ใช่"}
    ],
     6: [  # ✅ ข้อที่ 2 มี 2 ภาพ พร้อมข้อความตอบกลับ
        {"image_url": "https://drive.google.com/uc?export=view&id=1BD3OxHSOGJ_V2hwCj6z-RnoPQbrtsd9J", "label":"ใช่","text": "ใช่"},
        {"image_url": "https://drive.google.com/uc?export=view&id=1jY8EtS_SnRQyVgjAdenFUL0GiD9ktsx8", "label":"ไม่ใช่","text": "ไม่ใช่"}
    ],
     7: [  # ✅ ข้อที่ 2 มี 2 ภาพ พร้อมข้อความตอบกลับ
        {"image_url": "https://drive.google.com/uc?export=view&id=10XmzxuJpXIzJBUhUKRyNsnlvynPaKm3g", "label":"ใช่","text": "ใช่"},
         {"image_url": "https://drive.google.com/uc?export=view&id=1RWwSCLYIUKucpYUzUVSVSl1XaQS5PLmb", "label":"ฟันไม่ขึ้น" , "text" : "ไม่ใช่" },
        {"image_url": "https://drive.google.com/uc?export=view&id=1AzYLGZVscPCMQMH5JjWLHOcrhLxKoTci", "label":"ไม่ใช่","text": "ไม่ใช่"}
    ]
}



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
    
        tk = json_data['events'][0]['replyToken']
        user_id = json_data['events'][0]['source']['userId']
        if msg_type == 'text':
            msg = json_data['events'][0]['message']['text']
            reply_msg(line_bot_api, tk, user_id, msg)
        elif msg_type == 'image':
            message_id = json_data['events'][0]['message']['id']
            reply_msg(line_bot_api, tk, user_id, message_id)
        else:
            line_bot_api.reply_message(tk, TextSendMessage(text="ข้อความนี้ยังไม่รองรับ"))
        print("user_id",user_id)
    except Exception as e:
        print(e)
    return 'OK'

def reply_msg(line_bot_api,tk,user_id,msg):
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    conn = Neo4jConnection(uri, user, password)
    node_label = "user"
    property_name = "userID"
    variable_value = user_id
    if (msg == "Hello"):
        #check if the property userID exits
        exists = conn.check_property(node_label, property_name, variable_value)
        if exists:
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
        CREATE (n:user {nodeID:0,qNodeID:608,dayStep:0,userID : $userID,questionCount:0,
        phase:false,fetchNext:false,confirm:false,pushTime:1})
    '''
    parameters = {"userID": variable_value}
    with driver.session() as session:
        session.run(query, parameters)

def getDisplayName(conn, user_id):
    query = '''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.p_display_name = $p_display_name
    '''
    profile = line_bot_api.get_profile(user_id)
    p_display_name = profile.display_name
    conn.query(query, parameters={'user_id': user_id, 'p_display_name': p_display_name})

def display_node(line_bot_api, tk, user_id, msg):
    conn = Neo4jConnection(uri, user, password)
    count = 0
    phase = False
    node_data = fetch_user_node_data(conn, user_id)
    if node_data:
        node_id, day_step, node_step = node_data['nodeID'], node_data['dayStep'], node_data['nodeStep'] 
        node_var = fetch_node_variable(conn, node_id)
        #node_rel_var = fetch_rel_node_variable(conn, node_id)
        #node_image = fetch_node_image(conn, node_id)
        #question_tag = fetch_question_rel(conn, node_id)
        #final_score = fetch_show_score_rel(conn,user_id, node_id, question_tag,day_step)
        final_score = fetch_show_quiz_score(conn, user_id,node_id)
        question_tag =None
        showAnswer = False
        quiz_number = fetch_quiz(conn, node_id)
        print(f"🚀🚀🚀🚀🚀🚀QUIZ_NUMBER={quiz_number}🚀🚀🚀🚀🚀🚀")
        #wrongAnswers = fetch_answer(conn,user_id, node_id,question_tag,day_step)
        #phase = checkPhase(line_bot_api, conn, user_id)
        #count = checkCount(line_bot_api, tk, conn, user_id)
        #isEnd = check_end_node(conn, node_id)
        #isFetch = check_Is_Fetch(line_bot_api, tk, conn, user_id)
        #update_confirm(line_bot_api,  conn, user_id, msg)
        #isConfirm = read_confirm(line_bot_api,  conn, user_id)
        '''if isConfirm == True and isFetch == True:
            resetCount(conn,line_bot_api, tk, user_id, count)
            update_phase(line_bot_api, tk, conn, user_id,count,isConfirm)
            phase = checkPhase(line_bot_api, conn, user_id)
            count = checkCount(line_bot_api, tk, conn, user_id)
            updateCheckConfirm(line_bot_api,  conn, user_id,False)
            updateFetchNext(line_bot_api,  conn, user_id,False)'''
        if msg != "Hello":
            #updateisFetch(line_bot_api, tk, conn, userG_id,count)
            print(f'🚀🚀🚀🚀🚀🚀 msg = {msg}')
            update_quiz_score(conn,user_id,node_id,msg)
            if node_var:
                update_user_variable(conn,user_id,node_var,msg)
         #   if node_rel_var:
          #      update_user_rel_variable(conn, user_id, node_rel_var , node_id, msg)
           # if node_image:
            #    message_id = msg
             #   manage_image(conn,tk,user_id,message_id)
                
         #   if question_tag:
          #      update_user_score(conn,user_id, node_id, msg, question_tag)
           # if final_score:
            #    node_id = final_score
        #    elif showAnswer:
       #         node_id = showAnswer
         #   elif quiz_number:
          #      node_id = fetch_next_quiz(conn,node_id,quiz_number,msg,user_id)
            
            if not final_score:
                node_id = fetch_next_node(tk,conn, node_id, msg,day_step,user_id) or node_id
            else:
                node_id = final_score
        quiz_number = fetch_quiz(conn, node_id)
        isEnd = check_end_node(conn, node_id)

        #isAnswerRel = fetch_answer_rel(conn, node_id)
        update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag,isEnd,count,msg,tk,phase)
        
        if not quiz_number:
            send_node_info(line_bot_api, tk, conn, node_id, node_step, day_step,user_id)
        else:
            send_quiz_info(line_bot_api, tk, conn, node_id,user_id,quiz_number)
        """if phase == False:
            send_node_info(line_bot_api, tk, conn, node_id, node_step, day_step,user_id)
            resetCount(conn,line_bot_api, tk, user_id, count)
        if isEnd:
            phase = True
            update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag,isEnd,count,msg,tk,phase)
        if phase == True:
            is_question = False
            if count > 0 :
                update_phase(line_bot_api, tk, conn, user_id,count,isFetch)
                update_count(conn,line_bot_api, tk, user_id, count)
                count = checkCount(line_bot_api, tk, conn, user_id)
                if msg != "ไม่ใช่":
                    if msg != "ใช่":
                        return_message(line_bot_api, tk, user_id, msg)
                        start_question(line_bot_api, tk, conn, user_id)
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
        """
    else:
        print("No node data found")
def update_quiz_score(conn,user_id,node_id,msg):
    quiz_score = fetch_quiz_score(conn,node_id,msg)
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.quizScore = coalesce(n.quizScore, 0) + $quiz_score
    '''
    query2 = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.quizScore = coalesce(n.quizScore, 0) + 0
    '''
    print(f'QUIZ_MSG={msg}')
    isCorrect = check_is_quiz_correct(conn, node_id, msg)
    if isCorrect:
        conn.query(query, parameters={'user_id': user_id,'quiz_score':quiz_score})
    else:
        conn.query(query2, parameters={'user_id': user_id})

def check_is_quiz_correct(conn, node_id, msg):
    query = f'''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id AND r.choice = $msg
        RETURN r.isCorrect AS isCorrect
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': node_id, 'msg': msg})
        record = result.single()
        return record["isCorrect"] if record else None

def fetch_quiz_score(conn,node_id,msg):
    query = f'''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id AND r.choice = $msg
        RETURN r.score AS quiz_score
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': node_id, 'msg': msg})
        record = result.single()
        return record["quiz_score"] if record else 0

def fetch_next_quiz(conn,node_id,quiz_number,msg,user_id):
    query = f"""
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id AND r.choice = $msg
        RETURN b.quiz_number AS quiz_number
    """
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id, 'msg': msg})
        record = result.single()  # Fetch the single record from the result
        return record["quiz_number"] if record else None


def fetch_quiz(conn, node_id):
    query = '''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id
        RETURN a.quiz_number AS quiz_number
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': node_id})
        record = result.single()
        return record["quiz_number"] if record else None



def fetch_user_node_data(conn, user_id):
    query = '''
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.nodeStep as nodeStep, n.dayStep as dayStep, n.qNodeID as nodeID,
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

def update_user_variable(conn, user_id, node_var, msg):
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.{node_var} = $msg
    '''
    conn.query(query, parameters={'user_id': user_id, 'node_var': node_var, 'msg':msg})


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

def fetch_show_quiz_score(conn, user_id,node_id):
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.quizScore as quiz_score
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'user_id': user_id})
        score_record = result.single()
    score = score_record["quiz_score"] if score_record else None
    if score is not None:
        query = f'''
            MATCH (a)-[r:SCORE]->(b)
            WHERE id(a) = $current_node_id AND r.score = $score
            RETURN id(b) as node_id
        '''
        with conn._driver.session() as session:
            result = session.run(query, parameters={'current_node_id':node_id, 'score': score})
            record = result.single()
            return record["node_id"] if record else False
    else:
        return False
                    


def fetch_next_node(tk,conn, current_node_id, msg, day_step,user_id):
    isEnd = check_end_node(conn, current_node_id)
    count = checkCount(line_bot_api, tk, conn, user_id) 
    phase = checkPhase(line_bot_api, conn, user_id)
    if phase == False:
        node_label = f"Q"
        query = f'''
            MATCH (a:Q)
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
            SET n.dayStep = $day_step, n.qNodeID = $node_id, n.nodeStep = $node_step
        '''
    
    query2 = f'''
            MATCH (a:{node_label})
            WHERE a.step = 1
            RETURN id(a) AS node_id
        '''
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

def send_quiz_info(line_bot_api, tk, conn, node_id,user_id,quiz_number):
    node_step = 0
    entity_data = fetch_entity_data(conn, node_id, node_step,user_id)
    if entity_data:
        entity_data = replace_text_with_variable(conn,user_id,entity_data)
        send_quiz(line_bot_api, tk, entity_data,quiz_number,user_id)


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
        RETURN n.name as name, n.name2 as name2, n.photo as photo, r.choice as choice,r.name as quickreply,r.photo, coalesce(n.video, '') as video,n.pic1 as pic1,n.pic2 as pic2,n.pic3 as pic3
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

def send_quiz(line_bot_api, tk, entity_data,quiz_number,user_id):
    messages = []
    if entity_data["name"]:                                                            messages.append(TextSendMessage(text=entity_data["name"]))
    if entity_data["name2"]:
        messages.append(TextSendMessage(text=entity_data["name2"]))
    if entity_data["photo"]:                                                           messages.append(ImageSendMessage(original_content_url=entity_data["photo"], preview_image_url=entity_data["photo"]))
    if messages:
        line_bot_api.reply_message(tk, messages)
        send_image_carousel(user_id,quiz_number)
    else:
        print("No valid messages to send2222")


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

def send_image_carousel(user_id,quiz_number):
    print(f"✅✅✅✅✅Quiz_number:{quiz_number}✅✅✅✅")
    images = carousel_data.get(quiz_number, [])
    if not images:
        print(f"❌ No images found for question question_number")
        return
    carousel_template = TemplateSendMessage(
        alt_text=f"this is a image carousel template.",
        template=ImageCarouselTemplate(columns=[
            ImageCarouselColumn(
                image_url=item["image_url"],
                action=MessageTemplateAction(
                    label=item["label"],
                    text=item["text"]  # ✅ ใช้ข้อความที่กำหนดไว้ใน `carousel_data`
                )
            ) for item in images
        ])
    )
    line_bot_api.push_message(user_id, carousel_template)
    print(f"✅ Image Carousel for question sent successfully!")




if __name__ == "__main__":
    app.run(port=8080)




