from dotenv import load_dotenv
load_dotenv()

import ollama

# Name of the downloaded model
model = "gemma3:1b"

# Task Description
task = """Write a 50 word summary on ethics in AI."""

# Generate the result
result = ollama.generate(model=model, prompt=task)

print(result.response)
