from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for session

# -------- MySQL connection --------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="11223_11223",  # replace with your MySQL password
    database="food_order_db"   # replace with your DB name
)
cursor = db.cursor()

# -------- Sample Food Items --------
item1 = {"name": "Cheese Burger", "price": 149, "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd"}
item2 = {"name": "Veg Pizza", "price": 299, "img": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"}
item3 = {"name": "White Sauce Pasta", "price": 199, "img": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d"}
item4 = {"name": "French Fries", "price": 99, "img": "https://images.unsplash.com/photo-1563379091339-03246963d96c"}

# -------- ROUTES --------

@app.route('/')
def home():
    # Render index.html with individual variables
    return render_template('index.html', item1=item1, item2=item2, item3=item3, item4=item4)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    food_name = request.form['food_name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    # Initialize cart
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']

    # Check if item already in cart
    for item in cart:
        if item['food_name'] == food_name:
            item['quantity'] += quantity
            break
    else:
        cart.append({'food_name': food_name, 'price': price, 'quantity': quantity})

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_bill = sum(item['price'] * item['quantity'] for item in cart_items)

    # Assign individual items (for separate-variable approach)
    cart1 = cart_items[0] if len(cart_items) >= 1 else None
    cart2 = cart_items[1] if len(cart_items) >= 2 else None
    cart3 = cart_items[2] if len(cart_items) >= 3 else None
    cart4 = cart_items[3] if len(cart_items) >= 4 else None

    return render_template('cart.html', cart=cart_items, cart1=cart1, cart2=cart2, cart3=cart3, cart4=cart4, total_bill=total_bill)

@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    name = request.form['name']
    gmail = request.form['gmail']

    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('home'))

    # Insert customer if not exists
    cursor.execute("SELECT customer_id FROM customers WHERE gmail=%s", (gmail,))
    result = cursor.fetchone()
    if result:
        customer_id = result[0]
    else:
        cursor.execute("INSERT INTO customers (name, gmail) VALUES (%s, %s)", (name, gmail))
        db.commit()
        customer_id = cursor.lastrowid

    # Insert order
    ordered_items = ', '.join([f"{item['food_name']} x{item['quantity']}" for item in cart_items])
    total_bill = sum(item['price'] * item['quantity'] for item in cart_items)

    cursor.execute(
        "INSERT INTO orders (customer_id, ordered_items, total_bill) VALUES (%s, %s, %s)",
        (customer_id, ordered_items, total_bill)
    )
    db.commit()

    # Clear cart
    session.pop('cart', None)

    return render_template('success.html',
                           name=name,
                           ordered_items=ordered_items,
                           total_bill=total_bill,
                           date=datetime.now().strftime("%d %B %Y"))

# -------- RUN APP --------
if __name__ == '__main__':
    app.run(debug=True)
