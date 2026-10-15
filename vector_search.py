import numpy as np
import pymupdf
from sentence_transformers import SentenceTransformer
from chunker import chunk_text

# Shared model, but NOT shared documents
model = None


def get_model():
    global model

    if model is None:
        model = SentenceTransformer("google/embeddinggemma-2")

    return model


def load_document(pdf_bytes):
    # Validate PDF input
    if not isinstance(pdf_bytes, bytes):
        raise ValueError("PDF must be provided as bytes.")

    if len(pdf_bytes) > 10 * 1024 * 1024:
        raise ValueError("PDF must be smaller than 10 MB.")

    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF file.")

    chunks = []

    # Extract text from this PDF only
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        for page_number, page in enumerate(document):
            text = page.get_text()

            if not text.strip():
                continue

            for chunk in chunk_text(text):
                chunks.append({
                    "page_number": page_number + 1,
                    "text": chunk
                })

    if not chunks:
        raise ValueError("No readable text found in this PDF.")

    # Generate embeddings
    embedding_model = get_model()

    embeddings = embedding_model.encode_document(
        [chunk["text"] for chunk in chunks],
        normalize_embeddings=True
    )

    # Return an independent index for this PDF
    return {
        "chunks": chunks,
        "embeddings": embeddings
    }


def search_document(question, document_index, top_k=5):
    if document_index is None:
        raise ValueError("No document has been uploaded.")

    embedding_model = get_model()

    question_embedding = embedding_model.encode_query(
        question,
        normalize_embeddings=True
    )

    similarities = np.dot(
        document_index["embeddings"],
        question_embedding
    )

    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []

    for index in top_indices:
        chunk = document_index["chunks"][index]

        results.append({
            "page": chunk["page_number"],
            "text": chunk["text"],
            "score": float(similarities[index])
        })

    return results