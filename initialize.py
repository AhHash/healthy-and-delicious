from models import db, Food, Review, User, Config
from app import app
import random
import hashlib
import os

# Expanded list of Arabic food names and descriptions
foods = {
    "chicken_curry": [
        {
            "name": "كاري الدجاج بالكريمة",
            "description": "طبق دجاج كاري غني بالكريمة الطازجة.",
            "image": "1.jpg",
            "price": 35,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": False,
        },
        {
            "name": "كاري الدجاج الهندي",
            "description": "دجاج كاري حار بنكهة البهارات الهندية.",
            "image": "2.jpg",
            "price": 30,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": False,
        },
        {
            "name": "كاري الدجاج بالأعشاب",
            "description": "طبق دجاج كاري محضر بأعشاب طازجة.",
            "image": "3.jpg",
            "price": 32,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": True,
        },
        {
            "name": "كاري الدجاج بالنارجيل",
            "description": "كاري دجاج مميز بصلصة جوز الهند.",
            "image": "4.jpg",
            "price": 38,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": False,
        },
    ],
    "falafel": [
        {
            "name": "فلافل بالطحينة",
            "description": "فلافل مقرمشة تقدم مع صلصة الطحينة.",
            "image": "1.jpg",
            "price": 15,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": True,
        },
        {
            "name": "فلافل محشية بالخضار",
            "description": "كرات فلافل شهية محشوة بخضروات طازجة.",
            "image": "2.jpg",
            "price": 18,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": False,
        },
        {
            "name": "ساندويتش فلافل",
            "description": "ساندويتش فلافل لذيذ مع الخضار والمخللات.",
            "image": "3.jpg",
            "price": 20,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": True,
        },
        {
            "name": "طبق فلافل مشكل",
            "description": "طبق فلافل يقدم مع حمص ومقبلات.",
            "image": "4.jpg",
            "price": 22,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": True,
        },
    ],
    "greek_salad": [
        {
            "name": "سلطة يونانية بالجبنة",
            "description": "سلطة يونانية منعشة مع جبنة الفيتا.",
            "image": "1.jpg",
            "price": 25,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": True,
        },
        {
            "name": "سلطة يونانية بالخيار",
            "description": "سلطة يونانية طازجة بالخيار والطماطم.",
            "image": "2.jpg",
            "price": 22,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": True,
        },
        {
            "name": "سلطة يونانية بالزيتون",
            "description": "سلطة يونانية غنية بزيتون كالاماتا.",
            "image": "3.jpg",
            "price": 26,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": True,
        },
        {
            "name": "سلطة يونانية بزيت الزيتون",
            "description": "سلطة يونانية تقدم بزيت الزيتون البكر.",
            "image": "4.jpg",
            "price": 24,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": False,
        },
    ],
    "omelette": [
        {
            "name": "أومليت بالخضار",
            "description": "أومليت محضر بخضار طازجة ولذيذة.",
            "image": "1.jpg",
            "price": 18,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": False,
        },
        {
            "name": "أومليت بالجبنة",
            "description": "أومليت غني محشو بالجبنة الذائبة.",
            "image": "2.jpg",
            "price": 20,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": True,
        },
        {
            "name": "أومليت بالفطر",
            "description": "أومليت لذيذ مع قطع من الفطر الطازج.",
            "image": "3.jpg",
            "price": 19,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": False,
        },
        {
            "name": "أومليت بالأعشاب",
            "description": "أومليت خفيف بنكهة الأعشاب الطازجة.",
            "image": "4.jpg",
            "price": 17,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": True,
        },
    ],
    "steak": [
        {
            "name": "ستيك مشوي على الفحم",
            "description": "شريحة لحم مشوية بنكهة الفحم.",
            "image": "1.jpg",
            "price": 50,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": False,
        },
        {
            "name": "ستيك بصلصة الفلفل الأسود",
            "description": "ستيك طري مع صلصة الفلفل الأسود.",
            "image": "2.jpg",
            "price": 55,
            "diabetic_friendly": True,
            "high_blood_pressure_friendly": False,
        },
        {
            "name": "ستيك مع الخضار المشوية",
            "description": "ستيك يقدم مع تشكيلة من الخضار المشوية.",
            "image": "3.jpg",
            "price": 58,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": True,
        },
        {
            "name": "ستيك بصلصة المشروم",
            "description": "ستيك فاخر مع صلصة المشروم الكريمية.",
            "image": "4.jpg",
            "price": 60,
            "diabetic_friendly": False,
            "high_blood_pressure_friendly": False,
        },
    ],
}


