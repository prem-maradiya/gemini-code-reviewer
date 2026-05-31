# Gemini Code Reviewer

A command-line tool that reviews code using Google's Gemini models. Point it at a
file or at your uncommitted git changes, and it reports bugs, security issues, and
suggested improvements right in your terminal.

## Features

- Review an entire file, or only your staged/unstaged git changes (`--diff`)
- Focused output grouped into **Bugs**, **Security**, and **Suggestions**
- Color-highlighted headings for quick scanning
- Friendly error handling for missing files, missing keys, and non-git folders

## Requirements

- Python 3.10+
- A Google Gemini API key (free tier available at https://aistudio.google.com/apikey)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/prem-maradiya/gemini-code-reviewer.git
   cd gemini-code-reviewer
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS / Linux
   pip install google-genai python-dotenv colorama
   ```

3. Create a `.env` file in the project root with your API key:
   ```
   GEMINI_API_KEY=your_key_here
   ```

## Usage

Review a single file:
```bash
python reviewer.py example.py
```

Review your uncommitted git changes:
```bash
python reviewer.py --diff
```

On Windows you can also use the included launcher:
```bash
.\review example.py
.\review --diff
```

## How it works

1. Loads the API key from `.env`.
2. Collects the code to review — either by reading a file or by running `git diff`.
3. Sends it to Gemini with a reviewer prompt tuned for signal over noise.
4. Prints the review with color-coded sections.

```mermaid
flowchart TD
    A([Start: run the tool]) --> B{--diff flag?}
    B -- Yes --> C[Run git diff<br/>collect changed lines]
    B -- No --> D{Filename provided?}
    D -- No --> E[Print usage and exit]
    D -- Yes --> F[Read file contents]
    C --> G[Load API key from .env]
    F --> G
    G --> H[Build reviewer prompt<br/>system rules + code]
    H --> I[Send request to Gemini API]
    I --> J[Receive review text]
    J --> K[Color-code Bugs / Security / Suggestions]
    K --> L([Print review to terminal])

    classDef startEnd fill:#2563eb,stroke:#1e40af,color:#ffffff;
    classDef decision fill:#f59e0b,stroke:#b45309,color:#000000;
    classDef process fill:#e5e7eb,stroke:#9ca3af,color:#111827;
    class A,L startEnd;
    class B,D decision;
    class C,E,F,G,H,I,J,K process;
```

## Project structure

| File | Purpose |
|------|---------|
| `reviewer.py` | Main command-line tool |
| `review.bat` | Windows launcher |
| `example.py` | Sample file with intentional issues, for trying the tool |

## License

MIT
