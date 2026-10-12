
import ollama

MODEL = "llama3.2:3b"

messages = [
    {
        "role": "system",
        "content": (
            "You are Jarvis, Harsh's personal AI assistant. "
            "Be helpful, clear, friendly, and honest."
        ),
    }
]

print("🤖 Jarvis is online!")
print("Type 'exit' to quit.\n")

while True:
    try:
        user_text = input("Harsh: ").strip()

        if user_text.lower() in {"exit", "quit"}:
            print("Jarvis: Signing off, Harsh!")
            break

        if not user_text:
            continue

        messages.append({
            "role": "user",
            "content": user_text,
        })

        response = ollama.chat(
            model=MODEL,
            messages=messages,
        )

        answer = response["message"]["content"]
        messages.append({
            "role": "assistant",
            "content": answer,
        })

        print(f"\nJarvis: {answer}\n")

    except KeyboardInterrupt:
        print("\nJarvis: Goodbye, Harsh!")
        break

    except Exception as error:
        print(f"\nError: {error}\n")
