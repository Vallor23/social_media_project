# Django GraphQL API - User Auth & Social Follow System

This is a backend API built with **Django** and **Graphene-Django** that provides user authentication and a simple social interaction system (follow/unfollow users) via **GraphQL**.

---

## 🚀 Features

- User Registration & Login (JWT-based authentication)
- Secure Token Generation (with `django-graphql-jwt`)
- Profile Update for Authenticated Users
- Follow / Unfollow Other Users
- GraphQL endpoint with schema descriptions
- Well-structured and documented codebase

---

## 🛠️ Tech Stack

- Python & Django
- Graphene-Django (GraphQL for Django)
- Django-GraphQL-JWT (authentication)
- postgresQL
- GraphiQL interface for interactive querying

---

## 📦 Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

Create and activate virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run migrations:

bash
Copy
Edit
python manage.py migrate
Start the development server:

bash
Copy
Edit
python manage.py runserver
Access the GraphQL Playground:

Visit: http://127.0.0.1:8000/graphql/