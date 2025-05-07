-- Q1
SELECT u.first_name, u.last_name
FROM Users u
JOIN Passengers p USING (user_id)
WHERE p.user_id NOT IN (
    SELECT DISTINCT r.passenger_id
    FROM Reservation r
);
    
-- Q2
SELECT u.user_id , u.first_name , u.last_name
FROM Users u
JOIN Passengers p USING (user_id) 
WHERE p.user_id IN(
  SELECT DISTINCT passenger_id 
    FROM reservation
    WHERE reservation_status = 'Confirmed'
);

-- Q3
SELECT 
    u.user_id,
    u.first_name,
    u.last_name,
    YEAR(p.payment_date) AS payment_year,
    
    SUM(CASE WHEN MONTH(p.payment_date) = 1 THEN p.amount ELSE 0 END) AS January,
    SUM(CASE WHEN MONTH(p.payment_date) = 2 THEN p.amount ELSE 0 END) AS February,
    SUM(CASE WHEN MONTH(p.payment_date) = 3 THEN p.amount ELSE 0 END) AS March,
    SUM(CASE WHEN MONTH(p.payment_date) = 4 THEN p.amount ELSE 0 END) AS April,
    SUM(CASE WHEN MONTH(p.payment_date) = 5 THEN p.amount ELSE 0 END) AS May,
    SUM(CASE WHEN MONTH(p.payment_date) = 6 THEN p.amount ELSE 0 END) AS June,
    SUM(CASE WHEN MONTH(p.payment_date) = 7 THEN p.amount ELSE 0 END) AS July,
    SUM(CASE WHEN MONTH(p.payment_date) = 8 THEN p.amount ELSE 0 END) AS August,
    SUM(CASE WHEN MONTH(p.payment_date) = 9 THEN p.amount ELSE 0 END) AS September,
    SUM(CASE WHEN MONTH(p.payment_date) = 10 THEN p.amount ELSE 0 END) AS October,
    SUM(CASE WHEN MONTH(p.payment_date) = 11 THEN p.amount ELSE 0 END) AS November,
    SUM(CASE WHEN MONTH(p.payment_date) = 12 THEN p.amount ELSE 0 END) AS December

FROM Payment p
JOIN 
  Users u USING (user_id)
JOIN 
  Passengers pas USING (user_id)
WHERE 
  p.payment_status = 'Completed'
GROUP BY 
  u.user_id, YEAR(p.payment_date)
ORDER BY u.user_id ;

-- Q4
SELECT u.user_id ,u.first_name, u.last_name ,  ld.city AS departure
FROM Users u
JOIN 
  Passengers pas USING (user_id)
JOIN 
  reservation r ON r.passenger_id = u.user_id
JOIN 
    Ticket t ON r.ticket_id = t.ticket_id
JOIN 
  Location ld ON ld.location_id = t.departure_location_id
WHERE 
  r.reservation_status = 'Confirmed'
GROUP BY 
    u.user_id
    , t.departure_location_id
HAVING 
  COUNT(*) = 1;

-- Q5
SELECT u.user_id, u.first_name, u.last_name, u.email, r.reservation_date, t.ticket_id , l.city
FROM Reservation r
JOIN 
    Passengers p ON p.user_id = r.passenger_id
JOIN 
	Users u ON u.user_id = p.user_id
JOIN 
	Ticket t USING(ticket_id)
JOIN 
	Location l ON location_id = t.departure_location_id
WHERE 
	r.reservation_status = 'Confirmed'
ORDER BY r.reservation_date DESC
LIMIT 1;

-- Q6
SELECT u.user_id ,u.email 
FROM Payment pay
JOIN 
	Passengers p ON p.user_id = pay.user_id
JOIN 
	Users u ON u.user_id = p.user_id
WHERE 
	pay.payment_status = 'Completed'
GROUP BY p.user_id
HAVING SUM(pay.amount) > (
	SELECT AVG(user_total)
    FROM (
        SELECT SUM(amount) AS user_total
        FROM Payment
        WHERE payment_status = 'Completed'
        GROUP BY user_id
    ) AS avg_subquery
);

-- Q7
SELECT vehicle_type , COUNT(*) AS tickets_sold
FROM (
    SELECT 'Airplane' AS vehicle_type
    FROM Reservation r
    JOIN Ticket t ON r.ticket_id = t.ticket_id
    JOIN Airplane a ON t.vehicle_id = a.vehicle_id
    WHERE r.reservation_status = 'Confirmed'

    UNION ALL

    SELECT 'Train' AS vehicle_type
    FROM Reservation r
    JOIN Ticket t ON r.ticket_id = t.ticket_id
    JOIN Train tr ON t.vehicle_id = tr.vehicle_id
    WHERE r.reservation_status = 'Confirmed'

    UNION ALL

    SELECT 'Bus' AS vehicle_type
    FROM Reservation r
    JOIN Ticket t ON r.ticket_id = t.ticket_id
    JOIN Bus b ON t.vehicle_id = b.vehicle_id
    WHERE r.reservation_status = 'Confirmed'
) AS combined
GROUP BY vehicle_type;

