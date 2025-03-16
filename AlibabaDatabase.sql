CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    pass VARCHAR(255) NOT NULL,
    city_of_residence VARCHAR(100)
);

CREATE TABLE Passenger (
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

CREATE TABLE Ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    departure_location VARCHAR(100) NOT NULL,
    arrival_location VARCHAR(100) NOT NULL,
    arrival_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    departure_date DATE NOT NULL,
    remaining_capacity INT CHECK (remaining_capacity >= 0),
    cost DECIMAL(10,2) NOT NULL
);

CREATE TABLE ExpiryTime (
    expiry_time_id INT PRIMARY KEY AUTO_INCREMENT,
    expiry_time TIME NOT NULL
);

CREATE TABLE Reservation (
    reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT,
    class_trip_id INT,
    user_id INT,
    expiry_time_id INT,
    reservation_status ENUM('Pending', 'Confirmed', 'Cancelled') NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (expiry_time_id) REFERENCES ExpiryTime(expiry_time_id)
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
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Company (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(25) NOT NULL
);

CREATE TABLE Vehicle (
    vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT,
    ticket_id INT,
    FOREIGN KEY (company_id) REFERENCES Company(company_id),
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id)
);
-- ---------------------------
CREATE TABLE TrainFacilities (
    train_facilities_id INT PRIMARY KEY AUTO_INCREMENT,
    wifi_access BOOLEAN,
    catering BOOLEAN,
    ventilation BOOLEAN,
    flat_bed_seat BOOLEAN
);

CREATE TABLE AirplaneFacilities (
    airplane_facilities_id INT PRIMARY KEY AUTO_INCREMENT,
    wifi_access BOOLEAN,
    catering BOOLEAN,
    in_flight_entertainment BOOLEAN
);

CREATE TABLE BusFacilities (
    bus_facilities_id INT PRIMARY KEY AUTO_INCREMENT,
    ventilation BOOLEAN,
    catering BOOLEAN,
    personal_monitor BOOLEAN
);
-- -----------------------
CREATE TABLE Train (
    vehicle_id INT PRIMARY KEY,
    train_facilities_id INT,
    car_number INT NOT NULL,
    is_reserved_fully BOOLEAN NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (train_facilities_id) REFERENCES TrainFacilities(train_facilities_id)
);

CREATE TABLE Airplane (
    vehicle_id INT PRIMARY KEY,
    airplane_facilities_id INT,
    airline VARCHAR(100) NOT NULL,
    airplane_class VARCHAR(50) NOT NULL,
    arrival_airport VARCHAR(100) NOT NULL,
    departure_airport VARCHAR(100) NOT NULL,
    flight_number VARCHAR(50) UNIQUE NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (airplane_facilities_id) REFERENCES AirplaneFacilities(airplane_facilities_id)
);

CREATE TABLE Bus (
    vehicle_id INT PRIMARY KEY,
    bus_facilities_id INT,
    bus_type VARCHAR(50) NOT NULL,
    seats_row_per_row INT NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (bus_facilities_id) REFERENCES BusFacilities(bus_facilities_id)
);

CREATE TABLE Reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT,
    passenger_id INT Unique,
    admin_id INT Unique,
    category VARCHAR(100),
    report_description TEXT,
    report_status ENUM('Open', 'Closed', 'Pending'),
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id),
    FOREIGN KEY (passenger_id) REFERENCES Passenger(user_id),
    FOREIGN KEY (admin_id) REFERENCES Admins(user_id)
);
