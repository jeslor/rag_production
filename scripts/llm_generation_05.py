from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


def prompt_model(question:str, content: str):
    #Initiate the model
    llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0
    )

    # generate a prompt using the provided question and context
    prompt = ChatPromptTemplate.from_template("""
            You are a helpful assistant.
            Use the knowledge-base to improve your answer when useful, but respond naturally.
        
            Question:
            {question}
            
            Context:
            {content}
            
            Answer:
    """)

    normalized_prompt = prompt.format_messages(question=question, content=content)
    response = llm.invoke(normalized_prompt)
    return response



