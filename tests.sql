INSERT INTO Users (first_name, last_name, email, phone, pass, city_of_residence) VALUES
('Alice', 'Smith', 'alice@example.com', '1234567890', 'pass123', 'New York'),
('Bob', 'Johnson', 'bob@example.com', '2345678901', 'pass123', 'Chicago'),
('Carol', 'Williams', 'carol@example.com', '3456789012', 'pass123', 'Los Angeles'),
('David', 'Brown', 'david@example.com', '4567890123', 'pass123', 'Miami'),
('Eve', 'Jones', 'eve@example.com', '5678901234', 'pass123', 'Houston'),
('Frank', 'Garcia', 'frank@example.com', '6789012345', 'pass123', 'Dallas'),
('Grace', 'Miller', 'grace@example.com', '7890123456', 'pass123', 'Phoenix'),
('Henry', 'Davis', 'henry@example.com', '8901234567', 'pass123', 'San Diego'),
('Ivy', 'Martinez', 'ivy@example.com', '9012345678', 'pass123', 'San Jose'),
('Jack', 'Hernandez', 'jack@example.com', '0123456789', 'pass123', 'Austin'),
('John', 'Doe', 'john.doe1@example.com', '1234567893', 'hashedpass1', 'New York'),
('Jane', 'Smith', 'jane.smith2@example.com', '1234567891', 'hashedpass2', 'Los Angeles'),
('Alice', 'Johnson', 'alice.j3@example.com', '1234567892', 'hashedpass3', 'Chicago'),
('Arya', 'Johnson', 'Arya.j3@example.com', '1234567894', 'hashedpass4', 'Tehran'),
('Zahra', 'Aghaie', 'Zahra.j3@example.com', '1234567895', 'hashedpass5', 'Qazvin'),
('Mobin', 'Fallahi', 'mobin.j3@example.com', '1234567896', 'hashedpass6', 'Mashhad'),
('Ahmadreaza', 'Mousavi', 'ahmad.j3@example.com', '1234567897', 'hashedpass7', 'Arak'),
('Sepehr', 'Ghardashi', 'sepehr.j3@example.com', '2234567897', 'hashedpass8', 'Sari'),
('Ali', 'Alavi', 'ali.j3@example.com', '2234567896', 'hashedpass9', 'Tehran'),
('Shahrzad', 'Ouruji', 'shrz.j3@example.com', '2234567895', 'hashedpass10', 'Tehran'),
('Amir Hossein', 'Bagheri', 'amirhossein.j3@example.com', '2234567890', 'hashedpass11', 'Tehran'),
('Sadra', 'Soltani', 'sadra.j3@example.com', '3234567897', 'hashedpass8', 'Mashhad');


INSERT INTO Passengers (user_id, account_status) VALUES
(1, 'Active'), (2, 'Active'), (3, 'Active'),
(4, 'Active'), (5, 'Active'), (6, 'Active'),
(11, 'Active'), (12, 'Active'), (13, 'Active'), 
(15, 'Active'), (17, 'Deactive');

INSERT INTO Passengers (user_id, sign_up_date, account_status) VALUES
(18, '2024-01-10','Active');

INSERT INTO Admins (user_id, admin_role) VALUES
(7, 'Support Agent'),
(8, 'Manager'),
(9, 'Supervisor'),
(10, 'Tech Admin'),
(14, 'Manager'),
(16, 'Support Agent'),
(19, 'Support Agent'),
(20, 'Support Agent'),
(21, 'Support Agent'),
(22, 'Support Agent');

INSERT INTO Vehicle (company_name) VALUES
('Greyhound'),
('Amtrak'),
('Delta Airlines'),
('United Airlines'),
('Southwest'),
('Flixbus'),
('JetBlue'),
('Megabus'),
('American Airlines'),
('Spirit Airlines'),
('Mahan'),
('SNCF'),
('Deutsche Bahn'),
('Via Rail'),
('Renfe'),
('TGV'),
('Emirates'),
('Qatar Airways'),
('Lufthansa'),
('British Airways'),
('Air France'),
('Volvo Buses'),
('Mercedes-Benz Buses'),
('Scania Buses'),
('MAN Buses'),
('Iveco Buses'),
('Setra Buses'),
('Van Hool Buses'),
('Neoplan Buses'),
('Yutong Buses'),
('Higer Buses'),
('Tehran Bus Company'),
('Iran Railways (RAI)'),
('Seiro Safar Bus Company'),
('Sapco (Tehran Suburban Bus Co.)'),
('Parsian Bus Transport'),
('Arash Travel & Tourism Bus'),
('TTS (Tehran Taxi Services)'),
('Metro Tehran (Subway)'),
('Iran Peyma Bus Services'),
('Alborz Intercity Buses');

