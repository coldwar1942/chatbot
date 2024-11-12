from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np

#Step 1: Create a dataframe with the existing text and categories
data = [['ทำไมเราต้องแปรงฟันทั้งตอนเช้าและก่อนนอนวันละ 2 ครั้ง?', ' '], ['การแปรงฟันวันละ 2 ครั้ง ตอนเช้าและก่อน', ' '],  
['เพราะอะไรเราถึงต้องแปรงฟันตอนเช้าและก่อนนอนทุกวัน?', '' ], ['ทำไมถึงแทำไมถึงแนะนำให้แปรงฟันวันละ 2 ครั้ง โดยเฉพาอน?', ' '], 
['ทำไมการแปรงฟันในตอนเช้าและก่อนนอนถึงสำคัญ?',' '],['เหตุผลที่ต้องแปรงฟันทั้งตอนเช้าและก่อนนอนคืออะไร?',' '],
['ทำไมควรแปรงฟันวันละ 2 ครั้งในตอนเช้าและก่อนนอน?',' '],['ทำไมถึงต้องแปรงฟันก่อนนอนและตอนเช้าในทุก ๆ วัน?',' ']
['ทำไมการแปรงฟัน 2 ครั้งต่อวันจึงแนะนำ โดยเฉพาะตอนเช้าและก่อนนอน?',' '],['เพราะอะไรการแปรงฟันก่อนนอนและตอนเช้าถึงเป็นเรื่องจำเป็น?',' ']
['การแปรงฟันตอนเช้าและก่อนนอนสำคัญต่อสุขภาพฟันอย่างไร?',' '],['ทำไมแปรงฟันวันละ 2 ครั้งต้องทำตอนเช้าและก่อนเข้านอน?',' ']
['เพราะเหตุใดต้องแปรงฟันตอนเช้าและก่อนนอนทุกวัน?',' '],['การแปรงฟันวันละ 2 ครั้งในตอนเช้าและก่อนนอนมีประโยชน์อะไร?',' ']
['ทำไมการแปรงฟันในช่วงเช้าและก่อนนอนถึงมีความสำคัญมาก?',' '],['แปรงฟันตอนเช้าและก่อนนอนช่วยอะไร ทำไมต้องทำวันละ 2 ครั้ง?',' ']
['เพราะอะไรการแปรงฟันวันละ 2 ครั้งถึงเน้นในช่วงเช้าและก่อนนอน?',' '],['ทำไมต้องแปรงฟันในช่วงเช้าและก่อนนอนทุกวัน?',' ']
['การแปรงฟันตอนเช้าและก่อนนอนช่วยรักษาสุขภาพช่องปากอย่างไร?',' '],['ทำไมจึงควรแปรงฟันตอนเช้าและก่อนนอนวันละ 2 ครั้ง?',' ']]
df = pd.DataFrame(data, columns = ['question', 'answer'])
#Step 2: Create vectors from the text
text = df['question']
encoder = SentenceTransformer("paraphrase-mpnet-base-v2")
vectors = encoder.encode(text)
#Step 3: Build a FAISS index from the vectors
vector_dimension = vectors.shape[1]
index = faiss.IndexFlatL2(vector_dimension)
faiss.normalize_L2(vectors)
index.add(vectors)
#Step 4: Create a search vector
search_text = 'ทำไมต้องแปรงฟันวันละ 2 ครั้ง ตอนเช้าและก่อนนอน'
search_vector = encoder.encode(search_text)
_vector = np.array([search_vector])
faiss.normalize_L2(_vector)
#Step 5: Search
k = index.ntotal
distances, ann = index.search(_vector, k=k)
results = pd.DataFrame({'distances': distances[0], 'ann': ann[0]})
#Step 6: Sort search results
labels  = df['answer']
Sentence = text[ann[0][0]]
category = labels[ann[0][0]]
print(results)
print(Sentence+":"+category)
