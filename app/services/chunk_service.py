def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[dict[str, str | int]]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to 0.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size.")

    chunks: list[dict[str, str | int]] = []
    start = 0
    chunk_number = 1
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append({
                "text": chunk,
                "chunk_number": chunk_number
            })
            chunk_number += 1

        next_start = end - overlap
        if next_start <= start:
            next_start = start + 1

        start = next_start

    return chunks
