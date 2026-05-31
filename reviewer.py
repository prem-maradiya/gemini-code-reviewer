import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv
from google import genai
from google.genai import types
from colorama import init, Fore, Style

init(autoreset=True)


SYSTEM_PROMPT_FILE = """You are an experienced, practical software code reviewer.

Review the code the user gives you and report real problems only.
Focus, in order: 1) bugs and crashes, 2) security issues, 3) performance/readability.

Rules:
- Only raise issues that genuinely matter. Do NOT nitpick style.
- For each issue give: the problem, why it matters, and a concrete fix.
- If the code is fine, say so briefly.

Format under these headings:
### Bugs
### Security
### Suggestions
Keep it concise."""


SYSTEM_PROMPT_DIFF = """You are an experienced code reviewer reviewing a git diff.

Lines starting with '+' were ADDED. Lines starting with '-' were REMOVED.
Review ONLY the changes. Do not comment on unchanged context lines.
Focus, in order: 1) bugs and crashes, 2) security issues, 3) performance/readability.

Rules:
- Only raise issues that genuinely matter. Do NOT nitpick style.
- For each issue give: the problem, why it matters, and a concrete fix.
- If the changes look good, say so briefly.

Format under these headings:
### Bugs
### Security
### Suggestions
Keep it concise."""


def load_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "PASTE_YOUR_KEY_HERE":
        print("ERROR: No API key found. Open the .env file and paste your key in.")
        sys.exit(1)
    return api_key


def read_code_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: Could not find a file named '{filename}'.")
        print("Check the spelling, or include the full path.")
        sys.exit(1)


def get_git_diff():
    try:
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        print("ERROR: git is not installed or not on your PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("ERROR: 'git diff' failed. Are you inside a git repository?")
        sys.exit(1)
    return result.stdout


def print_review(title, review):
    print(Style.BRIGHT + "=" * 60)
    print(Style.BRIGHT + Fore.WHITE + title)
    print(Style.BRIGHT + "=" * 60)

    for line in review.splitlines():
        stripped = line.strip()
        if stripped.startswith("### Bugs"):
            print(Fore.RED + Style.BRIGHT + line)
        elif stripped.startswith("### Security"):
            print(Fore.YELLOW + Style.BRIGHT + line)
        elif stripped.startswith("### Suggestions"):
            print(Fore.CYAN + Style.BRIGHT + line)
        else:
            print(line)


def ask_gemini(api_key, system_prompt, user_content):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        contents=user_content,
    )
    return response.text


def main():
    parser = argparse.ArgumentParser(description="AI code reviewer powered by Gemini.")
    parser.add_argument("filename", nargs="?", help="a code file to review (optional)")
    parser.add_argument("--diff", action="store_true", help="review uncommitted git changes instead of a file")
    args = parser.parse_args()

    api_key = load_api_key()

    if args.diff:
        diff_text = get_git_diff()
        if not diff_text.strip():
            print("No changes to review — your working tree is clean.")
            sys.exit(0)
        print("Reviewing your git changes with Gemini...\n")
        review = ask_gemini(api_key, SYSTEM_PROMPT_DIFF, f"Review this git diff:\n\n```diff\n{diff_text}\n```")
        title = "CODE REVIEW: git diff (uncommitted changes)"

    elif args.filename:
        code_text = read_code_file(args.filename)
        print(f"Reviewing {args.filename} with Gemini...\n")
        review = ask_gemini(api_key, SYSTEM_PROMPT_FILE, f"Please review this file ({args.filename}):\n\n```\n{code_text}\n```")
        title = f"CODE REVIEW: {args.filename}"

    else:
        print("Tell me what to review:")
        print("  python reviewer.py somefile.py   (review a file)")
        print("  python reviewer.py --diff         (review your git changes)")
        sys.exit(1)

    print_review(title, review)


if __name__ == "__main__":
    main()
