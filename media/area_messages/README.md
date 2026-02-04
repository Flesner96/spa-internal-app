# 🛍️ Flask Shop Admin Panel

A lightweight internal admin dashboard built with Flask for managing products, clients, and orders. Designed for clarity, maintainability, and responsiveness — perfect for small business back offices or as a full-stack portfolio project.

---

## 🚀 Features

- ✅ Secure login with session-based authentication  
- ✅ Dashboard with key business metrics  
- ✅ Responsive UI using Tailwind CSS  
- ✅ Dynamic charts (Chart.js) with Vue-powered toggling  
- ✅ Product, client, and order management  
- ✅ CSV export for offline use  
- ✅ REST-style JSON API for `/products`, `/orders`, `/clients`  
- ✅ Pytest-based test suite (login, auth, route access, more)

---

## 🛠️ Tech Stack

| Layer    | Tech Used                |
|----------|--------------------------|
| Backend  | Flask (Python)           |
| Frontend | Jinja2 + Tailwind CSS    |
| Charts   | Chart.js + Vue.js        |
| Database | PostgreSQL (`psycopg2`)  |
| Testing  | Pytest                   |
| Export   | CSV via Flask streaming  |
| Auth     | Session-based login      |

---

## 📸 UI Highlights

- 💡 Flash messages styled with Tailwind  
- 📊 Chart toggling with Vue (bar ↔ line)  
- 🔒 Login-protected views  
- 🧾 Clean tables, form validation, and responsive layout  

---

## 🧪 Run Tests

```bash
pytest
```

Run from the project root after setting up your environment.

---

## 📌 Notes

- ✅ This project was originally a **command-line interface (CLI) app**, then refactored into a web-based admin panel — this transition can be seen in the [commit history](https://github.com/yourusername/flask-shop-admin/commits/main)
- 📦 The current **order system** still uses the CLI-style model: orders store only free-text descriptions and are **not yet linked to individual products** or **inventory tracking**
- 🔐 Admin credentials are hardcoded for now (`admin` / `admin123`)
- 🌐 App is designed for internal/admin use only
- 👨‍💻 Built as a portfolio project to demonstrate Flask full-stack skills with modern frontend integration

---

## 📬 License

MIT — free to use and modify for personal or commercial projects.