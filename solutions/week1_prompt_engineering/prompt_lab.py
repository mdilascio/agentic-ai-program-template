import os
import time
import json
import argparse
from datetime import datetime
from textwrap import shorten
from typing import Dict, Callable, List

import requests
import openai
import anthropic
import google.generativeai as genai

try:  # Optional dependency for .env loading
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# --- Configuration ---

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize clients
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Model Clients ---

def query_ollama(prompt, model="llama3"):
    """Sends a prompt to a local Ollama server."""
    print(f"\n--- Querying Ollama ({model}) ---")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to Ollama. Is it running? Details: {e}"

def query_openai(prompt, model="gpt-5-mini"):
    """Sends a prompt to the OpenAI API."""
    print(f"\n--- Querying OpenAI ({model}) ---")
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY not set."
    try:
        client = openai.OpenAI()
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error querying OpenAI: {e}"

def query_anthropic(prompt, model="claude-3-haiku-20240307"):
    """Sends a prompt to the Anthropic API."""
    print(f"\n--- Querying Anthropic ({model}) ---")
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set."
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error querying Anthropic: {e}"

def query_gemini(prompt, model="gemini-2.5-flash"):
    """Sends a prompt to the Google Gemini API."""
    print(f"\n--- Querying Gemini ({model}) ---")
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY not set."
    try:
        model = genai.GenerativeModel(model)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error querying Gemini: {e}"

DEFAULT_PROMPTS = {
    "Simple": "Explain photosynthesis.",
    "Role": "You are a biology professor. Explain photosynthesis to a high school student.",
    "Chain-of-Thought": """Explain photosynthesis step-by-step, start with inputs (what plants need) and end with outputs.""",
}


def build_prompts(custom_prompt: str | None) -> Dict[str, str]:
    prompts = DEFAULT_PROMPTS.copy()
    if custom_prompt:
        prompts["Custom"] = custom_prompt
    return prompts


def format_summary_row(model_name: str, prompt_name: str, response: str) -> Dict[str, str]:
    return {
        "model": model_name,
        "prompt_variant": prompt_name,
        "length": str(len(response.split())) if response else "0",
        "preview": shorten(response.replace("\n", " "), width=80, placeholder="…") if response else "",
    }


def write_json(results: List[Dict[str, str]], out_dir: str = "results") -> str:
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"week1_run_{timestamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return path

# --- Main Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 1 Prompt Engineering Lab Runner")
    parser.add_argument("--models", choices=["local", "cloud", "all"], default="all", help="Subset of models to query.")
    parser.add_argument("--custom-prompt", dest="custom_prompt", help="Add an extra custom prompt variant.")
    parser.add_argument("--log-json", action="store_true", help="Write results to results/week1_run_<timestamp>.json")
    parser.add_argument("--no-chain", action="store_true", help="Skip chain-of-thought prompt variant.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout for local model queries.")
    args = parser.parse_args()

    prompts = build_prompts(args.custom_prompt)
    if args.no_chain and "Chain-of-Thought" in prompts:
        del prompts["Chain-of-Thought"]

    # Model groups
    local_models: Dict[str, Callable[[str], str]] = {
        "Ollama (Llama3)": query_ollama,
        "Ollama (Mistral)": lambda p: query_ollama(p, model="mistral"),
    }
    cloud_models: Dict[str, Callable[[str], str]] = {
        "OpenAI (GPT-3.5)": query_openai,
        "Anthropic (Claude 3 Haiku)": query_anthropic,
        "Google (Gemini Pro)": query_gemini,
    }

    if args.models == "local":
        models_to_test = local_models
    elif args.models == "cloud":
        models_to_test = cloud_models
    else:
        models_to_test = {**local_models, **cloud_models}

    summary_rows: List[Dict[str, str]] = []

    for prompt_name, prompt_text in prompts.items():
        print("\n" + "=" * 70)
        print(f"PROMPT VARIANT: {prompt_name}")
        print("=" * 70)

        for model_name, query_function in models_to_test.items():
            start = time.time()
            response = query_function(prompt_text)
            elapsed = time.time() - start
            print(f"Response from {model_name} (latency: {elapsed:.2f}s):\n{response}\n")
            print("-" * 40)
            summary = format_summary_row(model_name, prompt_name, response)
            summary["latency_s"] = f"{elapsed:.2f}"
            summary_rows.append(summary)

    # Print summary table
    print("\nSUMMARY (Model | Variant | Words | Latency | Preview)")
    for row in summary_rows:
        print(f"- {row['model']} | {row['prompt_variant']} | {row['length']} | {row.get('latency_s','?')}s | {row['preview']}")

    if args.log_json:
        out_path = write_json(summary_rows)
        print(f"\nJSON results written to: {out_path}")
