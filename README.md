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
