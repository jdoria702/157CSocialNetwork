# Social Networking App (Django + Neo4j)

## 📌 Overview

This project is a social networking web application built using **Django** for backend/authentication and **Neo4j Aura** for graph-based social relationships.

The app allows users to:

* Create accounts and log in
* Maintain user profiles
* Store and manage social connections using a graph database

---

## 🚀 Features

### User Management

* User registration (username, name, email, optional bio)
* User login and logout
* Authentication using Django’s built-in auth system
* Protected routes (login required)

### Graph-Based Social System (Neo4j)

* Each user is stored as a **node** in Neo4j
* Supports graph relationships such as:

  * `FOLLOWS` (planned)
* Designed for:

  * Followers / Following
  * Mutual connections
  * Friend recommendations (via graph traversal)

---

## 🏗️ Tech Stack

* **Backend Framework:** Django
* **Database (Auth):** SQLite (default Django DB)
* **Graph Database:** Neo4j (AuraDB)
* **Language:** Python

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd social-network
```

---

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If no requirements file yet:

```bash
pip install django neo4j python-dotenv
```

---

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
NEO4J_URI=neo4j+s://<your-instance-id>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<your-password>
```

---

### 5. Apply migrations

```bash
python manage.py migrate
```

---

### 6. Run the server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## 🔐 Authentication Flow

* Landing page (public)
* Signup / Login
* Redirect to protected home page after login
* Logout returns user to landing page

---

## 🧠 Neo4j Integration

When a user registers:

* A Django user is created (SQL database)
* A corresponding **Neo4j node** is created:

```cypher
MERGE (u:User {django_id: $django_id})
SET u.username = $username,
    u.email = $email,
    u.first_name = $first_name,
    u.last_name = $last_name,
    u.bio = $bio
```

---

## 📁 Project Structure

```
social-network/
│
├── config/            # Django project settings
├── accounts/          # User authentication & profiles
│   ├── views.py
│   ├── forms.py
│   ├── neo4j_service.py
│   ├── urls.py
│   └── templates/
│
├── templates/         # Global templates (login)
├── venv/              # Virtual environment (ignored)
├── .env               # Environment variables (ignored)
└── manage.py
```

---

## 🛡️ Security Notes

* `.env` is ignored via `.gitignore`
* Neo4j credentials are **not committed**
* Django handles password hashing securely

---

## 🧪 Future Improvements

* Follow / Unfollow users (`FOLLOWS` relationship)
* View followers and following lists
* Mutual connections
* Friend recommendation system (graph traversal)
* User profile page with editable bio
* Posts, likes, and comments

---

## 👤 Author

Jason Doria
Computer Science @ San Jose State University

---

## 📄 License

This project is for academic purposes.
