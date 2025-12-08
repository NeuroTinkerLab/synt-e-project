# Synt-E: The Protocol for Talking to AIs 🚀

Synt-E is a "language" designed to give instructions to Artificial Intelligences (LLMs) as efficiently as possible. Instead of writing long sentences, you use short, dense commands that the AI understands better, faster, and at a lower cost.

---

## 🤔 Why Does Synt-E Exist? The Problem

When we talk to an AI like ChatGPT, we use human language, which is full of words that are useless to a machine.

**BEFORE (Natural Language):**
> "Hi, could you please write me a Python script to analyze data from a CSV file?"
*(Too many words, too many "tokens", risk of ambiguity)*

**AFTER (Synt-E):**
> `task:code lang:python action:analyze_data format:csv`
*(Few words, zero ambiguity, maximum efficiency)*

---

## ✨ How Does the Magic Work? The Logic Behind Synt-E

The secret is simple: **modern AIs have been trained on almost the entire Internet, and most of the Internet is in English.**

They have seen **billions of patterns** of code, terminal commands, configuration files, and technical texts in English. For them, technical English is not a language; it is their **native language**.

- **Technical English is a highway:** Giving a command in Synt-E is like getting on the highway. The request reaches its destination quickly and smoothly.
- **Other languages are country roads:** The AI understands them, but it has to "translate" and "interpret" more, wasting time and resources.

### The Concrete Advantages
1.  **💰 Token Savings (and Money):** Fewer words mean fewer "tokens" to pay for if you use a paid service. Locally, it means less load on your CPU/GPU.
2.  **⚡ Superior Speed:** The AI doesn't have to think about how to interpret your pleasantries. It gets straight to the point, giving you an answer faster.
3.  **✅ Better Answers:** By eliminating ambiguity, you reduce the risk of the AI misunderstanding and giving you a wrong or incomplete answer.

---

## 💻 Try It Now on Your PC! (with Ollama)

This project includes a simple Python program that transforms your sentences in Italian (or any other language) into the Synt-E protocol, using an AI that runs **free and offline** on your computer.

### Step 1: Prerequisites
1.  **Python:** Make sure you have it installed. If you don't, download it from [python.org](https://python.org).
2.  **Ollama:** Install Ollama to run AIs locally. Download it from [ollama.com](https://ollama.com).

### Step 2: Choose the Right Model (IMPORTANT)
Not all AI models are suitable for this task.
- **"Assistant" Models (like Llama 3.1 Instruct):** They are too "helpful." If you ask them to translate a request to write code, they will write the code instead of translating it. **They are the least suitable.**
- **"Raw" or "Unfiltered" Models (like GPT-OSS or Dolphin):** They are more flexible and obedient. They understand their role as a "compiler" and do not try to perform the task for you. **They are the best for this script.**

From your list, the winner was **`gpt-oss:20b`**.

### Step 3: Install and Run
1.  **Download the model:** Open the terminal and run this command.
    ```bash
    ollama pull gpt-oss:20b
    ```

2.  **Install the library:** In the project folder, run this command.
    ```bash
    pip install ollama
    ```

3.  **Run the script:** Make sure Ollama is running, then run the program.
    ```bash
    python synt_e.py
    ```

### Usage Examples
Now you can write your requests. The program will send them to your local model and return the translation in Synt-E.

**Example 1: Technical Request**
> **YOU >** Write a Python script that uses Keras for sentiment analysis.
>
> **AI >** `task:write_script language:python libraries:keras model:RNN dataset:movie_reviews task:sentiment_analysis`

**Example 2: Creative Request**
> **YOU >** Generate an image of a red dragon, in watercolor style.
>
> **AI >** `task:generate_image subject:red_dragon style:watercolor`

**Example 3: Complex Request**
> **YOU >** Prepare a PowerPoint presentation for the quarterly meeting with the CEO on the topic of sales.
>
> **AI >** `task:create_presentation format:powerpoint event:quarterly_meeting audience:ceo topic:sales`

---

## 🏗️ The Future of the Project
This script is just a prototype. The complete architecture of Synt-E (which we have explored) includes:
- A **hybrid engine** that uses fast rules for simple commands.
- A **security** system to block sensitive data.
- An **ecosystem** with extensions for editors like VS Code.

Have fun compiling your thoughts!