# Prompt Playbook v1

## Objective
Capture empirical observations comparing prompt variants and model behaviors. Use this as a living artifact you will refine in future weeks.

## How to Use This File
1. After each script run, append rows to the Results Table.
2. Tag failure modes (see legend) so patterns emerge quickly.
3. Summarize insights after completing stretch assignments.

## Scoring Rubric (1–5)
| Score | Instruction Adherence | Reasoning Depth | Style / Persona | Format Fidelity |
|-------|-----------------------|-----------------|-----------------|-----------------|
| 1 | Misses key directives | Single sentence | Ignores persona | Broken / ignores |
| 3 | Mostly follows | Some steps implicit | Partial persona | Minor drift |
| 5 | Precise & complete | Clear multi-step chain | Fully consistent | Exact, parsable |

## Failure Mode Tags
hallucination, verbosity, shallow, drift (format), persona-loss, json-break, constraint-fail

## Results Table (Populate During Lab)
| Prompt Pattern | Example Used | Model | Adherence (1–5) | Reasoning (1–5) | Style (1–5) | Format (1–5) | Failure Modes | Notes | Reuse? (Y/N) |
|----------------|--------------|-------|------------------|-----------------|-------------|--------------|---------------|-------|--------------|
Simple | Photosynthesis |  Ollama (Llama3) | 5 | 5 | 3 | 3 | N/A |  | N
Simple | Photosynthesis | Ollama (mistral)  | 5 | 5 | 4 | 4 | N/A | | N
Role |  Photosynthesis | Ollama (Llama3) | 5 | 5 | 4 | 4 | N/A |  | Y
Role |  Photosynthesis | Ollama (mistral) | 5 | 4 | 3 | 3 | N/A |  | N
Chain-of-Thought | Photosynthesis| Ollama (Llama3)| 5 | 5 | 4 | 4 | N/A | | Y
Chain-of-Thought | Photosynthesis| Ollama (mistral)| 5 | 5 | 4 | 4 | N/A |  | Y
Simple | Photosynthesis | gemini-2.5-flash | 5 | 5 | 5 | 5 | N/A | | Y
Role | Photosynthesis | gemini-2.5-flash | 5 | 5 | 5 | 5 | N/A | | Y
Chain-of-Thought | Photosynthesis| gemini-2.5-flash | 5 | 5 | 5 | 5 | N/A |  | Y

