from scripts import Processor, Retriever, Reranker


def rag_search(user_query: str):
    print(f"\nSearching for {user_query}.......")

    # 1. Processing
    processor = Processor()
    processed_query = processor.process_query(user_query)

    # 2. Retrieval
    print("starting retriever...")
    retrieved_docs = Retriever.search_knowledge_base(processed_query)
    print(retrieved_docs)
    print("*"*100)

    # 3. Reranking
    print("starting ranking...")
    ranker = Reranker(user_query, retrieved_docs)
    ranked_documents = ranker.rerank()
    print("✅ Completed RAG Pipeline\n")

    # 4. Display
    for i, doc in enumerate(ranked_documents):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', '?')
        score = doc.metadata.get('rerank_score', 0.0)
        print(f"[Match {i + 1}] (Score: {score:.4f}) Source: {source} (Page {page})")
        print(f"Content: {doc.page_content.strip()}")
        print("-" * 60)


if __name__ == "__main__":
    while True:
        query = input("\nSearch for something (or type 'exit'): ")
        if query.lower() == "exit":
            break
        if query.strip():
            rag_search(query)  # Standard function call!