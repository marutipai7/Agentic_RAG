from sentence_transformers import CrossEncoder

class Reranker:

    def __init__(self):
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rerank(self, query, documents):

        pairs = []

        for doc in documents:
            pairs.append((query, doc["content"]))

        scores = self.model.predict(pairs)

        for i in range(len(documents)):
            documents[i]["rerank_score"] = float(scores[i])

        documents = sorted(
            documents,
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return documents
