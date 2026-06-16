import tiktoken


encoder = tiktoken.get_encoding("cl100k_base")

class ContextBuilder:
    def __init__(self):
        pass
    def build(self, docs, max_token:int):
        context = []
        token_count = 0
        for doc in docs:
            text = doc["content"]
            tokens = len(encoder.encode(text))
            if tokens > max_token:
                break
            context.append(text)
            token_count += tokens
        return  context, token_count
