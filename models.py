from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    medical_condition = db.Column(
        db.String(50), nullable=False
    )  # 'healthy', 'diabetic', etc.

    # Relationships
    orders = db.relationship("Order", back_populates="user")
    reviews = db.relationship("Review", back_populates="user")
    cart_items = db.relationship("CartItem", back_populates="user")


class Food(db.Model):
    __tablename__ = "foods"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    diabetic_friendly = db.Column(db.Boolean, default=False)
    high_blood_pressure_friendly = db.Column(db.Boolean, default=False)

    # Relationships
    order_items = db.relationship("OrderItem", back_populates="food")
    cart_items = db.relationship("CartItem", back_populates="food")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date_created = db.Column(db.DateTime, default=func.now(), nullable=False)

    # Relationship with User
    user = db.relationship("User", back_populates="orders")

    # Many-to-many relationship with Food through OrderItem
    items = db.relationship("OrderItem", back_populates="order")


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id"))

    # Relationships
    order = db.relationship("Order", back_populates="items")
    food = db.relationship("Food", back_populates="order_items")


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    stars_count = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text)

    # Relationship with User
    user = db.relationship("User", back_populates="reviews")


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id"))

    # Relationships
    user = db.relationship("User", back_populates="cart_items")
    food = db.relationship("Food", back_populates="cart_items")


class Config(db.Model):
    __tablename__ = "config"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Boolean, default=False)
