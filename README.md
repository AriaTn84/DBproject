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