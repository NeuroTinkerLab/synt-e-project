
import time
import logging
import ollama
import sys
import pyperclip
import keyboard
import argparse
import threading
import win32gui
import win32process
import psutil
import os
import signal
import winsound
import ctypes
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# --- GLOBAL CONSTANTS ---
EMERGENCY_HOTKEY = 'ctrl+alt+q'
CANCEL_AI_HOTKEY = 'ctrl+alt+c'  # New hotkey to interrupt AI processing
BROWSER_PROCESSES = ['chrome.exe', 'msedge.exe', 'firefox.exe', 'brave.exe', 'opera.exe', 'applicationframehost.exe']
CONSOLE_PROCESSES = ['cmd.exe', 'powershell.exe', 'windowsTerminal.exe', 'terminalapp.exe', 'notepad.exe']

# --- KEYBOARD ANTI-LOCK MECHANISM ---
keyboard_blocked = False
operation_lock = threading.RLock()
ai_cancel_requested = False
AI_TIMEOUT = 120  # Maximum timeout for AI processing (2 minutes)

def play_beep(frequency=1000, duration=200):
    """Plays a beep sound, works on Windows 11."""
    try:
        winsound.Beep(frequency, duration)
    except:
        # Silent fallback if winsound is not available
        pass

def play_error_beep():
    """Plays a low-pitched error beep."""
    try:
        winsound.Beep(600, 300)
    except:
        pass

def play_success_beep():
    """Plays a double success beep."""
    try:
        winsound.Beep(1000, 150)
        time.sleep(0.05)
        winsound.Beep(1200, 150)
    except:
        pass

def play_cancel_beep():
    """Plays a cancellation beep."""
    try:
        winsound.Beep(800, 100)
        time.sleep(0.05)
        winsound.Beep(600, 100)
    except:
        pass

def emergency_keyboard_reset():
    """Complete keyboard reset WITHOUT changing window focus."""
    global keyboard_blocked
    logger.warning("🚨 EMERGENCY: Forced keyboard reset activated!")
    play_beep(400, 500)  # Long emergency beep
    
    try:
        # 1. Safely unhooks ALL hooks
        keyboard.unhook_all()
        keyboard.clear_all_hotkeys()
        
        # 2. Hardware reset of the keyboard (modifier keys ONLY)
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        for vk in [0x10, 0x11, 0x12, 0x5B, 0x5C]:  # SHIFT, CTRL, ALT, WIN
            user32.keybd_event(vk, 0, 2, 0)  # KEYEVENTF_KEYUP
        
        # 3. Waits for a full reset without changing windows
        time.sleep(0.5)
        
        logger.info("✅ Keyboard successfully reset!")
        keyboard_blocked = False
        return True
    except Exception as e:
        logger.error(f"❌ Error during emergency reset: {e}")
        return False

def cancel_ai_operation():
    """Cancels the ongoing AI processing."""
    global ai_cancel_requested
    ai_cancel_requested = True
    logger.info("🛑 AI processing cancellation request received")
    play_cancel_beep()
    return True

