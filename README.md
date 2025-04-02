# repo2readme


<p align="center">
  <img src="logo.jpg" alt="Logo" width="400"/>
</p>

🔹 **Transform any repository into a beautiful README with AI**

## 📖 Overview

repo2readme is a command-line tool that automatically generates professional README files for GitHub repositories. It analyzes your repository structure, code, and existing documentation, then uses AI to create a well-structured README following open-source best practices. Save time and ensure your projects make a great first impression with minimal effort.

## 🚀 Installation

```bash
# Install from PyPI
pip install repo2readme

# Set up environment variables
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

## 🛠️ Usage

Simply point the tool at your repository:

```bash
repo2readme /path/to/your/repository
```

The tool will:
1. Extract repository information
2. Generate a professional README using AI
3. Include your logo if present
4. Save the result as README.md in your repository

## 🔑 Environment Variables

Create a `.env` file with the following:

```
MODEL_ID=anthropic/claude-3.7-sonnet:thinking
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=your-key
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.