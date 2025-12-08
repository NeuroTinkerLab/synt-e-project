import time
import logging
import ollama

# --- CONFIGURAZIONE ---
# Il tuo modello locale (assicurati che sia scaricato)
MODEL_NAME = "gpt-oss:20b-unlocked"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Synt-E")

# --- IL CERVELLO (System Prompt) ---
# Qui diamo istruzioni rigide a Llama per comportarsi come un compilatore
SYSTEM_PROMPT = """
CRITICAL ROLE: You are a Synt-E compiler. Translate user requests into a token-efficient, single-line command.

OUTPUT RULES (MANDATORY):
1.  **NO QUOTES:** Use snake_case for multi-word values (e.g., "quarterly meeting" becomes quarterly_meeting).
2.  **NO ARROWS (->):** Chain actions by simple succession if necessary.
3.  **NO EXPLANATIONS:** Output ONLY the final command string.
4.  **BE COMPLETE:** Capture all critical details like format, quantity, or specific names.

--- EXAMPLES ---
User: "Prepara una presentazione in PowerPoint per il meeting sul Q3"
AI: task:create_presentation format:powerpoint event:quarterly_meeting topic:Q3_sales

User: "Cerca X e poi filtra per Y"
AI: task:search topic:X filter:Y

User: "Scrivi uno script python"
AI: task:code lang:python
--- END EXAMPLES ---
"""

def process_with_ai(text):
    start = time.time()
    logger.info(f"🧠 Invio a {MODEL_NAME}...")
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': text},
        ])
        
        result = response['message']['content'].strip()
        duration = time.time() - start
        
        # A volte i modelli chiacchierano, puliamo eventuali apici o markdown
        result = result.replace("`", "").replace("Here is the Synt-E:", "").strip()
        
        return result, duration
        
    except Exception as e:
        return f"ERROR: {e}", 0

# --- MAIN LOOP ---
def main():
    print(f"\n==================================================")
    print(f"   SYNT-E PURE AI (Powered by {MODEL_NAME})")
    print(f"   Modalità: INTELLIGENZA PURA (No Regex)")
    print(f"==================================================\n")

    while True:
        user_input = input("TU > ").strip()
        if not user_input: continue
        if user_input.lower() in ["exit", "esci"]: break
        
        # Chiamata diretta all'AI
        synt_e_code, time_taken = process_with_ai(user_input)
        
        print(f"AI > {synt_e_code}")
        print(f"     (Tempo: {time_taken:.2f}s)\n")

if __name__ == "__main__":
    main()
