from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash,
    jsonify,
)
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Food, Order, OrderItem, Review, CartItem
from functools import wraps


app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Initialize data in the tables
import initialize


# Decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            # Redirect to login page if user is not logged in
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Landing Route
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/homepage")
@login_required
def homepage():
    # Get filter parameters
    search = request.args.get("search", "")
    diabetic = request.args.get("diabetic", "false") == "true"
    high_blood_pressure = request.args.get("high_blood_pressure", "false") == "true"

    # Start with the base query
    query = Food.query

    # Apply filters if present
    if search:
        query = query.filter(Food.name.contains(search))
    if diabetic:
        query = query.filter(Food.diabetic_friendly.is_(True))
    if high_blood_pressure:
        query = query.filter(Food.high_blood_pressure_friendly.is_(True))

    # Fetch the filtered results
    food_items = query.order_by(db.func.random()).limit(20).all()

    # Check if it's an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("partials/food_grid.html", food_items=food_items)

    return render_template("homepage.html", food_items=food_items)


@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    user_id = session.get("user_id")

    data = request.json
    food_id = data.get("food_id")

    if not food_id or not user_id:
        return jsonify({"error": "معرف الغذاء أو معرف المستخدم مفقود"}), 400

    # Create a new CartItem
    new_cart_item = CartItem(user_id=user_id, food_id=food_id)
    db.session.add(new_cart_item)
    db.session.commit()

    return jsonify({"message": "تم إضافة السلعة إلى سلة التسوق"}), 200


@app.route("/cart", methods=["GET"])
@login_required
def cart():
    # Check if the user is logged in by confirming user_id in session
    user_id = session.get("user_id")

    # Query the cart items for the specific user
    cart_items = (
        db.session.query(CartItem, Food)
        .join(Food, CartItem.food_id == Food.id)
        .filter(CartItem.user_id == user_id)
        .all()
    )

    # Calculate the total amount for items in the cart
    total_amount = sum(food.price for _, food in cart_items)

    # Pass cart items and total amount to the template
    return render_template(
        "cart.html", cart_items=cart_items, total_amount=total_amount
    )


@app.route("/place_order", methods=["POST"])
@login_required
def place_order():
    user_id = session.get("user_id")
    if not user_id:
        flash("يجب عليك تسجيل الدخول لتقديم الطلب")
        return redirect(url_for("login"))

    # Retrieve all cart items for the user
    cart_items = db.session.query(CartItem).filter_by(user_id=user_id).all()

    if not cart_items:
        flash("سلة التسوق الخاصة بك فارغة")
        return redirect(url_for("cart"))

    # Create a new Order for the user
    new_order = Order(user_id=user_id)
    db.session.add(new_order)
    db.session.flush()  # Flush to get the new_order ID without committing

    # Create OrderItems for each item in the cart
    for cart_item in cart_items:
        order_item = OrderItem(order_id=new_order.id, food_id=cart_item.food_id)
        db.session.add(order_item)

    # Commit the new order and its items to the database
    db.session.commit()

    # Clear the user's cart after placing the order
    db.session.query(CartItem).filter_by(user_id=user_id).delete()
    db.session.commit()

    flash("لقد تم وضع طلبك بنجاح")
    return redirect(url_for("orders"))  # Redirect to orders page to view past orders


@app.route("/orders")
@login_required
def orders():
    user_id = session.get("user_id")
    if not user_id:
        flash("الرجاء تسجيل الدخول لعرض طلباتك")
        return redirect(url_for("login"))

    # Query to fetch all orders for the logged-in user
    user_orders = db.session.query(Order).filter_by(user_id=user_id).all()

    # Create a structured dictionary with order details
    orders_data = []
    for order in user_orders:
        order_items = []
        for item in order.items:
            food_item = db.session.query(Food).filter_by(id=item.food_id).first()
            order_items.append(
                {
                    "name": food_item.name,
                    "quantity": 1,
                    "image": food_item.image,
                    "price": food_item.price,
                }
            )
        order_items = order_items[:3]

        orders_data.append(
            {
                "order_id": order.id,
                "date": order.date_created.strftime(
                    "%Y-%m-%d"
                ),  # Assuming you have a date_created column
                "status": "مكتمل",  # Adjust this based on your Order model
                "order_items": order_items,
                "total_price": sum(item["price"] for item in order_items),
            }
        )

        print(orders_data)

    return render_template("orders.html", orders=orders_data)


@app.route("/submit_review", methods=["POST"])
def submit_review():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    stars_count = data.get("stars_count")
    text = data.get("text")

    # Check if both stars and text are provided
    if not stars_count or not text:
        return jsonify({"error": "Rating and comment are required"}), 400

    user_id = session["user_id"]

    # Create and save new review
    review = Review(user_id=user_id, stars_count=stars_count, text=text)
    db.session.add(review)
    db.session.commit()

    return jsonify({"message": "Review submitted successfully"}), 200


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("homepage"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        age = request.form["age"]
        medical_condition = request.form["status"]

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            flash("البريد الإلكتروني مسجل بالفعل", "error")
            return render_template("signup.html")

        # Hash password and create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            age=age,
            medical_condition=medical_condition,
        )

        db.session.add(new_user)
        db.session.commit()

        # Set session for the logged-in user
        session["user_id"] = new_user.id
        session["user_name"] = new_user.name

        return redirect(url_for("homepage"))

    return render_template("signup.html")


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if user is already logged in
    if session.get("user_id"):
        return redirect(url_for("homepage"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Find the user in the database
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # Set session variables for the logged-in user
            session["user_id"] = user.id
            session["user_name"] = user.name
            return redirect(url_for("homepage"))
        else:
            flash("البريد الإلكتروني أو كلمة المرور غير صالحة", "error")

    return render_template("login.html")


# Logout Route
@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for("index"))


@app.route("/reviews")
def reviews():
    # Query random reviews from the database
    reviews = (
        Review.query.order_by(db.func.random()).limit(10).all()
    )  # Randomly selects 10 reviews
    return render_template("reviews.html", reviews=reviews)


if __name__ == "__main__":
    app.run(debug=True)
