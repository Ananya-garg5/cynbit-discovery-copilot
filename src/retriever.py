import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_KNOWLEDGE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "cynbit_knowledge.json"
)


class CynbitRetriever:

    TYPE_WEIGHTS = {
        "service": 1.20,
        "product": 1.15,
        "case_study": 1.10,
        "company": 0.80,
        "process": 0.80,
        "program": 0.70,
    }

    def __init__(self, knowledge_path=DEFAULT_KNOWLEDGE_PATH):
        self.knowledge_path = Path(knowledge_path)
        self.documents = self._load_knowledge()

        self.search_texts = [
            self._build_search_text(document) for document in self.documents
        ]

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self.document_vectors = self.vectorizer.fit_transform(self.search_texts)

    def _load_knowledge(self):
        with open(self.knowledge_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Accept either a plain list or {"documents": [...]}
        if isinstance(data, dict):
            data = data.get("documents", [])
        return data

    def _build_search_text(self, document):
        title = document.get("title", "")
        text = document.get("text", "")
        hints = " ".join(document.get("retrieval_hints", []))
        return f"{title} {text} {hints}"

    def search(self, query: str, top_k: int = 5, allowed_types=None):
        if not query or not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]

        weighted_scores = []
        for index, similarity in enumerate(similarities):
            document = self.documents[index]
            document_type = document.get("type", "company")

            if allowed_types is not None and document_type not in allowed_types:
                weighted_scores.append(-1)
                continue

            weight = self.TYPE_WEIGHTS.get(document_type, 1.0)
            weighted_scores.append(float(similarity) * weight)

        ranked_indices = sorted(
            range(len(weighted_scores)),
            key=lambda index: weighted_scores[index],
            reverse=True,
        )

        results = []
        for index in ranked_indices:
            score = weighted_scores[index]
            if score <= 0:
                continue

            document = self.documents[index]
            results.append({
                "id": document["id"],
                "type": document["type"],
                "title": document["title"],
                "text": document["text"],
                "source_url": document.get("source_url", ""),
                "source_name": document.get("source_name", document["title"]),
                "score": round(score, 4),
            })

            if len(results) >= top_k:
                break

        return results