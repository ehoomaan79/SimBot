# Contributing to SimBot

Thank you for your interest in contributing to SimBot! This document provides guidelines and best practices for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check if the issue has already been reported. If not, create a new issue with:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Screenshots or logs (if applicable)
- Environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:

- A clear and descriptive title
- Detailed description of the proposed enhancement
- Use cases and benefits
- Any potential drawbacks or considerations

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` for your changes
3. Make your changes with clear, focused commits
4. Ensure all tests pass (if applicable)
5. Update documentation as needed
6. Submit a pull request with a clear description

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ehoomaan79/SimBot.git
   cd SimBot
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```env
   DISCORD_TOKEN=your_token
   SIGN_SECRET=your_secret
   API_URL=https://kingshot-giftcode.centurygame.com/api/gift_code
   ```

5. Run the bot:
   ```bash
   python bot/bot.py
   ```

## Code Style

- Follow PEP 8 style guide for Python code
- Use type hints where appropriate
- Write clear, descriptive variable and function names
- Add docstrings for public functions and classes
- Keep functions small and focused

## Testing

- Test your changes thoroughly before submitting
- Ensure the bot starts without errors
- Test Discord commands manually
- Verify database operations work correctly

## Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Examples:
```
feat(bot): add !status command
fix(database): handle expired codes correctly
docs(readme): update installation instructions
```

## Review Process

All pull requests require review before merging. Reviewers will check for:

- Code quality and style
- Correctness and completeness
- Test coverage
- Documentation updates
- Security considerations

## Questions?

If you have questions about contributing, feel free to open an issue or contact the maintainers.