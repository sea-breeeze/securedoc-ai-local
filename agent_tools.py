from vector_search import search_document


def search_approved_document(query: str, document_index: dict) -> dict:
    """
    Search only the document index provided for this session.
    This tool is read-only.
    """

    if not isinstance(query, str) or not query.strip():
        return {"error": "A search query is required."}

    if len(query) > 500:
        return {"error": "Search query is too long."}

    if document_index is None:
        return {"error": "No document has been uploaded."}

    results = search_document(
        query,
        document_index=document_index,
        top_k=5
    )

    passages = []

    for result in results:
        passages.append({
            "page": result["page"],
            "text": result["text"]
        })

    return {"passages": passages}