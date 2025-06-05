CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    pass VARCHAR(100) NOT NULL,
    city_of_residence VARCHAR(100),
    date_of_birth DATE DEFAULT NULL
);

CREATE TABLE Passengers (
    user_id INT PRIMARY KEY,
    sign_up_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	account_status ENUM('Deactive', 'Active') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Admins (
    user_id INT PRIMARY KEY,
    admin_role VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Vehicle (
    vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(50) NOT NULL
);

CREATE TABLE Location (
	location_id INT PRIMARY KEY AUTO_INCREMENT,
    country VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
    );
    
    CREATE TABLE Ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    departure_location_id INT NOT NULL,
    arrival_location_id INT NOT NULL,
    arrival_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    departure_date DATE NOT NULL,
    remaining_capacity INT CHECK (remaining_capacity >= 0),
    cost DECIMAL(10,2) NOT NULL,
	vehicle_id INT,
	FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (departure_location_id) REFERENCES Location(location_id) ON DELETE CASCADE,
    FOREIGN KEY (arrival_location_id) REFERENCES Location(location_id) ON DELETE CASCADE

);
    

CREATE TABLE Reservation (
    reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT,
    passenger_id INT,
    admin_id INT DEFAULT NULL,
    reservation_status ENUM('Pending', 'Confirmed', 'Cancelled By Passenger', 'Cancelled By Admin') NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id),
    FOREIGN KEY (passenger_id) REFERENCES Passengers(user_id),
    FOREIGN KEY (admin_id) REFERENCES Admins(user_id)
);

CREATE TABLE Payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    reservation_id INT,
    user_id INT,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status ENUM('Pending', 'Completed', 'Failed') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('Credit Card', 'PayPal', 'Bank Transfer') NOT NULL,
    FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id),
    FOREIGN KEY (user_id) REFERENCES Passengers(user_id)
);

-- -----------------------
CREATE TABLE Train (
    vehicle_id INT PRIMARY KEY,
	star ENUM('1', '2', '3', '4', '5'),
    car_number INT NOT NULL,
    is_reserved_fully BOOLEAN NOT NULL,
	wifi_access BOOLEAN,
    catering BOOLEAN,
    ventilation BOOLEAN,
	etc VARCHAR(100) ,
    flat_wagon BOOLEAN,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE Airplane (
    vehicle_id INT PRIMARY KEY,
    airline VARCHAR(100) NOT NULL,
    airplane_class ENUM('Business', 'Economy', 'Premium') NOT NULL,
    arrival_airport VARCHAR(100) NOT NULL,
    departure_airport VARCHAR(100) NOT NULL,
    catering BOOLEAN,    
    wifi_access BOOLEAN,
    flat_bed_seat BOOLEAN,
	etc VARCHAR(100) ,
    flight_number VARCHAR(50) UNIQUE NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE Bus (
    vehicle_id INT PRIMARY KEY,
    bus_type ENUM('VIP', 'Double Decker', 'Sleeper') NOT NULL,
    seats_row_per_row INT NOT NULL,
	ventilation BOOLEAN,
	etc VARCHAR(100) ,
    catering BOOLEAN,
    personal_monitor BOOLEAN,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE Reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT,
    passenger_id INT NOT NULL,
    admin_id INT,
    category VARCHAR(100),
    report_description TEXT,
    report_status ENUM('Open', 'Closed', 'Pending'),

    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id),
    FOREIGN KEY (passenger_id) REFERENCES Passengers(user_id),
    FOREIGN KEY (admin_id) REFERENCES Admins(user_id)
);

ALTER TABLE Reports
ADD COLUMN admin_response TEXT;


CREATE TABLE Wallet (
    wallet_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT chk_balance CHECK (balance >= 0)
);

ALTER TABLE Reservation MODIFY COLUMN reservation_status
ENUM('Pending', 'Confirmed', 'Cancelled By Passenger', 'Cancelled By Admin', 'Expired') NOT NULL;