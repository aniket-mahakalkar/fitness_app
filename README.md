# 🏋️‍♂️ Fitness App Backend

This is a backend service for a **Fitness Booking Application**, developed using **Flask**. It includes REST APIs for booking management and WebSocket integration for a RAG-based (Retrieval-Augmented Generation) chatbot.

---

## 🚀 Features

- ✅ REST APIs for booking fitness classes
- 💬 WebSocket endpoint for RAG-based chatbot interactions 
- 🧩 Modular folder structure for easy scalability
- 🗂️ ORM models using SQLAlchemy
- 🧪 Seeding scripts to fit instructors data
- 🌐 HTML support for chat with RAG  (index.html)

---

## API Collection

You can explore and test the API using the Postman collection below:

🔗 [Postman API Collection](https://web.postman.co/workspace/My-Workspace~739c091f-fac6-4ec3-8c9b-2b6b7c00b634/collection/40300563-5eaa2d2d-a044-401d-a732-3f040e01c7eb?action=share&source=copy-link&creator=40300563)


## 📁 Project Structure
```
fitness_app/
│
├── instance/ # For Database (e.g., SQLite files or config)
├── models/ # SQLAlchemy models
├── routes/ # API route handlers
├── seed/ # Seed scripts for instructor data
├── services/ # Business logic and core services
├── utils/ # Helper functions and utilities
│
├── .gitignore
├── .python-version
├── app.py # Main Flask app entry point
├── db.py # Database initialization
├── index.html # To test WebSocket and RAG application
├── pyproject.toml # Project dependencies (used by UV)
```

---

## 🧠 RAG Chatbot Integration

The app includes a WebSocket server for real-time interaction with a **RAG-based chatbot** (Retrieval-Augmented Generation). This enables users to:
- Ask fitness or booking-related questions
- Get contextual responses based on backend data


```bash
# Clone the repository
git clone https://github.com/your-username/fitness_app.git
cd fitness_app

# Create and activate a virtual environment
uv venv
.venv\Scripts\activate

uv add <dependecies (if needed)>

uv run python app.py
