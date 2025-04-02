import os
import sys
import subprocess
from pathlib import Path
from openai import OpenAI

def setup_env():
    import shutil
    from dotenv import load_dotenv
    from pathlib import Path
    import sys

    target_env = Path.home() / ".repo2readme.env"

    if not target_env.exists():
        try:
            example_path = Path(__file__).parent / "configs" / ".env.example"
            shutil.copy(example_path, target_env)
            print(f"✅ Created default env file at {target_env}")
            print("⚠️  Please edit this file with your actual configuration and run the command again.")
            print(f"🛠️  You can use this command to edit it:\n     nano {target_env}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to create default .env: {e}")
            sys.exit(1)

    load_dotenv(dotenv_path=target_env)
setup_env()

# Console text coloring
def colored(text, color):
    codes = {'red': '\033[31m', 'green': '\033[32m', 'blue': '\033[34m'}
    return f"{codes.get(color, '')}{text}\033[0m"

# Ensure required environment variables are present
def check_env():
    required = ["OPENROUTER_BASE_URL", "OPENROUTER_API_KEY", "MODEL_ID"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(colored(f"Missing env vars: {', '.join(missing)}", 'red'))
        sys.exit(1)

# Convert repo to markdown using repo2md
def get_repo_markdown(repo_path):
    try:
        result = subprocess.run(['repo2md', str(repo_path)], capture_output=True, text=True, check=True)
        repo_md = result.stdout
        assert repo_md, "repo2md output is empty"
        return repo_md
    except FileNotFoundError:
        print(colored("Error: `repo2md` not found. Install it and ensure it's in your PATH.", 'red'))
    except subprocess.CalledProcessError as e:
        print(colored("Error running `repo2md`:", 'red'))
        print(e.stderr)
    sys.exit(1)

# Read system prompt from file
def read_system_prompt():
    try:
        config_path = Path(__file__).parent / "configs" / "system_prompt.txt"
        with config_path.open("r", encoding="utf-8") as f:
            system_prompt = f.read().strip()
            assert system_prompt, "System prompt is empty"
            return system_prompt
    except Exception as e:
        print(colored(f"Error reading system prompt: {e}", 'red'))
        sys.exit(1)

# Generate README from markdown using OpenAI
def generate_readme(markdown):
    system_prompt = read_system_prompt()
    
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    response = client.chat.completions.create(
        model=os.getenv("MODEL_ID"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": markdown}
        ],
        temperature=0.3,
        max_tokens=4096
    )

    return response.choices[0].message.content.strip()

# Inject logo HTML snippet after the title
def inject_logo(content, repo_path):
    logo_path = Path(repo_path) / "logo.jpg"
    if not logo_path.exists(): return content

    logo_html = """
<p align="center">
  <img src="logo.jpg" alt="Logo" width="400"/>
</p>
""".strip()

    lines = content.split('\n')
    lines.insert(1, logo_html)
    lines.insert(1, '\n')
    return '\n'.join(lines)

# Write generated content to README.md
def write_readme(repo_path, content):
    readme_path = Path(repo_path) / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(colored(f"README.md written to {readme_path}", 'green'))

# Main entry point
def main():
    if len(sys.argv) < 2:
        print(colored("Usage: python main.py /path/to/repo", 'red'))
        sys.exit(1)

    repo_path = Path(sys.argv[1])
    if not repo_path.is_dir():
        print(colored(f"Invalid repo path: {repo_path}", 'red'))
        sys.exit(1)

    check_env()

    print("🔍 Extracting repo info...")
    markdown = get_repo_markdown(repo_path)

    print("🤖 Generating README.md...")
    readme = generate_readme(markdown)

    print("🖼️ Injecting logo...")
    readme = inject_logo(readme, repo_path)

    print("💾 Writing to README.md...")
    write_readme(repo_path, readme)

    print(colored("✅ All done!", 'green'))

if __name__ == "__main__":
    main()
