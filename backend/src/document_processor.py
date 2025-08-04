import logging

logger = logging.getLogger(__name__)

def process_document(text: str) -> list:
    """Process a document text into a format suitable for RAG."""
    # Currently splits by sentences, will need to be improved with more advanced NLP techniques
    paragraphs = text.split('\n')
    sentences = [paragraph.split('. ') for paragraph in paragraphs]
    sentences = [sentence.strip() for sublist in sentences for sentence in sublist if sentence.strip()]
    if not sentences:
        raise ValueError("No valid sentences found in the document.")
    logger.info(f"Processed document into {len(sentences)} sentences.")
    return sentences
    