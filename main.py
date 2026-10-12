import json
from pathlib import Path

import ollama

MODEL = "llama3.2:3b"
MEMORY_FILE = Path(__file__).with_name("memory.json")

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are Jarvis, Harsh's personal AI assistant. "
        "Be helpful, clear, friendly, and honest. "
        "Use the conversation history when it is relevant."
    ),
}


def load_history():
    if not MEMORY_FILE.exists():
        return []

    try:
        history = json.loads(
            MEMORY_FILE.read_text(encoding="utf-8")
        )

        if not isinstance(history, list):
            raise ValueError("Memory must be a list.")

        return [
            message
            for message in history
            if isinstance(message, dict)
            and message.get("role") in {"user", "assistant"}
            and isinstance(message.get("content"), str)
        ]

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Could not load memory: {error}")
        print("Starting with an empty conversation.")
        return []


def save_history(messages):
    history = messages[1:]  # Exclude the system instructions.
    temporary_file = MEMORY_FILE.with_suffix(".tmp")

    temporary_file.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(MEMORY_FILE)


messages = [SYSTEM_MESSAGE] + load_history()

print("🤖 Jarvis is online!")
print(f"🧠 Loaded {len(messages) - 1} previous messages.")
print("Type 'exit' to quit or 'clear' to erase conversation memory.\n")

while True:
    try:
        user_text = input("Harsh: ").strip()

        if user_text.lower() in {"exit", "quit"}:
            print("Jarvis: Signing off, Harsh!")
            break

        if user_text.lower() == "clear":
            messages = [SYSTEM_MESSAGE]
            if MEMORY_FILE.exists():
                MEMORY_FILE.unlink()
            print("Jarvis: Conversation memory cleared.\n")
            continue

        if not user_text:
            continue

        messages.append({
            "role": "user",
            "content": user_text,
        })

        try:
            response = ollama.chat(
                model=MODEL,
                messages=messages,
            )
        except Exception as error:
            messages.pop()
            print(f"\nJarvis couldn't respond: {error}\n")
            continue

        answer = response["message"]["content"]

        messages.append({
            "role": "assistant",
            "content": answer,
        })

        save_history(messages)
        print(f"\nJarvis: {answer}\n")

    except KeyboardInterrupt:
        print("\nJarvis: Goodbye, Harsh!")
        break
    except OSError as error:
        print(f"\nMemory file error: {error}\n")
