from sentence_transformers import CrossEncoder

# Initializes ONCE when imported
reranker_model = CrossEncoder("BAAI/bge-reranker-large")


class Reranker:
    def __init__(self, query: str, documents: list, top_k: int = 10, model: CrossEncoder = reranker_model):
        self.model = model
        self.query = query
        self.documents = documents
        self.top_k = top_k

    def rerank(self) -> list:
        if not self.documents:
            return []

        doc_texts = [doc.page_content for doc in self.documents]

        # Simple, straightforward synchronous execution
        rank_results = self.model.rank(
            query=self.query,
            documents=doc_texts,
            top_k=self.top_k
        )

        reranked_documents = []
        for hit in rank_results:
            original_index = hit['corpus_id']
            document = self.documents[original_index]
            document.metadata['rerank_score'] = float(hit['score'])
            reranked_documents.append(document)

        return reranked_documents