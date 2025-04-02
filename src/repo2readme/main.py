import os
import sys
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Console text coloring
def colored(text: str, color: str) -> str:
    codes = {'red': '\033[31m', 'green': '\033[32m', 'blue': '\033[34m'}
    return f"{codes.get(color, '')}{text}\033[0m"

# Setup environment and load .env
def setup_env():
    config_dir = Path.home() / "repo2readme"
    config_dir.mkdir(parents=True, exist_ok=True)
    env_path = config_dir / ".env"

    if not env_path.exists():
        example_path = Path(__file__).parent / "configs" / ".env.example"
        try:
            shutil.copy(example_path, env_path)
            print(f"✅ Created default env file at {env_path}")
            print("⚠️  Please edit this file with your actual configuration and run the command again.")
            print(f"🛠️  Use: nano {env_path}")
        except Exception as e:
            print(colored(f"❌ Failed to create default .env: {e}", 'red'))
        sys.exit(1)

    load_dotenv(dotenv_path=env_path)
    check_env_vars()

def check_env_vars():
    required_vars = ["MODEL_ID", "OPENROUTER_BASE_URL", "OPENROUTER_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(colored(f"Missing env vars: {', '.join(missing)}", 'red'))
        sys.exit(1)

def get_repo_markdown(repo_path: Path) -> str:
    try:
        result = subprocess.run(['repo2md', str(repo_path)], capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            raise ValueError("repo2md output is empty")
        return result.stdout
    except FileNotFoundError:
        print(colored("Error: `repo2md` not found. Install it and ensure it's in your PATH.", 'red'))
    except subprocess.CalledProcessError as e:
        print(colored("Error running `repo2md`:", 'red'))
        print(e.stderr)
    except Exception as e:
        print(colored(f"Unexpected error: {e}", 'red'))
    sys.exit(1)

def read_system_prompt() -> str:
    try:
        prompt_path = Path(__file__).parent / "configs" / "system_prompt.txt"
        content = prompt_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError("System prompt is empty")
        return content
    except Exception as e:
        print(colored(f"Error reading system prompt: {e}", 'red'))
        sys.exit(1)

def generate_readme(markdown: str) -> str:
    system_prompt = read_system_prompt()
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_ID"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": markdown}
            ],
            temperature=0.3,
            max_tokens=4096
        )
        readme = response.choices[0].message.content.strip()

        # Remove code fences if present
        lines = readme.splitlines()
        if lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        return '\n'.join(lines)

    except Exception as e:
        print(colored(f"❌ Failed to generate README: {e}", 'red'))
        sys.exit(1)

def inject_logo(content: str, repo_path: Path) -> str:
    logo = repo_path / "logo.jpg"
    if not logo.exists():
        return content

    logo_html = """
<p align="center">
  <img src="logo.jpg" alt="Logo" width="400"/>
</p>
""".strip()

    lines = content.splitlines()
    lines.insert(1, logo_html)
    return '\n'.join(lines)

def write_readme(repo_path: Path, content: str):
    readme_path = repo_path / "README.md"
    try:
        readme_path.write_text(content, encoding='utf-8')
        print(colored(f"✅ README.md written to {readme_path}", 'green'))
    except Exception as e:
        print(colored(f"❌ Failed to write README.md: {e}", 'red'))
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(colored("Usage: python main.py /path/to/repo", 'red'))
        sys.exit(1)

    repo_path = Path(sys.argv[1])
    if not repo_path.is_dir():
        print(colored(f"Invalid repo path: {repo_path}", 'red'))
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

    print(colored("🎉 All done!", 'green'))

if __name__ == "__main__":
    main()