# Sample data for generating random users
names = {
    "أحمد": "Ahmed",
    "ليلى": "Laila",
    "عمر": "Omar",
    "سارة": "Sara",
    "محمد": "Mohamed",
    "خالد": "Khaled",
    "نورة": "Noura",
    "فيصل": "Faisal",
    "منى": "Mona",
    "عبدالله": "Abdalla",
}

medical_conditions = ["healthy", "diabetic", "hypertension"]


# Password hashing function for simple random password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Directory where food images are stored
image_directory = "./static/img/food_img"


def get_image_path(folder_name, image_name):
    """Return the full path to an image in a given folder."""
    return f"{image_directory}/{folder_name}/{image_name}"


# Utility function to check if data population is required
def get_or_create_config(key):
    config = Config.query.filter_by(key=key).first()
    if not config:
        config = Config(key=key, value=False)
        db.session.add(config)
        db.session.commit()
    return config


# Add data if not already added
with app.app_context():
    # Check if food items are added
    food_flag = get_or_create_config("food_added")
    if not food_flag.value:
        # Loop through each food category and add each dish to the database
        for category, dishes in foods.items():
            for dish in dishes:
                # Construct the image path for each dish
                image_path = get_image_path(category, dish["image"])

                # Create a Food instance for each dish
                food = Food(
                    name=dish["name"],
                    description=dish["description"],
                    price=dish["price"],
                    diabetic_friendly=dish["diabetic_friendly"],
                    high_blood_pressure_friendly=dish["high_blood_pressure_friendly"],
                    image=image_path,
                )
                db.session.add(food)

        db.session.commit()
        food_flag.value = True
        db.session.commit()
        print("Fixed food items with specific images added to the database.")

    # Adding random users
    user_flag = get_or_create_config("user_added")
    if not user_flag.value:
        for i in range(25):  # Add 25 random users
            name = random.choice(list(names.keys()))
            email = f"{names[name].lower()}{i}{i}{i}@example.com"
            password = hash_password(names[name].lower())  # Use a generic password
            age = random.randint(18, 70)
            medical_condition = random.choice(medical_conditions)

            user = User(
                name=name,
                email=email,
                password=password,
                age=age,
                medical_condition=medical_condition,
            )

            db.session.add(user)

        db.session.commit()
        user_flag.value = True
        db.session.commit()
        print("Some random users added to the database.")

    # Check if reviews are added
    review_flag = get_or_create_config("reviews_added")
    if not review_flag.value:
        users = User.query.all()
        for _ in range(10):  # Add 500 reviews
            user = random.choice(users)
            stars_count = random.randint(3, 5)
            review_text = random.choice(
                [
                    "طعام رائع، سأطلب مرة أخرى بالتأكيد!",
                    "التوصيل سريع والطعام ممتاز!",
                    "أسعار مناسبة وخدمة ممتازة.",
                    "لم يكن الطعام كما توقعت، ولكن كان جيداً.",
                    "التجربة كانت رائعة! الطعام لذيذ!",
                ]
            )
            review = Review(user_id=user.id, stars_count=stars_count, text=review_text)
            db.session.add(review)
        db.session.commit()
        review_flag.value = True
        db.session.commit()
        print("10 random reviews added to the database.")
