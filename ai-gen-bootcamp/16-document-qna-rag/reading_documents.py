import os
# https://python.langchain.com/docs/how_to/#document-loaders
#pip install langchain
#pip install langchain-community
#pip install pypdf

from langchain_community.document_loaders import TextLoader, PyPDFLoader

file_path = os.path.join(os.path.dirname(__file__), "onboarding.txt")
loader = TextLoader(file_path)
docs = loader.load()
print(docs)

print("===========\n\n\n\n\n============")

file_path = os.path.join(os.path.dirname(__file__), "spgi-annual-report-2023.pdf")
loader = PyPDFLoader(file_path)
docs2 = loader.load()
print(docs2)

print("Done")

