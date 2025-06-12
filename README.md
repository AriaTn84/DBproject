# Raahi - Travel Ticket Reservation System

Welcome to the "Raahi" database project. This project is a back-end system for a travel ticket reservation service (airplane, train, and bus), developed using Django and MySQL. It also utilizes Redis for caching and managing scheduled tasks.

This document will guide you through setting up the back-end server, connecting to the database and Redis, and using the available APIs for development and testing.

---

### Setup and Run

Follow the steps below to run the project:

#### Prerequisites
- Python (version 3.8 or higher)
- Django
- MySQL
- Redis

#### 1. Clone the Project and Install Dependencies
First, clone the project from your code repository. Then, navigate into the project directory and install all the required Python packages using the `requirements.txt` file. This file contains all the libraries the project depends on, such as Django, djangorestframework, mysqlclient, redis, etc.

```
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
# use .venv/bin/python for python interpreter

# Install dependencies
pip install -r requirements.txt
```

#### 2. Database Setup
Create a MySQL database named `raahi_db` with `utf8mb4` encoding.
```sql
CREATE DATABASE IF NOT EXISTS `raahi_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Next, import the tables and sample data by executing the following SQL files in your database:

1. ```DBproject/raahi.sql```: This file creates the schema for all required tables in the system.
2. ```DBproject/tests.sql```: This file contains sample data for initial testing and development.

Finally, update your database connection information in the ```DBproject/settings.py``` file:
```python
# DBproject/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'raahi_db',
        'USER': 'your_mysql_user',       # Enter your MySQL username
        'PASSWORD': 'your_mysql_password', # Enter your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
```python
# DBproject/Raahi/db.py

import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='raahi_db',
            user='your_user_name',
            password='your_password'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
```
you can use ```DBproject/how_create_database.txt``` file for more detail.
#### 3. Redis Setup
Ensure your Redis server is active and running on the default port (`6379`).

#### 4. Running the Server and Worker
Run the Django development server:
```
python manage.py runserver
```
Before run worker file in separate terminal read `DBproject/how_run_worker`
,run the background worker script for managing reservations:
```
python DBproject/Raahi/api/reserve_a_ticket/reservation_worker.py
```

---

## API Endpoints

Below is a complete list of available APIs with descriptions of their input and output parameters.

### 1. Login with OTP

This is a two-step process used for user authentication.

-   **Send OTP Code**
    -   **Endpoint**: `POST /api/log-in/send-otp/`
    -   **Description**: Sends a one-time password (OTP) to the user's email. The code is valid for 5 minutes.
    -   **Input (Body)**:
        ```json
        {
            "email": "user@example.com"
        }
        ```
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "OTP sent successfully"
        }
        ```

-   **Verify OTP Code and Log In**
    -   **Endpoint**: `POST /api/log-in/verify-otp/`
    -   **Description**: Verifies the submitted OTP. If correct, it issues JWT Access and Refresh tokens for the user.
    -   **Input (Body)**:
        ```json
        {
            "email": "user@example.com",
            "otp": "123456"
        }
        ```
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "OTP verified successfully. User is logged in.",
            "refresh": "...",
            "access": "..."
        }
        ```
-   **Refresh Access Code**
    -   **Endpoint**: `POST /api/log-in/token/refresh/`
    -   **Description**: Create a new Access token Even after expire Access token.
    -   **Input (Body)**:
        ```json
        {
            "refresh": "..."
        }
        ```
    -   **Success Response (200 OK)**:
        ```json
        {
            "access": "..."
        }
        ```        

### 2. User Signup

-   **Endpoint**: `POST /api/sign-up/`
-   **Description**: Registers a new user in the system and creates a wallet with a zero balance for them.
-   **Input (Body)**:
    ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "09123456789",
        "password": "securepassword123",
        "city_of_residence": "Tehran"
    }
    ```
-   **Success Response (201 Created)**:
    ```json
    {
        "message": "User registered successfully",
        "refresh": "...",
        "access": "..."
    }
    ```

### 3. Update User Profile

