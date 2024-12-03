# FlaskCommerce

A robust e-commerce platform built with Flask, offering a modern shopping experience with secure payments and order management.

## Features

- User Authentication & Authorization
- Product Management
- Shopping Cart
- Order Processing
- Payment Integration
- Admin Dashboard
- RESTful API
- Database Migrations

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip

## Installation

1. Clone the repository:

git clone https://github.com/PetrJoe/Flask-Authentication-API.git


## Setup

1. Install required packages:

pip install flask-migrate


2. Initialize migrations in your Flask app:

flask db init


## Creating Migrations

1. After making changes to your models, create a new migration:

flask db migrate -m "Initial migration"


2. Review the generated migration script in `migrations/versions/` directory

## Applying Migrations

1. Apply pending migrations to the database:

flask db upgrade


2. To rollback migrations:

flask db downgrade


## Common Commands

- Show current migration version:

flask db current


- Show migration history:

flask db history


- Mark a migration as complete without running it:

flask db stamp <migration_id>


## Tips

- Always review generated migrations before applying them
- Backup your database before running migrations in production
- Keep migrations small and focused
- Test migrations in development environment first

## Project Structure

your_project/
├── migrations/
│   ├── versions/
│   │   └── (migration files)
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
├── app/
│   └── models.py
└── config.py


This README provides a clear overview of the FlaskCommerce project, including installation steps, features, project structure, and other essential information for developers. Feel free to customize it further based on your specific project needs!


