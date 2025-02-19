from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np
import json
from neo4j import GraphDatabase
import re
app = Flask(__name__)

# Neo4j database connection
uri = "neo4j:172.30.81.113:7687"  # Replace with your Neo4j URI
username = "neo4j"  # Replace with your Neo4j username
password = "password"  # Replace with your Neo4j password
driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to fetch data from Neo4j
def fetch_data_from_neo4j():
    query = """
    MATCH (n:QAM)-[r:Answer]->(m:QAM)
    RETURN n.answer AS answer,n.pic AS pic, m 
    """
    results = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            answer = record["answer"]
            pic = record.get("pic", "default_value")
            #n_properties = dict(record["n"].items())
            m_properties = dict(record["m"].items())  # Convert properties to dictionary
            results.append({
                "answer": answer,
                "pic": pic,
                "questions": m_properties
                })
    
    return results

# Fetch data from Neo4j and create the DataFrame
results = fetch_data_from_neo4j()
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
   # if isinstance(questions_dict, dict):
  #      questions_combined = " ".join(questions_dict.values())
   # else:
    #    questions_combined = questions_dict  # In case questions_dict is already a string
    # Append to the merged results list

#print(f"merged is {merged_results}")
#print(f"results is {results}")
flattened_data = []
#for item in merged_results:
 #   answers = item['answer'].values()
  #  questions = item['questions'].values()  # Extract all questions
   # for question in questions:
    #    flattened_data.append([question, answer])
#for item in merged_results:
    #answer = item.get('answer', '')
   # questions_dict = item['question']
    
   # merged_results.append({
      #  'answer': answer,
     #   'question': questions_dict
    #    })
for item in merged_results:
    if item['answer'] == "":
        answer = item['pic']
    else:
        answer = item['answer']
    question = item['question']
    flattened_data.append({'question': question, 'answer': answer})
print("Flattened Data:")
print(flattened_data)

#column_name = 'answer'
#print(flattened_data)
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


def check_sentence(msg):
    # Step 4: Create a search vector
    search_text = msg
    search_vector = encoder.encode(search_text)
    _vector = np.array([search_vector])
    faiss.normalize_L2(_vector)

    # Step 5: Search
    k = index.ntotal  # Number of nearest neighbors to retrieve
    distances, ann = index.search(_vector, k=k)
    results = pd.DataFrame({'distances': distances[0], 'ann': ann[0]})
    labels  = df['answer']
    Ques = df['question']
    Sentence = labels[ann[0][0]]


    # Step 6: Retrieve and format results
    if distances[0][0] <= 0.5:
        answer = labels[ann[0][0]]
        Sentence = Ques[ann[0][0]]
    else:
        Sentence = msg
        answer = msg

    return [Sentence, answer]

def return_message(line_bot_api, tk, user_id, msg):
    chk_msg = check_sentence(msg)
    response = f"Similar to: {chk_msg[0]} Answer: {chk_msg[1]}"
    
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
        
        return_message(line_bot_api, tk, user_id, msg)
        
    except Exception as e:
        print("Error:", e)
        print(body)
    return 'OK'

if __name__ == '__main__':
    app.run(port=8080)
