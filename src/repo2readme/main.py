import os
import sys
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ANSI colors
RED = '\033[31m'
GREEN = '\033[32m'
RESET = '\033[0m'

CONFIG_DIR = Path.home() / "repo2readme"
ENV_PATH = CONFIG_DIR / ".env"
REQUIRED_VARS = ["MODEL_ID", "OPENROUTER_BASE_URL", "OPENROUTER_API_KEY"]

def print_err(msg): print(f"{RED}{msg}{RESET}")
def print_ok(msg): print(f"{GREEN}{msg}{RESET}")

def setup_env():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not ENV_PATH.exists():
        try:
            shutil.copy(Path(__file__).parent / "configs" / ".env.example", ENV_PATH)
            print_ok(f"✅ Created default env file at {ENV_PATH}")
            print("⚠️  Please edit this file with your actual configuration and run again.")
            print(f"🛠️  Use: nano {ENV_PATH}")
        except Exception as e:
            print_err(f"❌ Failed to create default .env: {e}")
        sys.exit(1)
    load_dotenv(dotenv_path=ENV_PATH)
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        print_err(f"Missing env vars: {', '.join(missing)}")
        sys.exit(1)

def get_repo_markdown(repo_path: Path) -> str:
    try:
        result = subprocess.run(['repo2md', str(repo_path)], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if not output:
            raise ValueError("repo2md output is empty")
        return output
    except FileNotFoundError:
        print_err("Error: `repo2md` not found. Install it and ensure it's in your PATH.")
    except subprocess.CalledProcessError as e:
        print_err("Error running `repo2md`:")
        print(e.stderr)
    except Exception as e:
        print_err(f"Unexpected error: {e}")
    sys.exit(1)

def read_system_prompt() -> str:
    try:
        content = (Path(__file__).parent / "configs" / "system_prompt.txt").read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError("System prompt is empty")
        return content
    except Exception as e:
        print_err(f"Error reading system prompt: {e}")
        sys.exit(1)

def generate_readme(markdown: str) -> str:
    try:
        client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        response = client.chat.completions.create(
            model=os.getenv("MODEL_ID"),
            messages=[
                {"role": "system", "content": read_system_prompt()},
                {"role": "user", "content": markdown}
            ],
            temperature=0.3,
            max_tokens=4096
        )
        lines = response.choices[0].message.content.strip().splitlines()
        if lines and lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        return '\n'.join(lines)
    except Exception as e:
        print_err(f"❌ Failed to generate README: {e}")
        sys.exit(1)

def inject_logo(content: str, repo_path: Path) -> str:
    if not (repo_path / "logo.jpg").exists():
        return content
    logo_html = (
        '<p align="center">\n'
        '  <img src="logo.jpg" alt="Logo" width="400"/>\n'
        '</p>\n'
    )
    lines = content.splitlines()
    lines.insert(1, logo_html)
    return '\n'.join(lines)

def write_readme(repo_path: Path, content: str):
    try:
        (repo_path / "README.md").write_text(content, encoding='utf-8')
        print_ok(f"✅ README.md written to {repo_path / 'README.md'}")
    except Exception as e:
        print_err(f"❌ Failed to write README.md: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print_err("Usage: python main.py /path/to/repo")
        sys.exit(1)

    repo_path = Path(sys.argv[1])
    if not repo_path.is_dir():
        print_err(f"Invalid repo path: {repo_path}")
        sys.exit(1)

    setup_env()

    print("🔍 Extracting repo info...")
    markdown = get_repo_markdown(repo_path)

    print("🤖 Generating README.md...")
    readme = generate_readme(markdown)

    print("🖼️ Injecting logo if available...")
    readme = inject_logo(readme, repo_path)

    print("💾 Writing to README.md...")
    write_readme(repo_path, readme)

    print_ok("🎉 All done!")

if __name__ == "__main__":
    main()
