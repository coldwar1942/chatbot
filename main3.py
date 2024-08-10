import schedule
import time as tm
from datetime import time, timedelta, datetime
import subprocess
import flask_app
import datetime, pytz
from neo4j import GraphDatabase, basic_auth

time_str = 0;
tz = pytz.timezone('Asia/Bangkok')
now1 = datetime.datetime.now(tz)
time_compare = now1.strftime('%H')

driver = GraphDatabase.driver(
  "neo4j://172.30.81.223:7687",
  auth=basic_auth("neo4j", "password"))

def job():
    global time_str
    global time_compare
    now1 = datetime.datetime.now(tz)
    time_str = now1.strftime('%H')
     
    cypher_query = '''
    MATCH (n:USER) return n.pushTime as time,n.userID as UID;
    '''
    cypher_query2 = ''' 
    MATCH (n:d1) return n.name as text;
    '''

    Entity_corpus = []
    Entity_corpus2 = []
    with driver.session() as session:
        results = session.run(cypher_query)
        for record in results:
            #print(f"Time: {record['time']}, UID: {record['UID']}")
            Entity_corpus.append((record['time'],record['UID']))
        #using set() to remove duplicated from list
        Entity_corpus = list(set(Entity_corpus))
        results = session.run(cypher_query2)
        for record in results:
            Entity_corpus2.append((record['text']))
            


    for entity in Entity_corpus2:
       #print(f"Text1: {entity}")

        hour = entity[0][:2]
        uid = entity[1]
        print(hour)
        print(uid)
        if (time_str != time_compare and time_str == hour):
            print("Subscribe to World")
            run_flask_app();

        time_compare = time_str
    

schedule.every(5).seconds.do(job)

def run_flask_app():
    #subprocess.run(["python", "flask_app.py"])
    with flask_app.app.test_client() as client:
        response = client.get('/send_flex_message')
        print(response.data.decode())



if __name__ == "__main__":
    
    
    
    while True:
        schedule.run_pending()
        tm.sleep(1)
    
