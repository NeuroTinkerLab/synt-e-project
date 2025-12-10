# Synt-E: The Protocol for Talking to AIs 🚀

Synt-E is a protocol and a command-line tool for translating natural language into efficient machine commands, designed for interaction with local LLMs (via Ollama). Instead of writing long sentenc[...] 

This project is not just an experiment, but a **Power Tool** for developers and power users who want to optimize their AI workflow, and a prototype of a **Machine-to-Machine (M2M) communication pro[...] 

---

## 🤔 Why Does Synt-E Exist? The Problem

When we talk to an AI, we use colloquial language. This is fine for a chat, but in a professional workflow or an automated system, it is:
- **Slow:** The AI has to process unnecessary words.
- **Expensive:** More words = more tokens to compute (or pay for).
- **Ambiguous:** Human language can be misunderstood.

**BEFORE (Natural Language):**
> "Hi, could you write me a Python script to analyze data from a CSV file?"

**AFTER (Synt-E, activated with a shortcut):**
> `task:code lang:python action:analyze_data format:csv`

---

## 🛠️ Why is it Useful in Any Software Project?

In any development environment that integrates LLMs—whether it's a startup, a DevOps team, or an open-source project—efficiency is key. Synt-E offers concrete advantages:

1.  **💰 Cost Reduction (Token Saving):** A Synt-E prompt can be **up to 70% shorter** than a normal sentence, resulting in direct savings on costs and computational resources.
2.  **⚡ Increased Speed (Latency Reduction):** Fewer tokens to process means faster responses, which is essential for real-time applications.
3.  **🤖 Reliability and Testability (Fewer Bugs):** Synt-E is a standardized protocol. It makes interactions with AIs **predictable and easy to test**, reducing bugs.

### The Fundamental Discovery: The Right Model is Everything
During testing, we discovered that super-trained "assistant" models (like `Llama 3 Instruct`) are the **worst** for this task because their instinct to "execute" the command wins over the meta-ins[...]

The best models are those that are more "raw" or "unfiltered," which are more obedient to a strict `SYSTEM_PROMPT`. Our winner was **`gpt-oss:20b`**.

### System Limits: When NOT to use Synt-E
Synt-E is a protocol for **compressing complexity**, not always length.
- **Great for:** Long, descriptive, and complex sentences. Here, the savings are enormous.
- **Useless for:** Very short sentences (1-3 words). In this case, the AI has to "invent" the context (`task:`, `topic:`), and the output may be longer than the input.

---

## 💻 Usage Guide: Your Personal Compiler

This tool runs in the background, listening for a series of keyboard shortcuts to give you complete and safe control over the synthesis process.

### Installation
1.  **Install Ollama:** Download it from [ollama.com](https://ollama.com) and run it.
2.  **Download a Model:** Open the terminal and download the model you want to use (e.g., `gpt-oss` or `qwen3:30b`).
    ```bash
    ollama pull gpt-oss:20b
    ```
3.  **Install Python Libraries:**
    ```bash
    pip install ollama keyboard pyperclip pywin32 psutil winsound
    ```

### Startup and Command-Line Options
Start the script from the terminal. You can use different "flags" to customize its behavior.

**Basic Startup:**
```bash
python synt_e.py
(Uses default shortcuts and model)
```
**Startup with a Custom Model:**
```bash
python synt_e.py --model="qwen3:30b-a3b-unlocked"
```
**Startup with a Custom Shortcut:**
```bash
python synt_e.py --hotkey="ctrl+shift+x"
```

**Startup in "Append" Mode (does not replace, but adds at the end):**
```bash
python synt_e.py --append
```
You can combine as many options as you like!

### Daily Workflow (Safe Method)
The workflow has been designed to be 100% reliable, giving you full control.
1.  Start the script in a terminal and leave it open in the background.
2.  Go to any program (Chrome, VS Code, Notepad...).
3.  Select the text you want to synthesize.
4.  **Copy Manually:** Press `Ctrl+C`.
5.  **Activate Synthesis:** Press the shortcut (default: `Ctrl+Alt+S`).
Your text will be instantly replaced with the Synt-E version!

### All Shortcuts (Power User Features)
This tool is more than just a synthesizer. It's a command suite:
-   **Synthesize (`Ctrl+Alt+S`):** Compiles the text you have copied.
-   **Undo (`Ctrl+Alt+U`):** You have 10 seconds after a synthesis to press this hotkey and restore the original text. A lifesaver!
-   **Interrupt AI (`Ctrl+Alt+C`):** If the AI is taking too long for a complex request, press this shortcut to cancel the operation.
-   **Keyboard Emergency (`Ctrl+Alt+Q`):** In the very rare case that the script locks your keyboard, this is your forced "emergency exit" that resets everything.

![Screenshot of the app showing emergency shortcut]("Screenshot 2025-12-10 171345.png")

### Audio Feedback
-   **Double Beep:** Confirms that an operation (synthesis, undo) was successful.
-   **Single Low Beep:** Alerts you to an error (e.g., no text in the clipboard).
-   **Cancellation Beep:** Confirms that the AI operation has been interrupted.
