import json
from pathlib import Path

import ollama
from memory_store import remember, list_facts, forget_fact, load_facts

MODEL = "llama3.2:3b"
MEMORY_FILE = Path(__file__).with_name("memory.json")

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are Jarvis, Harsh's personal AI assistant. "
        "Be helpful, clear, friendly, and honest. "
        "Use conversation history and provided saved facts when relevant. "
        "Do not claim to remember facts that are not provided to you."
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
            raise ValueError("Conversation history must be a list.")

        return [
            message
            for message in history
            if isinstance(message, dict)
            and message.get("role") in {"user", "assistant"}
            and isinstance(message.get("content"), str)
        ]

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Could not load history: {error}")
        print("Starting with an empty conversation.")
        return []


def save_history(messages):
    history = messages[1:]
    temporary_file = MEMORY_FILE.with_suffix(".tmp")

    temporary_file.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(MEMORY_FILE)


messages = [SYSTEM_MESSAGE] + load_history()

print("🤖 Jarvis is online!")
print(f"🧠 Loaded {len(messages) - 1} previous messages.")
print("Commands:")
print("  remember: <fact>  Save an important fact")
print("  memory            List saved facts")
print("  forget: <number>  Delete a saved fact")
print("  clear             Clear conversation history")
print("  exit              Quit Jarvis\n")

while True:
    try:
        user_text = input("Harsh: ").strip()

        if user_text.lower() in {"exit", "quit"}:
            print("Jarvis: Signing off, Harsh!")
            break

        if not user_text:
            continue

        command = user_text.lower()

        if command == "memory":
            print(f"\nJarvis: Saved facts:\n{list_facts()}\n")
            continue

        if command.startswith("remember:"):
            fact = user_text[len("remember:"):].strip()
            print(f"\nJarvis: {remember(fact)}\n")
            continue

        if command.startswith("forget:"):
            number_text = user_text[len("forget:"):].strip()

            try:
                number = int(number_text)
                print(f"\nJarvis: {forget_fact(number)}\n")
            except ValueError:
                print("\nJarvis: Use 'forget: 1' with a valid fact number.\n")
            continue

        if command == "clear":
            messages = [SYSTEM_MESSAGE]
            if MEMORY_FILE.exists():
                MEMORY_FILE.unlink()
            print(
                "\nJarvis: Conversation history cleared. "
                "Your saved facts are unchanged.\n"
            )
            continue

        messages.append({
            "role": "user",
            "content": user_text,
        })

        chat_messages = [SYSTEM_MESSAGE]
        facts = load_facts()

        if facts:
            facts_text = "\n".join(
                f"- {item['fact']}" for item in facts
            )
            chat_messages.append({
                "role": "system",
                "content": (
                    "These are facts explicitly saved by the user. "
                    "Use them when relevant:\n" + facts_text
                ),
            })

        chat_messages.extend(messages[1:])

        try:
            response = ollama.chat(
                model=MODEL,
                messages=chat_messages,
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

        try:
            save_history(messages)
        except OSError as error:
            print(f"Warning: Could not save conversation history: {error}")

        print(f"\nJarvis: {answer}\n")

    except KeyboardInterrupt:
        print("\nJarvis: Goodbye, Harsh!")
        break
    except OSError as error:
        print(f"\nFile error: {error}\n")
