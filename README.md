Below is a comprehensive `README.md` file for your GitHub repository, covering the project up to the end of **Phase 2**.
---

# Travel Ticket Reservation System

## Project Overview

This project is a comprehensive platform for searching, filtering, reserving, and purchasing travel tickets for flights, trains, and buses, similar to the AliBaba platform. The system allows users to manage reservations, cancel tickets, and request refunds. It utilizes a relational database (MySQL) for persistent data storage and Redis for OTP management, caching, and improving search performance.

The project is divided into four mandatory phases:
1. ER Diagram and Database Design
2. Table Creation and Query Implementation
3. Server-Side Implementation and APIs
4. UI Design and Implementation (Website or Mobile App)

This repository currently covers Phase 1 and Phase 2, focusing on the database design, table creation, and query implementation.

---

## Features

- User Management: Users can register and log in using OTP sent via email or phone. Two roles are supported:
  - Regular Users (Travelers): Can purchase and manage tickets.
  - Admins (Support Staff): Manage the system and handle reports.
- Ticket Search and Reservation: Users can search for tickets based on origin, destination, travel date, passenger count, and transport type (flight, train, bus).
- Payment System: Reservations require payment (mocked locally). Unpaid reservations are automatically canceled after a set time.
- Reservation History: Users can view their booking history with statuses (successful, failed, canceled).
- Admin Actions: Admins can review and manage problematic reservations.
- Advanced Search: Filter tickets by price, transport company, departure time, stops, and amenities.
- Ticket Modifications: Users can cancel or modify tickets, subject to transport company policies.
- Reporting: Users can report issues with tickets or payments.
- Temporary Reservation Lock: Tickets can be reserved for a limited time (e.g., 10 minutes) before payment.
- Profile Management: Users can edit personal details, change passwords, and view transaction history.

---

## Technologies Used

- Database:
  - Relational: MySQL
  - NoSQL: Redis (for OTP and caching)
- Version Control: Git (with GitHub for repository management)

---

## Setup Instructions

### Prerequisites
- Git: For cloning and version control.
- MySQL For the relational database.
- Redis: For caching and OTP management.
 **Node.js/Other Backend Framework**: For future phases (not implemented in Phase 1 or 2).

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/AriaTn84/DBproject.git
   cd DBproject
   ```

2. Set Up MySQL:
   - Install MuSQL and ensure it's running.
   - Create a database:
     ```sql
     CREATE DATABASE raahi;
     ```

3. **Verify Setup**:
   - Run the query scripts in `query.sql` to test the database.
   - Run the stored procedures in `stored_procedures.sql` to verify functionality.

---

## Project Structure

```
├── Indexing.sql             
├── query.sql                
├── raahi.sql                
├── store_prosedure.sql      
├── tests.sql                 
├── Raahi.drawio.png          
├── Raahi.drawio.xml          
├── README.md                 

