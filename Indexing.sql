-- Indexing :
-- Users
CREATE INDEX idx_users_user_id ON Users(user_id);
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_phone ON Users(phone);

-- Passengers
CREATE INDEX idx_passengers_user_id ON Passengers(user_id);
CREATE INDEX idx_passengers_signup_date ON Passengers(sign_up_date);

-- Reservation
CREATE INDEX idx_reservation_passenger_id ON Reservation(passenger_id);
CREATE INDEX idx_reservation_ticket_id ON Reservation(ticket_id);
CREATE INDEX idx_reservation_admin_id ON Reservation(admin_id);
CREATE INDEX idx_reservation_status ON Reservation(reservation_status);
CREATE INDEX idx_reservation_date ON Reservation(reservation_date);

-- Payment
CREATE INDEX idx_payment_user_id ON Payment(user_id);
CREATE INDEX idx_payment_reservation_id ON Payment(reservation_id);
CREATE INDEX idx_payment_status ON Payment(payment_status);
CREATE INDEX idx_payment_date ON Payment(payment_date);

-- Ticket
CREATE INDEX idx_ticket_ticket_id ON Ticket(ticket_id);
CREATE INDEX idx_ticket_vehicle_id ON Ticket(vehicle_id);
CREATE INDEX idx_ticket_departure_location_id ON Ticket(departure_location_id);
CREATE INDEX idx_ticket_arrival_location_id ON Ticket(arrival_location_id);

-- Location
CREATE INDEX idx_location_location_id ON Location(location_id);
CREATE INDEX idx_location_city ON Location(city);
CREATE INDEX idx_location_state ON Location(state);

-- Vehicle
CREATE INDEX idx_vehicle_vehicle_id ON Vehicle(vehicle_id);
CREATE INDEX idx_vehicle_company_name ON Vehicle(company_name);

-- Airplane / Train / Bus 
CREATE INDEX idx_airplane_vehicle_id ON Airplane(vehicle_id);
CREATE INDEX idx_train_vehicle_id ON Train(vehicle_id);
CREATE INDEX idx_bus_vehicle_id ON Bus(vehicle_id);

-- Reports
CREATE INDEX idx_reports_ticket_id ON Reports(ticket_id);
CREATE INDEX idx_reports_category ON Reports(category);

-- Admins
CREATE INDEX idx_admins_user_id ON Admins(user_id);
