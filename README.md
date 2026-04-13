# DocuQuery

DocuQuery is a Flask-based web application that lets users upload a PDF, ask a question or request a review, and receive a streamed AI response grounded in the document content.

The app uses:

- Flask for the backend and templated frontend
- HTML, CSS, and vanilla JavaScript for the UI
- LangChain for PDF loading, chunking, and retrieval flow
- FAISS for in-memory vector search
- HuggingFace embeddings with `all-MiniLM-L6-v2`
- Groq API with `llama-3.1-8b-instant` for streamed review responses

## Features

- Upload PDF documents from the browser
- Extract text with PyMuPDF via LangChain's `PyMuPDFLoader`
- Split documents into searchable chunks
- Store embeddings in an in-memory FAISS vector store
- Retrieve the top relevant excerpts for each query
- Stream AI answers back to the browser in real time
- Show upload state, errors, and formatted review output

## Project Structure

```text
AI-based PDF Reviewer/
├── app.py
├── pdf_processor.py
├── reviewer.py
├── templates/
│   └── index.html
├── requirements.txt
├── .env.example
├── .gitignore
├── Procfile
└── README.md
```

## Requirements

- Python 3.10+
- A Groq API key

## Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd "AI-based PDF Reviewer"
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file from `.env.example`:

```env
GROQ_API_KEY=your_key_here
```

## Running the App

Start the Flask app with:

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

## How It Works

1. A PDF is uploaded through the browser.
2. The backend saves it temporarily using `tempfile.NamedTemporaryFile`.
3. `PyMuPDFLoader` loads the document.
4. `RecursiveCharacterTextSplitter` splits it into chunks.
5. `HuggingFaceEmbeddings` creates embeddings.
6. `FAISS` stores the chunks in memory.
7. On each review query, the top 3 relevant excerpts are retrieved.
8. Those excerpts are sent to Groq.
9. The response is streamed back to the frontend.

## Environment Variables

The application uses:

- `GROQ_API_KEY`: your Groq API key

Do not commit your real `.env` file. Only commit `.env.example`.

## Deployment

This project includes a `Procfile` for platforms like Render:

```text
web: gunicorn app:app
```

For deployment:

1. Push the repository to GitHub
2. Create a new Render web service
3. Connect the GitHub repository
4. Set `GROQ_API_KEY` in the Render environment variables
5. Deploy

## Notes

- The FAISS vector store is in memory only, so uploading a new PDF replaces the old one.
- The first embedding model download can take some time.
- On Windows, HuggingFace may show a symlink cache warning. This is usually harmless.
- The current UI is served entirely from `templates/index.html`.

## License

You can add your preferred license here before publishing publicly.
