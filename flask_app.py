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

    def check_property(self, label, property_name, variable_value):
        with self._driver.session() as session:
            result = session.read_transaction(self._check_property_query, label, property_name, variable_value)
            return result

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

def display_node(line_bot_api,tk,user_id,msg):

    conn = Neo4jConnection(uri, user, password)
    query = '''
        MATCH (n:user)
        WHERE n.userID = $variable_value
        RETURN n.nodeStep as property_value
                '''   # query nodeStep from USER     

    with driver.session() as session:
        result = session.run(query, variable_value=user_id)
        property_value = result.single().get("property_value")
        temp = property_value
        print(temp)
    #node_label = "user"
    #property_name = "nodeStep"
    #property_name2 = 
    #variable_value = 1
    #exists = conn.check_property(node_label, property_name, variable_value)
    #print(f"Text0: {property_value}")
    if property_value != 99: # when user reply message
        query_update = '''
                MATCH (n:user)
                WHERE n.userID = $userID
                SET n.nodeStep = $temp
                RETURN n
                                                        ''' # update nodeStep to user
        cypher_query = '''
                MATCH (n:d1)
                WHERE n.step = $variable_value
                RETURN n
                '''                         # query all node's properties from step variable
        Entity_corpus = []
        with driver.session() as session:
            temp = temp + 1
            print(temp)
            result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id, temp=temp))
            #result = session.run(query_update,userID=user_id,temp=temp+1)
        with driver.session() as session:
            #result = tx.run(query_update,userID =user_id, temp=temp+1)
            results = session.run(cypher_query,variable_value=temp)
            for record in results:
                Entity_corpus.append(record['n']['name']) #Accessing the 'name' property of the node
            Entity_corpus = list(set(Entity_corpus))
            #result = tx.run(query_update,userID =user_id, temp=temp+1)

            #for entity in Entity_corpus:
        #print(Entity_corpus)
        entity = Entity_corpus[0]
        #temp = TextSendMessage(text=entity)
        #line_bot_api.reply_message(tk,message)
        body = request.get_data(as_text=True)
        json_data = json.loads(body)
        tk = json_data['events'][0]['replyToken']
        cypher_query = '''
            MATCH (a:d1)-[r:NEXT]->(b:d1)
            WHERE a.step = $value1 AND b.step = $value2
            RETURN r.name AS text
        '''         # query relationship between start node to finish node     

        with driver.session() as session:
            result = session.run(cypher_query,value1=temp,value2=temp+1)
            text = None
            for record in result:
                text = record['text']
            
        print(text)    
        quick_reply_buttons = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label=text,text=text)),
            QuickReplyButton(action=MessageAction(label="Option 2", text="You selected option 2")),
            ])
        #quick_reply = QuickReply(item=quick_reply_buttons)
        message = TextSendMessage(
            text=entity,
            quick_reply=quick_reply_buttons
                )
        line_bot_api.reply_message(tk,message)
        msg = json_data['events'][0]['message']['text']
        
        if msg:
            print("msg=text")
            print(msg)


if __name__ == "__main__":
    app.run(port=8080)