def keyboard_operation():
    """Decorator ONLY for operations using the physical keyboard (no watchdog, short operations)."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global keyboard_blocked
            
            if keyboard_blocked:
                logger.warning("⚠️ Operation ignored: keyboard already locked by another operation")
                return None
            
            with operation_lock:
                keyboard_blocked = True
                try:
                    # Executes the operation (no automatic timeout, instant operations)
                    result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    logger.exception(f"🚨 Error during operation: {e}")
                    emergency_keyboard_reset()
                    return None
                finally:
                    keyboard_blocked = False
                    logger.debug("🔓 Keyboard unlocked after operation")
        return wrapper
    return decorator

# --- PARSER CONFIGURATION ---
parser = argparse.ArgumentParser(description="Synt-E Hotkey Tool")
parser.add_argument("--hotkey", default="ctrl+alt+s", help="Hotkey combination for synthesis.")
parser.add_argument("--undo-hotkey", default="ctrl+alt+u", help="Hotkey combination for undo.")
parser.add_argument("--append", action="store_true", help="Appends the synthesis instead of replacing.")
parser.add_argument("--verbose", action="store_true", help="Show detailed logs.")
parser.add_argument("--model", default="gpt-oss:20b", help="Ollama model to use.")
parser.add_argument("--max-chars", type=int, default=5000, help="Maximum length of text to process.")
args = parser.parse_args()

MODEL_NAME = args.model
last_synthesis = {"original": None, "timestamp": 0}
MAX_CHARS = args.max_chars

# --- LOGGING ---
log_level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Synt-E")
logging.getLogger("httpx").setLevel(logging.WARNING)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
CRITICAL ROLE: You are a Synt-E compiler. Translate user requests into token-efficient, single-line commands using ONLY the official ontology.

--- OUTPUT RULES (STRICT) ---
1.  **FORMAT:** `key1:value1 key2:value2` (space-separated, NO commas/brackets)
2.  **REQUIRED KEYS:** task (ALWAYS first), then other relevant keys
3.  **OFFICIAL ONTOLOGY:** task, topic, target, format, lang, style, action, filter, exclude, quantity, details, os, platform, product, theme, event, audience, content
4.  **KEY PRIORITY:** 
    - Use SPECIFIC keys first (task, lang, format) 
    - Use `details:` ONLY for uncategorizable info
    - NEVER invent new keys
5.  **VALUES:** snake_case, lowercase, NO quotes/brackets
6.  **NO EXPLANATIONS:** Output ONLY the final command string

--- CRITICAL EXAMPLES ---
User: "I want an image of a red dragon with golden wings"
AI: task:generate_image topic:red_dragon details:golden_wings

User: "Write python code that connects to a database on port 5432"
AI: task:code lang:python action:connect_database details:port_5432

User: "My website visits have plummeted. Prepare a report."
AI: task:analyze_data topic:website_traffic task:create_report target:team

User: "Create a markdown table with 3 columns: name, age, city"
AI: task:create_table format:markdown details:columns_name_age_city quantity:3
"""

# --- WINDOW UTILITY FUNCTIONS ---
def get_active_window_info():
    """Gets detailed information about the active window."""
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None
    
    title = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    try:
        process = psutil.Process(pid)
        exe_name = os.path.basename(process.exe()).lower()
        return {
            'hwnd': hwnd,
            'title': title,
            'exe': exe_name,
            'pid': pid,
            'is_browser': any(browser in exe_name for browser in BROWSER_PROCESSES),
            'is_console': any(console in exe_name for console in CONSOLE_PROCESSES)
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError):
        return {
            'hwnd': hwnd,
            'title': title,
            'exe': 'unknown',
            'pid': pid,
            'is_browser': False,
            'is_console': False
        }

def is_text_valid(text):
    """Checks if the text is valid for processing."""
    if not text:
        return False
    stripped = text.strip()
    if not stripped:
        return False
    # Exclude texts that are only whitespace or non-printable characters
    return len(stripped) >= 2

# --- AI PROCESSING WITH CANCELLATION ---
def process_with_ai(text):
    """Processes the text with AI with cancellation capability."""
    global ai_cancel_requested
    ai_cancel_requested = False  # Reset cancellation flag
    
    logger.info(f"🧠 Sending to {MODEL_NAME}...")
    logger.debug(f"⏳ Starting AI processing (text: {len(text)} characters)...")
    
    try:
        # Limit text length to avoid timeouts
        if len(text) > MAX_CHARS:
            logger.warning(f"⚠️ Text too long ({len(text)} > {MAX_CHARS} characters). Truncated.")
            text = text[:MAX_CHARS] + "... [truncated]"
        
        start_time = time.time()
        
        # Run processing in a separate thread to allow cancellation
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(ollama.chat, model=MODEL_NAME, messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': text},
            ])
            
            while not future.done():
                if ai_cancel_requested:
                    logger.warning("🛑 AI PROCESSING CANCELLED BY USER!")
                    executor.shutdown(wait=False, cancel_futures=True)
                    play_cancel_beep()
                    return "PROCESSING CANCELLED"
                
                time.sleep(0.2)  # Reduced for more responsiveness without increasing CPU usage
                
            response = future.result(timeout=AI_TIMEOUT)
        
        elapsed = time.time() - start_time
        logger.info(f"⚡ AI processed in {elapsed:.1f} seconds")
        
        if ai_cancel_requested:
            logger.warning("🛑 Processing completed but cancellation was requested. Ignoring result.")
            play_cancel_beep()
            return "PROCESSING CANCELLED"
        
        result = response['message']['content'].strip().replace("`", "")
        return result
    except FutureTimeoutError:
        logger.error(f"❌ AI processing timeout ({AI_TIMEOUT} seconds)")
        play_error_beep()
        return f"ERROR: Timeout after {AI_TIMEOUT} seconds"
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        play_error_beep()
        return f"ERROR: {e}"

