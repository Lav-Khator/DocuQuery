from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


vectorstore = None
_embeddings = None
_last_chunk_count = 0


def _get_embeddings():
    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings


def process_pdf(pdf_path):
    global vectorstore, _last_chunk_count

    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()

    if not documents:
        raise ValueError("The uploaded PDF did not contain any readable text.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("The PDF could not be split into chunks.")

    vectorstore = FAISS.from_documents(chunks, _get_embeddings())
    _last_chunk_count = len(chunks)
    return _last_chunk_count


def get_relevant_chunks(query, k=3):
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if vectorstore is None:
        raise ValueError("Please upload a PDF before starting a review.")

    relevant_docs = vectorstore.similarity_search(query.strip(), k=k)

    formatted_docs = []
    for doc in relevant_docs:
        content = (doc.page_content or "").strip()
        if not content:
            continue

        metadata = doc.metadata or {}
        page_number = metadata.get("page")
        source = metadata.get("source", "Uploaded PDF")

        formatted_docs.append(
            {
                "content": content,
                "page": page_number + 1 if isinstance(page_number, int) else None,
                "source": source,
            }
        )

    return formatted_docs


def get_chunk_count():
    return _last_chunk_count
