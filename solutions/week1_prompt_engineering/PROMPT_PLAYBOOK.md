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
|Do you ship to Canada? | 