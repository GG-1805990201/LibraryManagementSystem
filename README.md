# Library Management System (LMS) API

The Library Management System API is a RESTful web service designed to manage books, members, and loan transactions in a library. It provides endpoints for user authentication, book management, member management, and loan processing. The API supports JWT-based authentication and is documented using Swagger.

## Features

- **User Authentication**: Register and login with JWT-based security.
- **Books Management**: Add, update, delete, and view books with filtering and pagination.
- **Members Management**: Add, update, delete, and view library members.
- **Loans Management**: Create, update, delete, and view book loans.
- **HATEOAS**: Hypermedia links for easy navigation and resource discovery.
- **API Documentation**: Swagger documentation for easy integration and testing.

## Technology Stack

- **Framework**: Flask
- **Database**: SQLite
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: Swagger via Flasgger

## Getting Started

### Prerequisites

- Python 3.8+
- Pip (Python package manager)
- Virtual environment (optional but recommended)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/GG-1805990201/LibraryManagementSystem.git
   cd LibraryManagementSystem
2. Install dependencies:
  pip install -r requirements.txt
3. Run the application:
   run main..py file
The API will be accessible at http://localhost:9090.
and you can view through swagger UI at http://localhost:9090/apidocs

### API Endpoints
Auth
Register: POST /auth/register
Login: POST /auth/login
Protected: GET /auth/protected
Books
Create Book: POST /api/books
Get Books: GET /api/books
Get Book by ID: GET /api/books/{book_id}
Update Book: PUT /api/books/{book_id}
Delete Book: DELETE /api/books/{book_id}
Members
Get Members: GET /api/members
Get Member by ID: GET /api/members/{member_id}
Update Member: PUT /api/members/{member_id}
Delete Member: DELETE /api/members/{member_id}
Loans
Create Loan: POST /api/loans
Get Loans: GET /api/loans
Get Loan by ID: GET /api/loans/{loan_id}
Update Loan: PUT /api/loans/{loan_id}
Delete Loan: DELETE /api/loans/{loan_id}
Swagger Documentation
Access the API documentation at http://localhost:9090/apidocs.

Usage
Register a User: Use the /auth/register endpoint to create a new user.
Login: Use the /auth/login endpoint to obtain a JWT token.
Access Protected Endpoints: Include the JWT token in the Authorization header (as Bearer <token>) for protected routes.
