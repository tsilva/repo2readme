# 📦 repo2readme

<p align="center">
  <img src="logo.jpg" alt="Logo" width="400"/>
</p>

🤖 Generate beautiful READMEs for your repositories with AI

## 📖 Overview

repo2readme is a command-line tool that automatically generates professional README files for GitHub repositories. It analyzes your repository structure, code, and documentation, then uses AI to create a well-structured README following open-source best practices. Save time and ensure your projects make a great first impression with minimal effort.

## 🚀 Installation

```bash
pipx install . --force
```

After installation, set up your environment variables:

```bash
cp .env.example .env
# Edit the .env file with your OpenRouter API key
```

## 🛠️ Usage

Simply point the tool at your repository:

```bash
repo2readme /path/to/your/repository
```

The tool will:
1. Extract repository information
2. Generate a professional README using AI
3. Include your logo if present (named logo.jpg)
4. Save the result as README.md in your repository

## 📄 License

This project is licensed under the [MIT License](LICENSE).