INSERT INTO Location (country, state, city) VALUES
('United States', 'California', 'Los Angeles'),
('United States', 'New York', 'New York City'),
('Canada', 'Ontario', 'Toronto'),
('Canada', 'Quebec', 'Montreal'),
('United Kingdom', 'England', 'London'),
('France', 'Île-de-France', 'Paris'),
('Germany', 'Bavaria', 'Munich'),
('Japan', 'Tokyo', 'Tokyo'),
('China', 'Beijing', 'Beijing'),
('Australia', 'New South Wales', 'Sydney'),
('Brazil', 'São Paulo', 'São Paulo'),
('India', 'Maharashtra', 'Mumbai'),
('Russia', 'Moscow Oblast', 'Moscow'),
('South Korea', 'Seoul', 'Seoul'),
('Turkey', 'Istanbul', 'Istanbul'),
('Iran', 'Khorasan Razavi', 'Mashhad'),
('Iran', 'Tehran', 'Tehran'),
('Iran', 'Tehran', 'Rey'),
('Iran', 'Tehran', 'Varamin');

INSERT INTO Train (vehicle_id, star, car_number, is_reserved_fully, wifi_access, catering, ventilation, etc, flat_wagon) VALUES
(2, '4', 12, FALSE, TRUE, TRUE, TRUE, null, TRUE),
(6, '3', 10, TRUE, FALSE, TRUE, TRUE, 'Regional', FALSE),
(8, '5', 8, FALSE, TRUE, FALSE, TRUE, 'Luxury', TRUE),
(10, '3', 0, TRUE, TRUE, FALSE, TRUE, NULL, TRUE),
(12, '4', 15, FALSE, TRUE, FALSE, TRUE, 'Express', FALSE),
(13, '3', 20, TRUE, FALSE, TRUE, TRUE, 'Regional', TRUE),
(14, '5', 10, FALSE, TRUE, TRUE, TRUE, 'Luxury', FALSE),
(15, '4', 12, TRUE, TRUE, FALSE, TRUE, 'High-speed', TRUE),
(16, '3', 8, FALSE, FALSE, TRUE, TRUE, 'Commuter', FALSE),
(17, '4', 14, TRUE, TRUE, TRUE, TRUE, 'Sleeper', TRUE),
(18, '5', 6, FALSE, TRUE, TRUE, TRUE, 'Premium', FALSE),
(19, '3', 16, TRUE, FALSE, FALSE, TRUE, 'Local', TRUE),
(20, '4', 18, FALSE, TRUE, TRUE, TRUE, 'Intercity', FALSE);

