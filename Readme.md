# 3D AI-Based E-Commerce Store  

## Table of Contents  
- [Getting Started](#getting-started)  
- [Prerequisites](#prerequisites)  
- [Project Setup](#project-setup)  
  - [1. Clone the Repository](#1-clone-the-repository)  
  - [2. Set Up Python Environment](#2-set-up-python-environment)  
  - [3. Database Setup](#3-database-setup)  
  - [4. Create Admin User](#4-create-admin-user)  
  - [5. Create Test Users (Optional)](#5-create-test-users-optional)  
  - [6. Run the Development Server](#6-run-the-development-server)  
- [Project Structure](#project-structure)  
- [Authorization System](#authorization-system)  
- [API Documentation](#api-documentation)  
- [Troubleshooting](#troubleshooting)  
- [License](#license)  


## Getting Started  
This project is a **3D AI-based e-commerce store** built with Django and Django REST Framework. It includes user authentication, role-based access control, and interactive 3D product viewing.  


## Prerequisites  
Ensure you have the following installed:  

- **Python** (Version 3.8 or later)  
- **Git** (For cloning the repository)  
- **Virtual Environment (venv)** (For dependency management)  

---

## Project Setup  

### 1. Clone the Repository  

```bash
git clone https://github.com/MohammadAbdullah1214/3D-AI-based-Ecommerce-Store.git  
cd 3D-AI-based-Ecommerce-Store  
```

### 2. Set Up Python Environment
```bash
Create and activate a virtual environment:

python -m venv venv  
source venv/bin/activate  # For macOS/Linux  
venv\Scripts\activate  # For Windows  

Install dependencies from requirements.txt:
pip install -r requirements.txt  

If requirements.txt is not available, manually install the required packages:
pip install django djangorestframework djangorestframework-simplejwt drf-spectacular pillow  
pip install django-cors-headers
```

### 3. Database Setup
```bash
Run the following commands to set up the database:
python manage.py makemigrations  
python manage.py migrate  
```
### 4. Create Admin User
```bash
Create a superuser account for admin access:
python manage.py createsuperuser  
Follow the prompts to set a username, email, and password.
```
### 5. Create Test Users (Optional)
```bash
You can create test users for different roles using the Django shell:
python manage.py shell  

Then, run the following script:
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
```

### 6. Run the Development Server
```bash
python manage.py runserver  
Access the site at: http://127.0.0.1:8000/
```

###  Project Structure
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

### Authorization System
The system supports role-based access control with different permissions:

#### Admin Role

    Manage all products, orders, and users

    Access all analytics and reports

#### Seller Role

    Create and manage own products

    View orders containing their products

    Access analytics for their products

#### Customer Role

    Browse products and view 3D models

    Add products to cart

    Place and track orders

    Cannot access admin or seller features

### API Documentation
Once the server is running, access the API docs at:
http://127.0.0.1:8000/api/docs/

### Troubleshooting
Issue	Solution
Python not recognized	Ensure Python is added to your PATH
Package not found	Make sure your virtual environment is activated
Database errors	Delete db.sqlite3 and migrations folder (except __init__.py) and run migrations again
Permission issues	Run Command Prompt as Administrator

### License
This project is open-source and available under the MIT License.