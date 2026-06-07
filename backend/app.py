from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Allow HTML frontend to call this API

# ============ CONFIG ============
GROK_API_KEY = os.environ.get("GROK_API_KEY", "your-grok-api-key-here")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# ============ PRODUCTS DATA ============
PRODUCTS = [
    {"id":1,"dept":"women","name":"Floral Wrap Dress","brand":"Fabindia","category":"Dresses","price":1299,"mrp":2499,"rating":4.5,"reviews":128,"badge":"Bestseller","stock":45},
    {"id":2,"dept":"women","name":"Baby Pink Sling Bag","brand":"Lavie","category":"Bags","price":799,"mrp":1499,"rating":4.3,"reviews":89,"badge":"New","stock":120},
    {"id":3,"dept":"women","name":"White Cotton Frock","brand":"Global Desi","category":"Dresses","price":899,"mrp":1799,"rating":4.6,"reviews":203,"badge":"Hot","stock":67},
    {"id":4,"dept":"women","name":"Banarasi Silk Saree","brand":"Sundari Silks","category":"Ethnic Wear","price":2799,"mrp":5499,"rating":4.8,"reviews":312,"badge":"Premium","stock":30},
    {"id":5,"dept":"women","name":"Pearl Drop Earrings","brand":"Zaveri Pearls","category":"Accessories","price":499,"mrp":999,"rating":4.4,"reviews":167,"badge":"New","stock":200},
    {"id":6,"dept":"men","name":"Classic Oxford Shirt","brand":"Arrow","category":"Shirts","price":999,"mrp":1799,"rating":4.5,"reviews":189,"badge":"Bestseller","stock":78},
    {"id":7,"dept":"men","name":"Slim Fit Chinos","brand":"US Polo","category":"Trousers","price":1299,"mrp":2499,"rating":4.4,"reviews":134,"badge":"","stock":55},
    {"id":8,"dept":"men","name":"Men's Running Shoes","brand":"Nike","category":"Footwear","price":1899,"mrp":3499,"rating":4.7,"reviews":456,"badge":"Top Rated","stock":42},
    {"id":9,"dept":"kids","name":"Kids Floral Frock","brand":"H&M Kids","category":"Kids Wear","price":499,"mrp":999,"rating":4.6,"reviews":88,"badge":"New","stock":80},
    {"id":10,"dept":"kids","name":"Kids School Bag","brand":"Wildcraft","category":"Bags","price":699,"mrp":1299,"rating":4.5,"reviews":143,"badge":"Bestseller","stock":55},
    {"id":11,"dept":"home","name":"Macramé Wall Hanging","brand":"Craftly","category":"Home Decor","price":799,"mrp":1499,"rating":4.7,"reviews":210,"badge":"Trending","stock":40},
    {"id":12,"dept":"home","name":"Scented Soy Candles Set","brand":"Aroma Bliss","category":"Home Decor","price":449,"mrp":799,"rating":4.8,"reviews":320,"badge":"Hot","stock":200},
    {"id":13,"dept":"women","name":"Vitamin C Serum","brand":"Minimalist","category":"Beauty","price":399,"mrp":699,"rating":4.7,"reviews":870,"badge":"Bestseller","stock":500},
    {"id":14,"dept":"men","name":"Wireless Earbuds","brand":"boAt","category":"Electronics","price":1299,"mrp":2999,"rating":4.5,"reviews":1240,"badge":"Bestseller","stock":350},
    {"id":15,"dept":"women","name":"Matte Lipstick Set","brand":"Lakme","category":"Beauty","price":449,"mrp":799,"rating":4.6,"reviews":734,"badge":"Hot","stock":600},
]

# ============ ROUTES ============

# Home route
@app.route('/')
def home():
    return jsonify({
        "message": "Lucky Shop API is running!",
        "version": "1.0",
        "endpoints": [
            "/api/products",
            "/api/products/<id>",
            "/api/products/search?q=dress&dept=women&max_price=1500",
            "/api/orders",
            "/api/chat"
        ]
    })

# GET all products
@app.route('/api/products', methods=['GET'])
def get_products():
    dept     = request.args.get('dept', '')
    category = request.args.get('category', '')
    max_price= request.args.get('max_price', type=int)

    result = PRODUCTS.copy()

    if dept:
        result = [p for p in result if p['dept'] == dept]
    if category:
        result = [p for p in result if p['category'].lower() == category.lower()]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]

    return jsonify({
        "total": len(result),
        "products": result
    })

# GET single product
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)

# Search products
@app.route('/api/products/search', methods=['GET'])
def search_products():
    q         = request.args.get('q', '').lower()
    dept      = request.args.get('dept', '')
    max_price = request.args.get('max_price', type=int)

    result = PRODUCTS.copy()

    if q:
        result = [p for p in result if
                  q in p['name'].lower() or
                  q in p['brand'].lower() or
                  q in p['category'].lower()]
    if dept:
        result = [p for p in result if p['dept'] == dept]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]

    return jsonify({
        "query": q,
        "total": len(result),
        "products": result
    })

