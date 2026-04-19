HappyTummy – Food Donation & Distribution Platform

HappyTummy is a web-based platform designed to reduce food wastage by connecting restaurants, NGOs, and volunteers. It enables surplus food donations, efficient coordination, and transparent distribution to those in need.

Problem Statement

Large quantities of edible food are wasted every day while many people struggle with hunger. There is a lack of a centralized, structured system that connects food donors with organizations and volunteers who can distribute food efficiently.

HappyTummy bridges this gap.

Objectives

Minimize food wastage from restaurants

Enable NGOs to request and manage food donations

Allow volunteers to participate in food pickup and delivery

Provide role-based dashboards for smooth coordination

Ensure transparency and accountability in food distribution

User Roles
Restaurant

Register and log in

Submit surplus food details

Track donation status

NGO

Register and log in

Request food based on availability

Manage received donations

Volunteer

Register and log in

Accept delivery requests

Assist in food pickup and distribution

Tech Stack
Frontend

HTML5

CSS3

Bootstrap 5

JavaScript

Backend

Python

Django Framework

Database

SQLite (Development)

Easily extendable to PostgreSQL / MySQL

Authentication

Django Authentication System

Role-based access control

Key Features

Secure user authentication

Role-based dashboards (Restaurant / NGO / Volunteer)

Food surplus submission & confirmation

Real-time donation workflow

Organized database structure

Scalable and modular architecture

Installation & Setup

1️⃣ Clone the Repository
git clone https://github.com/your-username/HappyTummy.git
cd HappyTummy

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Migrations
python manage.py makemigrations
python manage.py migrate

5️⃣ Start the Server
python manage.py runserver


LIVE DEPLOYMENT LINK:

SMS Setup

Recommended provider for Indian mobile numbers: MSG91

1. Copy `.env.example` to `.env`.
2. Fill in your MSG91 values in `.env`:
   SMS_BACKEND=msg91
   MSG91_AUTH_KEY=your_msg91_auth_key
   MSG91_FLOW_ID=your_msg91_flow_id
   MSG91_SENDER_ID=your_msg91_sender_id
3. Restart the Django server after updating `.env`.
4. Send a test SMS before testing from the restaurant dashboard:
   python manage.py send_test_sms +919876543210

Important:
End users such as restaurants and NGOs do not need MSG91 accounts. They only use their regular phone numbers saved in HappyTummy. MSG91 is the SMS gateway configured once by the platform owner so the app can send SMS to those normal mobile numbers.

For Indian SMS delivery, MSG91 uses approved templates / flows. The donation notification flow in this project passes these variables:
- `restaurant_name`
- `quantity`
- `food_type`
- `address`
- `city`

Your MSG91 Flow template should use those same variable names.

If MSG91 is configured correctly, NGOs in the same city as the restaurant will receive a real SMS when a donation is posted.

Testing Credentials (Optional)

You can create test users using the registration pages for:

Restaurant

NGO

Volunteer

Or via Django Admin:

python manage.py createsuperuser

🚀 Future Enhancements

📍 Google Maps integration for live tracking

📱 Mobile app version

🔔 Notification system (SMS / Email)

☁️ Cloud database deployment

📈 Analytics dashboard for impact measurement

🤝 Contribution

Contributions are welcome!
Feel free to fork the repository and submit a pull request.

📜 License

This project is developed for educational purposes and is open for learning and improvement.

❤️ Acknowledgement

HappyTummy is inspired by the vision of creating a hunger-free society by leveraging technology for social good.
