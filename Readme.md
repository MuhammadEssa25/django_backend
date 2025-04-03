3D AI-Based E-Commerce Store
Table of Contents
Getting Started

Prerequisites

Project Setup

1. Clone the Repository

2. Set Up Python Environment

3. Database Setup

4. Create Admin User

5. Create Test Users (Optional)

6. Run the Development Server

Project Structure

Authorization System

API Documentation

Troubleshooting

License

Getting Started
This project is a 3D AI-based e-commerce store built with Django and Django REST Framework. It includes user authentication, role-based access control, and interactive 3D product viewing.

Prerequisites
Make sure you have the following installed:

Python (Version 3.8 or later)

Git (For cloning the repository)

Virtual Environment (venv) (To manage dependencies)

Project Setup
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/MohammadAbdullah1214/3D-AI-based-Ecommerce-Store.git  
cd 3D-AI-based-Ecommerce-Store  
2. Set Up Python Environment
Create and activate a virtual environment:

bash
Copy
Edit
python -m venv venv  
source venv/bin/activate  # For macOS/Linux  
venv\Scripts\activate  # For Windows  
Install dependencies from requirements.txt:

bash
Copy
Edit
pip install -r requirements.txt  
If requirements.txt is not available, manually install the required packages:

bash
Copy
Edit
pip install django djangorestframework djangorestframework-simplejwt drf-spectacular pillow  
3. Database Setup
Run the following commands to set up the database:

bash
Copy
Edit
python manage.py makemigrations  
python manage.py migrate  
4. Create Admin User
Create a superuser account for admin access:

bash
Copy
Edit
python manage.py createsuperuser  
Follow the prompts to set a username, email, and password.

5. Create Test Users (Optional)
You can create test users for different roles using the Django shell:

bash
Copy
Edit
python manage.py shell  
Then, run the following script:

python
Copy
Edit
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
6. Run the Development Server
bash
Copy
Edit
python manage.py runserver  
Access the site at: http://127.0.0.1:8000/

Project Structure
bash
Copy
Edit
3D-AI-based-Ecommerce-Store/  
│── analytics/      # Analytics and dashboard functionality  
│── carts/          # Shopping cart implementation  
│── core/           # Main project settings  
│── orders/         # Order processing and management  
│── products/       # Product catalog with 3D models  
│── users/          # User authentication and authorization  
│── db.sqlite3      # Database file (if using SQLite)  
│── manage.py       # Django project manager  
│── requirements.txt # Dependencies list  
└── README.md       # Project documentation  
Authorization System
The system supports role-based access control with different permissions:

Admin Role

Manage all products, orders, and users

Access all analytics and reports

Seller Role

Create and manage own products

View orders containing their products

Access analytics for their products

Customer Role

Browse products and view 3D models

Add products to cart

Place and track orders

Cannot access admin or seller features

API Documentation
Once the server is running, access the API docs at:
http://127.0.0.1:8000/api/docs/

Troubleshooting
Issue	Solution
Python not recognized	Ensure Python is added to your PATH
Package not found	Make sure your virtual environment is activated
Database errors	Delete db.sqlite3 and migrations folder (except __init__.py) and run migrations again
Permission issues	Run Command Prompt as Administrator
License
This project is open-source and available under the MIT License.