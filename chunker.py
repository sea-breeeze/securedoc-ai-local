def chunk_text(text, chunk_size=500,overlap=100):
    """
    Splits the input text into chunks of specified size with optional overlap.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum size of each chunk. Default is 500 characters.
        overlap (int): The number of overlapping characters between consecutive chunks. Default is 100 characters.

    Returns:
        list: A list of text chunks.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # Move the start index forward by chunk_size minus overlap

    return chunks