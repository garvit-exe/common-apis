# app/routers/text_manipulation.py
import re
import json
import csv
import io
import random
import hashlib
import base64
import uuid as uuid_generator_lib  # Alias to avoid conflict
from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel, Field
import markdown as md_parser

router = APIRouter()


# --- Models (Existing and New) ---
class TextRequest(BaseModel):
    text: str = Field(..., example="Hello World Example")


class SlugRequest(BaseModel):
    text: str = Field(..., example="My Awesome Title!")


class JsonPrettyPrintRequest(BaseModel):
    json_string: str = Field(..., example='{"name":"John Doe","age":30,"city":"New York"}')


class CsvToJsonRequest(BaseModel):
    csv_data: str = Field(..., example="name,age\nAlice,30\nBob,24")


class MarkdownToHtmlRequest(BaseModel):
    markdown_text: str = Field(..., example="# Hello\nThis is **markdown**.")


class UnitConversionRequest(BaseModel):
    value: float = Field(..., example=10.0)
    from_unit: str = Field(..., example="celsius")
    to_unit: str = Field(..., example="fahrenheit")
    category: str = Field(..., example="temperature", description="Supported: temperature, length, weight")


class CalculatorRequest(BaseModel):
    operand1: float = Field(..., example=10)
    operand2: float = Field(..., example=5)
    operation: str = Field(..., example="add", description="Supported: add, subtract, multiply, divide")


class HashRequest(BaseModel):
    text: str = Field(..., example="my secret data")
    algorithm: str = Field("sha256", example="sha256", description="Supported: md5, sha1, sha256, sha512")


class Base64Request(BaseModel):
    text: str = Field(..., example="Hello FastAPI!")
    action: str = Field("encode", example="encode", description="Supported: encode, decode")


# --- Helper Functions (Existing and New) ---
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


# --- Endpoints (Existing) ---
@router.post("/case-converter")
async def case_converter(
        data: TextRequest,
        to_case: str = Query(
            "uppercase",
            description="Target case: uppercase, lowercase, titlecase, camelcase, snakecase, kebabcase"
        )
):
    text = data.text
    if to_case == "uppercase":
        return {"original": text, "converted": text.upper()}
    elif to_case == "lowercase":
        return {"original": text, "converted": text.lower()}
    elif to_case == "titlecase":
        return {"original": text, "converted": text.title()}
    elif to_case == "camelcase":
        words = re.split(r'[\s_-]+', text)
        # Handle empty string or string with only delimiters
        if not any(words):
            return {"original": text, "converted": ""}
        first_word = words[0].lower()
        other_words = "".join(word.capitalize() for word in words[1:] if word)
        return {"original": text, "converted": first_word + other_words}
    elif to_case == "snakecase":
        return {"original": text, "converted": slugify(text).replace('-', '_')}
    elif to_case == "kebabcase":
        return {"original": text, "converted": slugify(text)}
    else:
        raise HTTPException(status_code=400, detail="Invalid 'to_case' parameter.")


@router.post("/string-reverser")
async def string_reverser(data: TextRequest):
    return {"original": data.text, "reversed": data.text[::-1]}


@router.post("/word-counter")
async def word_counter(data: TextRequest):
    text = data.text
    words = len(text.split()) if text else 0  # Handle empty string
    characters = len(text)
    characters_no_space = len(text.replace(" ", ""))
    lines = len(text.splitlines()) if text else 0  # Handle empty string
    return {
        "text": text,
        "word_count": words,
        "character_count_with_spaces": characters,
        "character_count_without_spaces": characters_no_space,
        "line_count": lines,
    }


@router.post("/slug-generator")
async def slug_generator(data: SlugRequest):
    return {"original": data.text, "slug": slugify(data.text)}


