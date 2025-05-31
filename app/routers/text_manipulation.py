# app/routers/text_manipulation.py
import re
import json
import csv
import io
from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel, Field
import markdown as md_parser # Renamed to avoid conflict with FastAPI's markdown

router = APIRouter()

# --- Models ---
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

# --- Helper Functions ---
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text) # Remove special chars except space and hyphen
    text = re.sub(r'\s+', '-', text)       # Replace spaces with hyphens
    text = re.sub(r'-+', '-', text)        # Replace multiple hyphens with single
    return text.strip('-')

# --- Endpoints ---
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
        return {"original": text, "converted": words[0].lower() + "".join(word.capitalize() for word in words[1:])}
    elif to_case == "snakecase":
        return {"original": text, "converted": slugify(text).replace('-', '_')}
    elif to_case == "kebabcase":
        return {"original": text, "converted": slugify(text)}
    else:
        raise HTTPException(status_code=400, detail="Invalid 'to_case' parameter. Supported: uppercase, lowercase, titlecase, camelcase, snakecase, kebabcase")

@router.post("/string-reverser")
async def string_reverser(data: TextRequest):
    return {"original": data.text, "reversed": data.text[::-1]}

@router.post("/word-counter")
async def word_counter(data: TextRequest):
    text = data.text
    words = len(text.split())
    characters = len(text)
    characters_no_space = len(text.replace(" ", ""))
    lines = len(text.splitlines())
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
        result = " ".join(words_list[:count]) if count <= len(words_list) else " ".join(words_list * (count // len(words_list) +1))[:count*6] # rough estimate
    elif type == "sentences":
        result = " ".join(sentences_list[:count]) if count <= len(sentences_list) else " ".join(sentences_list * (count // len(sentences_list) +1))[:count*15]
    elif type == "paragraphs":
        para = " ".join(sentences_list)
        result = "\n\n".join([para] * count)
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
        return {"csv": data.csv_data, "json": json.loads(json_data)} # Return parsed JSON
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting CSV: {str(e)}")

@router.post("/markdown-to-html")
async def markdown_to_html_converter(data: MarkdownToHtmlRequest):
    html_output = md_parser.markdown(data.markdown_text)
    return {"markdown": data.markdown_text, "html": html_output}

# TODO: Unit Converter, Basic Calculator, Random Number Generator