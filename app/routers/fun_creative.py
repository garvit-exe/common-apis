# app/routers/fun_creative.py
import random
import json
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException

router = APIRouter()

# --- Helper to load data ---
DATA_PATH = Path(__file__).parent.parent / "data"  # app/data/


def load_json_data(filename: str):
    try:
        with open(DATA_PATH / filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Data file {filename} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {filename}.")
        return []


famous_quotes_data = load_json_data("famous_quotes.json")
bad_jokes_data = load_json_data("bad_jokes.json")


# Add more data loading here: cat_facts, dog_facts etc.

# --- Endpoints ---
@router.get("/quote/famous")
async def get_famous_quote():
    if not famous_quotes_data:
        raise HTTPException(status_code=503, detail="Famous quotes data is unavailable.")
    return random.choice(famous_quotes_data)


@router.get("/quote/kanye")
async def get_kanye_quote():
    # For simplicity, embedding a few. For more, use a JSON file or external API.
    kanye_quotes = [
        "I am God's vessel. But my greatest pain in life is that I will never be able to see myself perform live.",
        "I still think I am the greatest.",
        "I feel like I'm too busy writing history to read it.",
        "Sometimes people write novels and they just be so wordy and so self-absorbed."
    ]
    return {"quote": random.choice(kanye_quotes), "source": "Kanye West (Simulated)"}


@router.get("/joke/bad")
async def get_bad_joke():
    if not bad_jokes_data:
        raise HTTPException(status_code=503, detail="Bad jokes data is unavailable.")
    return {"joke": random.choice(bad_jokes_data)}


@router.get("/random/color-hex")
async def random_hex_color():
    hex_color = f"#{random.randint(0, 0xFFFFFF):06x}"
    return {"hex_color": hex_color.upper()}


@router.get("/random/emoji")
async def random_emoji():
    # A small sample of emojis. You can expand this list greatly.
    emojis = ["😀", "😂", "😍", "🥳", "🚀", "🎉", "🌟", "💡", "💻", "🤔", "👍", "💯"]
    return {"emoji": random.choice(emojis)}


@router.get("/random/yes-no")
async def random_yes_no():
    answers = ["Yes", "No", "Maybe", "Definitely", "Not a chance", "Ask again later"]
    return {"answer": random.choice(answers)}


@router.get("/random/name")
async def random_name_generator(
        gender: str = Query(None, description="Optional: 'male', 'female', or leave blank for any")
):
    first_names_male = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph"]
    first_names_female = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]

    if gender == "male":
        first_name = random.choice(first_names_male)
    elif gender == "female":
        first_name = random.choice(first_names_female)
    else:
        first_name = random.choice(first_names_male + first_names_female)

    last_name = random.choice(last_names)
    return {"first_name": first_name, "last_name": last_name, "full_name": f"{first_name} {last_name}"}


@router.get("/magic-8-ball")
async def magic_8_ball(question: str = Query(..., description="Your yes/no question")):
    answers = [
        "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes – definitely.",
        "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
        "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
        "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]
    return {"question": question, "answer": random.choice(answers)}


@router.get("/coin-flipper")
async def coin_flipper():
    return {"result": random.choice(["Heads", "Tails"])}


@router.get("/dice-roller")
async def dice_roller(sides: int = Query(6, ge=2, le=100, description="Number of sides on the die")):
    return {"sides": sides, "roll": random.randint(1, sides)}

# TODO: Cat/Dog fact (load from JSON), other fun APIs