-- Q8
SELECT u.first_name, u.last_name, COUNT(r.reservation_id) AS tickets_bought
FROM Reservation r
JOIN Passengers p ON r.passenger_id = p.user_id
JOIN Users u ON u.user_id = p.user_id
WHERE 
	r.reservation_status = 'Confirmed'
	AND r.reservation_date >= NOW() - INTERVAL 7 DAY
GROUP BY p.user_id
ORDER BY tickets_bought DESC
LIMIT 3;

-- Q9
SELECT 
	l.city, COUNT(r.reservation_id) AS tickets_sold
FROM 
	Location l
LEFT JOIN 
	Ticket t ON l.location_id = t.departure_location_id
LEFT JOIN 
	Reservation r ON t.ticket_id = r.ticket_id AND r.reservation_status = 'Confirmed'
WHERE 
	l.state = 'Tehran'
GROUP BY 
	l.city
ORDER BY 
	tickets_sold DESC;
    
-- Q10
SELECT DISTINCT l.city
FROM Reservation r
JOIN Ticket t USING(ticket_id)
JOIN Location l ON t.departure_location_id = l.location_id
WHERE r.passenger_id = (
    SELECT p.user_id
    FROM Passengers p
    WHERE p.sign_up_date = (
		SELECT MIN(sign_up_date) 
		FROM Passengers)
)
AND r.reservation_status = 'Confirmed';


-- Q11
SELECT u.user_id ,a.admin_role ,u.first_name , u.last_name
FROM Admins a 
JOIN Users u USING (user_id);


-- Q12
SELECT 
    u.first_name,
    u.last_name,
    COUNT(*) AS ticket_count
FROM 
    Users u
JOIN 
    Passengers p USING (user_id)
JOIN 
    Reservation r ON u.user_id = r.passenger_id 
JOIN 
    Payment pay ON r.reservation_id = pay.reservation_id
WHERE 
    r.reservation_status = 'Confirmed'
GROUP BY 
    u.user_id
HAVING 
    COUNT(*) >= 2
ORDER BY 
	ticket_count;


-- Q13
SELECT u.first_name, u.last_name, COUNT(r.reservation_id) AS train_tickets
FROM Passengers p
JOIN Users u ON u.user_id = p.user_id
LEFT JOIN Reservation r ON u.user_id = r.passenger_id 
  AND r.reservation_status = 'Confirmed'
LEFT JOIN Ticket t ON r.ticket_id = t.ticket_id
LEFT JOIN Train tr ON t.vehicle_id = tr.vehicle_id
WHERE 
	tr.vehicle_id IS NOT NULL OR r.reservation_id IS NULL
GROUP BY u.user_id
HAVING COUNT(r.reservation_id) <= 2
ORDER BY train_tickets DESC;

-- Q14
SELECT u.user_id , u.phone , u.email
FROM Passengers p 
JOIN Users u USING(user_id)
WHERE EXISTS (
    SELECT 'Airplane Check'
    FROM Reservation r
    JOIN Ticket t ON r.ticket_id = t.ticket_id
    JOIN Airplane a ON t.vehicle_id = a.vehicle_id
    WHERE r.passenger_id = u.user_id AND r.reservation_status = 'Confirmed'
)
AND EXISTS (
    SELECT 'Train Check'
    FROM Reservation r
    JOIN Ticket t ON r.ticket_id = t.ticket_id
    JOIN Train tr ON t.vehicle_id = tr.vehicle_id
    WHERE r.passenger_id = u.user_id AND r.reservation_status = 'Confirmed'
)
AND EXISTS (
    SELECT 'Bus Check'
    FROM Reservation r
    JOIN Ticket t ON r.ticket_id = t.ticket_id
    JOIN Bus b ON t.vehicle_id = b.vehicle_id
    WHERE r.passenger_id = u.user_id AND r.reservation_status = 'Confirmed'
);

-- Q15
SELECT t.ticket_id , r.reservation_id , CONCAT(u.first_name , ' ' , u.last_name) AS 'name' , r.reservation_date
FROM Reservation r 
JOIN Passengers p ON p.user_id = r.passenger_id
JOIN Users u ON u.user_id = p.user_id
JOIN 
	Ticket t USING (ticket_id)
WHERE 
	r.reservation_status = 'Confirmed' 
    AND YEAR(r.reservation_date) = YEAR(NOW())
	AND MONTH(r.reservation_date) = MONTH(NOW())
    AND DAY(r.reservation_date) = DAY(NOW())
    AND HOUR(r.reservation_date) >= HOUR('00')
    AND MINUTE(r.reservation_date) >= MINUTE('00')
    AND SECOND(r.reservation_date) >= SECOND('00'); 