-   **Get Profile Information**
    -   **Endpoint**: `GET /api/profile/get/`
    -   **Description**: Returns the profile information of the authenticated user. Profile data is cached in Redis for faster access.
    -   **Input (Headers)**: `Authorization: Bearer <access_token>`
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "User profile fetched from database successfully",
            "data": {
                "user_id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "09123456789",
                "date_of_birth": "2000-01-01",
                "city_of_residence": "Tehran"
            },
            "source": "MySQL Database"
        }
        ```

-   **Edit Profile**
    -   **Endpoint**: `POST /api/profile/update-user/`
    -   **Description**: Allows a user to edit their profile information (first name, last name, phone, city, and date of birth). After an update, the cached data in Redis is also refreshed.
    -   **Input (Headers)**: `Authorization: Bearer <access_token>`
    -   **Input (Body)**:
        ```json
        {
            "first_name": "Johnny",
            "city_of_residence": "Shiraz"
        }
        ```
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "User profile updated successfully"
        }
        ```

### 4. Get Cities List

-   **Endpoint**: `GET /api/cities/`
-   **Description**: Returns a list of all unique cities from the `Location` table, intended for use in origin and destination fields.
-   **Success Response (200 OK)**:
    ```json
    {
        "cities": ["Los Angeles", "Mashhad", "New York City", "Paris", "Tehran"]
    }
    ```

### 5. Search Tickets

-   **Endpoint**: `GET /api/tickets/search/`
-   **Description**: Searches for available tickets based on origin, destination, and date. It also supports filtering by vehicle type (Airplane, Train, Bus). Search results are cached in Redis to improve performance.
-   **Parameters (Query Params)**:
    -   `departure_city` (required)
    -   `arrival_city` (required)
    -   `departure_date` (required, YYYY-MM-DD)
    -   `vehicle_type` (optional: `Airplane`, `Train`, `Bus`)
-   **Example**: `/api/tickets/search/?departure_city=Tehran&arrival_city=Mashhad&departure_date=2025-06-10&vehicle_type=Train`
-   **Success Response (200 OK)**:
    ```json
    {
        "message": "Search results fetched from database.",
        "source": "MySQL Database",
        "data": [
            {
                "ticket_id": 1,
                "departure_date": "2025-06-10",
                "departure_time": "10:30:00",
                ...
                "company_name": "Amtrak",
                "vehicle_type": "Train"
            }
        ]
    }
    ```

### 6. Get Ticket Details

-   **Endpoint**: `GET /api/get-ticket-details/`
-   **Description**: Displays the full details of a specific ticket, including origin, destination, price, remaining capacity, and vehicle-specific amenities.
-   **Input (Body)**:
    ```json
    {
        "ticket_id": 11
    }
    ```
-   **Success Response (200 OK)**:
    ```json
    {
        "message": "Ticket details fetched successfully",
        "data": {
            "ticket_id": 11,
            "origin": {"country": "United States", "state": "California", "city": "Los Angeles"},
            "destination": {"country": "Turkey", "state": "Istanbul", "city": "Istanbul"},
            "departure_date": "2025-05-06",
            "departure_time": "07:45:00",
            "arrival_date": "2025-06-10",
            "price": 500.0,
            "remaining_capacity": 200,
            "company_name": "Mahan",
            "vehicle_specifics": {
                "type": "Airplane",
                "amenities": {
                    "airline": "Mahan",
                    "airplane_class": "Premium",
                    "catering": 1,
                    ...
                }
            }
        }
    }
    ```

### 7 and 8. Reserve and Pay for a Ticket

This process is completed in three steps: initial reservation, payment, and viewing booking history.

-   **Step 1: Reserve Ticket**
    -   **Endpoint**: `POST /api/reserve-ticket/`
    -   **Description**: Reserves a ticket for the user for 10 minutes. The reservation status will be `Pending`, and a payment record with the same status is created. The ticket's capacity is decreased, and a key with an expiration time is set in Redis.
    -   **Input (Headers)**: `Authorization: Bearer <access_token>`
    -   **Input (Body)**:
        ```json
        {
            "ticket_id": 1
        }
        ```
    -   **Success Response (201 Created)**:
        ```json
        {
            "message": "Ticket successfully reserved. Please complete payment within the time limit.",
            "reservation_id": 123,
            "total_cost": 95.75,
            "payment_due_by": "YYYY-MM-DDTHH:MM:SS"
        }
        ```
        If you do not complete the payment after 10 minutes system cancel the reserve(You must run worker).