# GET orders summary (stats)
@app.route('/api/orders/stats', methods=['GET'])
def order_stats():
    # This returns mock stats — connect to Firebase if needed
    return jsonify({
        "total_orders": 0,
        "total_revenue": 0,
        "message": "Connect to Firebase Firestore for real order data"
    })

# Smart local reply when Grok API is unavailable
def smart_local_reply(message):
    msg = message.lower()
    if any(w in msg for w in ['dress','frock','saree','kurti','lehenga']):
        return "I love your style! 👗 Check out our Women's collection — we have Floral Wrap Dress (₹1299), Banarasi Silk Saree (₹2799), and Lehenga sets. Showing results below! ✨"
    elif any(w in msg for w in ['shirt','men','formal','blazer','chino']):
        return "Great choice! 👔 Our Men's collection has Classic Oxford Shirt (₹999), Slim Fit Chinos (₹1299) and Formal Blazer (₹3499). Check them out below!"
    elif any(w in msg for w in ['kids','child','baby','school','toy']):
        return "Adorable picks for your little ones! 🎒 We have Kids Floral Frock (₹499), School Bag (₹699) and fun toys. Showing below!"
    elif any(w in msg for w in ['home','decor','candle','planter','pillow']):
        return "Transform your space! 🏠 Our Home Decor section has Macramé Wall Hanging (₹799), Scented Candles (₹449) and Ceramic Planters. Check below!"
    elif any(w in msg for w in ['beauty','serum','lipstick','cream','skincare']):
        return "Glow up! 💄 We have Vitamin C Serum by Minimalist (₹399) and Lakme Matte Lipstick Set (₹449). Your skin will thank you! ✨"
    elif any(w in msg for w in ['shoe','footwear','sneaker','sandal','heel']):
        return "Step in style! 👟 Nike Running Shoes (₹1899), White Adidas Sneakers (₹1799) and Block Heel Sandals (₹1499) are trending now!"
    elif any(w in msg for w in ['bag','purse','wallet','handbag']):
        return "Bag it up! 👜 Baby Pink Sling Bag by Lavie (₹799) and Leather Wallet by Woodland (₹699) are customer favourites!"
    elif any(w in msg for w in ['earphone','earbud','electronics','phone','gadget']):
        return "Tech lover! 📱 boAt Wireless Earbuds (₹1299) are our bestseller with 1240+ reviews. Great value!"
    elif any(w in msg for w in ['cheap','budget','under','affordable','less than']):
        return "Budget shopping! 💰 We have great options under ₹500 — Pearl Earrings (₹499), Kids Frock (₹499), Candles (₹449). Showing affordable picks below!"
    elif any(w in msg for w in ['gift','gifting','present','someone']):
        return "Perfect gifting ideas! 🎁 Scented Candles Set (₹449), Pearl Earrings (₹499), or Vitamin C Serum (₹399) make wonderful gifts!"
    elif any(w in msg for w in ['wedding','party','occasion','festival']):
        return "Dress to impress! 💍 For weddings we have Banarasi Silk Saree (₹2799) and Lehenga Choli Set (₹2999). For parties, check our Strappy Maxi Dress (₹1199)!"
    else:
        return f"I'd love to help you find the perfect product! 🛍️ You can browse Women, Men, Kids, Home Decor or Beauty. What's your budget and style preference? ✨"

# ============ GROK AI CHAT ============
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "message is required"}), 400

    user_message = data['message']
    history      = data.get('history', [])  # previous messages

    # Build product context for Grok
    product_names = [f"{p['name']} by {p['brand']} (₹{p['price']}, {p['dept']})" for p in PRODUCTS]
    product_context = "\n".join(product_names[:20])

    system_prompt = f"""You are Lucky ✨, a friendly AI shopping assistant for Lucky Shop — 
an Indian e-commerce platform. Help users find products, give fashion advice, and suggest items.

Available products in our store:
{product_context}

Rules:
- Be warm, helpful, use occasional emojis
- Give concise replies (2-4 sentences)
- Suggest specific products from our store when relevant
- Mention prices in Indian Rupees (₹)
- If user asks for something not in store, suggest closest match"""

    # Build messages for Grok
    messages = [{"role": "system", "content": system_prompt}]

    # Add chat history
    for msg in history[-6:]:  # last 6 messages
        messages.append({
            "role": "user" if msg["role"] == "user" else "assistant",
            "content": msg["text"]
        })

    # Add current message
    messages.append({"role": "user", "content": user_message})

    # Call Grok API
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-3-latest",
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7
    }

    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            return jsonify({"reply": reply, "status": "success"})
        else:
            # Grok API failed — use smart local reply
            reply = smart_local_reply(user_message)
            return jsonify({"reply": reply, "status": "local"})

    except requests.exceptions.Timeout:
        return jsonify({"reply": "Sorry, I'm a bit slow right now! Try again 😊", "status": "timeout"})
    except Exception as e:
        reply = smart_local_reply(user_message)
        return jsonify({"reply": reply, "status": "local"})


# ============ RUN ============
if __name__ == '__main__':
    print("🚀 Lucky Shop Python Backend running!")
    print("📍 API: http://localhost:5000")
    app.run(debug=True, port=5000)
