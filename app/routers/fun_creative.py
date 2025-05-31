# app/routers/fun_creative.py
import random
import json
import string
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
import requests  # For Chuck Norris API

router = APIRouter()

# --- Helper to load data ---
DATA_PATH = Path(__file__).parent.parent / "data"


def load_json_data(filename: str):
    file_path = DATA_PATH / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                print(f"Warning: Data file {filename} at {file_path} is empty.")
                return []
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: Data file {filename} not found at {file_path}.")
        return []
    except json.JSONDecodeError as e:
        print(f"Warning: Could not decode JSON from {filename} at {file_path}. Error: {e}")
        return []


famous_quotes_data = load_json_data("famous_quotes.json")
bad_jokes_data = load_json_data("bad_jokes.json")
cat_facts_data = load_json_data("cat_facts.json")  # Load cat facts
dog_facts_data = load_json_data("dog_facts.json")  # Load dog facts


# --- Models for new endpoints ---
# (No specific models needed for these GET requests as params are simple queries)

# --- Endpoints (Existing) ---
@router.get("/quote/famous")
async def get_famous_quote():
    if not famous_quotes_data:
        raise HTTPException(status_code=503, detail="Famous quotes data is unavailable.")
    return random.choice(famous_quotes_data)


@router.get("/quote/kanye")
async def get_kanye_quote():
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
    emojis = ["😀", "😂", "😍", "🥳", "🚀", "🎉", "🌟", "💡", "💻", "🤔", "👍", "💯", "🐱", "🐶", "🍕", "❤️"]
    return {"emoji": random.choice(emojis)}


@router.get("/random/yes-no")
async def random_yes_no():
    answers = ["Yes", "No", "Maybe", "Definitely", "Not a chance", "Ask again later", "Signs point to yes",
               "Outlook not so good"]
    return {"answer": random.choice(answers)}


@router.get("/random/name")
async def random_name_generator(
        gender: str = Query(None,
                            description="Optional: 'male', 'female', or leave blank for any. Supported: male, female, any")
):
    first_names_male = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Charles",
                        "Thomas"]
    first_names_female = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah",
                          "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
                  "Martinez"]

    first_name = ""
    if gender and gender.lower() == "male":
        first_name = random.choice(first_names_male)
    elif gender and gender.lower() == "female":
        first_name = random.choice(first_names_female)
    elif gender is None or gender.lower() == "any":
        first_name = random.choice(first_names_male + first_names_female)
    else:
        raise HTTPException(status_code=400,
                            detail="Invalid gender. Supported: 'male', 'female', or leave blank/ 'any'.")

    last_name = random.choice(last_names)
    return {"first_name": first_name, "last_name": last_name, "full_name": f"{first_name} {last_name}"}


@router.get("/magic-8-ball")
async def magic_8_ball(question: str = Query(..., min_length=1, description="Your yes/no question")):
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
async def dice_roller(
        sides: int = Query(6, ge=2, le=1000, description="Number of sides on the die")):  # Increased max sides
    return {"sides": sides, "roll": random.randint(1, sides)}


# --- New Endpoints (TODOs Completed & More) ---

@router.get("/fact/cat")
async def get_cat_fact():
    if not cat_facts_data:
        raise HTTPException(status_code=503, detail="Cat facts data is unavailable or empty.")
    return {"fact": random.choice(cat_facts_data)}


@router.get("/fact/dog")
async def get_dog_fact():
    if not dog_facts_data:
        raise HTTPException(status_code=503, detail="Dog facts data is unavailable or empty.")
    return {"fact": random.choice(dog_facts_data)}


@router.get("/random/password")
async def random_password_generator(
        length: int = Query(12, ge=8, le=128, description="Length of the password (8-128)"),
        include_uppercase: bool = Query(True, description="Include uppercase letters"),
        include_digits: bool = Query(True, description="Include digits"),
        include_symbols: bool = Query(True, description="Include symbols")
):
    character_pool = string.ascii_lowercase
    if include_uppercase:
        character_pool += string.ascii_uppercase
    if include_digits:
        character_pool += string.digits
    if include_symbols:
        character_pool += string.punctuation

    if not character_pool:  # Should not happen with defaults, but good for robustness
        raise HTTPException(status_code=400,
                            detail="Cannot generate password with an empty character pool. Select at least one character type.")

    password = "".join(random.choice(character_pool) for _ in range(length))
    return {"length": length, "password": password,
            "criteria": {"uppercase": include_uppercase, "digits": include_digits, "symbols": include_symbols}}


@router.get("/joke/chuck-norris")
async def get_chuck_norris_joke(category: str = Query(None,
                                                      description="Optional category for the joke (e.g., dev, movie, food). See /joke/chuck-norris/categories for list.")):
    base_url = "https://api.chucknorris.io/jokes/random"
    params = {}
    if category:
        params["category"] = category

    try:
        response = requests.get(base_url, params=params, timeout=5)  # Added timeout
        response.raise_for_status()  # Raise an exception for HTTP errors
        joke_data = response.json()
        return {"joke": joke_data.get("value"), "id": joke_data.get("id"),
                "categories": joke_data.get("categories", [])}
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Request to Chuck Norris API timed out.")
    except requests.RequestException as e:
        # Check for specific error from API if category is invalid
        if e.response is not None and e.response.status_code == 404 and "No jokes found for category" in e.response.text:
            raise HTTPException(status_code=404,
                                detail=f"No jokes found for category '{category}'. Try /fun/joke/chuck-norris/categories for available ones.")
        raise HTTPException(status_code=503, detail=f"Could not fetch joke from Chuck Norris API: {str(e)}")


@router.get("/joke/chuck-norris/categories")
async def get_chuck_norris_joke_categories():
    try:
        response = requests.get("https://api.chucknorris.io/jokes/categories", timeout=5)
        response.raise_for_status()
        categories = response.json()
        return {"categories": categories}
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Request to Chuck Norris API timed out.")
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Could not fetch categories from Chuck Norris API: {str(e)}")