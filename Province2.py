from flask import Flask, request, jsonify
from rapidfuzz import process, fuzz



correct_provinces  = ["กรุงเทพมหานคร","สมุทรปราการ","นนทบุรี","ปทุมธานี","พระนครศรีอยุธยา","อ่างทอง","ลพบุรี","สิงห์บุรี","ชัยนาท","สระบุรี","ชลบุรี","ระยอง","จันทบุรี","ตราด","ฉะเชิงเทรา","ปราจีนบุรี","นครนายก","สระแก้ว","นครราชสีมา","บุรีรัมย์","สุรินทร์","ศรีสะเกษ","อุบลราชธานี","ยโสธร","ชัยภูมิ","อำนาจเจริญ","หนองบัวลำภู","ขอนแก่น","อุดรธานี","เลย","หนองคาย","มหาสารคาม","ร้อยเอ็ด","กาฬสินธุ์","สกลนคร","นครพนม","มุกดาหาร","เชียงใหม่","ลำพูน","ลำปาง","อุตรดิตถ์","แพร่","น่าน","พะเยา","เชียงราย","แม่ฮ่องสอน","นครสวรรค์","อุทัยธานี","กำแพงเพชร","ตาก","สุโขทัย","พิษณุโลก","พิจิตร","เพชรบูรณ์","ราชบุรี","กาญจนบุรี","สุพรรณบุรี","นครปฐม","สมุทรสาคร","สมุทรสงคราม","เพชรบุรี","ประจวบคีรีขันธ์","นครศรีธรรมราช","กระบี่","พังงา","ภูเก็ต","สุราษฎร์ธานี","ระนอง","ชุมพร","สงขลา","สตูล","ตรัง","พัทลุง","ปัตตานี","ยะลา","นราธิวาส","บึงกาฬ","Bangkok","Samut Prakan","Nonthaburi","Pathum Thani","Phra Nakhon Si Ayutthaya","Ang Thong","Loburi","Sing Buri","Chai Nat","Saraburi","Chon Buri","Rayong","Chanthaburi","Trat","Chachoengsao","Prachin Buri","Nakhon Nayok","Sa Kaeo","Nakhon Ratchasima","Buri Ram","Surin","Si Sa Ket","Ubon Ratchathani","Yasothon","Chaiyaphum","Amnat Charoen","Nong Bua Lam Phu","Khon Kaen","Udon Thani","Loei","Nong Khai","Maha Sarakham","Roi Et","Kalasin","Sakon Nakhon","Nakhon Phanom","Mukdahan","Chiang Mai","Lamphun","Lampang","Uttaradit","Phrae","Nan","Phayao","Chiang Rai","Mae Hong Son","Nakhon Sawan","Uthai Thani","Kamphaeng Phet","Tak","Sukhothai","Phitsanulok","Phichit","Phetchabun","Ratchaburi","Kanchanaburi","Suphan Buri","Nakhon Pathom","Samut Sakhon","Samut Songkhram","Phetchaburi","Prachuap Khiri Khan","Nakhon Si Thammarat","Krabi","Phangnga","Phuket","Surat Thani","Ranong","Chumphon","Songkhla","Satun","Trang","Phatthalung","Pattani","Yala","Narathiwat","buogkan"
]

app = Flask(__name__)

def check_province_name(input_name):
    # Use fuzz.ratio as the similarity scorer
    closest_match = process.extractOne(input_name, correct_provinces, scorer=fuzz.ratio)
    match_name, match_score = closest_match[0], closest_match[1]
    
    if match_score >= 55:  # Threshold for similarity
        return {"result": "correct", "province": match_name, "score": match_score}
    else:
        return {"result": "misspelled", "province": "ไม่มีข้อมูล", "score": match_score}

@app.route('/check_province', methods=['GET'])
def check_misspelling():
    input_name = request.args.get('province_name', '').strip()  # Get 'province_name' from query parameters
    
    if not input_name:
        return jsonify({"error": "province_name query parameter is required"}), 400

    result = check_province_name(input_name)
    response = jsonify(result)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


if __name__ == '__main__':
    app.run(debug=True, port=8080)

