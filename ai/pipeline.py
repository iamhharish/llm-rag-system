import os
import re
import csv
import torch
from datetime import datetime
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM

# Your existing local modules
from data_loader import load_document
from chunking import create_chunks
from retriever import build_index, retrieve_chunks, rerank_chunks
from online_retrieval import get_online_data

EMBED_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LOG_FILE = "project_logs.csv"

# ================= 1. SYSTEM INITIALIZATION =================
def initialize_system(folder="data"):
    text_data = ""
    if os.path.exists(folder):
        for file in os.listdir(folder):
            try:
                text_data += load_document(os.path.join(folder, file)) + "\n"
            except: pass
    
    chunks = create_chunks(text_data) if text_data else []
    embed_model = SentenceTransformer(EMBED_MODEL)
    index = build_index(embed_model.encode(chunks)) if chunks else None

    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    # Keep model loading compatible on machines without accelerate/GPU.
    if torch.cuda.is_available():
        llm = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL,
            dtype=torch.float16,
            device_map="auto"
        )
    else:
        llm = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL,
            dtype=torch.float32
        )
        llm = llm.to("cpu")
    
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["Timestamp", "Question", "Answer", "Source", "Marks"])
            
    return chunks, embed_model, index, tokenizer, llm

chunks, embed_model, index, tokenizer, llm = initialize_system()

# ================= 2. CORE UTILITIES =================
def log_interaction(query, answer, source, marks):
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([datetime.now().strftime("%H:%M:%S"), query, answer, source, marks])

def semantic_overlap(q, text):
    if not text: return 0.0
    qw = set(re.findall(r'\w+', q.lower()))
    tw = set(re.findall(r'\w+', text.lower()))
    return len(qw & tw) / (len(qw) + 1)

# ================= 3. DYNAMIC GENERATION LOGIC =================
def get_answer(query):
    if not query.strip(): return "⚠️ Please enter a question."

    # --- Step A: Hybrid Retrieval ---
    off_chunks = []
    if index:
        retrieved = retrieve_chunks(query, embed_model, index, chunks)
        off_chunks = rerank_chunks(query, retrieved)[:3]
    
    on_chunks = get_online_data(query)[:3]
    full_context = "[DOCS]: " + " ".join(off_chunks) + " [WEB]: " + " ".join(on_chunks)
    
    # Relevance Guard
    if semantic_overlap(query, full_context) < 0.08:
        return "I don't have enough data to answer this. Please upload a relevant document."

    # --- Step B: Marks & Structure Logic ---
    marks = 0
    mark_match = re.search(r'(\d+)\s*mark', query.lower())
    if mark_match: marks = int(mark_match.group(1))
    
    is_detailed = any(x in query.lower() for x in ["detail", "explain", "depth", "comprehensive"])

    # Define Instruction and Token Limit based on intent
    if marks >= 10 or (is_detailed and marks == 0):
        # Force a structured academic response
        instr = (
            f"Provide a COMPLETE and FULL academic answer for {marks if marks > 0 else 'detailed'} marks. "
            "Use clear Side Headings: 1. Introduction, 2. Key Concepts, 3. Detailed Explanation, 4. Conclusion."
        )
        token_limit = 700 
        temp = 0.3 # Allow slight creativity for "flow" in long text
    elif marks >= 2:
        instr = f"Provide a direct {marks}-mark answer with factual details."
        token_limit = 250
        temp = 0.1
    else:
        instr = "Provide a concise 1-sentence formal answer."
        token_limit = 100
        temp = 0.01

    # --- Step C: Optimized Prompting ---
    prompt = f"<|system|>\nContext: {full_context}\nTask: {instr} Do not repeat the question.</s>\n<|user|>\n{query}</s>\n<|assistant|>\n"

    inputs = tokenizer(prompt, return_tensors="pt").to(llm.device)
    
    with torch.no_grad():
        output = llm.generate(
            **inputs,
            max_new_tokens=token_limit,
            temperature=temp,
            do_sample=True if temp > 0.1 else False,
            repetition_penalty=1.3,
            eos_token_id=tokenizer.eos_token_id
        )

    # --- Step D: Post-Processing & Cleaning ---
    raw_answer = tokenizer.decode(output[0], skip_special_tokens=True)
    answer = raw_answer.split("<|assistant|>")[-1].strip()
    
    # Remove "Question: Answer:" loops that sometimes happen in TinyLlama
    answer = re.sub(r"^(Question:.*?Answer:|Answer:)", "", answer, flags=re.I | re.DOTALL).strip()

    # Ensure the answer doesn't end in a broken sentence
    if not answer.endswith(('.', '!', '?')):
        last_stop = max(answer.rfind('.'), answer.rfind('!'), answer.rfind('?'))
        if last_stop != -1:
            answer = answer[:last_stop+1]

    # Attribution Tag
    source_tag = "Offline Docs" if semantic_overlap(query, " ".join(off_chunks)) > 0.15 else "Online Search"
    if semantic_overlap(query, " ".join(off_chunks)) > 0.1 and semantic_overlap(query, " ".join(on_chunks)) > 0.1:
        source_tag = "Hybrid (Docs + Online)"

    log_interaction(query, answer, source_tag, marks)
    return f"{answer}\n\n📌 Source: {source_tag} | Marks: {marks if marks > 0 else 'General'}"

# ================= 4. EXECUTION =================
if __name__ == "__main__":
    print("\n🎓 Final Hybrid RAG Pipeline | Full Academic Mode Active")
    print("Logs are being saved to: project_logs.csv\n")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]: break
        print(f"\nAI: {get_answer(user_input)}")
        print("-" * 50)