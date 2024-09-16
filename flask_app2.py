from flask import Flask, request, abort
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

    def is_connected(self):
        try:
            # Try running a simple query to verify connection
            self.query("RETURN 1", single=True)
            return True
        except Exception as e:
            return False

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

        print(msg, tk)
        print("user_id",user_id)
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
    if conn.is_connected():
        print("Connected to Neo4j successfully!")
    else:
        print("Failed to connect!")
    node_label = "user"
    property_name = "userID"
    variable_value = user_id
    if (msg == "Hello"):
        #check if the property userID exits
        exists = conn.check_property(node_label, property_name, variable_value)
        if exists:
            print("User ID exit in neo4j")
            display_node(line_bot_api,tk,user_id,msg)
        else:
            print("User ID doesn't exit in neo4j")
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
        if msg != "Hello":
            node_id = fetch_next_node(conn, node_id, msg) or node_id

        update_user_progress(conn, user_id, node_id, day_step, node_step)
        send_node_info(line_bot_api, tk, conn, node_id, node_step, day_step)
    else:
        print("No node data found")


def fetch_user_node_data(conn, user_id):
    query = '''
        MATCH (n:user)
        WHERE n.userID = $user_id
        RETURN n.nodeStep as nodeStep, n.dayStep as dayStep, n.nodeID as nodeID
    '''
    
    record = conn.query(query, parameters={'user_id':user_id}, single=True)
    if record:
        return {"nodeStep": record["nodeStep"], "dayStep": record["dayStep"], "nodeID": record["nodeID"]}
    return None


def fetch_next_node(conn, current_node_id, msg):
    query = '''
        MATCH (a)-[r:NEXT]->(b)
        WHERE id(a) = $node_id AND r.choice = $msg
        RETURN id(b) AS node_id
    '''
    with conn.session() as session:
        record = conn.query(query, parameters={'node_id': current_node_id, 'msg': msg}, single=True)
        return record["node_id"] if record else None


def update_user_progress(conn, user_id, node_id, day_step, node_step):
    query = '''
        MATCH (n:user)
        WHERE n.userID = $user_id
        SET n.dayStep = $day_step, n.nodeID = $node_id, n.nodeStep = $node_step
    '''
    conn.query(query, parameters={'user_id': user_id, 'day_step': day_step, 'node_id': node_id, 'node_step': node_step})


def send_node_info(line_bot_api, tk, conn, node_id, node_step, day_step):
    entity_data = fetch_entity_data(conn, node_id, node_step)
    if entity_data:
        send_messages(line_bot_api, tk, entity_data)


def fetch_entity_data(conn, node_id, node_step):
    query = '''
        MATCH (n)-[r:NEXT]->(m)
        WHERE id(n) = $node_id
        RETURN n.name as name, n.name2 as name2, n.photo as photo, r.choice as choice
    '''
    entity = {"name": None, "name2": None, "photo": None, "choices": []}
    records = conn.query(query, parameters={'node_id': node_id})
        
    for record in records:
        if 'name' in record:
            entity["name"] = record["name"]
        if 'name2' in record:
            entity["name2"] = record["name2"]
        if 'photo' in record:
            entity["photo"] = record["photo"]
        if 'choice' in record:
            entity["choices"].append(record["choice"])
    return entity if any(entity.values()) else None


def send_messages(line_bot_api, tk, entity_data):
    messages = []
    if entity_data["name"]:
        messages.append(TextSendMessage(text=entity_data["name"]))
    if entity_data["name2"]:
        messages.append(TextSendMessage(text=entity_data["name2"]))
    if entity_data["photo"]:
        messages.append(ImageSendMessage(original_content_url=entity_data["photo"], preview_image_url=entity_data["photo"]))
    if entity_data["choices"]:
        quick_reply_buttons = [QuickReplyButton(action=MessageAction(label=c, text=c)) for c in entity_data["choices"]]
        quick_reply = QuickReply(items=quick_reply_buttons)
        messages.append(TextSendMessage(text="Choose an option:", quick_reply=quick_reply))

    if messages:
        line_bot_api.reply_message(tk, messages)
       

if __name__ == "__main__":
    app.run(port=8080)