```

---

## Phase 1: ER Diagram and Database Design

### Objectives
- Design an ER Diagram representing all entities, relationships, and constraints.
- Create initial table structures adhering to the **3rd Normal Form (3NF)**.
- Define primary keys, foreign keys, unique constraints, and check constraints.
- Ensure the database is optimized to avoid redundant data and inconsistencies.

### Key Models
- **User**: Stores user information (name, email/phone, role, city, hashed password, etc.).
- **Ticket**: Stores ticket details (transport type, route, date, price, capacity, etc.).
- **Reservation**: Manages user reservations (user ID, ticket ID, status, expiration time).
- **Payment**: Tracks payment transactions (user ID, reservation ID, amount, status).
- **Report**: Stores user-reported issues (user ID, ticket/reservation ID, report type, status).
- **Transport Details**:
  - **TrainDetails**: Train-specific features (stars, amenities, private coupe option).
  - **FlightDetails**: Flight-specific features (airline, class, stops, amenities).
  - **BusDetails**: Bus-specific features (company, type, seat layout, amenities).

### ER Diagram
The ER Diagram is located in `database/er_diagram/er_diagram.pdf`. It includes:
- **Entities**: User, Ticket, Reservation, Payment, Report, TrainDetails, FlightDetails, BusDetails.
- **Relationships**:
  - User → Reservation (1:N, one user can have multiple reservations).
  - Ticket → Reservation (1:N, one ticket can be reserved multiple times).
  - Reservation → Payment (1:1, each reservation has one payment).
  - Ticket → Transport Details (1:1, each ticket links to specific transport details).
- **Constraints**:
  - Unique email/phone for users.
  - Non-negative ticket prices.
  - Valid reservation expiration times.

### Outputs
- `AlibabaDatabase.sql`: SQL script for table creation.
- `DataBAse_Alibaba-page-drawio.png`: ER diagram png file.
- `DataBAse_Alibaba-page-drawio.xml`: ER diagram xml file.

---

## Phase 2: Table Creation and Query Implementation

### Objectives
- Finalize table structures in 3NF based on the ER Diagram.
- Implement tables in PostgreSQL with proper indexes and constraints.
- Write informational and analytical SQL queries.
- Create stored procedures for repetitive and complex operations.

### Table Creation
- Tables are created with:
  - **Primary Keys**: Unique identifiers for each record.
  - **Foreign Keys**: Ensure referential integrity.
  - **Indexes**: Optimize frequent search operations (e.g., ticket search by date or route).
  - **Constraints**: Unique, Check, and Not Null constraints to enforce data integrity.
- SQL script: `raahi.sql`.

### Initial Data
- At least 10 records per table are inserted to test functionality.
- SQL script: `tests.sql`.

### Queries
The following informational and analytical queries are implemented (see `query.sql`):
1. Users who have never reserved a ticket.
2. Users who have purchased at least one ticket.
3. Total payments by each user per month.
4. Users who purchased exactly one ticket in each city.
5. User who purchased the most recent ticket.
6. Users with payments above the average.
7. Number of tickets sold per transport type.
8. Top 3 users with the most ticket purchases in the last week.
9. Tickets sold in Tehran, broken down by city.
10. Cities where the oldest registered user made purchases.
11. List of site admins.
12. Users with at least 2 ticket purchases.
13. Users with at most 2 tickets for a specific transport type.
14. Users who purchased tickets for all transport types.
15. Tickets purchased today, ordered by purchase time.
16. Second most sold ticket.
17. Admin with the highest cancellation rate.
18. Change the last name of the user with the most canceled tickets to "Redington".
19. Delete all canceled tickets for user "Redington".
20. Delete all canceled tickets in the system.
21. Reduce the price of yesterday's Mahan Airlines tickets by 10%.
22. Report topic and count for the ticket with the most reports.

### Stored Procedures
The following stored procedures are implemented (see `stored_procedures.sql`):
1. List tickets purchased by a user (by email/phone).
2. List users whose reservations were canceled by an admin.
3. List tickets purchased in a specific city.
4. Search tickets by keyword in passenger name, route, or class.
5. List users from the same city as a given user.
6. Top N users with the most purchases since a given date.
7. List canceled tickets for a specific transport type.
8. List users with the most reports for a specific topic.

### Outputs
- `database/rahii.sql`: Final table creation script.
- `database/tests.sql`: Initial data insertion script.
- `database/query.sql`: Informational and analytical queries.
- `database/stored_procedures.sql`: Stored procedures for complex operations.

---

## Version Control

- **Repository**: Hosted on GitHub.
- **Branching Strategy**:
  - Each phase is developed in a separate branch (e.g., `Phase1_ER-diagram`, `phase2`).
  - Completed phases are merged into the `main` branch via Pull Requests.
- **Commits**: At least 5 meaningful commits per phase, documenting incremental progress.
- **Commit Guidelines**:
  - Use descriptive messages (e.g., "Add ER Diagram for Phase 1", "Implement reservation queries").
  - Avoid committing all changes at once to demonstrate iterative development.

---

## Bonus Features (Planned)
- **GitHub Actions**: Automate CI/CD for database migrations and testing (to be implemented for bonus points).
- **Query Optimization**: Use indexing and query optimization techniques for improved performance (partially implemented in Phase 2).

---

## How to Run

1. Ensure PostgreSQL and Redis are running.
2. Execute the SQL scripts in the following order:
   - `raahi.sql`
   - `tests.sql`
   - `query.sql` (to test queries)
   - `stored_procedures.sql` (to test procedures)
3. Use an SQL client to verify the results of queries and stored procedures.

---

## Future Phases

- **Phase 3**: Implement server-side logic and RESTful APIs using a backend framework (e.g., Node.js, Django).
- **Phase 4**: Develop a user-friendly UI (web or mobile app) for ticket search, reservation, and management.

---

## Contributing

This is a student project for the **Database Systems** course. Contributions are limited to the project team. For feedback or suggestions, contact the team via GitHub Issues.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

- **Course Instructor**: Dr. Pishgou
- **Senior TA**: Eng. Alireza Ghorbani
- **Supervising TA**: Eng. Mohammad Hossein Hooshmand
- **Repository Maintainer**: [Arya Tehrani/AryaTn84]

---

This README will be updated as the project progresses through Phases 3 and 4.

---

This `README.md` file provides a clear, professional, and detailed overview of the project up to the end of Phase 2, adhering to the project requirements. You can copy this content into a `README.md` file in your GitHub repository. Let me know if you need further adjustments or additional details!