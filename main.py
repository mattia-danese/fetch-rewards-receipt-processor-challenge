import math
import uuid
import json
import hashlib

from http import HTTPStatus
from flask import Flask, request, jsonify

db_scores = {} # receipt id -> receipt score
receipt_hashes = {} # receipt hash -> receipt id

def bad_request_error():
    return {
        "status": HTTPStatus.BAD_REQUEST,
        "message": "The receipt is invalid"
    }

def not_found_error():
    return {
        "status": HTTPStatus.NOT_FOUND,
        "message": "No receipt found for that ID."
    }

app = Flask(__name__)

@app.route("/receipts/process", methods=["POST"])
def process_receipt():
    try:
        receipt, score = request.get_json(), 0

        # checking if score for receipt was already computed
        receipt_str = json.dumps(receipt, sort_keys=True)
        receipt_hash = hashlib.sha256(receipt_str.encode('utf-8')).hexdigest()
        
        if receipt_hash in receipt_hashes:
            return jsonify({"id": receipt_hashes[receipt_hash]}), HTTPStatus.OK

        # 1 point for every alphanumeric character in the retailer name.
        score += sum(c.isalnum() for c in receipt["retailer"])
        
        # 50 points if the total is a round dollar amount with no cents.
        if receipt["total"].endswith("00"):
            score += 50
        
        # 25 points if the total is a multiple of 0.25
        if float(receipt["total"]) % 0.25 == 0:
            score += 25

        # 5 points for every two items on the receipt.
        score += (len(receipt["items"]) // 2) * 5
        
        # If the trimmed length of the item description is a multiple of 3, 
        # multiply the price by 0.2 and round up to the nearest integer. 
        # The result is the number of points earned.
        for item in receipt["items"]:
            if len(item["shortDescription"].strip()) % 3 == 0:
                score += math.ceil(float(item["price"]) * 0.2)

        # 6 points if the day in the purchase date is odd.
        if int(receipt["purchaseDate"].split("-")[2]) % 2 != 0:
            score += 6

        # 10 points if the time of purchase is after 2:00pm and before 4:00pm.
        time = int(receipt["purchaseTime"].replace(":", ""))
        if time >= 1401 and time <= 1559:
            score += 10
        
        # adding receipt score and receipt hash to database
        receipt_id = str(uuid.uuid4())
        
        db_scores[receipt_id] = int(score)
        receipt_hashes[receipt_hash] = receipt_id

        return jsonify({"id": receipt_id}), HTTPStatus.OK
    except:
        return jsonify(bad_request_error()), HTTPStatus.BAD_REQUEST

@app.route("/receipts/<id>/points")
def get_score(id):
    if id not in db_scores:
        return jsonify(not_found_error()), HTTPStatus.NOT_FOUND
    
    return jsonify({"points": db_scores[id]}), HTTPStatus.OK

if __name__ == "__main__":
    app.run(debug=True)