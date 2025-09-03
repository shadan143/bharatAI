# Embeddings wrapper. In production choose a managed embeddings API or a local embedding model.
# This file uses sentence-transformers if available.
try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    _model = None
    print('Warning: sentence-transformers not available in this runtime:', e)

def get_embedding(text: str):
    if _model:
        vec = _model.encode([text])[0].tolist()
        return vec
    # fallback: simple hash-based vector (not suitable for real use)
    return [float((hash(text) % 1000) / 1000.0)] * 384
