import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("LANGSMITH_TRACING"))
print(os.getenv("LANGSMITH_API_KEY"))

# demo_langsmith.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Define a simple chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise assistant."),
    ("human", "Question: {question}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chain = prompt | llm

# Run once (this is enough to see traces in LangSmith UI)
resp = chain.invoke({"question": "What is LangSmith?"})

print("Model output:", resp.content)