INSERT INTO Airplane (vehicle_id, airline, airplane_class, arrival_airport, departure_airport, catering, wifi_access, flat_bed_seat, etc, flight_number) VALUES
(3, 'Delta Airlines', 'Business', 'JFK', 'LAX', TRUE, TRUE, TRUE, 'Boeing 777', 'DL123'),
(4, 'United Airlines', 'Economy', 'ORD', 'SFO', TRUE, TRUE, FALSE, 'Airbus A320', 'UA456'),
(5, 'Southwest', 'Economy', 'LAX', 'HOU', FALSE, FALSE, FALSE, '737 Max', 'SW789'),
(7, 'JetBlue', 'Premium', 'BOS', 'MIA', TRUE, TRUE, TRUE, 'A321neo', 'JB321'),
(9, 'American Airlines', 'Business', 'DFW', 'ORD', TRUE, TRUE, TRUE, '787 Dreamliner', 'AA654'),
(10, 'Spirit Airlines', 'Economy', 'ATL', 'DEN', FALSE, FALSE, FALSE, 'A319', 'SP888'),
(11, 'Mahan', 'Premium', 'ATL', 'DEN', TRUE, TRUE, TRUE, 'A319', 'SP999'),
(21, 'Delta Airlines', 'Premium', 'LAX', 'JFK', TRUE, TRUE, TRUE, 'Boeing 747', 'DL124'),
(22, 'United Airlines', 'Premium', 'SFO', 'ORD', TRUE, TRUE, FALSE, 'Airbus A321', 'UA457'),
(23, 'Southwest', 'Economy', 'HOU', 'LAX', FALSE, FALSE, FALSE, '737-800', 'SW790'),
(24, 'JetBlue', 'Business', 'MIA', 'BOS', TRUE, TRUE, TRUE, 'A320', 'JB322'),
(25, 'American Airlines', 'Premium', 'ORD', 'DFW', TRUE, TRUE, TRUE, '777-300ER', 'AA655'),
(26, 'Spirit Airlines', 'Economy', 'DEN', 'ATL', FALSE, FALSE, FALSE, 'A320', 'SP889'),
(27, 'Mahan', 'Business', 'IKA', 'MHD', TRUE, TRUE, TRUE, 'A340', 'MH500'),
(28, 'Emirates', 'Premium', 'DXB', 'JFK', TRUE, TRUE, TRUE, 'A380', 'EK202'),
(29, 'Qatar Airways', 'Business', 'DOH', 'LHR', TRUE, TRUE, TRUE, '787-9', 'QR001'),
(30, 'Lufthansa', 'Premium', 'FRA', 'JFK', TRUE, TRUE, FALSE, 'A350', 'LH400');

INSERT INTO Bus (vehicle_id, bus_type, seats_row_per_row, ventilation, etc, catering, personal_monitor) VALUES
(1, 'Double Decker', 4, TRUE, 'Express', TRUE, TRUE),
(6, 'Sleeper', 3, TRUE, 'Night Service', TRUE, FALSE),
(31, 'VIP', 4, TRUE, 'Intercity', FALSE, FALSE),
(32, 'Double Decker', 3, TRUE, 'Shuttle', FALSE, FALSE),
(33, 'Double Decker', 4, TRUE, 'City Tour', FALSE, TRUE),
(34, 'Sleeper', 2, TRUE, 'Overnight', TRUE, FALSE),
(35, 'VIP', 4, TRUE, 'BRT', FALSE, FALSE),
(36, 'Double Decker', 3, TRUE, 'Student Transport', FALSE, FALSE),
(37, 'Double Decker', 4, TRUE, 'Eco Friendly', FALSE, TRUE),
(38, 'Sleeper', 3, TRUE, 'VIP Service', TRUE, TRUE),
(39, 'VIP', 4, TRUE, 'Airport Transfer', FALSE, FALSE),
(40, 'Double Decker', 3, TRUE, 'Business Class', TRUE, TRUE);

INSERT INTO Ticket (departure_location_id, arrival_location_id, arrival_date, departure_time, departure_date, remaining_capacity, cost, vehicle_id) VALUES
(1, 2, '2025-05-10', '10:30:00', '2025-05-10', 45, 95.75, 2), 
(2, 1, '2025-05-12', '14:15:00', '2025-05-12', 28, 110.00, 3),
(2, 3, '2025-05-15', '23:45:00', '2025-05-15', 120, 450.00, 4),
(3, 2, '2025-05-20', '08:30:00', '2025-05-20', 115, 420.50, 5),
(4, 5, '2025-05-11', '12:00:00', '2025-05-11', 60, 200.00, 6), 
(7, 8, '2025-05-14', '16:45:00', '2025-05-14', 85, 320.75, 7), 
(9, 10, '2025-06-01', '09:15:00', '2025-06-01', 40, 280.00, 8),
(11, 12, '2025-06-05', '20:30:00', '2025-06-05', 75, 350.50, 9), 
(13, 14, '2025-06-10', '11:00:00', '2025-06-10', 200, 550.00, 10),
(15, 1, '2025-06-15', '07:45:00', '2025-06-15', 180, 480.25, 1), 
(1, 15, CURDATE(), '07:45:00', '2025-05-06', 200, 500, 11),
(17, 15, CURDATE(), '07:45:00', '2025-05-06', 200, 500, 11),
(18, 15, CURDATE(), '07:45:00', '2025-05-06', 200, 500, 11),
(18, 1, '2025-05-05', '07:45:00', '2025-05-05', 200, 1000, 11),
(1, 15, CURDATE(), '07:45:00', '2025-05-05', 200, 500, 11);