@router.get("/lorem-ipsum")
async def lorem_ipsum_generator(
        type: str = Query("paragraphs", description="Type: paragraphs, sentences, words"),
        count: int = Query(3, ge=1, le=100)
):
    lorem_base = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    words_list = lorem_base.split()
    sentences_list = [s.strip() + "." for s in lorem_base.split('.') if s.strip()]

    if type == "words":
        result_words = []
        for _ in range(count):
            result_words.append(random.choice(words_list))
        result = " ".join(result_words)
    elif type == "sentences":
        result_sentences = []
        for _ in range(count):
            result_sentences.append(random.choice(sentences_list))
        result = " ".join(result_sentences)
    elif type == "paragraphs":
        paras = []
        for _ in range(count):
            num_sentences = random.randint(3, 7)  # Random length paragraphs
            para_sentences = random.choices(sentences_list, k=num_sentences)
            paras.append(" ".join(para_sentences))
        result = "\n\n".join(paras)
    else:
        raise HTTPException(status_code=400, detail="Invalid 'type'. Supported: paragraphs, sentences, words")
    return {"type": type, "count": count, "text": result}


@router.post("/json-pretty-printer")
async def json_pretty_printer(data: JsonPrettyPrintRequest):
    try:
        parsed_json = json.loads(data.json_string)
        pretty_json = json.dumps(parsed_json, indent=4, sort_keys=True)
        return {"original": data.json_string, "pretty": pretty_json}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON string provided.")


