import time
import logging
import ollama

# --- CONFIGURATION ---
# Your local model (make sure it's downloaded)
MODEL_NAME = "gpt-oss:20b"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Synt-E")

# --- THE BRAIN (System Prompt) ---
# Here we give strict instructions to Llama to act like a compiler
SYSTEM_PROMPT = """
CRITICAL ROLE: You are a Synt-E compiler. Translate user requests into a token-efficient, single-line command.

OUTPUT RULES (MANDATORY):
1.  **NO QUOTES:** Use snake_case for multi-word values (e.g., "quarterly meeting" becomes quarterly_meeting).
2.  **NO ARROWS (->):** Chain actions by simple succession if necessary.
3.  **NO EXPLANATIONS:** Output ONLY the final command string.
4.  **BE COMPLETE:** Capture all critical details like format, quantity, or specific names.

--- EXAMPLES ---
User: "Prepare a PowerPoint presentation for the Q3 meeting"
AI: task:create_presentation format:powerpoint event:quarterly_meeting topic:Q3_sales

User: "Search for X and then filter by Y"
AI: task:search topic:X filter:Y

User: "Write a python script"
AI: task:code lang:python
--- END EXAMPLES ---
"""

def process_with_ai(text):
    start = time.time()
    logger.info(f"🧠 Sending to {MODEL_NAME}...")
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': text},
        ])
        
        result = response['message']['content'].strip()
        duration = time.time() - start
        
        # Sometimes models get chatty, let's clean up any backticks or markdown
        result = result.replace("`", "").replace("Here is the Synt-E:", "").strip()
        
        return result, duration
        
    except Exception as e:
        return f"ERROR: {e}", 0

# --- MAIN LOOP ---
def main():
    print(f"\n==================================================")
    print(f"   SYNT-E PURE AI (Powered by {MODEL_NAME})")
    print(f"   Mode: PURE AI (No Regex)")
    print(f"==================================================\n")

    while True:
        user_input = input("YOU > ").strip()
        if not user_input: continue
        if user_input.lower() in ["exit"]:
            break
        
        # Direct call to the AI
        synt_e_code, time_taken = process_with_ai(user_input)
        
        print(f"AI > {synt_e_code}")
        print(f"     (Time: {time_taken:.2f}s)\n")

if __name__ == "__main__":
    main()
