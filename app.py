from datetime import datetime
import os
import shutil
import sqlite3
from urllib.parse import urlencode

from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "carwa-dev-secret")

APP_NAME = "CARWA"
LISTINGS_PER_PAGE = 6
HOME_FEATURED_CARS_LIMIT = 12
PRICE_FLOOR = 5000
PRICE_CEILING = 100000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_VERCEL = os.environ.get("VERCEL") == "1"
SOURCE_DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
DATABASE_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join("/tmp", "carwa_database.db") if IS_VERCEL else SOURCE_DATABASE_PATH,
)

if IS_VERCEL and os.path.exists(SOURCE_DATABASE_PATH) and not os.path.exists(DATABASE_PATH):
    shutil.copyfile(SOURCE_DATABASE_PATH, DATABASE_PATH)

UPLOAD_FOLDER = os.environ.get(
    "UPLOAD_FOLDER",
    os.path.join("/tmp", "carwa_uploads") if IS_VERCEL else "static/uploads",
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULT_ADMIN = {
    "username": "admin",
    "password": "carwa123",
}

ALL_CAR_BRANDS = [
    "Abarth",
    "Acura",
    "Aixam",
    "Alfa Romeo",
    "Aston Martin",
    "Audi",
    "BAIC",
    "Bentley",
    "Bestune",
    "BMW",
    "Borgward",
    "Brilliance",
    "Bugatti",
    "Buick",
    "BYD",
    "Cadillac",
    "Changan",
    "Chery",
    "Chevrolet",
    "Chrysler",
    "Citroen",
    "Cupra",
    "Dacia",
    "Daewoo",
    "Daihatsu",
    "Datsun",
    "Dodge",
    "Dongfeng",
    "Exeed",
    "Ferrari",
    "Fiat",
    "Fisker",
    "Ford",
    "Foton",
    "GAC",
    "Geely",
    "Genesis",
    "GMC",
    "Great Wall",
    "Haval",
    "Honda",
    "Hongqi",
    "Hummer",
    "Hyundai",
    "INEOS",
    "Infiniti",
    "Isuzu",
    "JAC",
    "Jaecoo",
    "Jaguar",
    "Jeep",
    "Jetour",
    "JMC",
    "Kaiyi",
    "Kia",
    "Koenigsegg",
    "Lada",
    "Lamborghini",
    "Lancia",
    "Land Rover",
    "Lexus",
    "Lincoln",
    "Lotus",
    "Lucid",
    "Mahindra",
    "Maserati",
    "Maybach",
    "Mazda",
    "McLaren",
    "Mercedes-Benz",
    "Mercury",
    "MG",
    "Mini",
    "Mitsubishi",
    "NIO",
    "Nissan",
    "Opel",
    "Pagani",
    "Peugeot",
    "Polestar",
    "Pontiac",
    "Porsche",
    "Proton",
    "Ram",
    "Renault",
    "Renault Samsung",
    "Rolls-Royce",
    "Rover",
    "Saab",
    "Saturn",
    "Scion",
    "Seat",
    "Skoda",
    "Smart",
    "Soueast",
    "SsangYong",
    "Subaru",
    "Suzuki",
    "Tata",
    "Tesla",
    "Toyota",
    "VinFast",
    "Volkswagen",
    "Volvo",
    "Wuling",
    "XPeng",
    "Zeekr",
    "Zotye",
]

ALL_CAR_CATEGORIES = [
    "Sedan",
    "SUV",
    "Pickup Truck",
    "Sports",
    "Hatchback",
    "Crossover",
    "Convertible",
    "Coupe",
    "Van",
    "Wagon",
    "Minivan",
]

SUNNY_2009_LISTING = {
    "title": "2009 Nissan Sunny 1.6 GCC Specs",
    "brand": "Nissan",
    "model": "Sunny 1.6",
    "year": 2009,
    "price": 7500,
    "mileage": 380000,
    "description": "Golden Nissan Sunny 1.6 with GCC specs, very well maintained, and ready for daily driving.",
    "image": "sunny_2009/sunny2009_1.HEIC",
    "gallery_images": [
        "sunny_2009/sunny2009_2.HEIC",
        "sunny_2009/sunny2009_3.HEIC",
        "sunny_2009/sunny2009_4.heic",
        "sunny_2009/sunny2009_5.HEIC",
        "sunny_2009/sunny2009_6.HEIC",
        "sunny_2009/sunny2009_7.HEIC",
        "sunny_2009/sunny2009_8.HEIC",
        "sunny_2009/sunny2009_9.HEIC",
        "sunny_2009/sunny2009_10.HEIC", 
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 1,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

ALTIMA_2017_LISTING = {
    "title": "2017 Nissan Altima GCC Specs",
    "brand": "Nissan",
    "model": "Altima",
    "year": 2017,
    "price": 20000,
    "mileage": 142000,
    "description": "White Nissan Altima with beige interior, GCC specs, excellent condition, and a strong maintenance profile.",
    "image": "altima_2017/altima2017_1.jpg",
    "gallery_images": [
        "altima_2017/altima2017_2.jpg",
        "altima_2017/altima2017_3.jpg",
        "altima_2017/altima2017_4.jpg",
        "altima_2017/altima2017_5.jpg",
        "altima_2017/altima2017_6.jpg",
        "altima_2017/altima2017_7.HEIC",
        "altima_2017/altima2017_8.HEIC",
        "altima_2017/altima2017_9.HEIC",
        "altima_2017/altima2017_10.HEIC",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 1,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

ES350_2010_LISTING = {
    "title": "2010 Lexus ES 350 American Specs",
    "brand": "Lexus",
    "model": "ES 350",
    "year": 2010,
    "price": 18000,
    "mileage": 260000,
    "description": "Dark grey Lexus ES 350 with American specs, beautiful interior, and orange leather seats in a well-presented cabin.",
    "image": "ES350_2010/es350_2010_1.jpg",
    "gallery_images": [
        "ES350_2010/es350_2010_2.jpg",
        "ES350_2010/es350_2010_3.jpg",
        "ES350_2010/es350_2010_4.jpg",
        "ES350_2010/es350_2010_5.HEIC",
        "ES350_2010/es350_2010_6.HEIC",
        "ES350_2010/es350_2010_7.HEIC",
        "ES350_2010/es350_2010_8.HEIC",
        "ES350_2010/es350_2010_9.HEIC",
        "ES350_2010/es350_2010_10.HEIC",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

GALANT_2008_LISTING = {
    "title": "2008 Mitsubishi Galant GCC Specs",
    "brand": "Mitsubishi",
    "model": "Galant",
    "year": 2008,
    "price": 8000,
    "mileage": 275000,
    "description": "Silver Mitsubishi Galant with GCC specs, full option, grey seats, and very well maintained condition.",
    "image": "galant_2008/galant_7.JPG",
    "gallery_images": [
        "galant_2008/galant_1.JPG",
        "galant_2008/galant_2.JPG",
        "galant_2008/galant_3.JPG",
        "galant_2008/galant_4.jpg",
        "galant_2008/galant_5.jpg",
        "galant_2008/galant_6.jpg",
        "galant_2008/galant_8.JPG",
        "galant_2008/galant_9.jpg",
        "galant_2008/galant_10.jpg",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

IS250_2011_LISTING = {
    "title": "2011 Lexus IS 250 American Specs",
    "brand": "Lexus",
    "model": "IS 250",
    "year": 2011,
    "price": 21000,
    "mileage": 262000,
    "description": "Dark grey Lexus IS 250 with American specs, black interior, black leather seats, full option, and excellent condition.",
    "image": "is250_2011/is250_2011_2.JPG",
    "gallery_images": [
        "is250_2011/is250_2011_2.JPG",
        "is250_2011/is250_2011_3.JPG",
        "is250_2011/is250_2011_4.JPG",
        "is250_2011/is250_2011_5.JPG",
        "is250_2011/is250_2011_6.JPG",
        "is250_2011/is250_2011_7.JPG",
        "is250_2011/is250_2011_8.JPG",
        "is250_2011/is250_2011_9.JPG",
        "is250_2011/is250_2011_10.JPG",
        "is250_2011/is250_2011_11.JPG",
        "is250_2011/is250_2011_12.JPG",
        "is250_2011/is250_2011_13.JPG",
        "is250_2011/is250_2011_14.JPG",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 1,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

SUNNY_2015_LISTING = {
    "title": "Nissan Sunny 2015 Manual Gear GCC",
    "brand": "Nissan",
    "model": "Sunny",
    "year": 2015,
    "price": 14000,
    "mileage": 162000,
    "description": "White Nissan Sunny with manual gear, GCC specs, and clean practical condition for everyday driving.",
    "image": "sunny_2015/sunny2015_5.jpg",
    "gallery_images": [
        "sunny_2015/sunny2015_2.jpg",
        "sunny_2015/sunny2015_3.jpg",
        "sunny_2015/sunny2015_4.jpg",
        "sunny_2015/sunny2015_5.jpg",
        "sunny_2015/sunny2015_6.jpg",
        "sunny_2015/sunny2015_7.JPG",
        "sunny_2015/sunny2015_8.JPG",
        "sunny_2015/sunny2015_9.JPG",
        "sunny_2015/sunny2015_10.JPG",
        "sunny_2015/sunny2015_11.JPG",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

SUNNY_2020_LISTING = {
    "title": "2020 Nissan Sunny GCC Specs",
    "brand": "Nissan",
    "model": "Sunny",
    "year": 2020,
    "price": 30000,
    "mileage": 88000,
    "description": "Silver Nissan Sunny with GCC specs, beige interior, agency maintained, and service history available.",
    "image": "sunny_2020/sunny2020_1.HEIC",
    "gallery_images": [
        "sunny_2020/sunny2020_2.HEIC",
        "sunny_2020/sunny2020_3.HEIC",
        "sunny_2020/sunny2020_4.HEIC",
        "sunny_2020/sunny2020_5.HEIC",
        "sunny_2020/sunny2020_6.HEIC",
        "sunny_2020/sunny2020_7.HEIC",
        "sunny_2020/sunny2020_8.HEIC",
        "sunny_2020/sunny2020_9.HEIC",
        "sunny_2020/sunny2020_10.HEIC",
        "sunny_2020/sunny2020_11.HEIC",
        "sunny_2020/sunny2020_12.HEIC",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

TIIDA_2007_LISTING = {
    "title": "2007 Nissan Tiida GCC Specs",
    "brand": "Nissan",
    "model": "Tiida",
    "year": 2007,
    "price": 7500,
    "mileage": 340000,
    "description": "White Nissan Tiida with GCC specs, beige interior, excellent condition, and a very well maintained history.",
    "image": "tiida_2007/tiida_1.JPG",
    "gallery_images": [
        "tiida_2007/tiida_2.JPG",
        "tiida_2007/tiida_3.JPG",
        "tiida_2007/tiida_4.JPG",
        "tiida_2007/tiida_5.JPG",
        "tiida_2007/tiida_6.JPG",
        "tiida_2007/tiida_7.JPG",
        "tiida_2007/tiida_8.JPG",
        "tiida_2007/tiida_9.JPG",
        "tiida_2007/tiida_10.JPG",
    ],
    "category": "Hatchback",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

TIIDA_2016_LISTING = {
    "title": "2016 Nissan Tiida GCC Specs",
    "brand": "Nissan",
    "model": "Tiida",
    "year": 2016,
    "price": 20000,
    "mileage": 158000,
    "description": "Pearl white Nissan Tiida with GCC specs, beige interior, mid option trim, and a clean, well-kept condition.",
    "image": "tiida_2016/tiida2016_9.jpg",
    "gallery_images": [
        "tiida_2016/tiida2016_2.jpg",
        "tiida_2016/tiida2016_3.JPG",
        "tiida_2016/tiida2016_4.JPG",
        "tiida_2016/tiida2016_5.JPG",
        "tiida_2016/tiida2016_6.jpg",
        "tiida_2016/tiida2016_7.JPG",
        "tiida_2016/tiida2016_8.JPG",
        "tiida_2016/tiida2016_9.jpg",
    ],
    "category": "Hatchback",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

ALTIMA_2007_LISTING = {
    "title": "2007 Nissan Altima 2.5 GCC Specs",
    "brand": "Nissan",
    "model": "Altima 2.5",
    "year": 2007,
    "price": 7500,
    "mileage": 202000,
    "description": "Grey Nissan Altima 2.5 with GCC specs, excellent condition, and a very well maintained history.",
    "image": "altima_2007/altima2007_6.jpg",
    "gallery_images": [
        "altima_2007/altima2007_2.HEIC",
        "altima_2007/altima2007_3.jpg",
        "altima_2007/altima2007_4.jpg",
        "altima_2007/altima2007_5.jpg",
        "altima_2007/altima2007_6.jpg",
        "altima_2007/altima2007_7.jpg",
        "altima_2007/altima2007_8.HEIC",
        "altima_2007/altima2007_9.HEIC",
        "altima_2007/altima2007_10.HEIC",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

AVALON_2011_LISTING = {
    "title": "2011 Toyota Avalon Limited American Specs",
    "brand": "Toyota",
    "model": "Avalon",
    "year": 2011,
    "price": 22000,
    "mileage": 320000,
    "description": "Dark grey Toyota Avalon Limited with American specs, beige interior, full option trim, and well maintained condition.",
    "image": "avalon_2011/avalon2011_1.jpg",
    "gallery_images": [
        "avalon_2011/avalon2011_2.jpg",
        "avalon_2011/avalon2011_3.jpg",
        "avalon_2011/avalon2011_4.HEIC",
        "avalon_2011/avalon2011_5.HEIC",
        "avalon_2011/avalon2011_6.jpg",
        "avalon_2011/avalon2011_7.jpg",
        "avalon_2011/avalon2011_8.jpg",
        "avalon_2011/avalon2011_9.HEIC",
        "avalon_2011/avalon2011_10.HEIC",
        "avalon_2011/avalon2011_11.HEIC",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

MICRA_2020_LISTING = {
    "title": "2020 Nissan Micra GCC Specs",
    "brand": "Nissan",
    "model": "Micra",
    "year": 2020,
    "price": 20000,
    "mileage": 128000,
    "description": "White Nissan Micra with GCC specs, black interior, excellent condition, and service history available.",
    "image": "micra_2020/micra2020_1.JPG",
    "gallery_images": [
        "micra_2020/micra2020_2.JPG",
        "micra_2020/micra2020_3.JPG",
        "micra_2020/micra2020_4.JPG",
        "micra_2020/micra2020_5.JPG",
        "micra_2020/micra2020_6.JPG",
        "micra_2020/micra2020_7.JPG",
        "micra_2020/micra2020_8.JPG",
        "micra_2020/micra2020_9.JPG",
        "micra_2020/micra2020_10.JPG",
    ],
    "category": "Hatchback",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

PATROL_2015_LISTING = {
    "title": "2015 Nissan Patrol Platinum V8 GCC Specs",
    "brand": "Nissan",
    "model": "Patrol",
    "year": 2015,
    "price": 55000,
    "mileage": 142000,
    "description": "Pearl white Nissan Patrol Platinum VIP Edition with GCC specs, beige interior, 5.6L V8, and excellent condition with strong maintenance history.",
    "image": "patrol_2015/patrol2015_5.JPG",
    "gallery_images": [
        "patrol_2015/patrol2015_2.jpg",
        "patrol_2015/patrol2015_3.jpg",
        "patrol_2015/patrol2015_4.jpg",
        "patrol_2015/patrol2015_5.JPG",
        "patrol_2015/patrol2015_6.JPG",
        "patrol_2015/patrol2015_7.JPG",
        "patrol_2015/patrol2015_8.JPG",
        "patrol_2015/patrol2015_9.JPG",
        "patrol_2015/patrol2015_10.JPG",
        "patrol_2015/patrol2015_11.JPG",
        "patrol_2015/patrol2015_12.JPG",
    ],
    "category": "SUV",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 1,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

RX350_2013_LISTING = {
    "title": "2013 Lexus RX 350 GCC Specs",
    "brand": "Lexus",
    "model": "RX 350",
    "year": 2013,
    "price": 45000,
    "mileage": 202000,
    "description": "Black Lexus RX 350 with GCC specs, black interior, brown seats, panoramic sunroof, full option trim, and excellent well maintained condition.",
    "image": "rx350_2013/rx350_2.jpg",
    "gallery_images": [
        "rx350_2013/rx350_2.jpg",
        "rx350_2013/rx350_3.jpg",
        "rx350_2013/rx350_4.JPG",
        "rx350_2013/rx350_5.jpg",
        "rx350_2013/rx350_6.jpg",
        "rx350_2013/rx350_7.jpg",
        "rx350_2013/rx350_8.JPG",
        "rx350_2013/rx350_9.JPG",
        "rx350_2013/rx350_10.JPG",
        "rx350_2013/rx350_11.JPG",
    ],
    "category": "SUV",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 1,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

RED_IS250_2010_LISTING = {
    "title": "2010 Lexus IS 250 American Specs",
    "brand": "Lexus",
    "model": "IS 250",
    "year": 2010,
    "price": 19000,
    "mileage": 222000,
    "description": "Red Lexus IS 250 with American specs, grey interior, full option trim, excellent condition, and well maintained history.",
    "image": "red_is250_2010/red_is250_4.JPG",
    "gallery_images": [
        "red_is250_2010/red_is250_2.HEIC",
        "red_is250_2010/red_is250_3.JPG",
        "red_is250_2010/red_is250_4.JPG",
        "red_is250_2010/red_is250_5.JPG",
        "red_is250_2010/red_is250_6.JPG",
        "red_is250_2010/red_is250_7.JPG",
        "red_is250_2010/red_is250_8.JPG",
        "red_is250_2010/red_is250_9.JPG",
        "red_is250_2010/red_is250_10.JPG",
        "red_is250_2010/red_is250_11.JPG",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

BLUE_IS250_2011_LISTING = {
    "title": "2011 Lexus IS 250 American Specs RWD",
    "brand": "Lexus",
    "model": "IS 250 RWD",
    "year": 2011,
    "price": 22000,
    "mileage": 252000,
    "description": "Dark blue Lexus IS 250 with American specs, rear wheel drive, full option trim, excellent condition, modified exhaust, rear spoiler, F Sport headlights and taillights, and 19-inch F Sport rims.",
    "image": "blue_is250_2011/blue_is250_2.JPG",
    "gallery_images": [
        "blue_is250_2011/blue_is250_2.JPG",
        "blue_is250_2011/blue_is250_3.jpg",
        "blue_is250_2011/blue_is250_4.jpg",
        "blue_is250_2011/blue_is250_5.JPG",
        "blue_is250_2011/blue_is250_6.JPG",
        "blue_is250_2011/blue_is250_7.JPG",
        "blue_is250_2011/blue_is250_8.JPG",
        "blue_is250_2011/blue_is250_9.jpg",
        "blue_is250_2011/blue_is250_10.jpg",
        "blue_is250_2011/blue_is250_11.jpg",
        "blue_is250_2011/blue_is250_12.JPG",
        "blue_is250_2011/blue_is250_13.JPG",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

IS250_2013_LISTING = {
    "title": "2013 Lexus IS 250 American Specs",
    "brand": "Lexus",
    "model": "IS 250",
    "year": 2013,
    "price": 22000,
    "mileage": 189000,
    "description": "Black Lexus IS 250 with American specs, clean title, beige interior, full option trim, excellent condition, and a well maintained history.",
    "image": "is250_2013/is250_2013_11.JPG",
    "gallery_images": [
        "is250_2013/is250_2013_2.JPG",
        "is250_2013/is250_2013_3.JPG",
        "is250_2013/is250_2013_4.JPG",
        "is250_2013/is250_2013_5.JPG",
        "is250_2013/is250_2013_6.JPG",
        "is250_2013/is250_2013_7.JPG",
        "is250_2013/is250_2013_8.JPG",
        "is250_2013/is250_2013_9.JPG",
        "is250_2013/is250_2013_10.JPG",
        "is250_2013/is250_2013_11.JPG",
        "is250_2013/is250_2013_12.JPG",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 1,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

CAMRY_2017_LISTING = {
    "title": "2017 Toyota Camry GCC Specs",
    "brand": "Toyota",
    "model": "Camry SE 2.5",
    "year": 2017,
    "price": 30000,
    "mileage": 208000,
    "description": "Maroon Toyota Camry SE with GCC specs, 2.5L 4-cylinder engine, 6-speed automatic gearbox, black leather seats, beige interior, excellent condition, well maintained, no maintenance required, and located in Sharjah.",
    "image": "camry_2016/camry2016_6.JPG",
    "gallery_images": [
        "camry_2016/camry2016_2.heic",
        "camry_2016/camry2016_3.heic",
        "camry_2016/camry2016_4.heic",
        "camry_2016/camry2016_5.JPG",
        "camry_2016/camry2016_6.JPG",
        "camry_2016/camry2016_7.heic",
        "camry_2016/camry2016_8.heic",
        "camry_2016/camry2016_9.JPG",
        "camry_2016/camry2016_10.JPG",
        "camry_2016/camry2016_11.JPG",
    ],
    "category": "Sedan",
    "location": "Sharjah",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

FORD_EXPLORER_2014_LISTING = {
    "title": "2014 Ford Explorer GCC Specs",
    "brand": "Ford",
    "model": "Explorer",
    "year": 2014,
    "price": 30000,
    "mileage": 212000,
    "description": "Silver Ford Explorer with GCC specs, black interior, mid option trim, excellent condition, and ready to buy and drive with no work required.",
    "image": "ford_explorer_2014/ford_explorer_3.jpg",
    "gallery_images": [
        "ford_explorer_2014/ford_explorer_2.JPG",
        "ford_explorer_2014/ford_explorer_3.jpg",
        "ford_explorer_2014/ford_explorer_4.jpg",
        "ford_explorer_2014/ford_explorer_5.jpg",
        "ford_explorer_2014/ford_explorer_6.jpg",
        "ford_explorer_2014/ford_explorer_7.JPG",
        "ford_explorer_2014/ford_explorer_8.JPG",
        "ford_explorer_2014/ford_explorer_9.JPG",
        "ford_explorer_2014/ford_explorer_10.JPG",
        "ford_explorer_2014/ford_explorer_11.JPG",
        "ford_explorer_2014/ford_explorer_12.JPG",
        "ford_explorer_2014/ford_explorer_13.JPG",
        "ford_explorer_2014/ford_explorer_14.JPG",
    ],
    "category": "SUV",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

SENTRA_2016_LISTING = {
    "title": "2016 Nissan Sentra GCC Specs",
    "brand": "Nissan",
    "model": "Sentra",
    "year": 2016,
    "price": 20000,
    "mileage": 162000,
    "description": "Grey Nissan Sentra with GCC specs, beige interior, mid option trim, excellent condition, and well maintained buy-and-drive readiness.",
    "image": "nissan_sentra/sentra2016_4.jpg",
    "gallery_images": [
        "nissan_sentra/sentra2016_2.jpg",
        "nissan_sentra/sentra2016_3.jpg",
        "nissan_sentra/sentra2016_4.jpg",
        "nissan_sentra/sentra2016_5.HEIC",
        "nissan_sentra/sentra2016_6.HEIC",
        "nissan_sentra/sentra2016_7.HEIC",
        "nissan_sentra/sentra2016_8.HEIC",
        "nissan_sentra/sentra2016_9.HEIC",
        "nissan_sentra/sentra2016_10.HEIC",
        "nissan_sentra/sentra2016_11.HEIC",
        "nissan_sentra/sentra2016_12.HEIC",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

AVALON_2009_LISTING = {
    "title": "2009 Toyota Avalon Limited GCC Specs",
    "brand": "Toyota",
    "model": "Avalon",
    "year": 2009,
    "price": 16000,
    "mileage": 298000,
    "description": "Pearl white Toyota Avalon Limited with GCC specs, beige interior, excellent condition, and no work required.",
    "image": "avalon_2008/avalon2008_1.jpg",
    "gallery_images": [
        "avalon_2008/avalon2008_2.jpg",
        "avalon_2008/avalon2008_3.HEIC",
        "avalon_2008/avalon2008_4.jpg",
        "avalon_2008/avalon2008_5.jpg",
        "avalon_2008/avalon2008_6.jpg",
        "avalon_2008/avalon2008_7.jpg",
        "avalon_2008/avalon2008_8.HEIC",
        "avalon_2008/avalon2008_9.HEIC",
        "avalon_2008/avalon2008_10.HEIC",
    ],
    "category": "Sedan",
    "location": "Dubai, Al Qusais 2",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

SUNNY_2018_LISTING = {
    "title": "nissan sunny 2018 manual gear gcc",
    "brand": "Nissan",
    "model": "Sunny 1.5",
    "year": 2018,
    "price": 18000,
    "mileage": 152000,
    "description": "White Nissan Sunny 1.5 with manual gear, GCC specs, beige interior, very clean condition, excellent overall shape, and service history available.",
    "image": "sunny_2018/sunny2018_9.JPG",
    "gallery_images": [
        "sunny_2018/sunny2018_2.JPG",
        "sunny_2018/sunny2018_3.JPG",
        "sunny_2018/sunny2018_4.JPG",
        "sunny_2018/sunny2018_5.JPG",
        "sunny_2018/sunny2018_6.JPG",
        "sunny_2018/sunny2018_7.JPG",
        "sunny_2018/sunny2018_8.JPG",
        "sunny_2018/sunny2018_9.JPG",
        "sunny_2018/sunny2018_10.JPG",
    ],
    "category": "Sedan",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

MURANO_2008_LISTING = {
    "title": "2008 Nissan Murano GCC Specs",
    "brand": "Nissan",
    "model": "Murano",
    "year": 2008,
    "price": 14000,
    "mileage": 262000,
    "description": "Pearl white Nissan Murano with GCC specs, beige interior, mid option trim, excellent condition, no issues, lady driven, and very well maintained.",
    "image": "murano_2008/murano_6.JPG",
    "gallery_images": [
        "murano_2008/murano_2.JPG",
        "murano_2008/murano_3.JPG",
        "murano_2008/murano_4.JPG",
        "murano_2008/murano_5.JPG",
        "murano_2008/murano_6.JPG",
        "murano_2008/murano_7.JPG",
        "murano_2008/murano_8.JPG",
        "murano_2008/murano_9.JPG",
        "murano_2008/murano_10.JPG",
        "murano_2008/murano_11.JPG",
        "murano_2008/murano_12.JPG",
    ],
    "category": "SUV",
    "location": "Sharjah",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

PAJERO_2014_LISTING = {
    "title": "2014 Mitsubishi Pajero GCC Specs",
    "brand": "Mitsubishi",
    "model": "Pajero",
    "year": 2014,
    "price": 25000,
    "mileage": 202000,
    "description": "Pearl white Mitsubishi Pajero with GCC specs, beige interior, full option trim, excellent condition, and service history available.",
    "image": "pajero_2012/pajero2012_6.HEIC.png",
    "gallery_images": [
        "pajero_2012/pajero2012_2.HEIC.png",
        "pajero_2012/pajero2012_3.HEIC.png",
        "pajero_2012/pajero2012_4.jpg",
        "pajero_2012/pajero2012_5.HEIC.png",
        "pajero_2012/pajero2012_6.HEIC.png",
        "pajero_2012/pajero2012_7.HEIC.png",
        "pajero_2012/pajero2012_8.HEIC.png",
        "pajero_2012/pajero2012_9.HEIC.png",
        "pajero_2012/pajero2012_10.HEIC.png",
        "pajero_2012/pajero2012_11.HEIC.png",
    ],
    "category": "SUV",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 0,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

PAJERO_2020_LISTING = {
    "title": "2020 Mitsubishi Pajero GCC Specs",
    "brand": "Mitsubishi",
    "model": "Pajero",
    "year": 2020,
    "price": 50000,
    "mileage": 108000,
    "description": "Red Mitsubishi Pajero with GCC specs, beige interior, excellent condition, no maintenance required, and service records available.",
    "image": "pajero_2016/pajero2020_1.heic.png",
    "gallery_images": [
        "pajero_2016/pajero2020_2.heic.png",
        "pajero_2016/pajero2020_3.heic.png",
        "pajero_2016/pajero2020_4.HEIC.png",
        "pajero_2016/pajero2020_5.HEIC.png",
        "pajero_2016/pajero2020_6.HEIC.png",
        "pajero_2016/pajero2020_7.heic.png",
        "pajero_2016/pajero2020_8.heic.png",
        "pajero_2016/pajero2020_9.heic.png",
        "pajero_2016/pajero2020_10.HEIC.png",
        "pajero_2016/pajero2020_11.HEIC.png",
    ],
    "category": "SUV",
    "location": "Dubai",
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "condition": "Used",
    "featured": 1,
    "status": "Available",
    "seller_name": "Private Seller",
    "seller_phone": "+971582119936",
    "seller_type": "Private Seller",
}

SAMPLE_CARS = [
    {
        "title": "Toyota Camry LE",
        "brand": "Toyota",
        "model": "Camry",
        "year": 2019,
        "price": 45000,
        "mileage": 90000,
        "description": "Single-owner sedan with a clean service history and great fuel economy.",
        "image": "camry.jpg",
        "category": "Sedan",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "Nissan Altima SV",
        "brand": "Nissan",
        "model": "Altima",
        "year": 2018,
        "price": 39000,
        "mileage": 120000,
        "description": "Well-kept daily driver with smooth handling and a spacious cabin.",
        "image": "altima.jpg",
        "category": "Sedan",
        "location": "Sharjah",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "BMW 520i Executive",
        "brand": "BMW",
        "model": "520i",
        "year": 2017,
        "price": 65000,
        "mileage": 80000,
        "description": "Comfortable luxury sedan with premium interior features and a strong road presence.",
        "image": "bmw.jpg",
        "category": "Sedan",
        "location": "Abu Dhabi",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "Mercedes-Benz C300",
        "brand": "Mercedes",
        "model": "C300",
        "year": 2020,
        "price": 95000,
        "mileage": 60000,
        "description": "Excellent condition car with modern tech, refined comfort, and low mileage.",
        "image": "merc.jpg",
        "category": "Sedan",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Certified Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "Toyota Camry Sport",
        "brand": "Toyota",
        "model": "Camry",
        "year": 2021,
        "price": 72000,
        "mileage": 42000,
        "description": "Recent-model Camry with sporty styling, advanced safety, and dealer service records.",
        "image": "camry.jpg",
        "category": "Sedan",
        "location": "Ajman",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "Hyundai Sonata Premium",
        "brand": "Hyundai",
        "model": "Sonata",
        "year": 2020,
        "price": 58000,
        "mileage": 70000,
        "description": "Feature-packed family sedan offering comfort, tech, and excellent value.",
        "image": "camry.jpg",
        "category": "Sedan",
        "location": "Ras Al Khaimah",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "Mercedes GLC 300",
        "brand": "Mercedes",
        "model": "GLC 300",
        "year": 2021,
        "price": 158000,
        "mileage": 54000,
        "description": "Premium SUV with panoramic roof, leather interior, and smooth city driving.",
        "image": "merc.jpg",
        "category": "SUV",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Certified Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "BMW X3 xDrive30i",
        "brand": "BMW",
        "model": "X3",
        "year": 2019,
        "price": 119000,
        "mileage": 76000,
        "description": "Balanced SUV with premium comfort, responsive steering, and GCC specs.",
        "image": "bmw.jpg",
        "category": "SUV",
        "location": "Abu Dhabi",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "2017 Nissan Patrol V6",
        "brand": "Nissan",
        "model": "Patrol",
        "year": 2017,
        "price": 62000,
        "mileage": 129000,
        "description": "Strong value SUV inspired by current UAE used-car pricing bands for full-size family 4x4s.",
        "image": "altima.jpg",
        "category": "SUV",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "2014 Mercedes ML350",
        "brand": "Mercedes",
        "model": "ML350",
        "year": 2014,
        "price": 42000,
        "mileage": 168000,
        "description": "Luxury SUV with GCC specs and realistic market pricing for older premium utility vehicles.",
        "image": "merc.jpg",
        "category": "SUV",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "2015 Renault Koleos",
        "brand": "Renault",
        "model": "Koleos",
        "year": 2015,
        "price": 13500,
        "mileage": 170000,
        "description": "Budget crossover with clean practical packaging and accessible entry pricing.",
        "image": "altima.jpg",
        "category": "Crossover",
        "location": "Sharjah",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2014 Toyota Zelas",
        "brand": "Toyota",
        "model": "Zelas",
        "year": 2014,
        "price": 23000,
        "mileage": 184000,
        "description": "Sporty coupe with Toyota reliability and pricing tuned to similar UAE enthusiast listings.",
        "image": "camry.jpg",
        "category": "Coupe",
        "location": "Ajman",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2015 Volkswagen Touareg",
        "brand": "Volkswagen",
        "model": "Touareg",
        "year": 2015,
        "price": 25000,
        "mileage": 174000,
        "description": "Comfortable SUV with premium road manners and a realistic mid-market UAE asking price.",
        "image": "bmw.jpg",
        "category": "SUV",
        "location": "Abu Dhabi",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2017 Chevrolet Captiva LTZ",
        "brand": "Chevrolet",
        "model": "Captiva",
        "year": 2017,
        "price": 22000,
        "mileage": 202000,
        "description": "7-seater crossover that follows local pricing patterns for practical family transport.",
        "image": "altima.jpg",
        "category": "SUV",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2016 Fiat 500 1.4L",
        "brand": "Fiat",
        "model": "500",
        "year": 2016,
        "price": 16500,
        "mileage": 139000,
        "description": "Compact hatchback for city buyers looking for style and lower entry cost.",
        "image": "camry.jpg",
        "category": "Hatchback",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2013 Mazda MX-5 Miata",
        "brand": "Mazda",
        "model": "MX-5",
        "year": 2013,
        "price": 30000,
        "mileage": 150000,
        "description": "Lightweight roadster with enthusiast appeal and pricing aligned to the current used niche segment.",
        "image": "bmw.jpg",
        "category": "Convertible",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2011 BMW X1",
        "brand": "BMW",
        "model": "X1",
        "year": 2011,
        "price": 15500,
        "mileage": 269000,
        "description": "Entry luxury crossover priced in line with older UAE compact SUV listings.",
        "image": "bmw.jpg",
        "category": "SUV",
        "location": "Sharjah",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2011 Mitsubishi Pajero GLS 7 Seater",
        "brand": "Mitsubishi",
        "model": "Pajero",
        "year": 2011,
        "price": 20000,
        "mileage": 142000,
        "description": "A familiar UAE family SUV with practical seating, easy maintenance, and dependable value.",
        "image": "altima.jpg",
        "category": "SUV",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2013 Ford Edge AWD",
        "brand": "Ford",
        "model": "Edge",
        "year": 2013,
        "price": 17000,
        "mileage": 191000,
        "description": "Clean midsize crossover with realistic budget pricing and family-focused comfort.",
        "image": "merc.jpg",
        "category": "SUV",
        "location": "Abu Dhabi",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2017 Mercedes C300",
        "brand": "Mercedes",
        "model": "C300",
        "year": 2017,
        "price": 35000,
        "mileage": 112000,
        "description": "Comfortable luxury sedan with pricing aligned to current Dubai used-market examples.",
        "image": "merc.jpg",
        "category": "Sedan",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "2015 Mercedes-Benz A45 AMG 4MATIC",
        "brand": "Mercedes",
        "model": "A45 AMG",
        "year": 2015,
        "price": 38000,
        "mileage": 179000,
        "description": "High-performance hot hatch with strong enthusiast appeal and GCC-style pricing.",
        "image": "merc.jpg",
        "category": "Hatchback",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "2014 Nissan Pathfinder 7 Seater",
        "brand": "Nissan",
        "model": "Pathfinder",
        "year": 2014,
        "price": 16000,
        "mileage": 300000,
        "description": "Roomy family SUV positioned for budget-conscious buyers needing seven seats.",
        "image": "altima.jpg",
        "category": "SUV",
        "location": "Ajman",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2015 Dodge Durango Limited",
        "brand": "Dodge",
        "model": "Durango",
        "year": 2015,
        "price": 26000,
        "mileage": 335000,
        "description": "Large SUV with a bold look and practical utility for buyers needing space on a budget.",
        "image": "bmw.jpg",
        "category": "SUV",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
    {
        "title": "2010 Mercedes S550",
        "brand": "Mercedes",
        "model": "S550",
        "year": 2010,
        "price": 19000,
        "mileage": 200000,
        "description": "Flagship sedan with classic luxury presence and realistic older-premium pricing.",
        "image": "merc.jpg",
        "category": "Sedan",
        "location": "Sharjah",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 1,
        "status": "Available",
    },
    {
        "title": "2013 Audi Q7 S Line",
        "brand": "Audi",
        "model": "Q7",
        "year": 2013,
        "price": 23500,
        "mileage": 172000,
        "description": "Luxury seven-seater SUV with premium styling and a competitive used-market price.",
        "image": "bmw.jpg",
        "category": "SUV",
        "location": "Dubai",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "condition": "Used",
        "featured": 0,
        "status": "Available",
    },
]

UNWANTED_LISTING_BRANDS = {
    "Audi",
    "BMW",
    "Chevrolet",
    "Fiat",
    "Hyundai",
    "Mercedes",
    "Mazda",
    "Volkswagen",
}

UNWANTED_LISTING_TITLES = {
    "Toyota Camry LE",
    "Toyota Camry Sport",
    "2017 Nissan Patrol V6",
    "2015 Renault Koleos",
    "2014 Toyota Zelas",
    "2011 Mitsubishi Pajero GLS 7 Seater",
    "2013 Ford Edge AWD",
    "2014 Nissan Pathfinder 7 Seater",
    "2015 Dodge Durango Limited",
}

SAMPLE_CARS = [
    car
    for car in SAMPLE_CARS
    if car["brand"] not in UNWANTED_LISTING_BRANDS
    and car["title"] not in UNWANTED_LISTING_TITLES
]

DESCRIPTION_OVERRIDES = {
    "Nissan Altima SV": "Well-kept sedan with a spacious cabin, smooth automatic drive, and comfortable everyday usability. Clean presentation, good fuel efficiency for its class, and practical family-friendly comfort make it an easy daily driver.",
    "2009 Nissan Sunny 1.6 GCC Specs": "Golden Nissan Sunny 1.6 with GCC specs, 380k km, and a very well maintained ownership history. Practical daily sedan with straightforward running costs, clean presentation, and dependable city-use comfort.",
    "2017 Nissan Altima GCC Specs": "White Nissan Altima with GCC specs, beige interior, and 142k km on the odometer. Excellent condition sedan with a roomy cabin, smooth automatic drive, and a strong maintenance profile for daily use.",
    "2010 Lexus ES 350 American Specs": "Dark grey Lexus ES 350 with American specs, 260k km, and a striking orange leather interior. Comfortable V6 luxury sedan with a quiet ride, refined cabin feel, and a beautifully presented interior that stands out from typical listings.",
    "2008 Mitsubishi Galant GCC Specs": "Silver Mitsubishi Galant with GCC specs, 275k km, grey seats, and full option trim. Very well maintained sedan with a spacious cabin, clean presentation, and dependable everyday usability.",
    "2011 Lexus IS 250 American Specs": "Dark grey Lexus IS 250 with American specs, 262k km, black interior, and black leather seats. Full option compact luxury sedan with sporty styling, excellent condition, and a well-kept cabin for daily driving.",
    "Nissan Sunny 2015 Manual Gear GCC": "White Nissan Sunny with manual gear, GCC specs, and 162k km on the odometer. Clean and economical daily sedan with straightforward ownership costs, tidy presentation, and dependable everyday practicality.",
    "2020 Nissan Sunny GCC Specs": "Silver Nissan Sunny with GCC specs, 88k km, beige interior, agency-maintained history, and service records available. Published Nissan Middle East information for the 2020 Sunny highlights a 1.6L engine, roomy cabin, and strong value-focused practicality for daily use.",
    "2007 Nissan Tiida GCC Specs": "White Nissan Tiida hatchback with GCC specs, 340k km, and a beige interior. Excellent condition and very well maintained, with practical cabin space and easy everyday usability for city driving.",
    "2007 Nissan Altima 2.5 GCC Specs": "Grey Nissan Altima 2.5 with GCC specs, 202k km, and excellent overall condition. Well maintained sedan with comfortable road manners, practical cabin space, and dependable daily usability.",
    "2011 Toyota Avalon Limited American Specs": "Dark grey Toyota Avalon Limited with American specs, beige interior, and full option trim. Full-size sedan with strong V6 comfort, a refined cabin, and premium equipment that suits long-distance and daily driving alike.",
    "2020 Nissan Micra GCC Specs": "White Nissan Micra hatchback with GCC specs, 128k km, black interior, and service history available. Compact and easy to park, with excellent condition and practical city-friendly usability for everyday driving.",
    "2015 Nissan Patrol Platinum V8 GCC Specs": "Pearl white Nissan Patrol Platinum VIP Edition with GCC specs, beige interior, and 142k km. Premium full-size SUV with a 5.6L V8, spacious cabin, strong road presence, and excellent condition backed by a solid maintenance history.",
    "2013 Lexus RX 350 GCC Specs": "Black Lexus RX 350 with GCC specs, 202k km, black interior, brown seats, and panoramic sunroof. Full option luxury crossover with a refined cabin, smooth V6 performance, and strong everyday comfort in excellent well-maintained condition.",
    "2010 Lexus IS 250 American Specs": "Red Lexus IS 250 with American specs, 222k km, grey interior, and full option trim. Sporty compact luxury sedan with excellent condition, well maintained history, and a clean presentation inside and out.",
    "2011 Lexus IS 250 American Specs RWD": "Dark blue Lexus IS 250 with American specs, rear-wheel drive, 252k km, and full option trim. Tastefully modified with F Sport-style lighting, rear spoiler, 19-inch F Sport rims, and exhaust upgrades while keeping strong everyday drivability.",
    "2014 Ford Explorer GCC Specs": "Silver Ford Explorer with GCC specs, 212k km, black interior, and mid option trim. Spacious SUV in excellent condition with practical family usability, smooth road manners, and no work required before driving.",
    "2016 Nissan Sentra GCC Specs": "Grey Nissan Sentra with GCC specs, 162k km, beige interior, and mid option trim. Well maintained sedan with practical daily comfort, clean presentation, and a dependable buy-and-drive character.",
    "2009 Toyota Avalon Limited GCC Specs": "Pearl white Toyota Avalon Limited with GCC specs, 298k km, and beige interior. Spacious full-size sedan in excellent condition with smooth road comfort, no work required, and a clean, well-kept cabin.",
    "nissan sunny 2018 manual gear gcc": "White Nissan Sunny 2018 manual gear GCC with 152k km, beige interior, and service history available. Very clean and economical daily sedan with practical 1.5L ownership appeal and excellent overall condition.",
    "2008 Nissan Murano GCC Specs": "Pearl white Nissan Murano with GCC specs, 262k km, beige interior, and mid option trim. Excellent condition SUV with no issues reported, lady-driven history, and very well maintained everyday comfort.",
    "2014 Mitsubishi Pajero GCC Specs": "Pearl white Mitsubishi Pajero with GCC specs, 202k km, beige interior, and full option trim. Excellent condition SUV with service history available, practical family usability, and strong all-round everyday dependability.",
    "2016 Nissan Tiida GCC Specs": "Pearl white Nissan Tiida hatchback with GCC specs, 158k km, beige interior, and mid option trim. Clean, well-kept condition with practical cabin space, easy daily usability, and tidy overall presentation.",
    "2013 Lexus IS 250 American Specs": "Black Lexus IS 250 with American specs, clean title, 189k km, beige interior, and full option trim. Excellent condition compact luxury sedan with sporty styling, well maintained history, and a clean upscale cabin feel.",
    "2017 Toyota Camry GCC Specs": "Maroon Toyota Camry SE with GCC specs, 208k km, black leather seats, beige interior, and Sharjah location. Published Toyota information for the 2017 Camry highlights the 2.5L four-cylinder with a six-speed automatic, giving this well-maintained SE a strong mix of comfort and everyday efficiency.",
    "2020 Mitsubishi Pajero GCC Specs": "Red Mitsubishi Pajero with GCC specs, 108k km, beige interior, and service records available. Excellent condition SUV with no maintenance required, strong family practicality, and the durable, high-riding character buyers expect from the Pajero nameplate.",
}

SAMPLE_BLOGS = [
    {
        "title": "How To Buy A Reliable Used Car In Dubai",
        "content": "Start with a realistic budget, inspect service history, compare ownership costs, and test drive before you commit.",
    },
    {
        "title": "Best Sedan Choices For Daily UAE Driving",
        "content": "Sedans remain a smart option for commuters who want comfort, fuel efficiency, and practical resale value.",
    },
    {
        "title": "What Mileage Is Too High For A Used Car?",
        "content": "Mileage should be evaluated alongside maintenance quality, model reputation, and major component condition.",
    },
]

TESTIMONIALS = [
    {
        "name": "Kasun Ranaweera",
        "quote": "The team explained the car clearly, the condition matched the listing, and the buying process felt smooth from start to finish.",
    },
    {
        "name": "Kim Gatapia",
        "quote": "Everything was handled professionally and the prices felt realistic for the UAE used car market.",
    },
    {
        "name": "Aslam Mohammed",
        "quote": "I appreciated the transparency and the way the staff took time to answer every question before I decided.",
    },
]

FAQS = [
    {
        "question": "How do I buy a car through CARWA?",
        "answer": "Browse the listings, filter by the features you want, open the detail page, and contact us through WhatsApp or the contact form.",
    },
    {
        "question": "Can I sell my car on CARWA?",
        "answer": "Yes. Use the add listing form to submit your car details and images, and we review the listing before publishing.",
    },
    {
        "question": "Can I book a test drive or ask for finance?",
        "answer": "Yes. CARWA now includes booking and finance inquiry forms so buyers can register interest directly from the site.",
    },
]


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cars(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            brand TEXT,
            model TEXT,
            year INTEGER,
            price INTEGER,
            mileage INTEGER,
            description TEXT,
            image TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS car_images(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            image TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS wishlist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS blogs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS admins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            name TEXT,
            email TEXT,
            phone TEXT,
            message TEXT,
            lead_type TEXT,
            status TEXT DEFAULT 'New',
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def ensure_columns(table_name, columns):
    conn = get_db()
    existing_columns = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    }

    for column_name, definition in columns.items():
        if column_name not in existing_columns:
            conn.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"
            )

    conn.commit()
    conn.close()


def migrate_db():
    ensure_columns(
        "cars",
        {
            "category": "TEXT DEFAULT 'Sedan'",
            "location": "TEXT DEFAULT 'Dubai'",
            "fuel_type": "TEXT DEFAULT 'Petrol'",
            "transmission": "TEXT DEFAULT 'Automatic'",
            "condition": "TEXT DEFAULT 'Used'",
            "featured": "INTEGER DEFAULT 0",
            "featured_rank": "INTEGER",
            "status": "TEXT DEFAULT 'Available'",
            "seller_name": "TEXT DEFAULT 'CARWA Auto'",
            "seller_phone": "TEXT DEFAULT '+971582119936'",
            "seller_type": "TEXT DEFAULT 'Dealership'",
        },
    )


def seed_sample_cars(force=False):
    conn = get_db()
    existing_count = conn.execute("SELECT COUNT(*) AS total FROM cars").fetchone()["total"]

    if existing_count and not force:
        conn.close()
        return False

    if force:
        conn.execute("DELETE FROM car_images")
        conn.execute("DELETE FROM wishlist")
        conn.execute("DELETE FROM cars")
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('cars', 'car_images', 'wishlist')")

    for car in SAMPLE_CARS:
        conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                car["title"],
                car["brand"],
                car["model"],
                car["year"],
                car["price"],
                car["mileage"],
                car["description"],
                car["image"],
                car["category"],
                car["location"],
                car["fuel_type"],
                car["transmission"],
                car["condition"],
                car["featured"],
                car["status"],
                car.get("seller_name", "CARWA Auto"),
                car.get("seller_phone", "+971582119936"),
                car.get("seller_type", "Dealership"),
            ),
        )

    conn.commit()
    conn.close()
    return True


def prune_unwanted_listings():
    conn = get_db()
    cars_to_remove = conn.execute(
        """
        SELECT id FROM cars
        WHERE brand IN ({brand_placeholders}) OR title IN ({title_placeholders})
        """.format(
            brand_placeholders=",".join("?" for _ in UNWANTED_LISTING_BRANDS),
            title_placeholders=",".join("?" for _ in UNWANTED_LISTING_TITLES),
        ),
        list(UNWANTED_LISTING_BRANDS) + list(UNWANTED_LISTING_TITLES),
    ).fetchall()

    if not cars_to_remove:
        conn.close()
        return False

    car_ids = [row["id"] for row in cars_to_remove]
    placeholders = ",".join("?" for _ in car_ids)
    conn.execute(f"DELETE FROM car_images WHERE car_id IN ({placeholders})", car_ids)
    conn.execute(f"DELETE FROM wishlist WHERE car_id IN ({placeholders})", car_ids)
    conn.execute(f"DELETE FROM leads WHERE car_id IN ({placeholders})", car_ids)
    conn.execute(f"DELETE FROM cars WHERE id IN ({placeholders})", car_ids)
    conn.commit()
    conn.close()
    return True


def normalize_listing_descriptions():
    conn = get_db()
    for title, description in DESCRIPTION_OVERRIDES.items():
        conn.execute(
            "UPDATE cars SET description = ? WHERE title = ?",
            (description, title),
        )
    conn.commit()
    conn.close()
    return True


def seed_sample_blogs(force=False):
    conn = get_db()
    existing_count = conn.execute("SELECT COUNT(*) AS total FROM blogs").fetchone()["total"]

    if existing_count and not force:
        conn.close()
        return False

    if force:
        conn.execute("DELETE FROM blogs")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'blogs'")

    for blog in SAMPLE_BLOGS:
        conn.execute(
            "INSERT INTO blogs (title, content) VALUES (?, ?)",
            (blog["title"], blog["content"]),
        )

    conn.commit()
    conn.close()
    return True


def ensure_sunny_listing():
    conn = get_db()
    sunny = SUNNY_2009_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE brand = ? AND year = ? AND LOWER(model) = LOWER(?)
        LIMIT 1
        """,
        (sunny["brand"], sunny["year"], sunny["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                sunny["title"],
                sunny["brand"],
                sunny["model"],
                sunny["year"],
                sunny["price"],
                sunny["mileage"],
                sunny["description"],
                sunny["image"],
                sunny["category"],
                sunny["location"],
                sunny["fuel_type"],
                sunny["transmission"],
                sunny["condition"],
                sunny["featured"],
                sunny["status"],
                sunny["seller_name"],
                sunny["seller_phone"],
                sunny["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sunny["title"],
                sunny["brand"],
                sunny["model"],
                sunny["year"],
                sunny["price"],
                sunny["mileage"],
                sunny["description"],
                sunny["image"],
                sunny["category"],
                sunny["location"],
                sunny["fuel_type"],
                sunny["transmission"],
                sunny["condition"],
                sunny["featured"],
                sunny["status"],
                sunny["seller_name"],
                sunny["seller_phone"],
                sunny["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in sunny["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_altima_listing():
    conn = get_db()
    altima = ALTIMA_2017_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE brand = ? AND year = ? AND LOWER(model) = LOWER(?)
        LIMIT 1
        """,
        (altima["brand"], altima["year"], altima["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                altima["title"],
                altima["brand"],
                altima["model"],
                altima["year"],
                altima["price"],
                altima["mileage"],
                altima["description"],
                altima["image"],
                altima["category"],
                altima["location"],
                altima["fuel_type"],
                altima["transmission"],
                altima["condition"],
                altima["featured"],
                altima["status"],
                altima["seller_name"],
                altima["seller_phone"],
                altima["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                altima["title"],
                altima["brand"],
                altima["model"],
                altima["year"],
                altima["price"],
                altima["mileage"],
                altima["description"],
                altima["image"],
                altima["category"],
                altima["location"],
                altima["fuel_type"],
                altima["transmission"],
                altima["condition"],
                altima["featured"],
                altima["status"],
                altima["seller_name"],
                altima["seller_phone"],
                altima["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in altima["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_es350_listing():
    conn = get_db()
    es350 = ES350_2010_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE brand = ? AND year = ? AND LOWER(model) = LOWER(?)
        LIMIT 1
        """,
        (es350["brand"], es350["year"], es350["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                es350["title"],
                es350["brand"],
                es350["model"],
                es350["year"],
                es350["price"],
                es350["mileage"],
                es350["description"],
                es350["image"],
                es350["category"],
                es350["location"],
                es350["fuel_type"],
                es350["transmission"],
                es350["condition"],
                es350["featured"],
                es350["status"],
                es350["seller_name"],
                es350["seller_phone"],
                es350["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                es350["title"],
                es350["brand"],
                es350["model"],
                es350["year"],
                es350["price"],
                es350["mileage"],
                es350["description"],
                es350["image"],
                es350["category"],
                es350["location"],
                es350["fuel_type"],
                es350["transmission"],
                es350["condition"],
                es350["featured"],
                es350["status"],
                es350["seller_name"],
                es350["seller_phone"],
                es350["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in es350["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_galant_listing():
    conn = get_db()
    galant = GALANT_2008_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE brand = ? AND year = ? AND LOWER(model) = LOWER(?)
        LIMIT 1
        """,
        (galant["brand"], galant["year"], galant["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                galant["title"],
                galant["brand"],
                galant["model"],
                galant["year"],
                galant["price"],
                galant["mileage"],
                galant["description"],
                galant["image"],
                galant["category"],
                galant["location"],
                galant["fuel_type"],
                galant["transmission"],
                galant["condition"],
                galant["featured"],
                galant["status"],
                galant["seller_name"],
                galant["seller_phone"],
                galant["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                galant["title"],
                galant["brand"],
                galant["model"],
                galant["year"],
                galant["price"],
                galant["mileage"],
                galant["description"],
                galant["image"],
                galant["category"],
                galant["location"],
                galant["fuel_type"],
                galant["transmission"],
                galant["condition"],
                galant["featured"],
                galant["status"],
                galant["seller_name"],
                galant["seller_phone"],
                galant["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in galant["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_is250_listing():
    conn = get_db()
    is250 = IS250_2011_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE brand = ? AND year = ? AND LOWER(model) = LOWER(?)
        LIMIT 1
        """,
        (is250["brand"], is250["year"], is250["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                is250["title"],
                is250["brand"],
                is250["model"],
                is250["year"],
                is250["price"],
                is250["mileage"],
                is250["description"],
                is250["image"],
                is250["category"],
                is250["location"],
                is250["fuel_type"],
                is250["transmission"],
                is250["condition"],
                is250["featured"],
                is250["status"],
                is250["seller_name"],
                is250["seller_phone"],
                is250["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                is250["title"],
                is250["brand"],
                is250["model"],
                is250["year"],
                is250["price"],
                is250["mileage"],
                is250["description"],
                is250["image"],
                is250["category"],
                is250["location"],
                is250["fuel_type"],
                is250["transmission"],
                is250["condition"],
                is250["featured"],
                is250["status"],
                is250["seller_name"],
                is250["seller_phone"],
                is250["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in is250["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_sunny_2015_listing():
    conn = get_db()
    sunny = SUNNY_2015_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (sunny["title"], sunny["brand"], sunny["year"], sunny["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                sunny["title"],
                sunny["brand"],
                sunny["model"],
                sunny["year"],
                sunny["price"],
                sunny["mileage"],
                sunny["description"],
                sunny["image"],
                sunny["category"],
                sunny["location"],
                sunny["fuel_type"],
                sunny["transmission"],
                sunny["condition"],
                sunny["featured"],
                sunny["status"],
                sunny["seller_name"],
                sunny["seller_phone"],
                sunny["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sunny["title"],
                sunny["brand"],
                sunny["model"],
                sunny["year"],
                sunny["price"],
                sunny["mileage"],
                sunny["description"],
                sunny["image"],
                sunny["category"],
                sunny["location"],
                sunny["fuel_type"],
                sunny["transmission"],
                sunny["condition"],
                sunny["featured"],
                sunny["status"],
                sunny["seller_name"],
                sunny["seller_phone"],
                sunny["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in sunny["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_sunny_2020_listing():
    conn = get_db()
    sunny = SUNNY_2020_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (sunny["title"], sunny["brand"], sunny["year"], sunny["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                sunny["title"],
                sunny["brand"],
                sunny["model"],
                sunny["year"],
                sunny["price"],
                sunny["mileage"],
                sunny["description"],
                sunny["image"],
                sunny["category"],
                sunny["location"],
                sunny["fuel_type"],
                sunny["transmission"],
                sunny["condition"],
                sunny["featured"],
                sunny["status"],
                sunny["seller_name"],
                sunny["seller_phone"],
                sunny["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sunny["title"],
                sunny["brand"],
                sunny["model"],
                sunny["year"],
                sunny["price"],
                sunny["mileage"],
                sunny["description"],
                sunny["image"],
                sunny["category"],
                sunny["location"],
                sunny["fuel_type"],
                sunny["transmission"],
                sunny["condition"],
                sunny["featured"],
                sunny["status"],
                sunny["seller_name"],
                sunny["seller_phone"],
                sunny["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in sunny["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_tiida_2007_listing():
    conn = get_db()
    tiida = TIIDA_2007_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (tiida["title"], tiida["brand"], tiida["year"], tiida["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                tiida["title"],
                tiida["brand"],
                tiida["model"],
                tiida["year"],
                tiida["price"],
                tiida["mileage"],
                tiida["description"],
                tiida["image"],
                tiida["category"],
                tiida["location"],
                tiida["fuel_type"],
                tiida["transmission"],
                tiida["condition"],
                tiida["featured"],
                tiida["status"],
                tiida["seller_name"],
                tiida["seller_phone"],
                tiida["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tiida["title"],
                tiida["brand"],
                tiida["model"],
                tiida["year"],
                tiida["price"],
                tiida["mileage"],
                tiida["description"],
                tiida["image"],
                tiida["category"],
                tiida["location"],
                tiida["fuel_type"],
                tiida["transmission"],
                tiida["condition"],
                tiida["featured"],
                tiida["status"],
                tiida["seller_name"],
                tiida["seller_phone"],
                tiida["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in tiida["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_tiida_2016_listing():
    conn = get_db()
    tiida = TIIDA_2016_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (tiida["title"], tiida["brand"], tiida["year"], tiida["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                tiida["title"],
                tiida["brand"],
                tiida["model"],
                tiida["year"],
                tiida["price"],
                tiida["mileage"],
                tiida["description"],
                tiida["image"],
                tiida["category"],
                tiida["location"],
                tiida["fuel_type"],
                tiida["transmission"],
                tiida["condition"],
                tiida["featured"],
                tiida["status"],
                tiida["seller_name"],
                tiida["seller_phone"],
                tiida["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tiida["title"],
                tiida["brand"],
                tiida["model"],
                tiida["year"],
                tiida["price"],
                tiida["mileage"],
                tiida["description"],
                tiida["image"],
                tiida["category"],
                tiida["location"],
                tiida["fuel_type"],
                tiida["transmission"],
                tiida["condition"],
                tiida["featured"],
                tiida["status"],
                tiida["seller_name"],
                tiida["seller_phone"],
                tiida["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in tiida["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_altima_2007_listing():
    conn = get_db()
    altima = ALTIMA_2007_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (altima["title"], altima["brand"], altima["year"], altima["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                altima["title"],
                altima["brand"],
                altima["model"],
                altima["year"],
                altima["price"],
                altima["mileage"],
                altima["description"],
                altima["image"],
                altima["category"],
                altima["location"],
                altima["fuel_type"],
                altima["transmission"],
                altima["condition"],
                altima["featured"],
                altima["status"],
                altima["seller_name"],
                altima["seller_phone"],
                altima["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                altima["title"],
                altima["brand"],
                altima["model"],
                altima["year"],
                altima["price"],
                altima["mileage"],
                altima["description"],
                altima["image"],
                altima["category"],
                altima["location"],
                altima["fuel_type"],
                altima["transmission"],
                altima["condition"],
                altima["featured"],
                altima["status"],
                altima["seller_name"],
                altima["seller_phone"],
                altima["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in altima["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_avalon_2011_listing():
    conn = get_db()
    avalon = AVALON_2011_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (avalon["title"], avalon["brand"], avalon["year"], avalon["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                avalon["title"],
                avalon["brand"],
                avalon["model"],
                avalon["year"],
                avalon["price"],
                avalon["mileage"],
                avalon["description"],
                avalon["image"],
                avalon["category"],
                avalon["location"],
                avalon["fuel_type"],
                avalon["transmission"],
                avalon["condition"],
                avalon["featured"],
                avalon["status"],
                avalon["seller_name"],
                avalon["seller_phone"],
                avalon["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                avalon["title"],
                avalon["brand"],
                avalon["model"],
                avalon["year"],
                avalon["price"],
                avalon["mileage"],
                avalon["description"],
                avalon["image"],
                avalon["category"],
                avalon["location"],
                avalon["fuel_type"],
                avalon["transmission"],
                avalon["condition"],
                avalon["featured"],
                avalon["status"],
                avalon["seller_name"],
                avalon["seller_phone"],
                avalon["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in avalon["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_micra_2020_listing():
    conn = get_db()
    micra = MICRA_2020_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (micra["title"], micra["brand"], micra["year"], micra["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                micra["title"],
                micra["brand"],
                micra["model"],
                micra["year"],
                micra["price"],
                micra["mileage"],
                micra["description"],
                micra["image"],
                micra["category"],
                micra["location"],
                micra["fuel_type"],
                micra["transmission"],
                micra["condition"],
                micra["featured"],
                micra["status"],
                micra["seller_name"],
                micra["seller_phone"],
                micra["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                micra["title"],
                micra["brand"],
                micra["model"],
                micra["year"],
                micra["price"],
                micra["mileage"],
                micra["description"],
                micra["image"],
                micra["category"],
                micra["location"],
                micra["fuel_type"],
                micra["transmission"],
                micra["condition"],
                micra["featured"],
                micra["status"],
                micra["seller_name"],
                micra["seller_phone"],
                micra["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in micra["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_patrol_2015_listing():
    conn = get_db()
    patrol = PATROL_2015_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (patrol["title"], patrol["brand"], patrol["year"], patrol["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                patrol["title"],
                patrol["brand"],
                patrol["model"],
                patrol["year"],
                patrol["price"],
                patrol["mileage"],
                patrol["description"],
                patrol["image"],
                patrol["category"],
                patrol["location"],
                patrol["fuel_type"],
                patrol["transmission"],
                patrol["condition"],
                patrol["featured"],
                patrol["status"],
                patrol["seller_name"],
                patrol["seller_phone"],
                patrol["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patrol["title"],
                patrol["brand"],
                patrol["model"],
                patrol["year"],
                patrol["price"],
                patrol["mileage"],
                patrol["description"],
                patrol["image"],
                patrol["category"],
                patrol["location"],
                patrol["fuel_type"],
                patrol["transmission"],
                patrol["condition"],
                patrol["featured"],
                patrol["status"],
                patrol["seller_name"],
                patrol["seller_phone"],
                patrol["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in patrol["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_rx350_2013_listing():
    conn = get_db()
    rx350 = RX350_2013_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (rx350["title"], rx350["brand"], rx350["year"], rx350["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                rx350["title"],
                rx350["brand"],
                rx350["model"],
                rx350["year"],
                rx350["price"],
                rx350["mileage"],
                rx350["description"],
                rx350["image"],
                rx350["category"],
                rx350["location"],
                rx350["fuel_type"],
                rx350["transmission"],
                rx350["condition"],
                rx350["featured"],
                rx350["status"],
                rx350["seller_name"],
                rx350["seller_phone"],
                rx350["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rx350["title"],
                rx350["brand"],
                rx350["model"],
                rx350["year"],
                rx350["price"],
                rx350["mileage"],
                rx350["description"],
                rx350["image"],
                rx350["category"],
                rx350["location"],
                rx350["fuel_type"],
                rx350["transmission"],
                rx350["condition"],
                rx350["featured"],
                rx350["status"],
                rx350["seller_name"],
                rx350["seller_phone"],
                rx350["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in rx350["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_red_is250_2010_listing():
    conn = get_db()
    red_is = RED_IS250_2010_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (red_is["title"], red_is["brand"], red_is["year"], red_is["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                red_is["title"],
                red_is["brand"],
                red_is["model"],
                red_is["year"],
                red_is["price"],
                red_is["mileage"],
                red_is["description"],
                red_is["image"],
                red_is["category"],
                red_is["location"],
                red_is["fuel_type"],
                red_is["transmission"],
                red_is["condition"],
                red_is["featured"],
                red_is["status"],
                red_is["seller_name"],
                red_is["seller_phone"],
                red_is["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                red_is["title"],
                red_is["brand"],
                red_is["model"],
                red_is["year"],
                red_is["price"],
                red_is["mileage"],
                red_is["description"],
                red_is["image"],
                red_is["category"],
                red_is["location"],
                red_is["fuel_type"],
                red_is["transmission"],
                red_is["condition"],
                red_is["featured"],
                red_is["status"],
                red_is["seller_name"],
                red_is["seller_phone"],
                red_is["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in red_is["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_blue_is250_2011_listing():
    conn = get_db()
    blue_is = BLUE_IS250_2011_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (blue_is["title"], blue_is["brand"], blue_is["year"], blue_is["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                blue_is["title"],
                blue_is["brand"],
                blue_is["model"],
                blue_is["year"],
                blue_is["price"],
                blue_is["mileage"],
                blue_is["description"],
                blue_is["image"],
                blue_is["category"],
                blue_is["location"],
                blue_is["fuel_type"],
                blue_is["transmission"],
                blue_is["condition"],
                blue_is["featured"],
                blue_is["status"],
                blue_is["seller_name"],
                blue_is["seller_phone"],
                blue_is["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                blue_is["title"],
                blue_is["brand"],
                blue_is["model"],
                blue_is["year"],
                blue_is["price"],
                blue_is["mileage"],
                blue_is["description"],
                blue_is["image"],
                blue_is["category"],
                blue_is["location"],
                blue_is["fuel_type"],
                blue_is["transmission"],
                blue_is["condition"],
                blue_is["featured"],
                blue_is["status"],
                blue_is["seller_name"],
                blue_is["seller_phone"],
                blue_is["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in blue_is["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_is250_2013_listing():
    conn = get_db()
    is250 = IS250_2013_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (is250["title"], is250["brand"], is250["year"], is250["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                is250["title"],
                is250["brand"],
                is250["model"],
                is250["year"],
                is250["price"],
                is250["mileage"],
                is250["description"],
                is250["image"],
                is250["category"],
                is250["location"],
                is250["fuel_type"],
                is250["transmission"],
                is250["condition"],
                is250["featured"],
                is250["status"],
                is250["seller_name"],
                is250["seller_phone"],
                is250["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                is250["title"],
                is250["brand"],
                is250["model"],
                is250["year"],
                is250["price"],
                is250["mileage"],
                is250["description"],
                is250["image"],
                is250["category"],
                is250["location"],
                is250["fuel_type"],
                is250["transmission"],
                is250["condition"],
                is250["featured"],
                is250["status"],
                is250["seller_name"],
                is250["seller_phone"],
                is250["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in is250["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_camry_2017_listing():
    conn = get_db()
    camry = CAMRY_2017_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (camry["title"], camry["brand"], camry["year"], camry["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                camry["title"],
                camry["brand"],
                camry["model"],
                camry["year"],
                camry["price"],
                camry["mileage"],
                camry["description"],
                camry["image"],
                camry["category"],
                camry["location"],
                camry["fuel_type"],
                camry["transmission"],
                camry["condition"],
                camry["featured"],
                camry["status"],
                camry["seller_name"],
                camry["seller_phone"],
                camry["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                camry["title"],
                camry["brand"],
                camry["model"],
                camry["year"],
                camry["price"],
                camry["mileage"],
                camry["description"],
                camry["image"],
                camry["category"],
                camry["location"],
                camry["fuel_type"],
                camry["transmission"],
                camry["condition"],
                camry["featured"],
                camry["status"],
                camry["seller_name"],
                camry["seller_phone"],
                camry["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in camry["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_ford_explorer_2014_listing():
    conn = get_db()
    explorer = FORD_EXPLORER_2014_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (explorer["title"], explorer["brand"], explorer["year"], explorer["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                explorer["title"],
                explorer["brand"],
                explorer["model"],
                explorer["year"],
                explorer["price"],
                explorer["mileage"],
                explorer["description"],
                explorer["image"],
                explorer["category"],
                explorer["location"],
                explorer["fuel_type"],
                explorer["transmission"],
                explorer["condition"],
                explorer["featured"],
                explorer["status"],
                explorer["seller_name"],
                explorer["seller_phone"],
                explorer["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                explorer["title"],
                explorer["brand"],
                explorer["model"],
                explorer["year"],
                explorer["price"],
                explorer["mileage"],
                explorer["description"],
                explorer["image"],
                explorer["category"],
                explorer["location"],
                explorer["fuel_type"],
                explorer["transmission"],
                explorer["condition"],
                explorer["featured"],
                explorer["status"],
                explorer["seller_name"],
                explorer["seller_phone"],
                explorer["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in explorer["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_sentra_2016_listing():
    conn = get_db()
    sentra = SENTRA_2016_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (sentra["title"], sentra["brand"], sentra["year"], sentra["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                sentra["title"],
                sentra["brand"],
                sentra["model"],
                sentra["year"],
                sentra["price"],
                sentra["mileage"],
                sentra["description"],
                sentra["image"],
                sentra["category"],
                sentra["location"],
                sentra["fuel_type"],
                sentra["transmission"],
                sentra["condition"],
                sentra["featured"],
                sentra["status"],
                sentra["seller_name"],
                sentra["seller_phone"],
                sentra["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sentra["title"],
                sentra["brand"],
                sentra["model"],
                sentra["year"],
                sentra["price"],
                sentra["mileage"],
                sentra["description"],
                sentra["image"],
                sentra["category"],
                sentra["location"],
                sentra["fuel_type"],
                sentra["transmission"],
                sentra["condition"],
                sentra["featured"],
                sentra["status"],
                sentra["seller_name"],
                sentra["seller_phone"],
                sentra["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in sentra["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_avalon_2009_listing():
    conn = get_db()
    avalon = AVALON_2009_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (avalon["title"], avalon["brand"], avalon["year"], avalon["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                avalon["title"],
                avalon["brand"],
                avalon["model"],
                avalon["year"],
                avalon["price"],
                avalon["mileage"],
                avalon["description"],
                avalon["image"],
                avalon["category"],
                avalon["location"],
                avalon["fuel_type"],
                avalon["transmission"],
                avalon["condition"],
                avalon["featured"],
                avalon["status"],
                avalon["seller_name"],
                avalon["seller_phone"],
                avalon["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                avalon["title"],
                avalon["brand"],
                avalon["model"],
                avalon["year"],
                avalon["price"],
                avalon["mileage"],
                avalon["description"],
                avalon["image"],
                avalon["category"],
                avalon["location"],
                avalon["fuel_type"],
                avalon["transmission"],
                avalon["condition"],
                avalon["featured"],
                avalon["status"],
                avalon["seller_name"],
                avalon["seller_phone"],
                avalon["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in avalon["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_sunny_2018_listing():
    conn = get_db()
    sunny = SUNNY_2018_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE LOWER(title) = LOWER(?) OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (sunny["title"], sunny["brand"], sunny["year"], sunny["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                sunny["title"],
                sunny["brand"],
                sunny["model"],
                sunny["year"],
                sunny["price"],
                sunny["mileage"],
                sunny["description"],
                sunny["image"],
                sunny["category"],
                sunny["location"],
                sunny["fuel_type"],
                sunny["transmission"],
                sunny["condition"],
                sunny["featured"],
                sunny["status"],
                sunny["seller_name"],
                sunny["seller_phone"],
                sunny["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sunny["title"],
                sunny["brand"],
                sunny["model"],
                sunny["year"],
                sunny["price"],
                sunny["mileage"],
                sunny["description"],
                sunny["image"],
                sunny["category"],
                sunny["location"],
                sunny["fuel_type"],
                sunny["transmission"],
                sunny["condition"],
                sunny["featured"],
                sunny["status"],
                sunny["seller_name"],
                sunny["seller_phone"],
                sunny["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in sunny["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_murano_2008_listing():
    conn = get_db()
    murano = MURANO_2008_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (murano["title"], murano["brand"], murano["year"], murano["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                murano["title"],
                murano["brand"],
                murano["model"],
                murano["year"],
                murano["price"],
                murano["mileage"],
                murano["description"],
                murano["image"],
                murano["category"],
                murano["location"],
                murano["fuel_type"],
                murano["transmission"],
                murano["condition"],
                murano["featured"],
                murano["status"],
                murano["seller_name"],
                murano["seller_phone"],
                murano["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                murano["title"],
                murano["brand"],
                murano["model"],
                murano["year"],
                murano["price"],
                murano["mileage"],
                murano["description"],
                murano["image"],
                murano["category"],
                murano["location"],
                murano["fuel_type"],
                murano["transmission"],
                murano["condition"],
                murano["featured"],
                murano["status"],
                murano["seller_name"],
                murano["seller_phone"],
                murano["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in murano["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def ensure_pajero_2014_listing():
    conn = get_db()
    pajero = PAJERO_2014_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (pajero["title"], pajero["brand"], pajero["year"], pajero["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                pajero["title"],
                pajero["brand"],
                pajero["model"],
                pajero["year"],
                pajero["price"],
                pajero["mileage"],
                pajero["description"],
                pajero["image"],
                pajero["category"],
                pajero["location"],
                pajero["fuel_type"],
                pajero["transmission"],
                pajero["condition"],
                pajero["featured"],
                pajero["status"],
                pajero["seller_name"],
                pajero["seller_phone"],
                pajero["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pajero["title"],
                pajero["brand"],
                pajero["model"],
                pajero["year"],
                pajero["price"],
                pajero["mileage"],
                pajero["description"],
                pajero["image"],
                pajero["category"],
                pajero["location"],
                pajero["fuel_type"],
                pajero["transmission"],
                pajero["condition"],
                pajero["featured"],
                pajero["status"],
                pajero["seller_name"],
                pajero["seller_phone"],
                pajero["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in pajero["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def seed_admin_user():
    conn = get_db()
    existing_admin = conn.execute(
        "SELECT id FROM admins WHERE username = ?",
        (DEFAULT_ADMIN["username"],),
    ).fetchone()

    if existing_admin:
        conn.close()
        return False

    password_hash = generate_password_hash(DEFAULT_ADMIN["password"])
    conn.execute(
        "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
        (DEFAULT_ADMIN["username"], password_hash),
    )
    conn.commit()
    conn.close()
    return True


def ensure_pajero_2020_listing():
    conn = get_db()
    pajero = PAJERO_2020_LISTING
    existing_car = conn.execute(
        """
        SELECT id FROM cars
        WHERE title = ? OR (brand = ? AND year = ? AND LOWER(model) = LOWER(?))
        LIMIT 1
        """,
        (pajero["title"], pajero["brand"], pajero["year"], pajero["model"]),
    ).fetchone()

    if existing_car:
        car_id = existing_car["id"]
        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?,
                seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                pajero["title"],
                pajero["brand"],
                pajero["model"],
                pajero["year"],
                pajero["price"],
                pajero["mileage"],
                pajero["description"],
                pajero["image"],
                pajero["category"],
                pajero["location"],
                pajero["fuel_type"],
                pajero["transmission"],
                pajero["condition"],
                pajero["featured"],
                pajero["status"],
                pajero["seller_name"],
                pajero["seller_phone"],
                pajero["seller_type"],
                car_id,
            ),
        )
        conn.execute("DELETE FROM car_images WHERE car_id = ?", (car_id,))
    else:
        cursor = conn.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pajero["title"],
                pajero["brand"],
                pajero["model"],
                pajero["year"],
                pajero["price"],
                pajero["mileage"],
                pajero["description"],
                pajero["image"],
                pajero["category"],
                pajero["location"],
                pajero["fuel_type"],
                pajero["transmission"],
                pajero["condition"],
                pajero["featured"],
                pajero["status"],
                pajero["seller_name"],
                pajero["seller_phone"],
                pajero["seller_type"],
            ),
        )
        car_id = cursor.lastrowid

    for image in pajero["gallery_images"]:
        conn.execute(
            "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
            (car_id, image),
        )

    conn.commit()
    conn.close()
    return True


def bootstrap_data():
    init_db()
    migrate_db()
    seed_sample_cars()
    prune_unwanted_listings()
    seed_sample_blogs()
    ensure_sunny_listing()
    ensure_altima_listing()
    ensure_es350_listing()
    ensure_galant_listing()
    ensure_is250_listing()
    ensure_sunny_2015_listing()
    ensure_sunny_2020_listing()
    ensure_tiida_2007_listing()
    ensure_tiida_2016_listing()
    ensure_altima_2007_listing()
    ensure_avalon_2011_listing()
    ensure_micra_2020_listing()
    ensure_patrol_2015_listing()
    ensure_rx350_2013_listing()
    ensure_red_is250_2010_listing()
    ensure_blue_is250_2011_listing()
    ensure_is250_2013_listing()
    ensure_camry_2017_listing()
    ensure_ford_explorer_2014_listing()
    ensure_sentra_2016_listing()
    ensure_avalon_2009_listing()
    ensure_sunny_2018_listing()
    ensure_murano_2008_listing()
    ensure_pajero_2014_listing()
    ensure_pajero_2020_listing()
    normalize_listing_descriptions()
    seed_admin_user()
    migrate_admin_passwords()


def fetch_search_options():
    conn = get_db()
    fuel_types = conn.execute("SELECT DISTINCT fuel_type FROM cars ORDER BY fuel_type").fetchall()
    transmissions = conn.execute(
        "SELECT DISTINCT transmission FROM cars ORDER BY transmission"
    ).fetchall()
    conditions = conn.execute(
        "SELECT DISTINCT condition FROM cars ORDER BY condition"
    ).fetchall()
    conn.close()
    return {
        "brands": ALL_CAR_BRANDS,
        "categories": ALL_CAR_CATEGORIES,
        "locations": [
            "Abu Dhabi",
            "Dubai",
            "Sharjah",
            "Ajman",
            "Ras Al Khaimah",
            "Fujairah",
            "Umm Al Quwain",
        ],
        "fuel_types": [row["fuel_type"] for row in fuel_types],
        "transmissions": [row["transmission"] for row in transmissions],
        "conditions": [row["condition"] for row in conditions],
        "price_floor": PRICE_FLOOR,
        "price_ceiling": PRICE_CEILING,
    }


def fetch_stats():
    conn = get_db()
    total_cars = conn.execute(
        "SELECT COUNT(*) AS total FROM cars WHERE status != 'Archived'"
    ).fetchone()["total"]
    featured_cars = conn.execute(
        "SELECT COUNT(*) AS total FROM cars WHERE featured = 1 AND status = 'Available'"
    ).fetchone()["total"]
    brand_count = conn.execute(
        "SELECT COUNT(DISTINCT brand) AS total FROM cars"
    ).fetchone()["total"]
    avg_price = conn.execute("SELECT AVG(price) AS avg_price FROM cars").fetchone()["avg_price"]
    lead_count = conn.execute("SELECT COUNT(*) AS total FROM leads").fetchone()["total"]
    conn.close()
    return {
        "total_cars": total_cars,
        "featured_cars": featured_cars,
        "brand_count": brand_count,
        "avg_price": int(avg_price or 0),
        "lead_count": lead_count,
    }


def fetch_car_options():
    conn = get_db()
    options = conn.execute(
        "SELECT id, title, year, price FROM cars WHERE status = 'Available' ORDER BY featured DESC, id DESC"
    ).fetchall()
    conn.close()
    return options


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password_hash, password):
    if password_hash.startswith("pbkdf2:") or password_hash.startswith("scrypt:"):
        return check_password_hash(password_hash, password)

    legacy_password = DEFAULT_ADMIN["password"]
    return password == legacy_password


def migrate_admin_passwords():
    conn = get_db()
    admins = conn.execute("SELECT id, password_hash FROM admins").fetchall()

    for admin in admins:
        password_hash = admin["password_hash"] or ""
        if password_hash.startswith("pbkdf2:") or password_hash.startswith("scrypt:"):
            continue

        conn.execute(
            "UPDATE admins SET password_hash = ? WHERE id = ?",
            (hash_password(DEFAULT_ADMIN["password"]), admin["id"]),
        )

    conn.commit()
    conn.close()


def build_car_search_query(args):
    clauses = []
    params = []

    keyword = args.get("keyword", "").strip()
    brand = args.get("brand", "").strip()
    category = args.get("category", "").strip()
    location = args.get("location", "").strip()
    location_query = args.get("location_query", "").strip()
    model = args.get("model", "").strip()
    year = args.get("year", "").strip()
    price = args.get("price", "").strip()
    min_price = args.get("min_price", "").strip()
    max_price = args.get("max_price", "").strip() or price
    fuel_type = args.get("fuel_type", "").strip()
    transmission = args.get("transmission", "").strip()
    condition = args.get("condition", "").strip()
    sort_by = args.get("sort", "").strip()

    if keyword:
        clauses.append("(LOWER(title) LIKE ? OR LOWER(brand) LIKE ? OR LOWER(model) LIKE ?)")
        keyword_like = f"%{keyword.lower()}%"
        params.extend([keyword_like, keyword_like, keyword_like])

    if brand and brand not in {"Any Brand", "All"}:
        clauses.append("brand = ?")
        params.append(brand)

    if category and category not in {"Any Category", "All"}:
        clauses.append("category = ?")
        params.append(category)

    if location and location not in {"Any Location", "All"}:
        clauses.append("location = ?")
        params.append(location)

    if location_query:
        clauses.append("LOWER(location) LIKE ?")
        params.append(f"%{location_query.lower()}%")

    if model:
        clauses.append("LOWER(model) LIKE ?")
        params.append(f"%{model.lower()}%")

    if year.isdigit():
        clauses.append("year = ?")
        params.append(int(year))

    if min_price.isdigit():
        clauses.append("price >= ?")
        params.append(max(int(min_price), PRICE_FLOOR))

    if max_price.isdigit():
        clauses.append("price <= ?")
        params.append(min(int(max_price), PRICE_CEILING))

    if fuel_type and fuel_type not in {"Any Fuel Type", "All"}:
        clauses.append("fuel_type = ?")
        params.append(fuel_type)

    if transmission and transmission not in {"Any Transmission", "All"}:
        clauses.append("transmission = ?")
        params.append(transmission)

    if condition and condition not in {"Any Condition", "All"}:
        clauses.append("condition = ?")
        params.append(condition)

    query = "SELECT * FROM cars WHERE status = 'Available'"
    if clauses:
        query += " AND " + " AND ".join(clauses)

    sort_map = {
        "price_low": "price ASC, id DESC",
        "price_high": "price DESC, id DESC",
        "year_new": "year DESC, id DESC",
        "year_old": "year ASC, id DESC",
        "mileage_low": "mileage ASC, id DESC",
        "latest": "featured DESC, id DESC",
    }
    query += " ORDER BY " + sort_map.get(sort_by, "featured DESC, id DESC")

    return query, params


def create_lead(car_id, name, email, phone, message, lead_type):
    conn = get_db()
    conn.execute(
        """
        INSERT INTO leads (car_id, name, email, phone, message, lead_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            car_id,
            name,
            email,
            phone,
            message,
            lead_type,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


def is_admin_logged_in():
    return bool(session.get("admin_username"))


def build_page_url(args, page_number):
    preserved_args = []
    for key, value in args.items():
        if key == "page" or value == "":
            continue
        preserved_args.append((key, value))
    preserved_args.append(("page", page_number))
    return "/cars?" + urlencode(preserved_args)


def merge_main_and_gallery_images(main_image, gallery_images):
    merged_images = []
    seen = set()
    for image in [main_image] + list(gallery_images):
        if not image or image in seen:
            continue
        seen.add(image)
        merged_images.append(image)
    return merged_images


def parse_int(value, default=None):
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def normalize_text(value):
    return (value or "").strip().lower()


def round_to_nearest_500(value):
    return int(round(value / 500) * 500)


def fetch_available_cars():
    conn = get_db()
    cars = conn.execute(
        """
        SELECT *
        FROM cars
        WHERE status = 'Available'
        ORDER BY featured DESC, id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(car) for car in cars]


def condition_factor(condition):
    factors = {
        "new": 1.12,
        "excellent": 1.06,
        "used": 1.0,
        "fair": 0.92,
        "damaged": 0.78,
    }
    return factors.get(normalize_text(condition), 1.0)


def fuel_factor(fuel_type):
    factors = {
        "electric": 1.08,
        "hybrid": 1.05,
        "petrol": 1.0,
        "diesel": 0.97,
    }
    return factors.get(normalize_text(fuel_type), 1.0)


def transmission_factor(transmission):
    factors = {
        "automatic": 1.02,
        "manual": 0.96,
    }
    return factors.get(normalize_text(transmission), 1.0)


def build_vehicle_profile(form_data):
    return {
        "brand": form_data.get("brand", "").strip(),
        "model": form_data.get("model", "").strip(),
        "year": parse_int(form_data.get("year")),
        "mileage": parse_int(form_data.get("mileage")),
        "category": form_data.get("category", "").strip(),
        "location": form_data.get("location", "").strip(),
        "fuel_type": form_data.get("fuel_type", "").strip() or "Petrol",
        "transmission": form_data.get("transmission", "").strip() or "Automatic",
        "condition": form_data.get("condition", "").strip() or "Used",
    }


def comparable_match_score(vehicle, car):
    score = 0
    brand = normalize_text(vehicle["brand"])
    model = normalize_text(vehicle["model"])
    car_brand = normalize_text(car.get("brand"))
    car_model = normalize_text(car.get("model"))
    car_title = normalize_text(car.get("title"))

    if brand and brand == car_brand:
        score += 28
    if model and (model == car_model or model in car_title):
        score += 30
    if vehicle["category"] and normalize_text(vehicle["category"]) == normalize_text(car.get("category")):
        score += 12
    if vehicle["location"] and normalize_text(vehicle["location"]) == normalize_text(car.get("location")):
        score += 6
    if vehicle["fuel_type"] and normalize_text(vehicle["fuel_type"]) == normalize_text(car.get("fuel_type")):
        score += 5
    if vehicle["transmission"] and normalize_text(vehicle["transmission"]) == normalize_text(car.get("transmission")):
        score += 5
    if vehicle["condition"] and normalize_text(vehicle["condition"]) == normalize_text(car.get("condition")):
        score += 4

    car_year = parse_int(car.get("year"), vehicle["year"])
    car_mileage = parse_int(car.get("mileage"), vehicle["mileage"])
    if vehicle["year"] and car_year:
        score += max(0, 16 - (abs(vehicle["year"] - car_year) * 3))
    if vehicle["mileage"] is not None and car_mileage is not None:
        score += max(0, 14 - (abs(vehicle["mileage"] - car_mileage) / 20000 * 3))

    return max(1, score)


def adjusted_comparable_price(vehicle, car):
    price = parse_int(car.get("price"), PRICE_FLOOR) or PRICE_FLOOR
    car_year = parse_int(car.get("year"), vehicle["year"]) or vehicle["year"]
    car_mileage = parse_int(car.get("mileage"), vehicle["mileage"]) or vehicle["mileage"]

    adjusted_price = float(price)

    if vehicle["year"] and car_year:
        yearly_adjustment = min(max(price * 0.055, 1200), 5200)
        adjusted_price += (vehicle["year"] - car_year) * yearly_adjustment

    if vehicle["mileage"] is not None and car_mileage is not None:
        mileage_adjustment = min(max(price * 0.012, 250), 950)
        adjusted_price -= ((vehicle["mileage"] - car_mileage) / 10000) * mileage_adjustment

    adjusted_price *= condition_factor(vehicle["condition"]) / condition_factor(car.get("condition"))
    adjusted_price *= fuel_factor(vehicle["fuel_type"]) / fuel_factor(car.get("fuel_type"))
    adjusted_price *= transmission_factor(vehicle["transmission"]) / transmission_factor(car.get("transmission"))

    return max(PRICE_FLOOR, round_to_nearest_500(adjusted_price))


def build_price_evaluation(form_data):
    vehicle = build_vehicle_profile(form_data)
    current_year = datetime.now().year
    errors = []

    if not vehicle["year"] or vehicle["year"] < 1980 or vehicle["year"] > current_year + 1:
        errors.append(f"Enter a valid model year between 1980 and {current_year + 1}.")
    if vehicle["mileage"] is None or vehicle["mileage"] < 0:
        errors.append("Enter a valid mileage value.")

    if errors:
        return {"errors": errors, "inputs": vehicle}

    all_cars = fetch_available_cars()
    scored_comparables = []

    for car in all_cars:
        score = comparable_match_score(vehicle, car)
        adjusted_price = adjusted_comparable_price(vehicle, car)
        if score >= 18:
            comparable = dict(car)
            comparable["match_score"] = min(100, int(round(score)))
            comparable["adjusted_price"] = adjusted_price
            scored_comparables.append(comparable)

    if not scored_comparables:
        for car in all_cars:
            comparable = dict(car)
            comparable["match_score"] = 12
            comparable["adjusted_price"] = adjusted_comparable_price(vehicle, car)
            scored_comparables.append(comparable)

    scored_comparables = sorted(
        scored_comparables,
        key=lambda car: (car["match_score"], -abs((parse_int(car.get("price"), 0) or 0) - PRICE_FLOOR)),
        reverse=True,
    )[:8]

    total_weight = sum(car["match_score"] for car in scored_comparables) or 1
    estimated_price = sum(
        car["adjusted_price"] * car["match_score"] for car in scored_comparables
    ) / total_weight
    estimated_price = max(PRICE_FLOOR, round_to_nearest_500(estimated_price))

    top_score = scored_comparables[0]["match_score"] if scored_comparables else 0
    confidence = min(94, int(46 + (len(scored_comparables) * 4) + (top_score * 0.32)))
    if top_score >= 78 and len(scored_comparables) >= 3:
        confidence_label = "High"
    elif top_score >= 48:
        confidence_label = "Medium"
    else:
        confidence_label = "Limited"

    spread = 0.1 if confidence_label == "High" else 0.14 if confidence_label == "Medium" else 0.18
    range_low = max(PRICE_FLOOR, round_to_nearest_500(estimated_price * (1 - spread)))
    range_high = round_to_nearest_500(estimated_price * (1 + spread))

    for car in scored_comparables:
        car["market_gap"] = parse_int(car.get("price"), 0) - estimated_price

    return {
        "errors": [],
        "inputs": vehicle,
        "estimate": estimated_price,
        "range_low": range_low,
        "range_high": range_high,
        "confidence": confidence,
        "confidence_label": confidence_label,
        "comparables": scored_comparables[:5],
        "comparable_count": len(scored_comparables),
        "notes": [
            "Estimate is based on active CARWA listings with adjustments for year, mileage, fuel, transmission, and condition.",
            "The range accounts for negotiation room, service history, accident history, and inspection results.",
        ],
    }


def has_recommendation_preferences(args):
    preference_keys = [
        "budget",
        "category",
        "brand",
        "location",
        "fuel_type",
        "transmission",
        "min_year",
        "max_mileage",
    ]
    has_filters = any(str(args.get(key, "")).strip() for key in preference_keys)
    priority = str(args.get("priority", "")).strip()
    return has_filters or priority not in {"", "balanced"}


def recommendation_reason(reasons, reason):
    if reason not in reasons:
        reasons.append(reason)


def score_recommendation(car, preferences, average_price):
    score = 34.0
    reasons = []
    budget = parse_int(preferences.get("budget"))
    min_year = parse_int(preferences.get("min_year"))
    max_mileage = parse_int(preferences.get("max_mileage"))
    priority = preferences.get("priority", "balanced")
    price = parse_int(car.get("price"), 0) or 0
    year = parse_int(car.get("year"), 0) or 0
    mileage = parse_int(car.get("mileage"), 0) or 0

    if budget:
        if price <= budget:
            score += 24
            recommendation_reason(reasons, "Within your budget")
            if price <= budget * 0.88:
                score += 4
                recommendation_reason(reasons, "Leaves budget room")
        else:
            over_budget = (price - budget) / budget
            score -= min(26, over_budget * 80)
            if over_budget <= 0.12:
                recommendation_reason(reasons, "Slightly above budget")

    if preferences.get("category") and normalize_text(preferences.get("category")) == normalize_text(car.get("category")):
        score += 15
        recommendation_reason(reasons, "Matches preferred body type")
    if preferences.get("brand") and normalize_text(preferences.get("brand")) == normalize_text(car.get("brand")):
        score += 11
        recommendation_reason(reasons, "Matches preferred brand")
    if preferences.get("location") and normalize_text(preferences.get("location")) == normalize_text(car.get("location")):
        score += 8
        recommendation_reason(reasons, "Available in preferred location")
    if preferences.get("fuel_type") and normalize_text(preferences.get("fuel_type")) == normalize_text(car.get("fuel_type")):
        score += 5
        recommendation_reason(reasons, "Preferred fuel type")
    if preferences.get("transmission") and normalize_text(preferences.get("transmission")) == normalize_text(car.get("transmission")):
        score += 5
        recommendation_reason(reasons, "Preferred transmission")

    if min_year:
        if year >= min_year:
            score += 10
            recommendation_reason(reasons, "Meets minimum year")
        else:
            score -= min(14, (min_year - year) * 3)

    if max_mileage:
        if mileage <= max_mileage:
            score += 10
            recommendation_reason(reasons, "Mileage fits your limit")
        else:
            score -= min(16, ((mileage - max_mileage) / 20000) * 3)

    if priority == "best_value":
        if average_price and price < average_price:
            score += min(11, ((average_price - price) / average_price) * 18)
            recommendation_reason(reasons, "Strong value versus inventory average")
        if mileage and year:
            score += max(0, min(7, (year - 2008) * 0.45 - (mileage / 120000)))
    elif priority == "low_mileage":
        score += max(0, min(14, 14 - (mileage / 25000)))
        recommendation_reason(reasons, "Prioritizes lower mileage")
    elif priority == "newest":
        score += max(0, min(14, (year - 2010) * 1.2))
        recommendation_reason(reasons, "Prioritizes newer model year")
    elif priority == "lowest_price":
        if average_price and price:
            score += max(0, min(14, ((average_price - price) / average_price) * 20))
        recommendation_reason(reasons, "Prioritizes lower price")

    if not reasons:
        recommendation_reason(reasons, "Balanced match from available inventory")

    scored_car = dict(car)
    scored_car["match_score"] = max(0, min(100, int(round(score))))
    scored_car["match_reasons"] = reasons[:4]
    scored_car["budget_gap"] = budget - price if budget else None
    return scored_car


def build_personalized_recommendations(args, limit=9):
    preferences = {
        "budget": args.get("budget", "").strip(),
        "category": args.get("category", "").strip(),
        "brand": args.get("brand", "").strip(),
        "location": args.get("location", "").strip(),
        "fuel_type": args.get("fuel_type", "").strip(),
        "transmission": args.get("transmission", "").strip(),
        "min_year": args.get("min_year", "").strip(),
        "max_mileage": args.get("max_mileage", "").strip(),
        "priority": args.get("priority", "balanced").strip() or "balanced",
    }
    cars = fetch_available_cars()
    prices = [parse_int(car.get("price"), 0) or 0 for car in cars]
    average_price = sum(prices) / len(prices) if prices else 0
    scored_cars = [
        score_recommendation(car, preferences, average_price)
        for car in cars
    ]
    return sorted(
        scored_cars,
        key=lambda car: (car["match_score"], car.get("featured", 0), car.get("year", 0)),
        reverse=True,
    )[:limit]


bootstrap_data()


@app.context_processor
def inject_app_globals():
    return {
        "app_name": APP_NAME,
        "app_version": "Version 7",
    }


@app.route("/")
def home():
    conn = get_db()
    search_options = fetch_search_options()
    featured_cars = conn.execute(
        """
        SELECT * FROM cars
        WHERE status = 'Available'
        ORDER BY
            featured DESC,
            CASE WHEN featured_rank IS NULL THEN 1 ELSE 0 END,
            featured_rank ASC,
            id DESC
        LIMIT ?
        """
    , (HOME_FEATURED_CARS_LIMIT,)).fetchall()
    featured_cars = [dict(car) for car in featured_cars]
    if featured_cars:
        featured_ids = [car["id"] for car in featured_cars]
        placeholders = ",".join("?" for _ in featured_ids)
        gallery_rows = conn.execute(
            f"""
            SELECT car_id, image
            FROM car_images
            WHERE car_id IN ({placeholders})
            ORDER BY id ASC
            """,
            featured_ids,
        ).fetchall()
        gallery_map = {car_id: [] for car_id in featured_ids}
        for row in gallery_rows:
            gallery_map.setdefault(row["car_id"], []).append(row["image"])
        for car in featured_cars:
            car["featured_images"] = merge_main_and_gallery_images(
                car["image"],
                gallery_map.get(car["id"], []),
            )
    category_counts = conn.execute(
        """
        SELECT category, COUNT(*) AS total
        FROM cars
        WHERE status = 'Available'
        GROUP BY category
        ORDER BY total DESC, category ASC
        """
    ).fetchall()
    latest_blogs = conn.execute(
        "SELECT * FROM blogs ORDER BY id DESC LIMIT 3"
    ).fetchall()
    conn.close()

    return render_template(
        "index.html",
        cars=featured_cars,
        category_counts=category_counts,
        featured_categories=search_options["categories"],
        latest_blogs=latest_blogs,
        testimonials=TESTIMONIALS,
        stats=fetch_stats(),
        search_options=search_options,
    )


@app.route("/cars")
def cars():
    query, params = build_car_search_query(request.args)
    conn = get_db()
    total_results = conn.execute(
        f"SELECT COUNT(*) AS total FROM ({query})",
        params,
    ).fetchone()["total"]
    current_page = request.args.get("page", "1")
    page = int(current_page) if current_page.isdigit() and int(current_page) > 0 else 1
    total_pages = max((total_results + LISTINGS_PER_PAGE - 1) // LISTINGS_PER_PAGE, 1)
    page = min(page, total_pages)
    offset = (page - 1) * LISTINGS_PER_PAGE
    paginated_query = query + " LIMIT ? OFFSET ?"
    results = conn.execute(
        paginated_query,
        params + [LISTINGS_PER_PAGE, offset],
    ).fetchall()
    results = [dict(car) for car in results]
    if results:
        car_ids = [car["id"] for car in results]
        placeholders = ",".join("?" for _ in car_ids)
        gallery_rows = conn.execute(
            f"""
            SELECT car_id, image
            FROM car_images
            WHERE car_id IN ({placeholders})
            ORDER BY id ASC
            """,
            car_ids,
        ).fetchall()
        gallery_map = {car_id: [] for car_id in car_ids}
        for row in gallery_rows:
            gallery_map.setdefault(row["car_id"], []).append(row["image"])
        for car in results:
            car["listing_images"] = merge_main_and_gallery_images(
                car["image"],
                gallery_map.get(car["id"], []),
            )
    conn.close()

    pagination = {
        "page": page,
        "total_pages": total_pages,
        "total_results": total_results,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_url": build_page_url(request.args, page - 1) if page > 1 else None,
        "next_url": build_page_url(request.args, page + 1) if page < total_pages else None,
    }

    return render_template(
        "cars.html",
        cars=results,
        search_options=fetch_search_options(),
        current_filters=request.args,
        pagination=pagination,
    )


@app.route("/car/<int:id>")
def car_details(id):
    conn = get_db()
    car = conn.execute("SELECT * FROM cars WHERE id = ?", (id,)).fetchone()
    images = conn.execute(
        "SELECT * FROM car_images WHERE car_id = ?",
        (id,),
    ).fetchall()
    related_cars = conn.execute(
        """
        SELECT * FROM cars
        WHERE category = (
            SELECT category FROM cars WHERE id = ?
        ) AND id != ? AND status = 'Available'
        ORDER BY featured DESC, id DESC
        LIMIT 3
        """,
        (id, id),
    ).fetchall()
    conn.close()

    if car is None:
        return redirect("/cars")

    return render_template(
        "car_details.html",
        car=car,
        images=images,
        related_cars=related_cars,
    )


@app.route("/car/<int:id>/edit", methods=["GET", "POST"])
def edit_car(id):
    if not is_admin_logged_in():
        return redirect("/login")

    conn = get_db()
    car = conn.execute("SELECT * FROM cars WHERE id = ?", (id,)).fetchone()

    if car is None:
        conn.close()
        return redirect("/cars")

    if request.method == "POST":
        title = request.form["title"]
        brand = request.form["brand"]
        model = request.form["model"]
        year = request.form["year"]
        price = request.form["price"]
        mileage = request.form["mileage"]
        description = request.form["description"]
        location = request.form.get("location", "Dubai")
        category = request.form.get("category", "Sedan")
        fuel_type = request.form.get("fuel_type", "Petrol")
        transmission = request.form.get("transmission", "Automatic")
        condition = request.form.get("condition", "Used")
        seller_name = request.form.get("seller_name", "CARWA Auto")
        seller_phone = request.form.get("seller_phone", "+971582119936")
        seller_type = request.form.get("seller_type", "Dealership")
        featured = 1 if request.form.get("featured") else 0
        status = request.form.get("status", "Available")

        image = request.files.get("image")
        filename = car["image"]

        if image and image.filename:
            filename = image.filename
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn.execute(
            """
            UPDATE cars
            SET title = ?, brand = ?, model = ?, year = ?, price = ?, mileage = ?,
                description = ?, image = ?, category = ?, location = ?, fuel_type = ?,
                transmission = ?, condition = ?, featured = ?, status = ?, seller_name = ?, seller_phone = ?, seller_type = ?
            WHERE id = ?
            """,
            (
                title,
                brand,
                model,
                year,
                price,
                mileage,
                description,
                filename,
                category,
                location,
                fuel_type,
                transmission,
                condition,
                featured,
                status,
                seller_name,
                seller_phone,
                seller_type,
                id,
            ),
        )

        gallery = request.files.getlist("gallery")
        for img in gallery:
            if img.filename:
                img_name = img.filename
                img.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))
                conn.execute(
                    "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
                    (id, img_name),
                )

        conn.commit()
        conn.close()
        return redirect(f"/car/{id}")

    images = conn.execute(
        "SELECT * FROM car_images WHERE car_id = ? ORDER BY id DESC",
        (id,),
    ).fetchall()
    conn.close()

    return render_template(
        "edit_car.html",
        car=car,
        images=images,
        search_options=fetch_search_options(),
    )


@app.route("/add", methods=["GET", "POST"])
def add_car():
    if request.method == "POST":
        title = request.form["title"]
        brand = request.form["brand"]
        model = request.form["model"]
        year = request.form["year"]
        price = request.form["price"]
        mileage = request.form["mileage"]
        description = request.form["description"]
        location = request.form.get("location", "Dubai")
        category = request.form.get("category", "Sedan")
        fuel_type = request.form.get("fuel_type", "Petrol")
        transmission = request.form.get("transmission", "Automatic")
        condition = request.form.get("condition", "Used")
        seller_name = request.form.get("seller_name", "CARWA Auto")
        seller_phone = request.form.get("seller_phone", "+971582119936")
        seller_type = request.form.get("seller_type", "Dealership")

        image = request.files["image"]
        filename = image.filename
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO cars
            (title, brand, model, year, price, mileage, description, image, category, location, fuel_type, transmission, condition, featured, status, seller_name, seller_phone, seller_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                brand,
                model,
                year,
                price,
                mileage,
                description,
                filename,
                category,
                location,
                fuel_type,
                transmission,
                condition,
                0,
                "Pending Review",
                seller_name,
                seller_phone,
                seller_type,
            ),
        )

        car_id = cur.lastrowid
        gallery = request.files.getlist("gallery")

        for img in gallery:
            if img.filename:
                img_name = img.filename
                img.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))
                conn.execute(
                    "INSERT INTO car_images (car_id, image) VALUES (?, ?)",
                    (car_id, img_name),
                )

        conn.commit()
        conn.close()
        return redirect("/admin" if is_admin_logged_in() else "/cars")

    return render_template(
        "add_car.html",
        search_options=fetch_search_options(),
    )


@app.route("/search")
def search():
    return redirect(f"/cars?{request.query_string.decode()}")


@app.route("/wishlist/<int:car_id>")
def wishlist(car_id):
    conn = get_db()
    conn.execute("INSERT INTO wishlist (car_id) VALUES (?)", (car_id,))
    conn.commit()
    conn.close()
    return redirect("/mywishlist")


@app.route("/mywishlist")
def mywishlist():
    conn = get_db()
    saved_cars = conn.execute(
        """
        SELECT cars.*
        FROM cars
        JOIN wishlist ON cars.id = wishlist.car_id
        ORDER BY wishlist.id DESC
        """
    ).fetchall()
    conn.close()
    return render_template("wishlist.html", cars=saved_cars)


@app.route("/blog")
def blog():
    conn = get_db()
    blogs = conn.execute("SELECT * FROM blogs ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("blog.html", blogs=blogs)


@app.route("/faq")
def faq():
    return render_template("faq.html", faqs=FAQS)


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/contact", methods=["POST"])
def contact_submit():
    create_lead(
        None,
        request.form["name"],
        request.form["email"],
        request.form.get("phone", ""),
        request.form.get("message", ""),
        "general",
    )
    return redirect("/contact?submitted=1")


@app.route("/compare")
def compare():
    car1_id = request.args.get("car1", "").strip()
    car2_id = request.args.get("car2", "").strip()

    conn = get_db()
    selected_cars = []

    for car_id in [car1_id, car2_id]:
        if car_id.isdigit():
            car = conn.execute(
                "SELECT * FROM cars WHERE id = ?",
                (int(car_id),),
            ).fetchone()
            if car:
                selected_cars.append(car)

    conn.close()

    return render_template(
        "compare.html",
        cars=selected_cars,
        car_options=fetch_car_options(),
        selected_ids={"car1": car1_id, "car2": car2_id},
    )


@app.route("/dealer")
def dealer():
    conn = get_db()
    featured_inventory = conn.execute(
        """
        SELECT * FROM cars
        WHERE seller_type = 'Dealership' AND status = 'Available'
        ORDER BY featured DESC, id DESC
        LIMIT 6
        """
    ).fetchall()
    conn.close()
    return render_template(
        "dealer.html",
        cars=featured_inventory,
        stats=fetch_stats(),
    )


@app.route("/finance", methods=["GET", "POST"])
def finance():
    if request.method == "POST":
        message = (
            f"Budget: AED {request.form['budget']} | "
            f"Down payment: AED {request.form['down_payment']} | "
            f"Months: {request.form['tenure_months']}"
        )
        create_lead(
            request.form.get("car_id") or None,
            request.form["name"],
            request.form["email"],
            request.form["phone"],
            message,
            "finance",
        )
        return redirect("/finance?submitted=1")

    return render_template("finance.html", car_options=fetch_car_options())


@app.route("/recommendations")
def recommendations():
    has_preferences = has_recommendation_preferences(request.args)
    recommendations = build_personalized_recommendations(
        request.args,
        limit=9 if has_preferences else 6,
    )

    if has_preferences:
        session["recommendation_preferences"] = {
            key: request.args.get(key, "")
            for key in [
                "budget",
                "category",
                "brand",
                "location",
                "fuel_type",
                "transmission",
                "min_year",
                "max_mileage",
                "priority",
            ]
        }

    return render_template(
        "recommendations.html",
        recommendations=recommendations,
        search_options=fetch_search_options(),
        current_preferences=request.args,
        has_preferences=has_preferences,
    )


@app.route("/lead/contact/<int:car_id>", methods=["POST"])
def contact_seller(car_id):
    create_lead(
        car_id,
        request.form["name"],
        request.form["email"],
        request.form["phone"],
        request.form.get("message", ""),
        "seller",
    )
    return redirect(f"/car/{car_id}?contact=sent")


@app.route("/lead/book/<int:car_id>", methods=["POST"])
def book_test_drive(car_id):
    message = (
        f"Preferred date: {request.form.get('preferred_date', '')} | "
        f"Preferred time: {request.form.get('preferred_time', '')}"
    )
    create_lead(
        car_id,
        request.form["name"],
        request.form["email"],
        request.form["phone"],
        message,
        "test_drive",
    )
    return redirect(f"/car/{car_id}?booking=sent")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admins WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()

        if admin and verify_password(admin["password_hash"], request.form["password"]):
            session["admin_username"] = admin["username"]
            return redirect("/admin")

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/admin")
def admin():
    if not is_admin_logged_in():
        return redirect("/login")

    conn = get_db()
    all_cars = conn.execute("SELECT * FROM cars ORDER BY id DESC").fetchall()
    recent_leads = conn.execute(
        """
        SELECT leads.*, cars.title AS car_title
        FROM leads
        LEFT JOIN cars ON cars.id = leads.car_id
        ORDER BY leads.id DESC
        LIMIT 12
        """
    ).fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        cars=all_cars,
        leads=recent_leads,
        stats=fetch_stats(),
        app_name=APP_NAME,
    )


@app.route("/admin/feature/<int:car_id>")
def admin_feature(car_id):
    if not is_admin_logged_in():
        return redirect("/login")

    conn = get_db()
    conn.execute(
        """
        UPDATE cars
        SET featured = CASE WHEN featured = 1 THEN 0 ELSE 1 END
        WHERE id = ?
        """,
        (car_id,),
    )
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/admin/status/<int:car_id>/<status>")
def admin_status(car_id, status):
    if not is_admin_logged_in():
        return redirect("/login")

    allowed_statuses = {"Available", "Pending Review", "Sold", "Archived"}
    if status not in allowed_statuses:
        return redirect("/admin")

    conn = get_db()
    conn.execute("UPDATE cars SET status = ? WHERE id = ?", (status, car_id))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/admin/lead/<int:lead_id>/<status>")
def admin_lead_status(lead_id, status):
    if not is_admin_logged_in():
        return redirect("/login")

    allowed_statuses = {"New", "Contacted", "Qualified", "Closed"}
    if status not in allowed_statuses:
        return redirect("/admin")

    conn = get_db()
    conn.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/admin/password", methods=["POST"])
def admin_password():
    if not is_admin_logged_in():
        return redirect("/login")

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    username = session["admin_username"]

    conn = get_db()
    admin = conn.execute(
        "SELECT * FROM admins WHERE username = ?",
        (username,),
    ).fetchone()

    if admin and verify_password(admin["password_hash"], current_password) and len(new_password) >= 8:
        conn.execute(
            "UPDATE admins SET password_hash = ? WHERE username = ?",
            (hash_password(new_password), username),
        )
        conn.commit()

    conn.close()
    return redirect("/admin")


@app.route("/evaluate", methods=["GET", "POST"])
def evaluate():
    result = None
    if request.method == "POST":
        result = build_price_evaluation(request.form)

    return render_template(
        "evaluate.html",
        result=result,
        search_options=fetch_search_options(),
        current_values=request.form if request.method == "POST" else request.args,
        current_year=datetime.now().year,
    )


@app.route("/evaluate_result", methods=["POST"])
def evaluate_result():
    result = build_price_evaluation(request.form)
    return render_template(
        "evaluate.html",
        result=result,
        search_options=fetch_search_options(),
        current_values=request.form,
        current_year=datetime.now().year,
    )


@app.route("/seed")
def seed():
    seed_sample_cars(force=True)
    prune_unwanted_listings()
    seed_sample_blogs(force=True)
    ensure_sunny_listing()
    ensure_altima_listing()
    ensure_es350_listing()
    ensure_galant_listing()
    ensure_is250_listing()
    ensure_sunny_2015_listing()
    ensure_sunny_2020_listing()
    ensure_tiida_2007_listing()
    ensure_tiida_2016_listing()
    ensure_altima_2007_listing()
    ensure_avalon_2011_listing()
    ensure_micra_2020_listing()
    ensure_patrol_2015_listing()
    ensure_rx350_2013_listing()
    ensure_red_is250_2010_listing()
    ensure_blue_is250_2011_listing()
    ensure_is250_2013_listing()
    ensure_camry_2017_listing()
    ensure_ford_explorer_2014_listing()
    ensure_sentra_2016_listing()
    ensure_avalon_2009_listing()
    ensure_sunny_2018_listing()
    ensure_murano_2008_listing()
    ensure_pajero_2014_listing()
    ensure_pajero_2020_listing()
    normalize_listing_descriptions()
    conn = get_db()
    conn.execute("DELETE FROM leads")
    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'leads'")
    conn.commit()
    conn.close()
    return "Sample marketplace data reset successfully"


if __name__ == "__main__":
    app.run(debug=True)
