# Contributing to AINS

Thank you for your interest in contributing to AINS! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

- Use the GitHub Issues page to report bugs
- Provide clear description and steps to reproduce
- Include system information and screenshots when relevant

### Feature Requests

- Check if the feature has already been requested
- Provide clear use case and expected behavior
- Consider implementation complexity and project scope

### Code Contributions

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit with conventional commit messages
7. Push to your fork and submit a Pull Request

## 📋 Development Guidelines

### Code Style

- **Frontend**: Follow Prettier and ESLint configurations
- **Backend**: Follow Black, isort, and flake8 configurations
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

- `feat(api): add claim confidence scoring`
- `fix(frontend): resolve offline mode caching issue`
- `docs: update installation instructions`

### Testing

- Write tests for new functionality
- Ensure all existing tests pass
- Maintain test coverage above 80%
- Use meaningful test descriptions

### Documentation

- Update README.md for significant changes
- Add inline code documentation
- Update API documentation for backend changes
- Include examples in documentation

## 🔧 Development Setup

See the main README.md for detailed setup instructions.

### Quick Start

```cmd
git clone https://github.com/your-username/Hackathon-AINS.git
cd Hackathon-AINS
setup.bat
```

## 🏗️ Project Structure

```
Hackathon-AINS/
├── frontend/          # SvelteKit PWA
├── apis/             # FastAPI backend
├── .github/          # GitHub workflows
└── docs/             # Documentation
```

## 📝 Pull Request Process

1. Ensure your branch is up to date with main
2. Run tests and ensure they pass
3. Update documentation if needed
4. Fill out the Pull Request template
5. Request review from maintainers
6. Address feedback and update as needed

### Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Descriptive commit messages
- [ ] PR description explains changes

## 🐛 Bug Reports

Include:

- Operating system and version
- Browser/app version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots or error messages
- Network conditions (if relevant)

## 💡 Feature Requests

Include:

- Clear problem description
- Proposed solution
- Alternative solutions considered
- Use cases and examples
- Implementation suggestions

## 📚 Resources

- [SvelteKit Documentation](https://kit.svelte.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Capacitor Documentation](https://capacitorjs.com/)
- [Azure Documentation](https://docs.microsoft.com/azure/)

## ❓ Questions?

- Check existing issues and discussions
- Join our Discord community
- Contact maintainers directly

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to AINS! 🎉
