# Common APIs Hub

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Vercel Deploy](https://deploy-badge.vercel.app/vercel/common-apis)

A versatile collection of commonly needed and fun API endpoints, built with FastAPI and deployable on Vercel's free tier. This project aims to provide a handy set of tools for developers, content creators, and anyone in need of quick utility or creative data APIs.

## ✨ Features

The API is organized into several categories:

### 📝 Text Manipulation
*   **/text/case-converter**: Convert text to `uppercase`, `lowercase`, `titlecase`, `camelcase`, `snakecase`, `kebabcase`.
*   **/text/string-reverser**: Reverse a given string.
*   **/text/word-counter**: Count words, characters (with/without spaces), and lines in a text.
*   **/text/slug-generator**: Convert a string into a URL-friendly slug.
*   **/text/lorem-ipsum**: Generate Lorem Ipsum dummy text (words, sentences, paragraphs).
*   **/text/json-pretty-printer**: Format a minified JSON string nicely.
*   **/text/csv-to-json**: Convert CSV data to JSON format.
*   **/text/markdown-to-html**: Convert basic Markdown to HTML.
*   **/text/hash**: Generate hash (MD5, SHA1, SHA256, SHA512) of a given text.
*   **/text/base64**: Encode text to Base64 or decode from Base64.
*   **/text/uuid**: Generate a UUID (v4).

### 🛠️ Utilities & Data Transformation
*   **/text/unit-converter**: Convert between common units (temperature, length, weight).
*   **/text/calculator**: Perform basic arithmetic operations (add, subtract, multiply, divide).
*   **/text/random-number**: Generate random integers or floats within a specified range.

### 😂 Fun & Creative
*   **/fun/quote/famous**: Get a random famous quote.
*   **/fun/quote/kanye**: Get a random (simulated) Kanye West quote.
*   **/fun/joke/bad**: Get a random "bad" joke.
*   **/fun/joke/chuck-norris**: Get a random Chuck Norris joke (optionally by category).
*   **/fun/joke/chuck-norris/categories**: List available Chuck Norris joke categories.
*   **/fun/fact/cat**: Get a random cat fact.
*   **/fun/fact/dog**: Get a random dog fact.
*   **/fun/random/color-hex**: Get a random hex color code.
*   **/fun/random/emoji**: Get a random emoji.
*   **/fun/random/yes-no**: Get a random "Yes/No" style answer.
*   **/fun/random/name**: Generate a random first and last name (optionally by gender).
*   **/fun/random/password**: Generate a random secure password with customizable criteria.
*   **/fun/magic-8-ball**: Ask the Magic 8-Ball a question.
*   **/fun/coin-flipper**: Flip a virtual coin (Heads/Tails).
*   **/fun/dice-roller**: Roll a virtual die with a specified number of sides.

### 🧑‍💻 Developer Utilities
*   **/dev/user-agent**: Parse a User-Agent string into structured information.
*   **/dev/ip-info**: Get basic information about the requesting IP address.
*   **/dev/http-status**: Get an explanation and a fun image link (http.cat) for an HTTP status code.
*   **/dev/timestamp-converter**: Convert between Unix timestamps and human-readable UTC datetime strings.
*   **/dev/view-headers**: View the HTTP headers sent in the request.

### 🌍 Data Fetching
*   **/data/country-info**: Get basic information about a country (from a simplified dataset).
*   **/data/timezones**: List common IANA timezone names.
*   **/data/time/convert**: Convert time between different timezones.
*   **/data/holidays**: Get public holidays for a given country and year.

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   pip
*   Git

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/garvit-exe/common-apis.git
    cd common-apis
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the development server:**
    ```bash
    uvicorn api.index:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.
    Interactive documentation (Swagger UI) will be at `http://127.0.0.1:8000/` or `http://127.0.0.1:8000/docs`.
    Alternative documentation (ReDoc) is at `http://127.0.0.1:8000/redoc`.

## ☁️ Deployment to Vercel

This project is configured for easy deployment on Vercel.

1.  **Sign up/Log in to Vercel** (preferably with your GitHub account).
2.  Click "Add New..." -> "Project".
3.  Import your `common-apis` repository from GitHub.
4.  Vercel should automatically detect it as a Python project using the settings in `vercel.json`.
    *   **Framework Preset:** Should be "Other" or automatically detected.
    *   **Build Command:** Vercel uses `vercel build` which respects `vercel.json`.
    *   **Output Directory:** Not needed as it's a serverless function.
    *   **Install Command:** `pip install -r requirements.txt` (Vercel handles this).
    *   **Root Directory:** Should be the root of your repository.
5.  Click "Deploy".
6.  Once deployed, Vercel will provide you with a live URL (e.g., `your-project-name.vercel.app`).

## 🛠️ API Usage

Once deployed (or running locally), you can access the interactive API documentation (Swagger UI) at the root URL (e.g., `https://your-project-name.vercel.app/`) to try out the endpoints.

**Example Request (Case Converter):**
```bash
curl -X 'POST' \
  'https://your-project-name.vercel.app/text/case-converter?to_case=uppercase' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Hello World Example"
}'
```

**Example Response:**
```json
{
  "original": "Hello World Example",
  "converted": "HELLO WORLD EXAMPLE"
}
```

## 🤝 Contributing
Contributions are welcome! If you have ideas for new APIs, improvements, or bug fixes, please:
1. Fork the repository.
2. Create a new branch (git checkout -b feature/your-feature-name).
3. Make your changes.
4. Test your changes thoroughly.
5. Commit your changes (git commit -m 'Add some feature').
6. Push to the branch (git push origin feature/your-feature-name).
7. Open a Pull Request.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.