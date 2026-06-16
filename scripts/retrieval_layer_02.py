from langchain_huggingface import HuggingFaceEmbeddings
import config
import os
from langchain_chroma import Chroma

class Retriever:
    def __init__(self):
        pass
    
    @staticmethod
    def search_knowledge_base(query, num_of_candidates=10):
        chipset = config.get_optimal_chipset()
        embedding = HuggingFaceEmbeddings(
            model_name=config.MODEL_NAME,
            model_kwargs={'device': chipset}
        )
        vector_db = Chroma(persist_directory=config.DB_DIR, embedding_function=embedding)
        return vector_db.similarity_search(query, num_of_candidates)



if(__name__ == "__main__"):
    user_query = "ebola | intent:general"
    retriever = Retriever()
    documents = retriever.search_knowledge_base(user_query)
    print(documents)