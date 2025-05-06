-- Q1
DELIMITER //

CREATE PROCEDURE GetUserPurchasedTickets(
    IN p_email VARCHAR(100),
    IN p_phone VARCHAR(20)
)
BEGIN
    IF (p_email IS NULL AND p_phone IS NULL) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Either email or phone must be provided';
    ELSE
        SELECT 
            t.ticket_id,
            CONCAT(dep.city, ', ', dep.state, ', ', dep.country) AS departure_location,
            CONCAT(arr.city, ', ', arr.state, ', ', arr.country) AS arrival_location,
            t.departure_date,
            t.departure_time,
            t.arrival_date,
            t.cost,
            v.company_name AS vehicle_company,
            CASE 
                WHEN tr.vehicle_id IS NOT NULL THEN 'Train'
                WHEN ap.vehicle_id IS NOT NULL THEN 'Airplane'
                WHEN b.vehicle_id IS NOT NULL THEN 'Bus'
                ELSE 'Unknown'
            END AS vehicle_type,
            r.reservation_date AS purchase_date,
            p.payment_status
        FROM 
            Users u
        JOIN Passengers ps ON u.user_id = ps.user_id
        JOIN Reservation r ON ps.user_id = r.passenger_id
        JOIN Payment p ON r.reservation_id = p.reservation_id AND ps.user_id = p.user_id
        JOIN Ticket t ON r.ticket_id = t.ticket_id
        JOIN Vehicle v ON t.vehicle_id = v.vehicle_id
        LEFT JOIN Train tr ON v.vehicle_id = tr.vehicle_id
        LEFT JOIN Airplane ap ON v.vehicle_id = ap.vehicle_id
        LEFT JOIN Bus b ON v.vehicle_id = b.vehicle_id
        JOIN Location dep ON t.departure_location_id = dep.location_id
        JOIN Location arr ON t.arrival_location_id = arr.location_id
        WHERE 
            (
            (p_email IS NOT NULL AND u.email = p_email) OR 
            (p_phone IS NOT NULL AND u.phone = p_phone)
            )
            AND r.reservation_status = 'Confirmed'
            AND p.payment_status = 'Completed'
        ORDER BY 
            r.reservation_date DESC;
    END IF;
END //

DELIMITER ;

-- Q2
DELIMITER //

CREATE PROCEDURE GetUsersWithCancelledReservations(
    IN admin_email VARCHAR(100),
    IN admin_phone VARCHAR(20)
)
BEGIN
    IF (admin_email IS NULL AND admin_phone IS NULL) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Either admin email or phone must be provided';
    ELSE
        SELECT DISTINCT
            u.user_id,
            CONCAT(u.first_name, ' ', u.last_name) AS user_name,
            u.email AS user_email,
            u.phone AS user_phone,
            COUNT(r.reservation_id) AS total_cancelled_reservations,
            MAX(r.reservation_date) AS last_cancellation_date
        FROM 
            Users admin
        JOIN Admins a ON admin.user_id = a.user_id
        JOIN Reservation r ON a.user_id = r.admin_id
        JOIN Users u ON r.passenger_id = u.user_id
    WHERE(
      (admin_email IS NOT NULL AND admin.email = admin_email) OR 
      (admin_phone IS NOT NULL AND admin.phone = admin_phone)
      )
      AND r.reservation_status = 'Cancelled By Admin'

        GROUP BY
            u.user_id, user_name, user_email, user_phone
        HAVING
            COUNT(r.reservation_id) > 0
        ORDER BY
            total_cancelled_reservations DESC;
    END IF;
END //

DELIMITER ;

-- Q3
DELIMITER //

CREATE PROCEDURE GetTicketsByDepartureCity(
    IN p_city VARCHAR(100))
