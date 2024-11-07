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

from linebot import LineBotApi

import requests
import re
import json
from flask import abort
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.models import *

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
def push_line_message(user_id, message_text):
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
    response = requests.post(line_api_url, headers=headers, json=payload)
    return response.status_code, response.text

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
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    message_text = "Do you want to continue?"
    status_code, response_text = push_line_message(user_id, message_text)
    if status_code == 200:
        print('Message sent successfully!')
        return jsonify({'message': 'Message sent successfully!'}), 200
    else:
        print(f'Failed to send message: {response_text}')
        return jsonify({'error': f'Failed to send message: {response_text}'}), 500


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
        msg = json_data['events'][0]['message']['text']
        tk = json_data['events'][0]['replyToken']
        user_id = json_data['events'][0]['source']['userId']
        #msg_reply = reply_msg(msg,user_id)
        #line_bot_api.reply_message(tk,TextSendMessage(text=msg_reply[0],quick_reply=msg_reply[1]))                             
        reply_msg(line_bot_api,tk,user_id,msg)

      #  print(msg, tk)
       # print("user_id",user_id)
    except Exception as e:
        print(e) 
    return 'OK'


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
    conn = Neo4jConnection(uri, user, password)
    getDisplayName(conn, user_id)
    node_label = "user"
    property_name = "userID"
    variable_value = user_id
    if (msg == "Hello"):
        #check if the property userID exits
        exists = conn.check_property(node_label, property_name, variable_value)
        if exists:
            #print("User ID exit in neo4j")
            display_node(line_bot_api,tk,user_id,msg)
    else:
        display_node(line_bot_api,tk,user_id,msg)

def return_message(line_bot_api,tk,user_id,msg):
    if(msg == "Hello"):
        flex = response_flex()
        line_bot_api.reply_message(tk,fkex)

def display_node(line_bot_api, tk, user_id, msg):
    conn = Neo4jConnection(uri, user, password)
    
    node_data = fetch_user_node_data(conn, user_id)
     
    if node_data:
        node_id, day_step, node_step = node_data['nodeID'], node_data['dayStep'], node_data['nodeStep'] 
        node_var = fetch_node_variable(conn, node_id)
        question_tag = fetch_question_rel(conn, node_id)
        if msg != "Hello":
            if node_var:
                update_user_variable(conn,user_id,node_var,msg)
            if question_tag:
                update_user_score(conn,user_id, node_id, msg, question_tag)
            node_id = fetch_next_node(conn, node_id, msg,day_step) or node_id

        update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag)
        send_node_info(line_bot_api, tk, conn, node_id, node_step, day_step,user_id)
    else:
        print("No node data found")

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

def fetch_question_rel(conn, current_node_id):
    query= '''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id AND r.isCorrect IS NOT NULL
        RETURN labels(a) AS label
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id})
        record = result.single()
        return record["label"] if record else None

def fetch_next_node(conn, current_node_id, msg, day_step):
    isEnd = check_end_node(conn, current_node_id)
    if isEnd == False:
        node_label = f"d{day_step}"
        query = f'''
            MATCH (a:{node_label})
            WHERE id(a) = $node_id  
            OPTIONAL MATCH (a:{node_label})-[r:NEXT]->(b:{node_label})
            WHERE r.choice = $msg OR r.choice IS NULL OR r.choice = ""
            RETURN id(b) AS node_id
        '''
    else:
        #day_step = day_step + 1
        node_label = f"d{day_step}"
        query = f'''
            MATCH (a:{node_label})
            WHERE a.step = 1
            OPTIONAL MATCH (a:{node_label})-[r:NEXT]->(b:{node_label})
            WHERE a.step = 1 AND (r.choice = $msg OR r.choice IS NULL OR r.choice = "")
            RETURN id(a) AS node_id
        '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id, 'msg': msg})
        record = result.single()  # Fetch the single record from the result
        return record["node_id"] if record else None

def check_end_node(conn, current_node_id):
    query = f'''
        MATCH (a)
        WHERE id(a) = $node_id AND a.isEnd = true
        RETURN true AS result
    '''
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': current_node_id})
        record = result.single()  
        return record["result"] if record else False

def update_user_progress(conn, user_id, node_id, day_step, node_step, question_tag):
    isEnd = check_end_node(conn, node_id)
    #dayScore = f"{question_tag}Score"
    print(isEnd)
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.dayStep = $day_step, n.nodeID = $node_id, n.nodeStep = $node_step,
        
    '''
    if isEnd:
        day_step = day_step + 1
        node_step = 1
    conn.query(query, parameters={'user_id': user_id, 'day_step': day_step, 'node_id': node_id, 'node_step': node_step})
    
def update_user_variable(conn, user_id, node_var, msg):
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.{node_var} = $msg
    '''
    conn.query(query, parameters={'user_id': user_id, 'node_var': node_var, 'msg':msg})

def update_user_score(conn, user_id, node_id, msg, question_tag):
    dayScore = f"{question_tag}Score"
    query = f'''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.{dayScore} = coalesce(n.{dayScore}, 0) + 1
    '''
    isCorrect = check_is_correct(conn, node_id, msg)
    if isCorrect:
        conn.query(query, parameters={'user_id': user_id})


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
    entity_data = fetch_entity_data(conn, node_id, node_step)
    if entity_data:
        entity_data = replace_text_with_variable(conn,user_id,entity_data)
        send_messages(line_bot_api, tk, entity_data)


def fetch_entity_data(conn, node_id, node_step):
    query = '''
        MATCH (n)
        WHERE id(n) = $node_id
        OPTIONAL MATCH (n)-[r:NEXT]->(m)
        RETURN n.name as name, n.name2 as name2, n.photo as photo, r.choice as choice,r.name as quickreply
    '''
    entity = {"name": None, "name2": None, "photo": None,"quickreply":None, "choices": []}
    
    with conn._driver.session() as session:
        result = session.run(query, parameters={'node_id': node_id})
        records = list(result)
        if not records:
            print(f"No records found for node_id: {node_id}")
            return None
        for record in records:
            entity["name"] = record.get("name", entity["name"]).strip()
        
            entity["name2"] = record.get("name2", entity["name2"]).strip()
    
            entity["photo"] = record.get("photo", entity["photo"]).strip()
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
    messages = []
    if entity_data["name"]:
        messages.append(TextSendMessage(text=entity_data["name"]))
    if entity_data["name2"]:
        messages.append(TextSendMessage(text=entity_data["name2"]))
    if entity_data["photo"]:
        messages.append(ImageSendMessage(original_content_url=entity_data["photo"], preview_image_url=entity_data["photo"]))
    
    if entity_data["quickreply"] is not None:
        quick_reply_buttons = [QuickReplyButton(action=MessageAction(label=c, text=c)) for c in entity_data["choices"]
        if c.strip()]
        if quick_reply_buttons:
            quick_reply = QuickReply(items=quick_reply_buttons)
            messages.append(TextSendMessage(text=entity_data["quickreply"], quick_reply=quick_reply))
    

    if messages:
        
        line_bot_api.reply_message(tk, messages)
    else:
        print("No valid messages to send")

if __name__ == "__main__":
    app.run(port=8080)