-   **Step 2: Make Payment**
    -   **Endpoint**: `POST /api/payment/pay/`
    -   **Description**: Processes the payment for a `Pending` reservation and finalizes the ticket. The reservation status is updated to `Confirmed` and the payment status to `Completed`. If the wallet is used, the amount is deducted from it.
    -   **Input (Headers)**: `Authorization: Bearer <access_token>`
    -   **Input (Body)**:
        ```json
        {
            "reservation_id": 123,
            "payment_method": "Wallet"  // Available: Wallet, Credit Card, PayPal
        }
        ```
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "Payment successful. Your ticket is confirmed."
        }
        ```


### 9. Check Cancellation Penalty
-   **Endpoint**: `POST /api/reservation/cancel-penalty/`
-   **Description**: Calculates and displays the penalty percentage and refundable amount before final cancellation.
-   **Input (Headers)**: `Authorization: Bearer <access_token>`
    -   **Input (Body)**:
        ```json
        {
            "reservation_id": 4
        }
        ```
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "Review your cancellation penalty. To confirm, send the request again with \"confirm\": true.",
            "ticket_cost": "420.50",
            "penalty_percentage": "10%",
            "refund_amount": "378.45"
        }
        ```
If you want cancel it do :
-   **Input (Headers)**: `Authorization: Bearer <access_token>`
    -   **Input (Body)**:
        ```json
        {
            "reservation_id": 1,
            "confirm": true
        }
        ```
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "Reservation cancelled successfully",
            "refund_processed": true,
            "amount_refunded_to_wallet": "47.88"
        }
        ```
### 10. Admin Ticket Management

These APIs require an access token from a user with the `Admin` role.

-   **List User Reports**: `GET /api/admin/management/reports/` 
-   **Respond to a Report**: `POST /api/admin/management/reports/<report_id>/update/`
-   **List Cancelled Reservations**: `GET /api/admin/management/reservations/cancelled/`
-   **Manually Confirm Reservation**: `POST /api/admin/management/reservations/<reservation_id>/confirm/`
-   **Cancel Reservation by Admin**: `POST /api/admin/management/reservations/<reservation_id>/cancel/`

you can see the example in ```DBproject/json_output/10.admin_ticket_management``` folder.

### 11. Get User Booking
-   **Endpoint**: GET /api/get-bookings/
-   **Description**: Displays a list of all confirmed tickets purchased by the user.
-   **Input** (Headers): ```Authorization: Bearer <access_token>```
-   **Parameters (Query Params):**
    - ```status```: ```future``` (upcoming trips), ```past``` (completed trips), ```cancelled```
-   **Success Response (200 OK):** 
    ```JSON
    {
      "bookings": [
          {
            "reservation_id": 4,
            "reservation_status": "Confirmed",
            "cost": "420.50",
            ...
            "departure_city": "Toronto",
            "arrival_city": "New York City"           
          }   
      ]
    }  
    ```
    
### 12. Cancel And Refund
- **Endpoint**: ```POST /api/reservation/cancel/```
- **Description**: Cancels the ticket, increments its capacity in the ```Ticket``` table by one, and refunds the appropriate amount (after deducting the penalty) to the user's wallet.
- **Input (Headers)**: `Authorization: Bearer <access_token>`
- **Input (Body)**:
  ```JSON
  {
    "reservation_id": 4
  }
  ```
- **Success Response (200 OK)**:
  ```JSON
  {
    "message": "Reservation cancelled successfully.",
    "refund_processed": true,
    "amount_refunded_to_wallet": "378.45"
  }
  ```
### 13. Report Ticket Issue

-   **Endpoint**: `POST /api/report-ticket-issue/`
-   **Description**: Allows a user to report issues related to a specific reservation (e.g., payment problems or incorrect information) to support.
-   **Input (Headers)**: `Authorization: Bearer <access_token>`
-   **Input (Body)**:
    ```json
    {
        "reservation_id": 9,
        "category": "Payment Problem",
        "description": "The amount was deducted from my account but the ticket was not confirmed."
    }
    ```
-   **Success Response (201 Created)**:
    ```json
    {
        "message": "Ticket issue reported successfully.",
        "report_id": 12
    }
    ```

---
### Another API Endpoint:
### Wallet

-   **Get Wallet Balance**
    -   **Endpoint**: `GET /api/wallet/get/`
    -   **Description**: Displays the user's wallet information and balance.
    -   **Input (Headers)**: `Authorization: Bearer <access_token>`
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "User profile fetched from database successfully",
            "data": {
                "balance": "150000.00",
                "first_name": "Alice",
                ...
            },
            "source": "MySQL Database"
        }
        ```

