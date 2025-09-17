# Quill + OpenAI Autocomplete Demo

This mini-project shows how to integrate **real-time autocomplete** into your editor workflow using:

- [Quill.js](https://quilljs.com/) as the rich-text editor
- [FastAPI](https://fastapi.tiangolo.com/) backend with [LangChain](https://www.langchain.com/) + OpenAI API
- A simple **ghost text overlay** that displays completions inline, just like Gmail/IDE autocompletion

---

## 🚀 Features

- ✍️ **Inline ghost text**: Autocomplete suggestions appear directly at the caret, grayed out until accepted.
- ⌨️ **Keyboard integration**: Accept suggestions with **Tab** or **→ Arrow**; dismiss with **Esc**.
- 🧠 **Smart prefixing**: Only sends the text fragment since the last `.` (sentence boundary) to reduce noise.
- 🛑 **User-first control**: After you accept a suggestion, the system waits for your next keystroke before fetching again.
- 🔄 **Debounced + cancelable requests**: Prevents spamming the API on every keystroke, and cancels stale calls.
- ⚡ **FastAPI backend**: Streams or one-shot suggestions from an OpenAI model via LangChain.

---

## 📂 Project Structure

```
.
├── backend/
│   ├── main.py             # FastAPI app exposing /complete_once
│   ├── queryModel.py       # Pydantic model for input
│   └── .env                # Store OPENAI_API_KEY
│
├── frontend/
│   ├── index.html          # Loads Quill editor + ghost suggestion overlay
│   ├── main.js             # Autocomplete logic (debounce, overlay, API calls)
│   └── styles.css          # Quill + ghost suggestion styling
│
└── README.md
```

---

## 🛠️ Setup

### 1. Clone & Install
```bash
git clone <this-repo>
cd backend
pip install fastapi uvicorn langchain-openai python-dotenv
```

### 2. Configure `.env`
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run Backend
```bash
uvicorn main:app --reload
```
This serves the autocomplete endpoint at `http://127.0.0.1:8000/complete_once`.

### 4. Open Frontend
- Go to `frontend/index.html` in your browser.
- Start typing — ghost suggestions appear as you write!

---

## 🧩 How to Use in Your Workflow

- **Docs & Emails**: Drop this component into any Quill-based editor to draft faster.
- **Internal Tools**: Add autocomplete to support ticket systems, CRMs, or internal wikis.
- **Coding Tools**: Swap Quill with a code editor (Monaco/CodeMirror) and reuse the same backend logic.
- **Custom AI Models**: Replace the OpenAI call with your own hosted LLM or fine-tuned model.

The backend is modular — any completion provider that takes a prompt and returns text will work.

---

## 🔮 Next Steps

- ✅ Add **streaming completions** for token-by-token display
- ✅ Support multiple trigger keys (`,` `;` etc.)
- 🔒 Secure endpoints (auth, rate limiting)
- 📊 Log usage metrics
- 🎨 Extend to multi-line / paragraph suggestions

---

## 📸 Demo

![Demo Screenshot](docs/demo.png)

Ghost suggestions appear as grayed-out inline text, accepted with Tab/→.

---

## 🤝 Contributing

This project is a minimal demo. PRs are welcome to:

- Improve UI/UX of ghost overlay
- Add support for streaming completions
- Integrate with other editors (CKEditor, TipTap, Monaco)

---

## 📜 License
MIT
