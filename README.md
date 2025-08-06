# AI Auto Reply API 🤖📩

This project is a smart email auto-responder built with FastAPI and HuggingFace's zero-shot classification model.  
It detects the intent of incoming messages (like offers, meetings, or thank-you notes), checks user availability or leave status, and generates context-aware replies.

---

## 🚀 Features

- 📨 Intent detection using transformers (XLM-RoBERTa)
- 📅 Checks user availability and leave dates
- ⏰ Suggests free time slots based on user calendar
- 🧠 Smart auto-reply logic (for thank you, meetings, offers)
- ⚡ FastAPI backend

---

## 🛠 Technologies

- FastAPI
- Hugging Face Transformers
- Python 3.10+
- Pydantic
- JSON-based mock database

---

## 🧪 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-auto-reply-api.git
cd ai-auto-reply-api
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
uvicorn app:app --reload
```

---

## 📬 Example POST Request (Postman)

URL:
```
http://127.0.0.1:8000/auto-reply
```

Body (JSON):
```json
{
  "email": "test@example.com",
  "text": "Teklif hakkında görüşmek istiyorum.",
  "date": "2025-08-06"
}
```

---

## 📄 users.json Format

```json
{
  "users": [
    {
      "name": "Seçkin Aktaş",
      "email": "test@example.com",
      "is_on_leave": true,
      "leave_dates": {
        "start": "2025-08-01",
        "end": "2025-08-10"
      },
      "leave_note": "İzindeyim, acil durumlarda WhatsApp'tan ulaşabilirsiniz.",
      "calendar": [
        {
          "date": "2025-08-06",
          "busy_slots": ["10:00-11:00", "14:00-15:00"]
        }
      ]
    }
  ]
}
```

---

## 🧠 Author

**Seçkin Aktaş**  
Software Engineer | AI & Computer Vision Enthusiast  
[GitHub](https://github.com/sseckinaktass) • [LinkedIn](https://www.linkedin.com/in/seckinaktas/)

---

## 📜 License

MIT
