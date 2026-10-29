# 🔐 Bookmark Vault API

A secure, modular FastAPI backend for managing personal bookmarks with JWT authentication and ownership enforcement. Built to demonstrate production-ready backend practices: security, testing, and containerization.

## 🌐 Live Demo
**[Try the API here](https://bookmark-vault-t1xz.onrender.com/docs)**  
*(Note: may take 30-60s to wake up on first request)*

## 🚀 Features
- **Secure Auth:** Password hashing (PBKDF2 + Salt) and stateless JWT tokens.
- **Ownership Protection:** Strict IDOR prevention — users can only access/delete their own data.
- **Modular Architecture:** Clean separation of routers, models, schemas, and config.
- **Automated Testing:** 100% test coverage for auth and CRUD flows using `pytest`.
- **Clean Test Output:** Configured `pytest.ini` to filter third-party deprecation warnings (per [pytest docs](https://docs.pytest.org/en/stable/how-to/capture-warnings.html)), ensuring CI/CD logs remain readable.
- **Containerized:** Fully Dockerized for consistent deployment anywhere.

## 🛠️ Tech Stack
- **Framework:** FastAPI
- **Database:** SQLModel (SQLite locally, Postgres ready via Env Vars)
- **Auth:** PyJWT, OAuth2PasswordBearer
- **Testing:** Pytest, TestClient
- **Deployment:** Docker, Render

## 🏃 How to Run Locally

### Prerequisites
- Python 3.10+
- pip

### Steps
1. Clone the repo:
   ```bash
   git clone https://github.com/Siddharta99/bookmark-vault.git
   cd bookmark-vault