# --- SIMPLIFIED MAIN FUNCTION ---
def trigger_synthesis():
    """SIMPLIFIED VERSION: ONLY READS FROM CLIPBOARD WITHOUT SIMULATING COPY"""
    print("-" * 42)
    logger.info(f"🔥 Hotkey '{args.hotkey}' detected!")
    
    # 1. Save the original clipboard state
    original_clipboard = pyperclip.paste()
    logger.debug(f"📋 Original clipboard saved ({len(original_clipboard)} characters)")
    
    try:
        # 2. Read DIRECTLY from the clipboard (no key simulation!)
        selected_text = pyperclip.paste()
        
        # 3. Check if the text is valid
        if not is_text_valid(selected_text):
            logger.error("❌ NO VALID TEXT IN CLIPBOARD!")
            logger.error("💡 INSTRUCTION: Before pressing Ctrl+Alt+S, MANUALLY COPY the text with Ctrl+C")
            play_error_beep()
            return
        
        # 4. Detect the active window for logging only
        win_info = get_active_window_info()
        if win_info:
            logger.info(f"🖥️ Active app: '{win_info['title']}' ({win_info['exe']})")
        logger.info(f"📋 Text from clipboard ({len(selected_text)} characters): '{selected_text[:70]}...'")
        
        # 5. Process with AI (NO KEYBOARD LOCK)
        synt_e_command = process_with_ai(selected_text)
        
        # If processing was cancelled, exit without pasting
        if synt_e_command == "PROCESSING CANCELLED":
            logger.info("⏭️ Skipping paste phase due to cancelled processing")
            return
        
        # 6. Paste the result (KEYBOARD LOCK ONLY FOR THIS PHASE)
        with operation_lock:
            keyboard_blocked = True
            try:
                global last_synthesis
                last_synthesis['original'] = selected_text
                last_synthesis['timestamp'] = time.time()
                
                if args.append:
                    final_text = selected_text + f"\n--- Synt-E: {synt_e_command}"
                    pyperclip.copy(final_text)
                    keyboard.send('ctrl+v')
                    logger.info("✅ Synthesis added to the original text.")
                else:
                    pyperclip.copy(synt_e_command)
                    keyboard.send('ctrl+v')
                    logger.info(f"✅ Pasted result: '{synt_e_command[:50]}...'")
                
                play_success_beep()
                
                # Restore original clipboard after a short delay
                threading.Timer(1.0, lambda: pyperclip.copy(original_clipboard)).start()
            finally:
                keyboard_blocked = False
                logger.debug("🔓 Keyboard unlocked after paste")
                
    except Exception as e:
        logger.exception(f"🚨 Critical error during processing: {e}")
        play_error_beep()
    finally:
        logger.debug("🔧 Cleanup completed for this operation")

@keyboard_operation()
def trigger_undo():
    global last_synthesis
    if time.time() - last_synthesis['timestamp'] < 10:
        logger.info("↩️ UNDO activated! Restoring original text...")
        pyperclip.copy(last_synthesis['original'])
        keyboard.send('ctrl+v')
        last_synthesis = {"original": None, "timestamp": 0}
        play_success_beep()
    else:
        logger.warning("❌ Undo not available (older than 10 seconds)")
        play_error_beep()

# --- RESOURCE MANAGEMENT ---
def setup_emergency_hotkeys():
    """Configures the emergency hotkey to restore the keyboard."""
    try:
        keyboard.add_hotkey(EMERGENCY_HOTKEY, lambda: emergency_keyboard_reset(), 
                          suppress=True, timeout=1.0)
        keyboard.add_hotkey(CANCEL_AI_HOTKEY, lambda: cancel_ai_operation(),
                          suppress=True, timeout=1.0)
        logger.info(f"🚨 EMERGENCY HOTKEY ACTIVE: Press '{EMERGENCY_HOTKEY}' if the keyboard gets stuck!")
        logger.info(f"🛑 AI CANCELLATION HOTKEY: Press '{CANCEL_AI_HOTKEY}' to stop LLM processing")
    except Exception as e:
        logger.error(f"❌ Error setting up emergency hotkeys: {e}")

