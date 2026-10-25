# OLMS - Online Library Management System
**Release One - Review & Leadership Transition**
GROUP 1 / Members 1-6

> A reliable small-library system that helps staff find books and manage loans.

**Project Managers:**
* Outgoing Manager: Muhammad Huzaifa Asif
* Incoming Manager: Nazir Imran

### 🔗 Project Repository
This repository contains the source code, setup guide, and test logs for OLMS Release 1 & 2.

### 🎯 Product Goal
To build a reliable system for small libraries that helps staff maintain a searchable catalogue and manage loans efficiently without losing records.

### 🚀 Release Roadmap

| Release | Focus | Expected Result |
| :--- | :--- | :--- |
| **R1 - Weeks 1-2** | Catalogue and Members | Staff can maintain books, copies and member status. |
| **R2 - Weeks 3-4** | Borrowing and Returns | Staff can issue and return copies. **MVP Target** |
| **R3 - Weeks 5-6** | Overdue Loans | Staff can identify overdue loans + History |
| **R4 - Weeks 7-8** | Quality and Reporting | Regression checks, docs, CSV/filtering |

### ✨ Features Implemented

#### Release 1 (Current Release)
**1. Catalogue Management:**
- Register and edit books (Title, Author, Edition)
- Search by title or author
- Deactivate and Reactivate books without deleting their records (Record Preservation)

**2. Physical Copies:**
- Assign unique Copy IDs for each book
- Show Available / Total copy counts

**3. Access and Membership:**
- Staff Login / Logout (Authorized access)
- Register new members and toggle Active/Inactive status (Eligibility control)

**4. Data Integrity:**
- All records survive after restart
- No hard-delete for books

#### Release 2 (Next Sprint - MVP)
- Validate member and copy before issuing
- Save loan with due date
- Issuing reduces availability, Returning restores it
- Reject: inactive members, unavailable copies, and repeat returns

### 📋 Prioritised Product Backlog

| IDs | Backlog Item | Priority | Release |
| :--- | :--- | :--- | :--- |
| PB-01-03 | Staff login, book registration, physical copies | Must | R1 |
| PB-04-05 | Title/author search, edit and deactivate books | Must | R1 |
| PB-06-07 | Member registration and eligibility | Must | R1 |
| PB-08-09 | Borrowing with due dates, returns | Must | R2 |
| PB-10 | Overdue loan listing | Must | R3 |

### 🛠️ Tech Stack
> Update this according to your actual code
- Frontend: [e.g., HTML, CSS, JavaScript / React]
- Backend: [e.g., Java / Python / PHP]
- Database: [e.g., MySQL / SQLite]
- Tools: Git, GitHub

### ⚙️ How to Run Locally

1. Clone the repository:
   
   git clone https://github.com/021Engr-imran/OLMS.git