@router.post("/csv-to-json")
async def csv_to_json_converter(data: CsvToJsonRequest):
    csv_file = io.StringIO(data.csv_data)
    try:
        reader = csv.DictReader(csv_file)
        json_data = json.dumps(list(reader))
        return {"csv": data.csv_data, "json": json.loads(json_data)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting CSV: {str(e)}")


@router.post("/markdown-to-html")
async def markdown_to_html_converter(data: MarkdownToHtmlRequest):
    html_output = md_parser.markdown(data.markdown_text)
    return {"markdown": data.markdown_text, "html": html_output}


# --- New Endpoints (TODOs Completed & More) ---

@router.post("/unit-converter")
async def unit_converter(req_data: UnitConversionRequest):
    value = req_data.value
    from_u = req_data.from_unit.lower()
    to_u = req_data.to_unit.lower()
    category = req_data.category.lower()
    converted_value = None

    conversions = {
        "temperature": {
            "celsius_to_fahrenheit": lambda c: (c * 9 / 5) + 32,
            "fahrenheit_to_celsius": lambda f: (f - 32) * 5 / 9,
            "celsius_to_kelvin": lambda c: c + 273.15,
            "kelvin_to_celsius": lambda k: k - 273.15,
            "fahrenheit_to_kelvin": lambda f: (f - 32) * 5 / 9 + 273.15,
            "kelvin_to_fahrenheit": lambda k: (k - 273.15) * 9 / 5 + 32,
        },
        "length": {
            "meters_to_feet": lambda m: m * 3.28084,
            "feet_to_meters": lambda ft: ft / 3.28084,
            "kilometers_to_miles": lambda km: km * 0.621371,
            "miles_to_kilometers": lambda mi: mi / 0.621371,
            "inches_to_cm": lambda i: i * 2.54,
            "cm_to_inches": lambda cm: cm / 2.54,
        },
        "weight": {
            "kg_to_lbs": lambda kg: kg * 2.20462,
            "lbs_to_kg": lambda lbs: lbs / 2.20462,
            "grams_to_ounces": lambda g: g * 0.035274,
            "ounces_to_grams": lambda oz: oz / 0.035274,
        }
    }

    if category not in conversions:
        raise HTTPException(status_code=400,
                            detail=f"Unsupported category: {category}. Supported: {list(conversions.keys())}")

    conversion_key = f"{from_u}_to_{to_u}"
    if from_u == to_u:
        converted_value = value
    elif conversion_key in conversions[category]:
        converted_value = conversions[category][conversion_key](value)
    else:
        raise HTTPException(status_code=400,
                            detail=f"Unsupported conversion from {from_u} to {to_u} in category {category}.")

    return {
        "original_value": value,
        "original_unit": from_u,
        "category": category,
        "converted_value": round(converted_value, 4) if converted_value is not None else None,  # Round for precision
        "converted_unit": to_u
    }


@router.post("/calculator")
async def basic_calculator(req_data: CalculatorRequest):
    op1 = req_data.operand1
    op2 = req_data.operand2
    operation = req_data.operation.lower()
    result = None

    if operation == "add":
        result = op1 + op2
    elif operation == "subtract":
        result = op1 - op2
    elif operation == "multiply":
        result = op1 * op2
    elif operation == "divide":
        if op2 == 0:
            raise HTTPException(status_code=400, detail="Cannot divide by zero.")
        result = op1 / op2
    else:
        raise HTTPException(status_code=400, detail="Invalid operation. Supported: add, subtract, multiply, divide.")

    return {"operand1": op1, "operand2": op2, "operation": operation, "result": result}


@router.get("/random-number")
async def random_number_generator(
        min_val: int = Query(0, description="Minimum value (inclusive)"),
        max_val: int = Query(100, description="Maximum value (inclusive)"),
        type: str = Query("integer", description="Type of number: 'integer' or 'float'")
):
    if min_val > max_val:
        raise HTTPException(status_code=400, detail="min_val cannot be greater than max_val.")

    rand_val = None
    if type == "integer":
        rand_val = random.randint(min_val, max_val)
    elif type == "float":
        rand_val = random.uniform(min_val, max_val)
    else:
        raise HTTPException(status_code=400, detail="Invalid type. Supported: 'integer', 'float'.")

    return {"min": min_val, "max": max_val, "type": type, "random_value": rand_val}


@router.post("/hash")
async def hash_text(req_data: HashRequest):
    text_to_hash = req_data.text.encode('utf-8')  # hashlib works with bytes
    algo = req_data.algorithm.lower()
    hashed_value = ""

    if algo == "md5":
        hashed_value = hashlib.md5(text_to_hash).hexdigest()
    elif algo == "sha1":
        hashed_value = hashlib.sha1(text_to_hash).hexdigest()
    elif algo == "sha256":
        hashed_value = hashlib.sha256(text_to_hash).hexdigest()
    elif algo == "sha512":
        hashed_value = hashlib.sha512(text_to_hash).hexdigest()
    else:
        raise HTTPException(status_code=400, detail="Unsupported algorithm. Supported: md5, sha1, sha256, sha512.")

    return {"original": req_data.text, "algorithm": algo, "hashed_value": hashed_value}


@router.post("/base64")
async def base64_converter(req_data: Base64Request):
    text = req_data.text
    action = req_data.action.lower()
    result = ""

    try:
        if action == "encode":
            result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        elif action == "decode":
            result = base64.b64decode(text.encode('utf-8')).decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Supported: encode, decode.")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400,
                            detail="Error decoding text. Ensure it's valid UTF-8 or the Base64 string is correct.")
    except base64.binascii.Error:  # Catches incorrect padding or invalid base64 characters
        raise HTTPException(status_code=400, detail="Invalid Base64 string for decoding.")

    return {"original": text, "action": action, "result": result}


@router.get("/uuid")
async def generate_uuid(version: int = Query(4,
                                             description="UUID version to generate. Currently only v4 is fully supported without extra params.")):
    if version == 4:
        new_uuid = str(uuid_generator_lib.uuid4())
    # elif version == 1:
    #     new_uuid = str(uuid_generator_lib.uuid1()) # UUID1 can reveal MAC address, consider implications
    else:
        raise HTTPException(status_code=400,
                            detail="Unsupported UUID version. Currently supports v4 reliably. v1, v3, v5 might require more parameters or have privacy implications.")
    return {"uuid_version": f"v{version}", "uuid": new_uuid}