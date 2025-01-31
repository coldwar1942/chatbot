import schedule
import time as tm
from datetime import time, timedelta, datetime
import subprocess
import flask_app
import datetime, pytz
from neo4j import GraphDatabase, basic_auth
import requests

time_str = 0;
tz = pytz.timezone('Asia/Bangkok')
now1 = datetime.datetime.now(tz)
time_compare = now1.strftime('%M')

driver = GraphDatabase.driver(
  "neo4j://172.30.81.113:7687",
  auth=basic_auth("neo4j", "password"))
user_id = 'U941269aa045b31f401009f8a369f2198'
uri = "neo4j:172.30.81.113:7687"
user = "neo4j"
password= "password"

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
    def close(self):
        self._driver.close()

conn = Neo4jConnection(uri, user, password)

def job():
    global time_str
    global time_compare
    now1 = datetime.datetime.now(tz)
    time_str = now1.strftime('%M')
    print(time_str)  
    cypher_query = '''
    MATCH (n:user) 
    return n.pushTime as time,n.userID as UID;
    '''
    cypher_query2 = ''' 
    MATCH (n:d1) return n.name as text;
    '''
    users = []
    Entity_corpus = []
    Entity_corpus2 = []
    with conn._driver.session() as session:
        results = session.run(cypher_query)
        for record in results:
            push_time = record['time']
            user_id = record['UID']
            #print(f"Time: {record['time']}, UID: {record['UID']}")
            users.append({'userID': user_id, 'pushTime': push_time})
        #using set() to remove duplicated from list
        print(users)
       # Entity_corpus = list(set(Entity_corpus))
       # results = session.run(cypher_query2)
       # for record in results:
          #  Entity_corpus2.append((record['text']))
    #user_ids = [user['userID'] for user in users]
    for user in users:
        user_id = user['userID']
        push_time = user['pushTime']
        hour = push_time#[:2]
        print(hour)
        if (time_str != time_compare and int(time_str) % int(hour) == 0):
            run_flask_app(user_id)
        time_compare = time_str

    #for entity in Entity_corpus2:
     #   print(f"Text1: {entity}")

        #hour = entity[0]#[:2]
        #uid = entity[1]
        #print(hour)
        #print(uid)
      #  if (time_str != time_compare and time_str == hour):
       #     print("Subscribe to World")
      #      run_flask_app();

        #time_compare = time_str
    

schedule.every(5).seconds.do(job)

def run_flask_app(user_id):
    #subprocess.run(["python", "flask_app.py"])
   # with flask_app.app.test_client() as client:
      #  response = client.get('/send_message_with_id')
     #   print(response.data.decode())
    url = 'http://127.0.0.1:8080/push_message_with_id'
    data = {
            'user_id': user_id
        }
    response = requests.post(url, json=data)
    print('Response status code:', response.status_code)
    print('Response body:', response.json())

if __name__ == "__main__":
    
    
    
    while True:
        schedule.run_pending()
        tm.sleep(1)
    