def cleanup_on_exit():
    """Cleans up all resources when the program exits."""
    logger.info("🧹 Cleaning up resources...")
    try:
        # 1. Remove all hotkeys
        keyboard.unhook_all()
        keyboard.clear_all_hotkeys()
        
        # 2. Reset the keyboard
        emergency_keyboard_reset()
        
        logger.info("✅ Resources cleaned up successfully")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")

def signal_handler(sig, frame):
    logger.info("\n⏹️  Interrupt received. Cleaning up...")
    cleanup_on_exit()
    sys.exit(0)

# --- MAIN PROGRAM ---
def main():
    # Signal handling for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 1. Setup emergency hotkeys first
    setup_emergency_hotkeys()
    
    # 2. Check dependencies
    try:
        import win32gui
        import win32process
        import psutil
        import winsound
    except ImportError as e:
        logger.error(f"❌ Missing Windows packages: {e}")
        logger.error("Install with: pip install pywin32 psutil keyboard pyperclip ollama")
        cleanup_on_exit()
        sys.exit(1)
    
    # 3. Check Ollama
    try:
        ollama.list()
        logger.info("✅ Ollama is active and reachable.")
    except Exception as e:
        logger.error(f"❌ Ollama not reachable: {e}. Start Ollama before continuing.")
        cleanup_on_exit()
        sys.exit(1)
    
    # 4. Display user interface
    print(f"\n{'=' * 70}")
    print(f"   SYNT-E HOTKEY TOOL v16.0 (With AI Cancellation)")
    print(f"   ✓ 100% SAFE METHOD: No more automatic copying!")
    print(f"   ✓ FUNCTIONAL BEEPS on Windows 11")
    print(f"   ✓ ABILITY TO INTERRUPT LLM processing (Ctrl+Alt+C)")
    print(f"{ '=' * 70}\n")
    print(f"🔧 CONFIGURATION:")
    print(f"   • Synthesize: '{args.hotkey}'")
    print(f"   • Undo: '{args.undo_hotkey}' (within 10s)")
    print(f"   • Interrupt LLM: '{CANCEL_AI_HOTKEY}' (during processing)")
    print(f"   • Keyboard Emergency: '{EMERGENCY_HOTKEY}'")
    print(f"   • Mode: {'Append' if args.append else 'Replace'}")
    print(f"   • Model: '{MODEL_NAME}'")
    print(f"   • Text Limit: {MAX_CHARS} characters")
    print(f"   • AI Timeout: {AI_TIMEOUT} seconds\n")
    print(f"✅ USAGE METHOD (3 SIMPLE STEPS):")
    print(f"   1. SELECT the text in your application")
    print(f"   2. PRESS CTRL+C to copy it MANUALLY")
    print(f"   3. PRESS CTRL+ALT+S for the synthesis\n")
    print(f"🛑 TO INTERRUPT A LONG PROCESS:")
    print(f"   - During processing, press '{CANCEL_AI_HOTKEY}'")
    print(f"   - You will hear a beep and the operation will be cancelled\n")
    print(f"⏹️  CLOSE THIS WINDOW TO TERMINATE THE PROGRAM")
    print(f"{ '=' * 70}\n")

    # 5. Register main hotkeys
    try:
        keyboard.add_hotkey(args.hotkey, trigger_synthesis, suppress=False)
        keyboard.add_hotkey(args.undo_hotkey, trigger_undo, suppress=False, timeout=1.0)
        logger.info("✅ Hotkeys registered successfully")
    except Exception as e:
        logger.error(f"❌ Error registering hotkeys: {e}")
        cleanup_on_exit()
        sys.exit(1)
    
    # 6. Start the main loop
    logger.info("✅ Program started successfully. LISTENING...")
    print("🔊 Listening for commands... (press the hotkeys to activate)\n")
    
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        logger.info("\n⏹️  Keyboard interrupt. Cleaning up...")
    except Exception as e:
        logger.exception(f"🚨 Unexpected error in main loop: {e}")
    finally:
        cleanup_on_exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"❌ Fatal error on startup: {e}")
        cleanup_on_exit()
        sys.exit(1)
