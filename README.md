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

2. **Create and activate virtual environment**:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**:
pip install -r requirements.txt

4. **Run migrations**:
python manage.py migrate

5. **Start the development server**:
python manage.py runserver

6. **Access the GraphQL Playground**:
Visit: <http://127.0.0.1:8000/graphql/>

## 🧪 Sample GraphQL Queries

Register

```bash
mutation {
  registerUser(username: "testuser", email: "test@example.com", password: "secure123", firstName: "user", lastName: "user") {
    token
    user {
      id
      username
      firstName
      lastName
    }
  }
}
```

Login

```bash
mutation {
  loginUser(username: "testuser", password: "secure123") {
    token
    user {
      id
      username
    }
  }
}
```

updateProfile

- Updates the current user's profile details (e.g., bio, avatar, etc.).

```bash
mutation {
  updateProfile(bio: "New bio") {
    success
    user {
      id
      bio
      userName
    }
  }
}
```

followUser/unfollowUser

```bash
mutation {
  followUser(username: "anotheruser") {
    success
    message
  }
}

mutation {
  unfollowUser(username: "anotheruser") {
    success
    message
  }
}
```

Get Current User Profile

```bash
query {
  userProfile {
    id
    username
    email
    firstName
    lastName
  }
}
```

## ✅ More User Features

- isFollowing: Boolean – indicates if the current authenticated user is following another user.

- followersCount: Number of users following this user.

- followingCount: Number of users this user is following.

- followers: List of users following the current user.

- following: List of users the current user is following.

## 🔐 Note: Some operations require Authorization header

Authorization: JWT <your-token>
