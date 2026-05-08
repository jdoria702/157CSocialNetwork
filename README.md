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

## 📊 Populating the Neo4j Dataset

This project supports importing a mock social graph dataset into Neo4j AuraDB for testing graph traversal features such as:

* Followers / Following
* Mutual connections
* Friend recommendations
* Popular users

The dataset consists of:

* `users.csv` → User nodes
* `follows.csv` → `FOLLOWS` relationships

---

### 1. Generate Mock Users with Mockaroo

Use:

[Mockaroo](https://mockaroo.com/?utm_source=chatgpt.com)

Create a dataset with the following fields:

| Field Name | Type |
|---|---|
| django_id | Row Number |
| first_name | First Name |
| last_name | Last Name |
| username | Username |
| email | Email Address |
| bio | Sentences |
| password | Password |

Important:

* Set `django_id` to start at a high value such as `10001`
* This prevents collisions with real Django users stored in SQLite

Example:

```csv
django_id,first_name,last_name,username,email,bio,password
10001,John,Smith,johnsmith,john@example.com,"CS student",password123
10002,Amy,Chen,amychen,amy@example.com,"Coffee lover",password123
```

Download the file as:

```text
users.csv
```

---

### 2. Generate Follow Relationships

Create a Python file:

```text
generate_follows.py
```

Add:

```python
import csv
import random

START_ID = 10001
NUM_USERS = 100
NUM_FOLLOWS = 500

user_ids = list(range(START_ID, START_ID + NUM_USERS))
pairs = set()

while len(pairs) < NUM_FOLLOWS:
    follower_id = random.choice(user_ids)
    following_id = random.choice(user_ids)

    if follower_id != following_id:
        pairs.add((follower_id, following_id))

with open("follows.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["follower_id", "following_id"])
    writer.writerows(pairs)

print("Created follows.csv")
```

Run:

```bash
python generate_follows.py
```

This creates:

```text
follows.csv
```

---

### 3. Import into Neo4j AuraDB

Open:

[Neo4j Data Importer](https://data-importer.neo4j.io/?utm_source=chatgpt.com)

Upload:

* `users.csv`
* `follows.csv`

---

### 4. Configure Node Import

Create a `User` node using:

| Setting | Value |
|---|---|
| Label | User |
| ID Field | django_id |

Map the remaining fields as properties.

---

### 5. Configure Relationship Import

Create a relationship:

```text
(:User)-[:FOLLOWS]->(:User)
```

Using:

| Source Field | Target Field |
|---|---|
| follower_id | following_id |

Relationship type:

```text
FOLLOWS
```

---

### 6. Run the Import

Click:

```text
Run Import
```

Neo4j AuraDB will create:

* User nodes
* Follow relationships

---

### 7. Verify Import

Run the following Cypher queries in Neo4j Browser.

Count users:

```cypher
MATCH (u:User)
RETURN count(u);
```

Count follow relationships:

```cypher
MATCH ()-[r:FOLLOWS]->()
RETURN count(r);
```

Visualize the graph:

```cypher
MATCH (u:User)-[:FOLLOWS]->(f)
RETURN u, f
LIMIT 50;
```

---

### Example Graph Queries

Most-followed users:

```cypher
MATCH (u:User)<-[:FOLLOWS]-(follower)
RETURN u.username, count(follower) AS followers
ORDER BY followers DESC
LIMIT 10;
```

Users following the most people:

```cypher
MATCH (u:User)-[:FOLLOWS]->(following)
RETURN u.username, count(following) AS following_count
ORDER BY following_count DESC
LIMIT 10;
```

Friend recommendations:

```cypher
MATCH (me:User {username: "johnsmith"})
      -[:FOLLOWS]->(:User)-[:FOLLOWS]->(recommended)

WHERE NOT (me)-[:FOLLOWS]->(recommended)
AND me <> recommended

RETURN recommended.username, count(*) AS score
ORDER BY score DESC
LIMIT 10;
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

* Friend recommendation system (graph traversal)
* Posts, likes, and comments
* UI Update

---

## 👤 Author

Jason Doria
Computer Science @ San Jose State University

---

## 📄 License

This project is for academic purposes.