-   **Charge Wallet**
    -   **Endpoint**: `POST /api/wallet/charge/`
    -   **Description**: Adds a specified amount to the user's wallet balance.
    -   **Input (Headers)**: `Authorization: Bearer <access_token>`
    -   **Input (Body)**:
        ```json
        {
            "amount": 50000
        }
        ```
    -   **Success Response (200 OK)**:
        ```json
        {
            "message": "Wallet charged successfully",
            "data": {
                "new_balance": "200000.00"
            }
        }
        ```

---
## How to Test the APIs

You can use tools like `cURL` or **Postman** to test the APIs.

### Testing with Postman

Postman is a powerful tool with a graphical user interface for API testing. Here’s how you can use it for this project.

**1. Initial Setup:**
* Create a new **Collection** in Postman for the "Raahi" project.
* Create a new **Environment** and define a variable named `base_url` with the value `http://127.0.0.1:8000`. This will allow you to easily change the base address for all requests.

**2. Sign Up a New User:**
* Create a new `POST` request with the URL `{{base_url}}/api/sign-up/`.
* Go to the **Body** tab, select the **raw** option, and choose **JSON** from the dropdown.
* Enter the request body:
    ```json
    {
        "first_name": "Postman",
        "last_name": "User",
        "email": "postman@example.com",
        "phone": "09121112233",
        "password": "password123",
        "city_of_residence": "Tehran"
    }
    ```
* Hit **Send**. If successful, you will receive `access` and `refresh` tokens in the response.

**3. Log In and Save the Access Token:**
After signing up, you need to log in and save the token to access protected APIs.
* First, get the OTP sent to your email (`POST {{base_url}}/api/log-in/send-otp/`).
* Send a `POST` request to `{{base_url}}/api/log-in/verify-otp/` with your email and the received OTP.
* In this request, go to the **Tests** tab and add the following script. This script will automatically extract the access token from the response and save it as an environment variable:
    ```javascript
    var jsonData = pm.response.json();
    if (jsonData && jsonData.access) {
        pm.environment.set("access_token", jsonData.access);
        console.log("Access Token has been saved.");
    }
    ```
* After sending this request, the `access_token` variable will be saved in your environment.

**4. Send Authenticated Requests (e.g., Get Profile):**
* Create a new `GET` request with the URL `{{base_url}}/api/profile/get/`.
* Go to the **Authorization** tab.
* From the dropdown menu, select the type **Bearer Token**.
* In the token field, enter the variable `{{access_token}}`.
* Now, when you hit **Send**, your request will be sent with the correct `Authorization` header, and you will receive the profile information.

**5. Search for Tickets (with Parameters):**
* Create a `GET` request to `{{base_url}}/api/tickets/search/`.
* Go to the **Params** tab.
* Enter the required query parameters, such as `departure_city`, `arrival_city`, and `departure_date`, along with their values.
* Hit **Send** to see the search results.
---
## Contributing

This is a student project for the **Database Systems** course. Contributions are limited to the project team. For feedback or suggestions, contact the team via GitHub Issues.

---
## Contact

- **Course Instructor**: Dr. Pishgou
- **Senior TA**: Eng. Alireza Ghorbani
- **Supervising TA**: Eng. Mohammad Hossein Hooshmand
- **Repository Maintainer**: [Arya Tehrani/AryaTn84]
