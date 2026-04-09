import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))


def truncate_to_token_limit(text: str, max_tokens: int, model: str = "gpt-4o-mini") -> str:
    encoder = tiktoken.encoding_for_model(model)
    tokens = encoder.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated_tokens = tokens[:max_tokens]
    return encoder.decode(truncated_tokens)