BEGIN
    IF (p_city IS NULL) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Departure city must be specified';
    ELSE
        SELECT 
            t.ticket_id,
            CONCAT(u.first_name, ' ', u.last_name) AS passenger_name,
            u.city_of_residence AS passenger_city,
            CONCAT(dep.city, ', ', dep.country) AS departure,
            CONCAT(arr.city, ', ', arr.country) AS arrival,
            t.departure_date,
            t.departure_time,
            t.arrival_date,
            t.cost,
            v.company_name AS carrier,
            CASE 
                WHEN tr.vehicle_id IS NOT NULL THEN 'Train'
                WHEN ap.vehicle_id IS NOT NULL THEN 'Airplane'
                WHEN b.vehicle_id IS NOT NULL THEN 'Bus'
                ELSE 'Unknown'
            END AS vehicle_type,
            r.reservation_date AS purchase_date,
            p.payment_method
        FROM 
            Ticket t
        JOIN Location dep ON t.departure_location_id = dep.location_id
        JOIN Location arr ON t.arrival_location_id = arr.location_id
        JOIN Vehicle v ON t.vehicle_id = v.vehicle_id
        JOIN Reservation r ON t.ticket_id = r.ticket_id
        JOIN Payment p ON r.reservation_id = p.reservation_id
        JOIN Passengers ps ON r.passenger_id = ps.user_id
        JOIN Users u ON ps.user_id = u.user_id
        LEFT JOIN Train tr ON v.vehicle_id = tr.vehicle_id
        LEFT JOIN Airplane ap ON v.vehicle_id = ap.vehicle_id
        LEFT JOIN Bus b ON v.vehicle_id = b.vehicle_id
        WHERE 
            dep.city = p_city
            AND p.payment_status = 'Completed'
            AND r.reservation_status = 'Confirmed'
        ORDER BY 
            t.departure_date DESC, 
            t.departure_time DESC;
    END IF;
END //

DELIMITER ;

-- Q4
DELIMITER //

CREATE PROCEDURE SearchTicketsByTerm(
    IN p_search_term VARCHAR(100))
BEGIN
    IF (p_search_term IS NULL OR p_search_term = '') THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Search term must be specified';
    ELSE
        SELECT 
            t.ticket_id,
            CONCAT(dep.city, ', ', dep.country) AS departure,
            CONCAT(arr.city, ', ', arr.country) AS arrival,
            t.departure_date,
            t.departure_time,
            t.arrival_date,
            t.cost,
            v.company_name AS carrier,
            CASE 
                WHEN tr.vehicle_id IS NOT NULL THEN 
                    CONCAT('Train (', tr.star, ' star)')
                WHEN ap.vehicle_id IS NOT NULL THEN 
                    CONCAT('Airplane (', ap.airplane_class, ' class)')
                WHEN b.vehicle_id IS NOT NULL THEN 
                    CONCAT('Bus (', b.bus_type, ')')
                ELSE 'Unknown'
            END AS vehicle_details,
            t.remaining_capacity
        FROM 
            Ticket t
        JOIN Location dep ON t.departure_location_id = dep.location_id
        JOIN Location arr ON t.arrival_location_id = arr.location_id
        JOIN Vehicle v ON t.vehicle_id = v.vehicle_id
        LEFT JOIN Train tr ON v.vehicle_id = tr.vehicle_id
        LEFT JOIN Airplane ap ON v.vehicle_id = ap.vehicle_id
        LEFT JOIN Bus b ON v.vehicle_id = b.vehicle_id
        WHERE 
            dep.city LIKE CONCAT('%', p_search_term, '%') OR
            arr.city LIKE CONCAT('%', p_search_term, '%') OR
            (ap.vehicle_id IS NOT NULL AND ap.airplane_class LIKE CONCAT('%', p_search_term, '%')) OR
            (b.vehicle_id IS NOT NULL AND b.bus_type LIKE CONCAT('%', p_search_term, '%')) OR
            (tr.vehicle_id IS NOT NULL AND tr.star LIKE CONCAT('%', p_search_term, '%'))
        ORDER BY 
            t.departure_date,
            t.departure_time;
    END IF;
END //

DELIMITER ;

-- Q5
DELIMITER //

CREATE PROCEDURE FindSameCityUsersExcludingSelf(
    IN p_user_email VARCHAR(100),
    IN p_user_phone VARCHAR(20))
BEGIN
    DECLARE v_city VARCHAR(100);
    DECLARE v_user_id INT;
    
    IF (p_user_email IS NULL AND p_user_phone IS NULL) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Either email or phone must be provided';
    ELSE
        SELECT city_of_residence, user_id INTO v_city, v_user_id
        FROM Users
        WHERE (p_user_email IS NOT NULL AND email = p_user_email)
           OR (p_user_phone IS NOT NULL AND phone = p_user_phone);
        
        IF (v_city IS NULL) THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'User not found with provided credentials';
        ELSE
            SELECT 
                u.user_id,
                CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                u.email,
                u.phone,
                u.city_of_residence
            FROM 
                Users u
            WHERE 
                u.city_of_residence = v_city
                AND u.user_id != v_user_id
            ORDER BY 
                u.last_name, u.first_name;
        END IF;
    END IF;
END //

DELIMITER ;

-- Q6
DELIMITER //

