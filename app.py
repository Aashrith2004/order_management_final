from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('RapidXcel.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route to display products
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT stock_id, stock_name, price, quantity FROM stocks').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Place order route (handles order preview and pin code validation)
@app.route('/place_order', methods=['POST'])
def place_order():
    # Get customer inputs
    delivery_address = request.form['delivery_address']
    pin_code = request.form['pin_code']
    phone_number = request.form['phone_number']

    # Validate pin code
    if not validate_pin_code(pin_code):
        return "Invalid Pin Code. We do not service this area."

    # Retrieve products and calculate total cost and update stock
    products = []
    total_cost = 0
    shipping_cost = 0
    conn = get_db_connection()

    for product in conn.execute('SELECT stock_id, stock_name, price, quantity FROM stocks'):
        # Get quantity ordered, default to 0 if not selected
        quantity_ordered = request.form.get(f'quantity_{product["stock_id"]}', type=int, default=0)

        # Only process the product if a valid quantity > 0 is entered
        if quantity_ordered > 0:
            total_cost += product['price'] * quantity_ordered
            products.append({
                'stock_name': product['stock_name'],
                'quantity_ordered': quantity_ordered,
                'price': product['price'],
                'total': product['price'] * quantity_ordered
            })
            # Decrease the stock quantity in the database
            conn.execute('UPDATE stocks SET quantity = quantity - ? WHERE stock_id = ?',
                         (quantity_ordered, product['stock_id']))
    
    # Calculate shipping cost based on pin code and total weight
    total_weight = sum([prod['quantity_ordered'] for prod in products])
    shipping_cost = calculate_shipping_cost(pin_code, total_weight)

    conn.commit()
    conn.close()

    # Show order preview
    return render_template('preview.html', products=products, total_cost=total_cost, shipping_cost=shipping_cost, 
                           delivery_address=delivery_address, pin_code=pin_code, phone_number=phone_number)

# Function to validate pin code
import requests

def validate_pin_code(pin_code):
    """
    Validates an Indian PIN code using the PostalPincode.in API.
    Returns True if the PIN code is valid, otherwise False.
    """
    try:
        response = requests.get(f'https://api.postalpincode.in/pincode/{pin_code}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data[0]['Status'] == "Success" and data[0]['PostOffice']:
                return True  # PIN code is valid
        return False  # PIN code is invalid
    except requests.exceptions.RequestException as e:
        print(f"Error validating PIN code: {e}")
        return False



def calculate_shipping_cost(pin_code, total_weight):
    # Define cost per kg based on location
    if pin_code.startswith("500"):  # Local
        cost_per_kg = 10
    elif pin_code.startswith("5"):  # Regional
        cost_per_kg = 15
    else:  # National or other
        cost_per_kg = 20

    # Calculate the total shipping cost
    return total_weight * cost_per_kg


# Confirm order route
@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    delivery_address = request.form['delivery_address']
    pin_code = request.form['pin_code']
    phone_number = request.form['phone_number']
    return render_template(
        'confirm_order.html',
        delivery_address=delivery_address,
        pin_code=pin_code,
        phone_number=phone_number
    )


if __name__ == '__main__':
    app.run(debug=True)
