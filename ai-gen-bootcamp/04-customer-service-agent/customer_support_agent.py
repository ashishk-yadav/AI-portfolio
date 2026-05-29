# customer_support_agent.py — Provider-agnostic RAG + Order Lookup
#
# Replaced LangChain initialize_agent (CONVERSATIONAL_REACT_DESCRIPTION) with a
# direct retrieve→answer pipeline. The old agent approach caused parse failures
# with non-OpenAI LLMs and relied on deprecated agent.run() interface.

import os
import chromadb
from langchain.schema import HumanMessage, SystemMessage
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from llm_provider import get_langchain_llm, get_langchain_embeddings


def load_support_docs(docs_dir="docs"):
    all_docs = []
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(docs_dir, filename))
            docs = loader.load()
            for d in docs:
                d.metadata["source"] = filename
            all_docs.extend(docs)
    return all_docs


def build_retriever(docs):
    """Build an in-memory ChromaDB retriever — avoids the 0.5.x tenant init bug."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    embeddings = get_langchain_embeddings()
    client = chromadb.EphemeralClient()
    vectordb = Chroma.from_documents(split_docs, embeddings,
                                     collection_name="support_docs", client=client)
    return vectordb.as_retriever(search_kwargs={"k": 3})


def order_lookup(order_id: str, orders: list) -> str:
    order_id = order_id.strip()
    for o in orders:
        if o["order_id"] == order_id:
            return (
                f"Order ID: {o['order_id']}\n"
                f"Item: {o['item']}\n"
                f"Status: {o['status']}\n"
                f"Date: {o['date']}"
            )
    return f"No order found with ID '{order_id}'."


class SupportAgent:
    """Direct retrieve→answer agent — no LangChain agent framework needed."""

    def __init__(self, retriever, orders):
        self.retriever = retriever
        self.orders = orders
        self.memory = ConversationBufferMemory(return_messages=True)

    def run(self, query: str) -> str:
        llm = get_langchain_llm(temperature=0.0)

        # Check if query looks like an order lookup
        q_lower = query.lower()
        order_context = ""
        if any(w in q_lower for w in ["order", "status", "shipment", "tracking", "delivery"]):
            # Try to extract an order ID (simple heuristic: uppercase alphanumeric token)
            import re
            ids = re.findall(r'\b[A-Z0-9]{4,}\b', query)
            if ids:
                order_context = "\n\nOrder lookup result:\n" + order_lookup(ids[0], self.orders)

        # RAG retrieval
        rag_docs = self.retriever.get_relevant_documents(query)
        rag_context = "\n\n".join(
            [f"[{d.metadata.get('source','doc')}]: {d.page_content.strip()}" for d in rag_docs]
        ) if rag_docs else "No relevant documentation found."

        # Build conversation history
        history = self.memory.load_memory_variables({}).get("history", [])
        history_text = "\n".join(
            [f"{'User' if m.type == 'human' else 'Agent'}: {m.content}" for m in history[-6:]]
        ) if history else ""

        prompt = f"""You are a friendly and helpful customer support agent.
Use the knowledge base excerpts and order information below to answer the customer's question accurately.
If you cannot find the answer, say so honestly and offer to escalate.

Knowledge Base:
{rag_context}
{order_context}

{'Conversation so far:' + chr(10) + history_text if history_text else ''}

Customer: {query}
Agent:"""

        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()

        # Update memory
        self.memory.save_context({"input": query}, {"output": response})
        return response
