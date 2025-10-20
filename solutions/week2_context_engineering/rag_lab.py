import argparse
import requests
import json
import chromadb
import time

# --- 1. Configuration ---
OLLAMA_ENDPOINT = "http://localhost:11434/api"
OLLAMA_CONFIG = {
    "model": "llama3",
    "stream": False,
}
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "faq_collection"
DEFAULT_TOP_K = 2
DELIMITER = "-----"
PRINT_LATENCY = True


# --- 2. Knowledge Base ---
# In a real-world scenario, this would come from a file, database, or API.
FAQ_DATA = [
    {"id": "faq1", "question": "What is the return policy?", "answer": "You can return any item within 30 days of purchase for a full refund."},
    {"id": "faq2", "question": "How do I track my order?", "answer": "Once your order has shipped, you will receive an email with a tracking number."},
    {"id": "faq3", "question": "Do you ship internationally?", "answer": "Yes, we ship to most countries worldwide. Shipping costs may vary."},
    {"id": "faq4", "question": "How can I contact customer support?", "answer": "You can reach our customer support team via email at support@example.com or by calling our toll-free number."},
    {"id": "faq5", "question": "What payment methods do you accept?", "answer": "We accept all major credit cards, PayPal, and Apple Pay."},
    {"id": "faq6", "question": "Can I change my shipping address?", "answer": "If your order has not yet shipped, you can contact customer support to update your shipping address."},
    {"id": "faq7", "question": "What are your business hours?", "answer": "Our customer support is available Monday to Friday, from 9 AM to 5 PM EST."},
    {"id": "faq8", "question": "Do you offer gift wrapping?", "answer": "Yes, we offer gift wrapping for an additional fee. You can select this option at checkout."},
    {"id": "faq9", "question": "How do I use a discount code?", "answer": "You can apply your discount code in the 'Promo Code' box at checkout."},
    {"id": "faq10", "question": "What if my item is damaged?", "answer": "If your item arrives damaged, please contact customer support immediately for a replacement or refund."}
]

# --- 3. ChromaDB Setup ---
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

# --- 4. Helper Functions ---

def get_embedding(text):
    """
    Generates an embedding for the given text using the Ollama API.
    """
    try:
        response = requests.post(
            f"{OLLAMA_ENDPOINT}/embeddings",
            json={"model": OLLAMA_CONFIG["model"], "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting embedding: {e}")
        return None

def index_knowledge_base():
    """
    Indexes the knowledge base into ChromaDB.
    """
    print("Indexing knowledge base...")
    for item in FAQ_DATA:
        # We are embedding the questions to find similar user queries.
        embedding = get_embedding(item["question"])
        if embedding:
            collection.add(
                ids=[item["id"]],
                embeddings=[embedding],
                documents=[item["answer"]],  # Store the answer as the document
                metadatas=[{"question": item["question"]}]
            )
    print("Indexing complete.")

def parse_args():
    """
    Parse CLI arguments.
    --k <int>       : number of documents to retrieve from Chroma
    --no-context    : if set, do not retrieve any context from Chroma
    """
    parser = argparse.ArgumentParser(description="FAQ RAG with Ollama + ChromaDB")
    parser.add_argument("--k", type=int, default=DEFAULT_TOP_K, help="Top-K documents to retrieve from Chroma.")
    parser.add_argument("--no-context", action="store_true", help="Skip retrieving context from Chroma.")
    parser.add_argument("--query", "-q", type=str, help="Single user question to answer. If omitted, demo test queries will run.")
    return parser.parse_args() 

def query_rag_agent(user_query: str, k: int, no_context: bool = False):
    """
    Queries the RAG agent with a user's question.
    """
    print(f"\n--- Querying for: '{user_query}' ---")
    
    # 0) Timers
    t0_total = time.perf_counter()

    # 1. Get embedding for the user query
    query_embedding = get_embedding(user_query)
    if not query_embedding:
        return "Sorry, I couldn't process your query."

    retrieved_context = ""
    source_ids: list[str] = []  # for citation, safe even with --no-context
    t_retrieve = 0.0         # retrieval latency (0 if --no-context)

    # 2. Query ChromaDB for relevant context
    if no_context:
        print("--no-context active: skipping context retrieval.\n")
    else:
        t0_ret = time.perf_counter()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=max(1, k)
        )
        t_retrieve = time.perf_counter() - t0_ret
        
        ids = (results.get("ids") or [[]])[0]
        docs = (results.get("documents") or [[]])[0]        
        source_ids = [fid for fid in ids if fid]

        chunks = []
        for doc, fid in zip(docs, ids):
            if not (doc and fid):
                continue
            chunk = f"{DELIMITER} [{fid}]\n{doc}\n{DELIMITER}"
            chunks.append(chunk)
        retrieved_context = "\n".join(chunks)
        
        if retrieved_context:
            print(f"Retrieved context (top {k}):\n{retrieved_context}\n")
            print(f"Sources: {source_ids}\n")
        else:
            print("No relevant information found.\n")

    #3) Build the prompt for the LLM (with or without context)
    context_block = (
        "No additional context was provided."
        if not retrieved_context
        else f"Here is some context that might be relevant:\n'{retrieved_context}'"
    )

    # 4. Construct the prompt for the LLM
    prompt = f"""
You are a helpful FAQ assistant. A user has asked the following question:
'{user_query}'

   
{context_block}

Based on this context, please provide a clear and concise answer. If the context is not relevant, say so.
Sources: {source_ids}
""".strip()

    t0_gen = time.perf_counter()

    # 4. Send the prompt to the LLM
    try:
        response = requests.post(
            f"{OLLAMA_ENDPOINT}/generate",
            json={"prompt": prompt, **OLLAMA_CONFIG}
        )
        response.raise_for_status()
        model_answer = json.loads(response.text)["response"]
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the model: {e}"
    t_generate = time.perf_counter() - t0_gen
    t_total = time.perf_counter() - t0_total

    if PRINT_LATENCY:
        print(f"Latency | retrieve={t_retrieve:.3f}s | generate={t_generate:.3f}s | total={t_total:.3f}s")
    return model_answer

# --- 5. Main Execution ---
if __name__ == "__main__":
    
    args = parse_args()
    top_k = max(1, args.k) 
    use_no_context = args.no_context # True if --no-context was provided
    single_query = args.query

    # Check if the collection is empty before indexing
    if not use_no_context and collection.count() == 0:
        index_knowledge_base()
    else:
        print("Knowledge base is already indexed.")

    # --- Test Queries ---
    if single_query:  # <-- run a single question and exit
        answer = query_rag_agent(single_query, top_k, no_context=use_no_context)
        print(f"Answer: {answer}")
    else:
        test_queries = [
            "How can I return a product?",
            "What's the process for tracking my package?",
            "Do you ship to Canada?",
            "What are the support hours?",
            "Can I pay with Bitcoin?" # A question not in the knowledge base
        ]

        for query in test_queries:
            answer = query_rag_agent(query, top_k, no_context=use_no_context)
            print(f"Answer: {answer}")
