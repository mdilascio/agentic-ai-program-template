import argparse
import requests
import json
import chromadb

# --- 1. Configuration ---
OLLAMA_ENDPOINT = "http://localhost:11434/api"
OLLAMA_CONFIG = {
    "model": "llama3",
    "stream": False,
}
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "faq_collection"
DEFAULT_TOP_K = 2

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
    return parser.parse_args() 

def query_rag_agent(user_query: str, k: int, no_context: bool = False):
    """
    Queries the RAG agent with a user's question.
    """
    print(f"\n--- Querying for: '{user_query}' ---")
    
    # 1. Get embedding for the user query
    query_embedding = get_embedding(user_query)
    if not query_embedding:
        return "Sorry, I couldn't process your query."

    # 2. Query ChromaDB for relevant context
    if no_context:
        retrieved_context = ""
        print("--no-context active: skipping context retrieval.\n")
    else:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=max(1,k) 
      )
        
    ids = (results.get("ids") or [[]])[0]
    docs = (results.get("documents") or [[]])[0]
    
     # Format each context line as: "<answer> (<faqId>)"
    formatted_context_list = [
        f"{doc} ({faq_id})"
        for doc, faq_id in zip(docs, ids)
        if doc and faq_id
    ]
    retrieved_context = "\n".join(formatted_context_list)
    
    if retrieved_context:
        print(f"Retrieved context (top {k}):\n{retrieved_context}\n")
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
    """

    # 4. Send the prompt to the LLM
    try:
        response = requests.post(
            f"{OLLAMA_ENDPOINT}/generate",
            json={"prompt": prompt, **OLLAMA_CONFIG}
        )
        response.raise_for_status()
        return json.loads(response.text)["response"]
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the model: {e}"

# --- 5. Main Execution ---
if __name__ == "__main__":
    
    args = parse_args()
    top_k = max(1, args.k) 
    use_no_context = args.no_context # True if --no-context was provided

    # Check if the collection is empty before indexing
    if collection.count() == 0:
        index_knowledge_base()
    else:
        print("Knowledge base is already indexed.")

    # --- Test Queries ---
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
