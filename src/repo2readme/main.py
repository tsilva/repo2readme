import os
import sys
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ANSI colors
RED, GREEN, RESET = '\033[31m', '\033[32m', '\033[0m'

CONFIG_DIR = Path.home() / ".repo2readme"
ENV_PATH = CONFIG_DIR / ".env"
REQUIRED_VARS = ["MODEL_ID", "OPENROUTER_BASE_URL", "OPENROUTER_API_KEY"]

def log_err(msg): print(f"{RED}{msg}{RESET}")
def log_ok(msg): print(f"{GREEN}{msg}{RESET}")

def fatal(msg):
    log_err(msg)
    sys.exit(1)

def setup_env():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not ENV_PATH.exists():
        try:
            shutil.copy(Path(__file__).parent / "configs" / ".env.example", ENV_PATH)
            log_ok(f"✅ Created default env file at {ENV_PATH}")
            print("⚠️  Edit this file with your config and rerun.")
            print(f"🛠️  Use: nano {ENV_PATH}")
        except Exception as e:
            fatal(f"❌ Could not create .env: {e}")
        sys.exit(1)
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        fatal(f"Missing env vars: {', '.join(missing)}")

def get_repo_markdown(repo_path: Path) -> str:
    try:
        result = subprocess.run(['repo2md', str(repo_path)], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if not output:
            raise ValueError("repo2md returned empty output")
        return output
    except FileNotFoundError:
        fatal("`repo2md` not found. Install and add to PATH.")
    except subprocess.CalledProcessError as e:
        log_err("Error running `repo2md`:\n" + e.stderr)
    except Exception as e:
        fatal(f"Unexpected repo2md error: {e}")
    sys.exit(1)

def read_system_prompt() -> str:
    path = Path(__file__).parent / "configs" / "system_prompt.txt"
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError("System prompt is empty")
        return content
    except Exception as e:
        fatal(f"Error reading system prompt: {e}")

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
        content = response.choices[0].message.content.strip()
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        return content.strip()
    except Exception as e:
        fatal(f"❌ README generation failed: {e}")

def inject_logo(content: str, repo_path: Path) -> str:
    if (repo_path / "logo.jpg").exists():
        logo_html = (
            '<p align="center">\n'
            '  <img src="logo.jpg" alt="Logo" width="400"/>\n'
            '</p>\n'
        )
        lines = content.splitlines()
        lines.insert(1, logo_html)
        return '\n'.join(lines)
    return content

def write_readme(repo_path: Path, content: str):
    try:
        (repo_path / "README.md").write_text(content, encoding='utf-8')
        log_ok(f"✅ README.md written at {repo_path / 'README.md'}")
    except Exception as e:
        fatal(f"❌ Failed to write README.md: {e}")

def main():
    if len(sys.argv) < 2:
        fatal("Usage: python main.py /path/to/repo")

    repo_path = Path(sys.argv[1])
    if not repo_path.is_dir():
        fatal(f"Invalid repo path: {repo_path}")

    setup_env()

    print("🔍 Parsing repo...")
    markdown = get_repo_markdown(repo_path)

    print("🤖 Generating README...")
    readme = generate_readme(markdown)

    print("🖼️ Injecting logo (if found)...")
    readme = inject_logo(readme, repo_path)

    print("💾 Writing README.md...")
    write_readme(repo_path, readme)

    log_ok("🎉 Done.")

if __name__ == "__main__":
    main()
