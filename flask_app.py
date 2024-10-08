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
   # print(f"Message is {msg}")
    conn = Neo4jConnection(uri, user, password)
    query = '''
        MATCH (n:user)
        WHERE n.userID = $variable_value
        RETURN n.nodeStep as property_value , n.dayStep as dayStep, n.nodeID as nodeID,n.rs_id as rs_id
                '''   # query nodeStep from USER     #STEP 1

    
    with driver.session() as session:
        result = session.run(query, variable_value=user_id)
        record = result.single()
        property_value = record.get("property_value")
        dayStep = record.get("dayStep")
        node_id = record.get("nodeID")
        #rs_id = record.get("rs_id")
        node_label = f"d{dayStep}"
        temp = property_value
        nodeStep = temp
    #    print(temp)
    #node_label = "user"
    #property_name = "nodeStep"
    #property_name2 = 
    #variable_value = 1
    #exists = conn.check_property(node_label, property_name, variable_value)
    cypher_query4 = f'''
        MATCH (a:{node_label})-[r:NEXT]->(b:{node_label})
        WHERE id(a) = $node_id AND r.choice = $msg
        RETURN id(b) AS node_id
    '''
    
    cypher_query6 = f'''
        MATCH (a:{node_label})-[r:NEXT]->(b:{node_label})
        WHERE id(a) = $node_id 
        RETURN id(b) AS node_id,r.name AS quickReply
    '''
    reply = True
    #print(f"Text0: {property_value}")
    if (msg != "Hello"): #when user click quickreply button
        #reply = None
        with driver.session() as session: 
            node_id_temp = node_id
            hasReply = False
            result = session.run(cypher_query6,node_id=node_id) # id(a) (a)-[r:NEXT]-> (b)
            print(cypher_query6)
            record = result.single()
            if record:                           
                reply = record.get('quickReply') # (a) -[r:NEXT]-> (b)
                hasReply = True
                node_id2 = record.get('node_id') # id(b) 
            else:
                hasReply = False # no relationship from (a)
        #find id(c)
        if hasReply == True:
            node_id = node_id2
        #if hasReply == True: # have relation between (a) and (b)
        with driver.session() as session: # if (a) -[r:NEXT]-> (b) and msg = r.choice
            result = session.run(cypher_query4,node_id=node_id_temp,msg=msg) # id(b)
            print(cypher_query4)
            record = result.single()
            if record:    
                node_id = record.get('node_id') # specific node id(b) from multinode 
        

        #else hasReply == False:
         #   with driver.session() as session:

                   # node_id = node_id2
   # print(f"start node id = {node_id}")        


    if property_value != 99: # when user reply message
        query_update = '''
                MATCH (n:user)
                WHERE n.userID = $userID
                SET n.dayStep = $temp2, n.nodeID = $nodeID,n.nodeStep = $nodeStep
                RETURN n
         ''' #STEP 4
        query_norelationship = f'''
                MATCH (n:{node_label})
                WHERE id(n) = $node_id
                RETURN n
        '''
        
        # update nodeStep to user
        cypher_query = f'''
                MATCH (a:{node_label})-[r:NEXT]->(b:{node_label})
                WHERE id(a) = $nodeID 
                RETURN id(b) AS id_n ,a,b
                '''                         # query all node's properties from step variable
        #STEP 2
        cypher_query5 = f'''
            MATCH (n:{node_label})
            WHERE n.step = $variable_value
            RETURN id(n) AS id_n ,n
        '''
        rs_query = f'''
            MATCH (n)-[r:NEXT]->(m)
            WHERE id(n) = $node_id
            RETURN m.step AS step , id(m) AS node_id
        '''

       # node_label = f"d{dayStep}"

        Entity_corpus = []
        Entity_corpus2 = []
        Entity_corpus3 = []
        isEnd = False
        isFound = False
        node_ids = []
        #rs_ids = []
        #with driver.session() as session:
            #temp = temp + 1 # update nodeStep by 1
            
            #result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id, temp=temp))
            #result = session.run(query_update,userID=user_id,temp=temp+1)
        if isEnd is False:
            with driver.session() as session:
               # isFound = False
            #result = tx.run(query_update,userID =user_id, temp=temp+1)
                results = session.run(cypher_query,nodeID = node_id) # id(b) get node b and c
               # print(cypher_query)
                for record in results:
                    isFound = True # if find (b)-[r:NEXT]->(c)
                    node = record['a']
                    node2 = record['b']
                #Entity_corpus.append(record['n']['name']) #Accessing the 'name' property of the node
                #Entity_corpus2.append(record['n']['name2'])
                #Entity_corpus3.append(record['n']['photo'])
                    if 'name' in node:
                        Entity_corpus.append(node['name'])   # get (b) properties
                    if 'name2' in node:
                        Entity_corpus2.append(node['name2'])
                    if 'photo' in node:
                        Entity_corpus3.append(node['photo'])
                   # if 'isEnd' in node2:
                    #    isEnd = node2['isEnd']
     #   print(f"isFound boolean value = {isFound}")
        if isFound is False: # if not find (b)-[r:NEXT]->(c) or no relation from node b
            with driver.session() as session:
                Entity_corpus = []
                Entity_corpus2 = []
                Entity_corpus3 = []
                results = session.run(query_norelationship,node_id=node_id2)
                print(query_norelationship)
                for record in results:
                    node = record['n']      # get (b) properties
                    if 'name' in node:
                        Entity_corpus.append(node['name'])
                    if 'name2' in node:
                        Entity_corpus2.append(node['name2'])
                    if 'photo' in node:
                        Entity_corpus3.append(node['photo'])
                    if 'isEnd' in node:
                        isEnd = node['isEnd']

                #node_ids.append(record['id_n']) 
                #isEnd = result.single().get("isEnd")
            
            
            #print(f"node_id is {node_ids}")
            Entity_corpus = list(set(Entity_corpus))
            Entity_corpus2 = list(set(Entity_corpus2))
            Entity_corpus3 = list(set(Entity_corpus3))
           # with driver.session() as session:
                #results = session.run(cypher_query,variable_value=temp+1)
            #    for record in results:
             #       node_ids.append(node['id_n'])
           # node_id = node_ids[0]
            #result = tx.run(query_update,userID =user_id, temp=temp+1)
        ''' if isEnd is False:
                temp = temp + 1
                result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id, temp=temp
                                                                     , temp2 = dayStep,nodeID=node_id))
            elif isEnd is True: # when end any day
                temp = 1
                dayStep = dayStep + 1
                node_label = f"d{dayStep}" 
                # reset nodeStep to 0
                result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id, temp=temp,
                                                                     temp2 = dayStep))
           ''' #for entity in Entity_corpus:
        #print(Entity_corpus)
        entity = Entity_corpus[0] if Entity_corpus else None     # properties from (b)
        entity2 = Entity_corpus2[0] if Entity_corpus2 else None
        entity3 = Entity_corpus3[0] if Entity_corpus3 else None
      #  print(entity)
       # print(entity2)
       # print(entity3)
        #node_id = node_ids[0]
        if entity and entity.strip():
            message1 = TextSendMessage(text=entity)
        else:
            message1 = TextSendMessage(text="")
        if entity2 and entity2.strip():
            message2 = TextSendMessage(text=entity2)
        else:
            message2 = TextSendMessage(text="") 
        #line_bot_api.reply_message(tk,temp)
        body = request.get_data(as_text=True)
        json_data = json.loads(body)
        tk = json_data['events'][0]['replyToken']
        
        cypher_query3 =f'''
            MATCH (a:{node_label})-[r:NEXT]->(b:{node_label})
            WHERE b.step = $nodeStep  AND id(a) = $nodeID  
            RETURN b.isEnd AS isEnd ,r.choice AS choice,r.name AS name,id(b) AS node_id,id(r) AS rs_id,b.step AS nodeStep
            '''         # query relationship between start node to finish node     
                        # STEP 3
        cypher_query4 = f'''
            MATCH (a:{node_label})-[r:NEXT]->(b:{node_label})
            WHERE id(a) = $node_id AND r.choice = $msg
            RETURN id(b) AS node_id
        '''# STEP 3.5
        

        if isFound is False:  #if not find (b)-[r:NEXT]->(c) or no relation from node b
            temp = 1
            dayStep = dayStep + 1  # proceed to next day first node
            node_label = f"d{dayStep}"
            cypher_query5 = f'''
                        MATCH (n:{node_label})
                        WHERE n.step = $variable_value
                        RETURN id(n) AS id_n ,n
                                                        '''

            # move to next day
            with driver.session() as session:
                results = session.run(cypher_query5,variable_value=temp)
                print(cypher_query5)
                for record in results:
                    node_ids.append(record['id_n'])
                node_ids = list(set(node_ids))
                if node_ids:
                    node_id3 = node_ids[0]  # get next day id(a)
            #result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id, temp=temp, temp2 = dayStep,nodeID=node_id#))
       # if isEnd is False:
          #  temp = temp + 1

       # with driver.session() as session:
            
         #   result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id, temp=temp, temp2 = dayStep,nodeID=node_id))
        if isFound is True: #find (b)-[r:NEXT]->(c)
            with driver.session() as session:
                result = session.run(rs_query,node_id=node_id) # find (c) node step from id(b)
                nodes = []
                for record in result:
                    node = record['step']
                    nodes.append(node)
                if nodes:
                    node = nodes[0] # day node step
                    print(f"node step = {node}")
                else:
                    node = 1 # next day node step
        choice = []
        name = []
        #if reply == False:
        if isFound is True: #find (b)-[r:NEXT]->(c)
            with driver.session() as session:
                choice = []
                name = []
                print(f"current nodeStep is {node}")  # (c) nodestep
                print(f"current nodeID is {node_id}") # id(b) 
                # id(b), (b)-[r:NEXT]->(c) get r properties
                result = session.run(cypher_query3,nodeStep=node,nodeID=node_id) # (b)-[r:NEXT]->(c)
                records_found = False
                for record in result:
                    records_found = True # found relation properties
                    records_found = True
                    choice_value = record['choice'].strip() if record['choice'] else ""
                    #choice.append(record['choice'])
                    name_value = record['name'].strip() if record['name'] else ""
                    if choice_value:
                        choice.append(choice_value)
                    if name_value:
                        name.append(name_value)

                if not records_found: # not found relation properties
                    choice = None
                    name = None
               # node_ids.append(record['node_id']) # node_id of next node 
                #rs_ids.append(record['rs_id'])
                #node_ids.append(record['node_id'])
        #print(text)    
        #print(f"relationship id is {rs_id}")
        # update
        #if (msg != "Hello"):
         #   with driver.session() as session:
          #      result = session.run(cypher_query4,node_id=node_id,msg=msg)
           #     record = result.single()
            #    node_id = record.get('node_id')
       # else :
        #    node_id = node_ids[0]
        #rs_id = rs_ids[0]
        #node_id = node_ids[0]
        with driver.session() as session: 
            if isFound is True: #if find (b)-[r:NEXT]->(c)
                result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id,temp2 = dayStep,nodeID=node_id,nodeStep = node))  # updated node id is (b)
            if isFound is False:#if not find (b)-[r:NEXT]->(c) or (b)
                result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id,temp2 = dayStep,nodeID=node_id3,nodeStep = temp)) # updated node id is next day (a)

        message3 = TextSendMessage(text="") 
        #if (not choice and not name):
         #   message3 = TextSendMessage(text="")
        #else:
        quick_reply_buttons = []
        if choice:
            for x in choice:
                quick_reply_buttons.append(QuickReplyButton(action=MessageAction(label=x, text=x)))
            quick_reply = QuickReply(items=quick_reply_buttons)
        
            #quick_reply_buttons = QuickReply(items=[
               # QuickReplyButton(action=MessageAction(label=choice[0],text=choice[0])),
               # QuickReplyButton(action=MessageAction(label=choice[1], text=choice[1])),
                #QuickReplyButton(action=MessageAction(label=choice[2], text=choice[2])),
                #QuickReplyButton(action=MessageAction(label=choice[3], text=choice[3])),
                #])
        #quick_reply = QuickReply(item=quick_reply_buttons)
       #message = TextSendMessage(text=
        #demo = name[0]
        #print(f"QucikReplyName is {demo}")
        
        message3 = TextSendMessage(text="")
        if choice is not None and name is not None and len(choice)>0:
            message3 = TextSendMessage(
                text=name[0],
                quick_reply=quick_reply
        )
        if entity3:
            image_message = ImageSendMessage(
                original_content_url=entity3,
                preview_image_url=entity3
                )
            message4 = image_message
        else:
            message4 = TextSendMessage(text="")
        isEmpty = TextSendMessage(text="")
        #if message2 == isEmpty and message3 == isEmpty: # missing 2,3 
         #   line_bot_api.reply_message(tk,[message1])
        #elif message2 == isEmpty: # missing 2
         #   line_bot_api.reply_message(tk,[message1,message4,message3])
        #elif message3 == isEmpty: # missing 3
         #   line_bot_api.reply_message(tk,[message1,message2])
        #else:
         #   line_bot_api.reply_message(tk,[message1,message2,message3])
        messages = []
        if message1 != isEmpty:
            messages.append(message1)

        if message2 != isEmpty:
            messages.append(message2)


        
        #if message4 != ImageSendMessage(
         #       original_content_url="",
        #        preview_image_url=""
         #       ):
        if message4 != isEmpty:
            messages.append(message4)

        if message3 != isEmpty:
            messages.append(message3)
#        with driver.session() as session:
 #           result = session.write_transaction(lambda tx: tx.run(query_update, userID=user_id, temp=temp, temp2 = dayStep,nodeID=node_id))
        if messages: 
            line_bot_api.reply_message(tk,messages)
        else:
            print("No valid messages to send.")
        msg = json_data['events'][0]['message']['text']
        
    
            
if __name__ == "__main__":
    app.run(port=8080)
