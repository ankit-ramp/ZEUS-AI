# 🚀 Full Stack PO Automation App

A modern full-stack web application built using **FastAPI** (Python) for the backend and **Next.js** (React) for the frontend. The app provides **Purchase Order (PO) automation** using AI-driven tools, including OCR, data extraction, and LangChain-powered language workflows.

---

## 📃 Features

- PO (Purchase Order) data extraction using AI  
- PDF & image parsing with OCR (Tesseract + PDF2IMG)  
- Natural language workflows using LangChain and LangGraph  
- Modern UI with Next.js and Ant Design  
- Supabase integration for storage/auth (if configured)  
- API-driven architecture  

---

## 📦 Tech Stack

### Frontend

- [Next.js](https://nextjs.org/)  
- React  
- Tailwind CSS *(optional but supported)*  
- Axios or SWR *(for API communication)*  
- Supabase *(for backend storage/auth)*  
- Ant Design *(UI components)*

### Backend

- [FastAPI](https://fastapi.tiangolo.com/)  
- Pydantic *(data validation and parsing)*  
- SQLAlchemy *(ORM/database access)*  
- Tesseract OCR & PDF2Image *(document parsing)*  
- LangChain *(language model orchestration)*  
- LangGraph *(graph-based LLM workflows)*

---

## 🗂️ Project Structure

```
project-root/
│
├── backend/                  # FastAPI backend
│   ├── main/                 # main file
│   ├── routes/               # API routes
│   ├── models/               # pydantic models for llm, langgraph and database
│   └── services/             # Logic and graph files
|   └── tools/                # reusable code snippets
│
│
├── frontend/                 # Next.js frontend
│   ├── app/ -------├── api  
                    |── auth 
                    ├── dashboard  # App pages (React) and routes
                    |── login   
│   ├── components/                  # API utils
│   ├── utils/               # Static assets
│   ├── tailwind.config.js    #  tailwind config
│   └── .env.local            # Frontend environment variables
│
└── README.md                 # Project documentation
```

---

## 🧑‍💻 Getting Started

### 🔧 Prerequisites

- Node.js v16+  
- Python 3.9+  
- Tesseract OCR installed   

---

## 🖥️ Frontend Setup (Next.js)

1. **Set up environment variables:**

   Create a `.env.local` file in `frontend/`:


2. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

3. **Run frontend:**

   - Development:
     ```bash
     npm run dev
     ```
   - Production:
     ```bash
     npm run build
     npm run start
     ```

---

## 🖥️ Backend Setup (FastAPI)

1. **Set up environment variables:**

   Create a `.env` file in `backend/`:

   ```
   OPENAI_API_KEY=your-openai-key
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-key
   ```

2. **Set up virtual environment:**

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run FastAPI server:**

   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📬 API Reference

### `POST /chat`

- **Description**: Send a message to the LangChain-based assistant
- **Request Body**:
  ```json
  {
    "input": "What’s the PO number in this document?"
  }
  ```
- **Response**:
  ```json
  {
    "response": "PO Number: 12345"
  }
  ```

### `POST /extract-po`

- **Description**: Upload a PDF/image to extract PO information
- **Request**: `multipart/form-data`
  - `file`: PDF or image file
- **Response**:
  ```json
  {
    "po_number": "123456",
    "date": "2024-01-01",
    "vendor": "ACME Inc"
  }
  ```

---

## 🧠 LangChain & LangGraph Overview

- LangChain handles LLM prompts, memory, and agents  
- LangGraph builds structured flows between tasks (e.g., OCR → extract → chat → verify)  
- Easily extensible via nodes and tools  

---

## 🧩 Extending the App

- **Add more endpoints** in FastAPI via `app/routers`  
- **Connect to a database** using SQLAlchemy models   
- **Add frontend pages** in `frontend/pages/` with API integration  

---

## 🔐 Security Considerations

- Use HTTPS and secure API keys in production  
- Enable CORS restrictions in FastAPI  
- Use Supabase  Auth for login-based protection  
- Sanitize user inputs before processing with LLMs  

---

## 🧪 Testing

### Backend

- Use `pytest` or `unittest`  
- Mock LangChain tools for fast testing  

### Frontend

- Use `Jest` with React Testing Library  

---

## 📤 Deployment Options

- **Frontend**: Zeus network using docker
- **Backend**:  Zeus network using docker  

###: Docker Support

Add `Dockerfile` and `docker-compose.yml` for local or production containerization.

---

## 📄 License

MIT License

---