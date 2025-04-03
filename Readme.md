3D AI-Based E-Commerce Store

This is a Django-based e-commerce store featuring AI-driven 3D models for product visualization. Follow this guide to set up and run the project.

📌 Table of Contents

📂 Clone the Repository

⚙️ Set Up Python Environment

🗄️ Database Setup

🔑 Create Admin User

👥 Create Test Users (Optional)

🚀 Run the Development Server

📁 Project Structure

🔐 Authorization System

📜 API Documentation

🐞 Troubleshooting

📜 License

📂 Clone the Repository

git clone https://github.com/MohammadAbdullah1214/3D-AI-based-Ecommerce-Store.git
cd 3D-AI-based-Ecommerce-Store

⚙️ Set Up Python Environment

🔹 Create and Activate Virtual Environment

For Windows:

python -m venv venv
venv\Scripts\activate

For Mac/Linux:

python -m venv venv
source venv/bin/activate

🔹 Install Dependencies

pip install -r requirements.txt

If requirements.txt is not available, install these packages manually:

pip install django djangorestframework djangorestframework-simplejwt drf-spectacular pillow

🗄️ Database Setup

🔹 Create and Apply Migrations

python manage.py makemigrations
python manage.py migrate

🔑 Create Admin User

python manage.py createsuperuser

Follow the prompts to enter a username, email, and password.

👥 Create Test Users (Optional)

🔹 Open Django Shell

python manage.py shell

🔹 Add Test Users

from users.models import CustomUser

# Create a seller
CustomUser.objects.create_user(
    username='seller1',
    email='seller1@example.com',
    password='sellerpass123',
    role='seller'
)

# Create a customer
CustomUser.objects.create_user(
    username='customer1',
    email='customer1@example.com',
    password='customerpass123',
    role='customer'
)

exit()

🚀 Run the Development Server

python manage.py runserver

Access the site at http://127.0.0.1:8000/

📁 Project Structure

3D-AI-based-Ecommerce-Store/
│── analytics/     # Analytics and dashboard functionality
│── carts/         # Shopping cart implementation
│── core/          # Main project settings
│── order_items/   # Order item models and views
│── orders/        # Order processing and management
│── payments/      # Payment processing
│── products/      # Product catalog with 3D models
│── users/         # User authentication and authorization

🔐 Authorization System

The project implements a role-based access control system:

👑 Admin Role

Full access to all features

Manage all products, orders, and users

Access all analytics and reports

🏪 Seller Role

Create and manage own products

View orders containing their products

Access analytics for their products

🛍️ Customer Role

Browse products and view 3D models

Add products to cart

Place and track orders

Cannot access admin or seller features

📜 API Documentation

📌 Access the API documentation at http://127.0.0.1:8000/api/docs/ when the server is running.

🐞 Troubleshooting

🔹 Common Issues & Fixes

Python not recognized? Ensure Python is added to your PATH.

Package not found? Make sure your virtual environment is activated.

Database errors? Delete db.sqlite3 and migration files (except __init__.py), then run migrations again.

Permission issues? Run Command Prompt as Administrator.

📜 License

This project is open-source and available under the MIT License.

