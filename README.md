Simple Flask app for the Fetch Rewards [receipt-processor-challenge](https://github.com/fetch-rewards/receipt-processor-challenge).

```bash
# Build the image
docker build -t receipt-processor .

# Run the container
docker run -p 5000:5000 receipt-processor

# /receipts/{id}/points
curl http://localhost:5000/receipts/<receipt-id>/points

# /receipts/process
curl -X POST http://localhost:5000/receipts/process \
     -H "Content-Type: application/json" \
     -d @sample-receipt.json

