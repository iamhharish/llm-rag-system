import faiss
import numpy as np
import re

STOPWORDS = {
    "what","when","where","who","which","how","is","was","are","were",
    "the","a","an","of","in","on","at","to","for","and","or","it","this",
    "that","did","do","does","about","explain","describe","give"
}

MIN_SCORE = 0.35


def build_index(embeddings):
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return index


def retrieve_chunks(query, embed_model, index, chunks, top_k=10):
    q_emb = embed_model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(q_emb)

    scores, indices = index.search(q_emb, k=top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if score >= MIN_SCORE:
            results.append((float(score), chunks[idx]))

    return results


def rerank_chunks(query, scored_chunks):
    q_words = set(re.findall(r'\w+', query.lower())) - STOPWORDS

    reranked = []
    for faiss_score, chunk in scored_chunks:
        c_words = set(re.findall(r'\w+', chunk.lower())) - STOPWORDS

        overlap = len(q_words & c_words) / (len(c_words) + 1)

        combined = (faiss_score * 1.5) + (overlap * 2.0)

        reranked.append((combined, chunk))

    reranked.sort(reverse=True, key=lambda x: x[0])
    return [chunk for _, chunk in reranked[:3]]