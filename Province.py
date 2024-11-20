from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Step 1: Create a dataframe with only the text column using a single array list
data = ["กรุงเทพมหานคร","สมุทรปราการ","นนทบุรี","ปทุมธานี","พระนครศรีอยุธยา","อ่างทอง","ลพบุรี","สิงห์บุรี","ชัยนาท","สระบุรี","ชลบุรี","ระยอง","จันทบุรี","ตราด","ฉะเชิงเทรา","ปราจีนบุรี","นครนายก","สระแก้ว","นครราชสีมา","บุรีรัมย์","สุรินทร์","ศรีสะเกษ","อุบลราชธานี","ยโสธร","ชัยภูมิ","อำนาจเจริญ","หนองบัวลำภู","ขอนแก่น","อุดรธานี","เลย","หนองคาย","มหาสารคาม","ร้อยเอ็ด","กาฬสินธุ์","สกลนคร","นครพนม","มุกดาหาร","เชียงใหม่","ลำพูน","ลำปาง","อุตรดิตถ์","แพร่","น่าน","พะเยา","เชียงราย","แม่ฮ่องสอน","นครสวรรค์","อุทัยธานี","กำแพงเพชร","ตาก","สุโขทัย","พิษณุโลก","พิจิตร","เพชรบูรณ์","ราชบุรี","กาญจนบุรี","สุพรรณบุรี","นครปฐม","สมุทรสาคร","สมุทรสงคราม","เพชรบุรี","ประจวบคีรีขันธ์","นครศรีธรรมราช","กระบี่","พังงา","ภูเก็ต","สุราษฎร์ธานี","ระนอง","ชุมพร","สงขลา","สตูล","ตรัง","พัทลุง","ปัตตานี","ยะลา","นราธิวาส","บึงกาฬ","B"]
df = pd.DataFrame(data, columns=['text'])


# Step 2: Create vectors from the text
text = df['text']
encoder = SentenceTransformer("kornwtp/simcse-model-wangchanberta")
vectors = encoder.encode(text)

# Step 3: Build a FAISS index from the vectors
vector_dimension = vectors.shape[1]
index = faiss.IndexFlatL2(vector_dimension)
faiss.normalize_L2(vectors)
index.add(vectors)

# Step 4: Search function
def search_in_index(search_text):
    # Encode the search query into a vector
    search_vector = encoder.encode(search_text)
    _vector = np.array([search_vector])
    faiss.normalize_L2(_vector)
    
    # Perform search
    k = index.ntotal  # k is set to the total number of items in the index
    distances, ann = index.search(_vector, k=k)
    
    # Retrieve and return the closest text result
    closest_text = text.iloc[ann[0][0]]  # Get the text from the dataframe based on the closest index
    return closest_text

# Step 5: Define API route for search
@app.route('/search', methods=['GET'])
def search():
    # Get the 'query' parameter from the URL
    search_text = request.args.get('query')
    
    if not search_text:
        return jsonify({'error': 'Query parameter is required'}), 400

    # Search and get closest text match
    result = search_in_index(search_text)
    
    return jsonify({'search_text': search_text, 'closest_text': result})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'success', 'message': 'Service is running'}), 200


# Step 6: Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=8080)
