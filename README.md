# **📦 repo2readme**

<p align="center">
  <img src="logo.jpg" alt="Logo" width="400"/>
</p>


🔹 🤖 Generate beautiful READMEs for your repositories with AI

## 📖 Overview

`repo2readme` is a command-line tool that leverages AI to automatically create clean and modern README files for your GitHub repositories. It analyzes your repository structure using `repo2md`, sends this information to an AI model via OpenRouter, and generates a well-structured README following open-source best practices.

The tool handles everything from repository analysis to README generation in one simple command, making documentation easier and more consistent across your projects.

## 🚀 Installation

```bash
pipx install . --force
```

The tool will create a default configuration file at `~/.repo2readme/.env` on first run. Edit this file to add your OpenRouter API key and configure the AI model you want to use.

## 🛠️ Usage

Simply run the command with the path to your repository:

```bash
repo2readme /path/to/your/repository
```

This will:
- Analyze your repository structure
- Generate a README using AI
- Save the new README.md to your repository root
- Automatically include your logo.jpg if present

## 📄 License

This project is licensed under the [MIT License](LICENSE).