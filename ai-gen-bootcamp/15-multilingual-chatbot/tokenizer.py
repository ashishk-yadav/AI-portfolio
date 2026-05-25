# Demonstrates tokenization (breaking text into words or subwords)
import re

def simple_tokenize(text: str):
    """
    Very basic whitespace + punctuation tokenizer.
    Example: "Hello, world!" -> ["Hello", "world"]
    """
    tokens = re.findall(r"\b\w+\b", text.lower())
    return tokens

if __name__ == "__main__":
    print(simple_tokenize("Hello, how are you doing today?"))
