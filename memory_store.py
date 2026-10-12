import json
from pathlib import Path

MEMORY_FILE = Path(__file__).with_name("facts.json")


def load_facts():
    """Load saved facts from local storage."""
    if not MEMORY_FILE.exists():
        return []

    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [
                item for item in data
                if isinstance(item, dict)
                and isinstance(item.get("fact"), str)
            ]
    except (OSError, json.JSONDecodeError):
        print("Warning: Could not read facts.json.")

    return []


def save_facts(facts):
    """Save facts safely to local storage."""
    temporary_file = MEMORY_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(facts, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(MEMORY_FILE)


def remember(fact):
    """Store a fact unless it is already saved."""
    fact = fact.strip()

    if not fact:
        return "Please provide a fact to remember."

    facts = load_facts()

    if any(item["fact"].casefold() == fact.casefold() for item in facts):
        return "I already remember that."

    facts.append({"fact": fact})
    save_facts(facts)
    return f"I'll remember: {fact}"


def list_facts():
    """Return all saved facts."""
    facts = load_facts()

    if not facts:
        return "I don't have any saved facts yet."

    return "\n".join(
        f"{index}. {item['fact']}"
        for index, item in enumerate(facts, start=1)
    )


def forget_fact(number):
    """Delete one fact by its displayed number."""
    facts = load_facts()

    if number < 1 or number > len(facts):
        return "That fact number doesn't exist."

    removed = facts.pop(number - 1)
    save_facts(facts)
    return f"I forgot: {removed['fact']}"


def clear_facts():
    """Delete all saved facts."""
    save_facts([])
    return "All saved facts have been cleared."