INSERT INTO Reservation (ticket_id, passenger_id, reservation_status, reservation_date) VALUES
(1, 1, 'Confirmed','2023-01-20'),
(2, 2, 'Pending', '2024-01-21'),
(3, 3, 'Cancelled By Passenger','2024-01-22'),
(4, 4, 'Confirmed','2024-01-23'),
(5, 5, 'Pending','2024-01-24'),
(6, 6, 'Confirmed','2024-01-25'),
(7, 1, 'Confirmed', '2024-01-26'),
(8, 2, 'Cancelled By Passenger','2024-01-27'),
(9, 3, 'Confirmed','2024-01-28'),
(10, 3, 'Pending','2024-01-29'),
(1, 1, 'Confirmed','2024-01-30'),
(1, 1, 'Pending','2024-02-01'),
(2, 1, 'Cancelled By Passenger','2024-02-02'),
(2, 2, 'Confirmed', '2024-02-03'),
(3, 2, 'Pending', '2024-02-04'),
(3, 2, 'Confirmed','2024-02-05'),
(4, 2, 'Confirmed' , '2024-02-06'),
(4, 3, 'Cancelled By Passenger','2024-02-07'),
(5, 3, 'Confirmed','2024-02-08'),
(6, 3, 'Pending','2024-02-09'),
(6, 5, 'Confirmed','2024-02-10'),
(7, 5, 'Pending','2024-02-11'),
(7, 6, 'Cancelled By Passenger','2024-03-09'),
(8, 6, 'Confirmed','2024-03-19'),
(8, 1, 'Pending','2024-03-20'),
(9, 11, 'Confirmed','2024-03-21'),
(9, 11, 'Confirmed','2024-04-09'),
(10, 12, 'Cancelled By Passenger','2024-05-01'),
(10, 15, 'Confirmed','2024-05-05'),
(10, 2, 'Pending','2024-05-09'),
(1, 2, 'Confirmed','2024-10-01'),
(10, 4, 'Cancelled By Admin','2024-10-10'),
(10, 18, 'Confirmed','2024-10-11'),
(4, 18, 'Confirmed','2024-10-12'),
(11, 18, 'Confirmed','2025-03-04'),
(11, 4, 'Confirmed','2025-03-05'),
(12, 18, 'Confirmed','2025-03-10'),
(12, 2, 'Confirmed','2025-03-11'),
(13, 5, 'Confirmed','2025-03-18'),
(1, 4, 'Cancelled By Passenger','2025-04-09'),
(1, 18, 'Confirmed','2025-05-03'),
(14, 3, 'Confirmed', '2025-05-4'),
(14, 2, 'Confirmed', '2025-05-4'),
(2, 2, 'Confirmed', '2024-01-20');