## Model Summary (After Initial Pass)
| Capability | Best Model(s) | Evidence Snippet | Notes |
|------------|---------------|------------------|-------|
| Explanatory Clarity |gemini-2.5-flash |1.  **Sunlight (Light Energy):** Provides the energy to power the reactions. 2.  **Carbon Dioxide ($CO_2$):** Absorbed from the atmosphere through tiny pores on leaves called **stomata**. This provides the carbon atoms for building sugars. 3.  **Water ($H_2O$):** Absorbed from the soil through the plant's roots. This provides hydrogen atoms and electrons, and is split to release oxygen. |easy to understand|
| Chain-of-Thought | gemini-2.5-flash|Photosynthesis is the remarkable process by which plants, algae, and some bacteria convert light energy into chemical energy, in the form of glucose (sugar). It's essentially how plants "eat" and, in doing so, produce the oxygen we breathe. | detailed |
| JSON Adherence | | | |
| Persona Control |(gemini-2.5-flash | Alright class, settle in! Grab your notebooks – or just lean forward and listen, because today, we're diving into one of the most fundamental, most incredible processes on Earth: **Photosynthesis**.| |
| Instruction Strictness | | | |

## Insight Log
Record notable surprises, regressions, or improvements.
- Day 1:
- Day 2:
- Day 3:

---

### 1. Role Prompting

*   **Best Practice:**
    *   Clearly define the persona or role you want the AI to adopt. This helps to set the context, tone, and level of detail in the response.
*   **Example:**
    *   Instead of "Explain black holes," use "You are an astrophysicist. Explain the concept of a black hole to a curious 10-year-old."

---

### 2. Few-Shot Learning

*   **Best Practice:**
    *   Provide a few examples of the desired input and output format. This is especially useful for tasks like classification, summarization, or code generation.
*   **Example:**
    *   When asking for a summary, provide one or two examples of a text and its corresponding summary before providing the text you want to be summarized.

---

### 3. Chain-of-Thought (CoT)

*   **Best Practice:**
    *   Encourage the model to "think step by step" or to "show its work." This is particularly effective for complex reasoning tasks, such as math problems or logic puzzles.
*   **Example:**
    *   Append "Let's think step by step" to your prompt when you need the model to reason through a problem.

---

### 4. Anti-Patterns to Avoid
## Reflection (End of Week)
Answer briefly:
1. Which two prompt patterns yielded the largest delta between models?
2. Which failure mode was most frequent? Root cause?
3. Default model choice for: explanation / reasoning / structure.
4. Open questions heading into Week 2.
*   **Ambiguity:**
    *   Avoid vague or open-ended questions. Be as specific as possible.
*   **Leading Questions:**
    *   Don't phrase your prompt in a way that suggests a desired answer.
*   **Overly Complex Prompts:**
    *   Break down complex tasks into smaller, more manageable prompts.

---
# Week 2 Lab: Building a Mini RAG FAQ Agent

## Original rag_lab.py script.

## Baseline 

--- Querying for: 'How can I return a product?' ---
Retrieved context: You can return any item within 30 days of purchase for a full refund.
You can reach our customer support team via email at support@example.com or by calling our toll-free number.
Answer: According to our return policy, you can return any item within 30 days of purchase for a full refund. To initiate the return process, simply reach out to our customer support team via email at support@example.com or by calling our toll-free number. We'll guide you through the rest of the process and ensure that your return is processed smoothly.

--- Querying for: 'What's the process for tracking my package?' ---
Retrieved context: Once your order has shipped, you will receive an email with a tracking number.
You can reach our customer support team via email at support@example.com or by calling our toll-free number.
Answer: Based on the provided context, here's a clear and concise answer:

"Once your order has shipped, you will receive an email with a tracking number. You can use this tracking number to track the status of your package. No further action is required from your end."

(Note: I didn't mention reaching out to customer support because that's not necessary for tracking your package. The context suggests that the tracking information will be provided via email.)

--- Querying for: 'Do you ship to Canada?' ---
Retrieved context: Yes, we ship to most countries worldwide. Shipping costs may vary.
Yes, we offer gift wrapping for an additional fee. You can select this option at checkout.
Answer: According to our shipping policy, yes, we do ship to Canada!

--- Querying for: 'What are the support hours?' ---
Retrieved context: Our customer support is available Monday to Friday, from 9 AM to 5 PM EST.
We accept all major credit cards, PayPal, and Apple Pay.
Answer: According to our available information, our customer support hours are Monday to Friday, from 9 AM to 5 PM EST.

--- Querying for: 'Can I pay with Bitcoin?' ---
Retrieved context: We accept all major credit cards, PayPal, and Apple Pay.
Yes, we ship to most countries worldwide. Shipping costs may vary.
Answer: Based on the provided context, it does not explicitly mention Bitcoin as an accepted payment method. The list of accepted payment methods includes all major credit cards, PayPal, and Apple Pay. Therefore, I must answer:

"No, we do not accept Bitcoin as a payment method."

##  python rag_labv2.py --k 3
| Query | Mode (raw/RAG) | k | Retrieved IDs | Strengths | Weaknesses | Failure Modes | Notes |
|-------|----------------|---|---------------|-----------|------------|---------------|-------|
|'How can I return a product?| RAG |3 | FAQ1,FAQ4, FAQ10 | accurate | n/a | n/a | clear answer |
|What's the process for tracking my package?| RAG | 3 | faq2,faq4, faq9| clear information about the steps | n/a |n/a| |
|Do you ship to Canada? | RAG | 3 |faq3,faq8, faq6 | clear indications | n/a|n/a|
|'What are the support hours | RAG | 3 | faq7, faq5, faq4 | Gives a concrete window and time zone, reducing temporal ambiguity.|n/a| n/a|
| Can I pay with Bitcoin? |RAG |3|faq5, faq3, faq6| direct answer| n/a|n/a||

##  python rag_labv2.py --k 3 --No-Context
| Query | Mode (raw/RAG) | k | Retrieved IDs | Strengths | Weaknesses | Failure Modes | Notes |
|-------|----------------|---|---------------|-----------|------------|---------------|-------|
|'How can I return a product?| RAW | 3 |---|--- |very open information | answers with steps never indicated | |
|What's the process for tracking my package? | RAW | 3 | ----| clear steps for tracking a package | take steps at a general level, not specific ones|---|
|'Do you ship to Canada?' | RAW| 3| ---| clear indication | speculation of different tariffs within Canada | ---|---|
|What are the support hours? | RAW| 3| --|  direct answer | speculation about schedule changes on holidays, for example | -- | --|
|Can I pay with Bitcoin? |RAw |3| ----| --- | wrong information |information that is not real |--|

 python rag_labv2.py --k 3 --query
| Query | Mode (raw/RAG) | k | Retrieved IDs | Strengths | Weaknesses | Failure Modes | Notes |
|-------|----------------|---|---------------|-----------|------------|---------------|-------|
|'How do I track my order?| RAG| 3| faq2, faq4,faq6| Concise  | --- | ----| ---|
|'How do I track my order?| RAW| 3| ---- | step by step how track a package  | no the real steps for this exercise| ----| ---|


#  python rag_labv2.py Use and example
```
python rag_lab.py --k 3 
```

```
Knowledge base is already indexed.

--- Querying for: 'How can I return a product?' ---
Retrieved context (top 3):
----- [faq1]
You can return any item within 30 days of purchase for a full refund.
-----
----- [faq4]
You can reach our customer support team via email at support@example.com or by calling our toll-free number.
-----
----- [faq10]
If your item arrives damaged, please contact customer support immediately for a replacement or refund.
-----

Sources: ['faq1', 'faq4', 'faq10']

Latency | retrieve=0.015s | generate=2.625s | total=3.754s
Answer: To return a product, you can follow these steps:

* Contact our customer support team via email at support@example.com or by calling our toll-free number.
* Let us know that you would like to initiate a return and provide your order details.
* Returns are accepted within 30 days of purchase for a full refund.

Note: If the item arrives damaged, please contact us immediately so we can assist with a replacement or refund.

--- Querying for: 'What's the process for tracking my package?' ---
Retrieved context (top 3):
----- [faq2]
Once your order has shipped, you will receive an email with a tracking number.
-----
----- [faq4]
You can reach our customer support team via email at support@example.com or by calling our toll-free number.
-----
----- [faq9]
You can apply your discount code in the 'Promo Code' box at checkout.
-----

Sources: ['faq2', 'faq4', 'faq9']

Latency | retrieve=0.001s | generate=2.403s | total=3.528s
Answer: To track your package, you will receive an email with a tracking number once your order has shipped. This email notification will keep you updated on the status of your delivery. If you need further assistance or have questions about your shipment, you can reach our customer support team via email at support@example.com or by calling our toll-free number.

Sources: ['faq2']

--- Querying for: 'Do you ship to Canada?' ---
Retrieved context (top 3):
----- [faq3]
Yes, we ship to most countries worldwide. Shipping costs may vary.
-----
----- [faq8]
Yes, we offer gift wrapping for an additional fee. You can select this option at checkout.
-----
----- [faq6]
If your order has not yet shipped, you can contact customer support to update your shipping address.
-----

Sources: ['faq3', 'faq8', 'faq6']

Latency | retrieve=0.001s | generate=1.710s | total=2.829s
Answer: According to our shipping policies, yes, we do ship to Canada! In fact, we ship to most countries worldwide, with varying costs for each destination.

--- Querying for: 'What are the support hours?' ---
Retrieved context (top 3):
----- [faq7]
Our customer support is available Monday to Friday, from 9 AM to 5 PM EST.
-----
----- [faq5]
We accept all major credit cards, PayPal, and Apple Pay.
-----
----- [faq4]
You can reach our customer support team via email at support@example.com or by calling our toll-free number.
-----

Sources: ['faq7', 'faq5', 'faq4']

Latency | retrieve=0.001s | generate=1.981s | total=3.089s
Answer: According to our FAQs, our customer support hours are Monday to Friday, from 9 AM to 5 PM EST. You can reach out to us via email at support@example.com or by calling our toll-free number during these hours.

--- Querying for: 'Can I pay with Bitcoin?' ---
Retrieved context (top 3):
----- [faq5]
We accept all major credit cards, PayPal, and Apple Pay.
-----
----- [faq3]
Yes, we ship to most countries worldwide. Shipping costs may vary.
-----
----- [faq6]
If your order has not yet shipped, you can contact customer support to update your shipping address.
-----

Sources: ['faq5', 'faq3', 'faq6']

Latency | retrieve=0.001s | generate=2.160s | total=3.281s
Answer: According to our payment options listed in [faq5], we currently do not accept Bitcoin as a form of payment. We only accept major credit cards, PayPal, and Apple Pay. If you're looking for alternative cryptocurrency payment methods, you may want to consider other retailers that support Bitcoin payments.
```

