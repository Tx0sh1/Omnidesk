# Project Brainstorm - OmniDesk

## Ticketing Flow

- Users can sign up and log in
- Create new tickets with:
  - Title
  - Description
  - Category
  - Priority (Low, Medium, High)
- Tickets have statuses:
  - Open
  - In Progress
  - Closed
- Admin can:
  - View all tickets
  - Assign tickets to users
  - Update status
- Users and Admins can comment on tickets

## Tech Notes

- Backend: Flask + SQLite for MVP
- Frontend: Vanilla JS with fetch API for HTTP requests
- Authentication: Flask-Login or JWT (to decide)
- Future: React frontend, Rust microservices

## Goals for Next Days

- Plan DB schema
- Setup Flask routes
- Setup frontend basic UI