-- Q16
 WITH TicketSales AS (
    SELECT 
        t.ticket_id,
        CONCAT(l1.city, ' to ', l2.city) AS route,
        v.company_name,
        COUNT(r.reservation_id) AS tickets_sold
    FROM 
        Ticket t
    JOIN 
        Reservation r ON t.ticket_id = r.ticket_id
    JOIN 
        Vehicle v ON t.vehicle_id = v.vehicle_id
    JOIN 
        Location l1 ON t.departure_location_id = l1.location_id
    JOIN 
        Location l2 ON t.arrival_location_id = l2.location_id
    WHERE 
        r.reservation_status = 'Confirmed'
    GROUP BY 
        t.ticket_id
)
SELECT * FROM TicketSales
ORDER BY tickets_sold DESC
LIMIT 1 OFFSET 1;


-- Q17
WITH AdminCancellations AS (
    SELECT 
        CONCAT(U.first_name, ' ', U.last_name) AS admin_name,
        COUNT(*) AS admin_cancel_count
    FROM 
        Reservation R
    JOIN 
        Admins A ON R.admin_id = A.user_id
    JOIN 
        Users U ON A.user_id = U.user_id
    WHERE 
        R.reservation_status IN ('Cancelled By Admin')
        AND R.admin_id IS NOT NULL
    GROUP BY 
        R.admin_id
),
TotalCancellations AS (
    SELECT 
        COUNT(*) AS total_cancel_count
    FROM 
        Reservation
    WHERE 
        reservation_status IN ('Cancelled By Passenger', 'Cancelled By Admin')
)
SELECT 
    AC.admin_name,
    AC.admin_cancel_count,
    TC.total_cancel_count,
    ROUND(100.0 * AC.admin_cancel_count / TC.total_cancel_count, 2) AS cancel_percentage
FROM 
    AdminCancellations AC
CROSS JOIN 
    TotalCancellations TC
ORDER BY 
    AC.admin_cancel_count DESC
LIMIT 1;



-- Q18
UPDATE Users
SET last_name = 'Redington'
WHERE user_id = (
SELECT r.passenger_id
FROM Reservation r
    JOIN Passengers p ON r.passenger_id = p.user_id
    WHERE r.reservation_status = 'Cancelled By Passenger' OR r.reservation_status = 'Cancelled By Admin'
    GROUP BY r.passenger_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
);

-- Q19
SET SQL_SAFE_UPDATES = 0;
DELETE FROM Payment
WHERE reservation_id IN (
	SELECT reservation_id
	FROM Reservation r
	JOIN Users u ON r.passenger_id = u.user_id
	JOIN Passengers p ON u.user_id = p.user_id
	WHERE r.reservation_status IN ('Cancelled By Passenger', 'Cancelled By Admin') AND u.last_name = 'Redington'
);

DELETE FROM Reservation
WHERE reservation_status IN ('Cancelled By Passenger', 'Cancelled By Admin')
	AND passenger_id IN (
		SELECT user_id
		FROM Users u
		JOIN Passengers p USING (user_id)
		WHERE u.last_name = 'Redington'
);

-- Q20
DELETE FROM Payment
WHERE reservation_id IN (
    SELECT reservation_id
    FROM Reservation
    WHERE reservation_status IN ('Cancelled By Passenger', 'Cancelled By Admin')
);
DELETE FROM Reservation
WHERE reservation_status IN ('Cancelled By Passenger', 'Cancelled By Admin');

-- Q21
UPDATE Ticket t
JOIN Vehicle v ON t.vehicle_id = v.vehicle_id
JOIN Reservation r ON r.ticket_id = t.ticket_id
SET t.cost = t.cost * 0.9
WHERE 
    v.company_name = 'Mahan'
    AND r.reservation_status = 'Confirmed'
    AND DATE(r.reservation_date) = CURDATE() - INTERVAL 1 DAY;

-- Q22
SELECT 
    t.ticket_id,
    CONCAT(l1.city, ' to ', l2.city) AS route,
    rp.category AS report_topic,
    COUNT(rp.report_id) AS report_count
FROM 
    Reports rp
JOIN 
    Ticket t ON rp.ticket_id = t.ticket_id
JOIN 
    Location l1 ON t.departure_location_id = l1.location_id
JOIN 
    Location l2 ON t.arrival_location_id = l2.location_id
GROUP BY 
    t.ticket_id, l1.city, l2.city, rp.category
HAVING 
    t.ticket_id = (
        SELECT ticket_id
        FROM Reports
        GROUP BY ticket_id
        ORDER BY COUNT(report_id) DESC
        LIMIT 1
    )
ORDER BY 
    report_count DESC;
    
