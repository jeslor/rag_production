from scripts import Processor, Retriever, Reranker, ContextBuilder
from scripts.build_context_04 import ContextBuilder


def rag_search(user_query: str):
    print(f"\nSearching for {user_query}.......")

    # 1. Processing
    print("starting processing...")
    processor = Processor()
    processed_query = processor.process_query(user_query)
    print("✅ Completed retrieving information using vector db\n")

    # 2. Retrieval
    print("starting retriever...")
    retrieved_docs = Retriever.search_knowledge_base(processed_query)
    print("✅ Completed retrieving information using vector db\n")

    # 3. Reranking
    print("starting ranking...")
    ranker = Reranker(user_query, retrieved_docs)
    ranked_documents = ranker.rerank()
    print(f"✅ Completed Reranking of docks total returned:({len(ranked_documents)} docs)\n")

    # 4. Build context and count tokens
    print("starting context building...")
    context_builder = ContextBuilder()
    context, token_count = context_builder.build(ranked_documents, 3100)
    print("✅ Completed context building\n")


    # 4. Display
    for i, doc in enumerate(ranked_documents):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', '?')
        score = doc.metadata.get('rerank_score', 0.0)
        print(f"[Match {i + 1}] (Score: {score:.4f}) Source: {source} (Page {page})")
        print(f"Content: {doc.page_content.strip()}")



if __name__ == "__main__":
    while True:
        query = input("\nSearch for something (or type 'exit'): ")
        if query.lower() == "exit":
            break
        if query.strip():
            rag_search(query)  # Standard function call!