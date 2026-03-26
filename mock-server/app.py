from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Load customer data from JSON file
def load_customers():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')
    with open(json_path, 'r') as f:
        return json.load(f)

CUSTOMERS = load_customers()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get paginated list of customers"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Calculate pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        paginated_customers = CUSTOMERS[start_idx:end_idx]
        
        return jsonify({
            "data": paginated_customers,
            "total": len(CUSTOMERS),
            "page": page,
            "limit": limit
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get single customer by ID"""
    try:
        customer = next((c for c in CUSTOMERS if c['customer_id'] == customer_id), None)
        
        if not customer:
            return jsonify({"error": f"Customer {customer_id} not found"}), 404
        
        return jsonify(customer), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
