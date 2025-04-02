# **📦 repo2readme**
<p align="center">
  <img src="logo.jpg" alt="Logo" width="400"/>
</p>

🔹 🤖 Generate beautiful READMEs for your repositories with AI

📖 **Overview**

`repo2readme` is a command-line tool that uses AI to automatically generate clean, modern `README.md` files for your GitHub repositories.

It works by first creating a Markdown representation of the target repository's structure and file contents using the `repo2md` utility. This Markdown dump is then sent to an AI model via OpenRouter, along with a specific system prompt, to generate a well-structured README based on open-source best practices. The resulting `README.md` is saved in the root of the target repository.

🚀 **Installation**

1.  Install the tool using pipx:
    ```bash
    pipx install . --force
    ```
2.  Configure your environment. The tool automatically creates a default configuration file at `~/.repo2readme.env` on its first run if one doesn't exist. Edit this file to add your OpenRouter API key:
    ```bash
    # Example command (use your preferred editor):
    nano ~/.repo2readme.env
    ```
    *   Ensure the `OPENROUTER_API_KEY` variable is set within this file. You can find an example in `src/repo2readme/configs/.env.example`.

🛠️ **Usage**

Run the tool from your terminal, providing the path to the local repository you want to document:

```bash
repo2readme /path/to/your/repository
```

The tool will:
*   Analyze the repository at the specified path using `repo2md`.
*   Generate a new `README.md` using the configured AI model via OpenRouter.
*   Save the generated `README.md` to the root of the target repository, overwriting any existing file.

📄 **License**

This project is licensed under the [MIT License](LICENSE).