CREATE PROCEDURE GetTopUsersByPurchasesAfterDate(
    IN p_start_date DATE,
    IN p_limit INT)
BEGIN
    IF (p_start_date IS NULL OR p_limit IS NULL) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Both date and limit parameters must be provided';
    ELSEIF (p_limit <= 0) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Limit must be a positive number';
    ELSE
        SELECT 
            u.user_id,
            CONCAT(u.first_name, ' ', u.last_name) AS user_name,
            u.email,
            u.phone,
            COUNT(r.reservation_id) AS total_purchases,
            SUM(t.cost) AS total_spent
        FROM 
            Users u
        JOIN Passengers p ON u.user_id = p.user_id
        JOIN Reservation r ON p.user_id = r.passenger_id
        JOIN Payment py ON r.reservation_id = py.reservation_id
        JOIN Ticket t ON r.ticket_id = t.ticket_id
        WHERE 
            r.reservation_date >= p_start_date
            AND py.payment_status = 'Completed'
            AND r.reservation_status = 'Confirmed'
        GROUP BY 
            u.user_id, user_name, u.email, u.phone
        ORDER BY 
            total_purchases DESC,
            total_spent DESC
        LIMIT p_limit;
    END IF;
END //

DELIMITER ;

-- Q7
DELIMITER //

CREATE PROCEDURE GetCancelledTicketsByVehicleType(
    IN p_vehicle_type ENUM('Train', 'Airplane', 'Bus'))
BEGIN
    -- Validate input parameter
    IF (p_vehicle_type IS NULL) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Vehicle type must be specified (Train, Airplane, or Bus)';
    ELSE
        -- Get cancelled tickets for specified vehicle type
        SELECT 
            t.ticket_id,
            CONCAT(u.first_name, ' ', u.last_name) AS passenger_name,
            CONCAT(dep.city, ', ', dep.country) AS departure,
            CONCAT(arr.city, ', ', arr.country) AS arrival,
            t.departure_date,
            t.departure_time,
            t.cost,
            v.company_name AS carrier,
            r.reservation_date,
            r.reservation_status
        FROM 
            Ticket t
        JOIN Vehicle v ON t.vehicle_id = v.vehicle_id
        JOIN Location dep ON t.departure_location_id = dep.location_id
        JOIN Location arr ON t.arrival_location_id = arr.location_id
        JOIN Reservation r ON t.ticket_id = r.ticket_id
        JOIN Passengers ps ON r.passenger_id = ps.user_id
        JOIN Users u ON ps.user_id = u.user_id
        WHERE 
            r.reservation_status IN ('Cancelled By Passenger', 'Cancelled By Admin')
            AND (
                (p_vehicle_type = 'Train' AND EXISTS (SELECT 1 FROM Train WHERE vehicle_id = v.vehicle_id))
                OR (p_vehicle_type = 'Airplane' AND EXISTS (SELECT 1 FROM Airplane WHERE vehicle_id = v.vehicle_id))
                OR (p_vehicle_type = 'Bus' AND EXISTS (SELECT 1 FROM Bus WHERE vehicle_id = v.vehicle_id))
            )
        ORDER BY 
            t.departure_date DESC, 
            t.departure_time DESC;
    END IF;
END //

DELIMITER ;

-- Q8
DELIMITER //

CREATE PROCEDURE GetUsersByReportCategory(
    IN p_report_category VARCHAR(100))
BEGIN
    IF (p_report_category IS NULL OR p_report_category = '') THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Report category must be specified';
    ELSE
        SELECT 
            u.user_id,
            CONCAT(u.first_name, ' ', u.last_name) AS user_name,
            u.email,
            u.phone,
            COUNT(r.report_id) AS report_count
        FROM 
            Users u
        JOIN Reports r ON u.user_id = r.passenger_id
        WHERE 
            r.category = p_report_category
        GROUP BY 
            u.user_id, user_name, u.email, u.phone
        ORDER BY 
            report_count DESC;
    END IF;
END //

DELIMITER ;


-- --------------------------------------
-- CALL GetUserPurchasedTickets('user@example.com', NULL);
-- CALL GetUsersWithCancelledReservations('sadra.j3@example.com', NULL);
-- CALL GetTicketsByDepartureCity('Tehran');
-- CALL SearchTicketsByTerm('Business');
-- CALL FindSameCityUsersExcludingSelf('ali.j3@example.com', NULL);
-- CALL GetTopUsersByPurchasesAfterDate('2025-01-01', 5);
-- CALL GetCancelledTicketsByVehicleType('Airplane');
-- CALL GetUsersByReportCategory('Comfort');