INSERT INTO Payment (reservation_id, user_id, payment_status, amount, payment_method) VALUES
(1, 1, 'Completed', 120.50, 'Credit Card'),
(2, 2, 'Pending', 75.00, 'PayPal'),
(3, 3, 'Failed', 199.99, 'Bank Transfer'),
(4, 4, 'Completed', 45.00, 'Credit Card'),
(5, 5, 'Pending', 89.00, 'PayPal'),
(6, 6, 'Completed', 99.00, 'Credit Card'),
(7, 1, 'Completed', 65.00, 'Bank Transfer'),
(8, 2, 'Failed', 149.00, 'Credit Card'),
(9, 3, 'Completed', 130.00, 'PayPal'),
(10, 4, 'Completed', 55.00, 'Credit Card'),
(11, 1, 'Completed', 120.50, 'Credit Card'),
(12, 1, 'Completed', 75.00, 'PayPal'),
(13, 1, 'Completed', 199.99, 'Bank Transfer'),
(14, 2, 'Completed', 45.00, 'Credit Card'),
(15, 2, 'Pending', 89.00, 'PayPal'),
(16, 2, 'Completed', 99.00, 'Credit Card'),
(17, 2, 'Completed', 65.00, 'Bank Transfer'),
(18, 3, 'Failed', 149.00, 'Credit Card'),
(19, 3, 'Completed', 130.00, 'PayPal'),
(20, 3, 'Completed', 55.00, 'Credit Card'),
(21, 5, 'Completed', 120.50, 'Credit Card'),
(22, 5, 'Pending', 75.00, 'PayPal'),
(23, 6, 'Failed', 199.99, 'Bank Transfer'),
(24, 6, 'Completed', 45.00, 'Credit Card'),
(25, 1, 'Pending', 89.00, 'PayPal'),
(26, 11, 'Completed', 99.00, 'Credit Card'),
(27, 11, 'Completed', 65.00, 'Bank Transfer'),
(28, 12, 'Failed', 149.00, 'Credit Card'),
(29, 15, 'Completed', 130.00, 'PayPal'),
(30, 2, 'Completed', 55.00, 'Credit Card'),
(35, 18, 'Completed', 480.25, 'Credit Card'),
(36, 18, 'Completed', 420.50, 'Credit Card'),
(37, 18, 'Completed', 500, 'Credit Card'),
(38, 2, 'Completed', 500, 'Credit Card'),
(39, 5, 'Completed', 500, 'Credit Card'),
(41, 18, 'Completed', 500, 'Credit Card');

INSERT INTO Payment (reservation_id, user_id, payment_date, payment_status, amount, payment_method) VALUES
(42, 3, '2025-05-4', 'Completed', 1000, 'Credit Card'),
(43, 2, '2025-05-4', 'Completed', 1000, 'Credit Card'),
(44, 2, '2024-01-20', 'Completed', 120.50, 'Credit Card');

INSERT INTO Reports (ticket_id, passenger_id, admin_id, category, report_description, report_status) VALUES
(1, 1, 7, 'Delay', 'Departure was delayed by 45 minutes without proper announcement', 'Open'),
(2, 2, 8, 'Cleanliness', 'Seat was dirty with food stains from previous passenger', 'Pending'),
(4, 4, 9, 'Comfort', 'Air conditioning was not working during the entire trip', 'Open'),
(6, 6, 10, 'Safety', 'Luggage compartment door was not properly secured during travel', 'Closed'),
(9, 3, 14, 'Service', 'Staff was rude when asked for assistance with luggage', 'Pending'),
(4, 2, 16, 'Facilities', 'Promised WiFi service was not available on board', 'Open'),
(9, 11, 19, 'Schedule', 'Departure time changed last minute without notification', 'Closed'),
(10, 18, 20, 'Comfort', 'Seat recliner mechanism was broken', 'Pending'),
(11, 18, 21, 'Pricing', 'Charged extra fees not mentioned at time of booking', 'Open'),
(10, 4, 22, 'Cancelled by admin', 'Hazard in transaction', 'Closed');


UPDATE Reservation SET admin_id = 7 WHERE reservation_id = 1;
UPDATE Reservation SET admin_id = 8 WHERE reservation_id = 14;
UPDATE Reservation SET admin_id = 9 WHERE reservation_id = 4;
UPDATE Reservation SET admin_id = 10 WHERE reservation_id = 6;
UPDATE Reservation SET admin_id = 14 WHERE reservation_id = 9;
UPDATE Reservation SET admin_id = 16 WHERE reservation_id = 17;
UPDATE Reservation SET admin_id = 19 WHERE reservation_id = 26;
UPDATE Reservation SET admin_id = 20 WHERE reservation_id = 35;
UPDATE Reservation SET admin_id = 21 WHERE reservation_id = 37;
UPDATE Reservation SET admin_id = 22 WHERE reservation_id = 32;

-- --------------------------------------
-- Q1
-- CALL GetUserPurchasedTickets('user@example.com', NULL);

-- Q2
-- CALL GetUsersWithCancelledReservations('sadra.j3@example.com', NULL);

-- Q3
-- CALL GetTicketsByDepartureCity('Tehran');

-- Q4
-- CALL SearchTicketsByTerm('Business');
-- CALL SearchTicketsByTerm('Smith');
-- CALL SearchTicketsByTerm('Premium');
-- CALL SearchTicketsByTerm('Los Angeles');

