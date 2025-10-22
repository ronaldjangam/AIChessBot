# Contributing to AI Chess Learning Platform

Thank you for your interest in contributing to the AI Chess Learning Platform! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, Node version)
- Screenshots if applicable

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Potential implementation approach (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: `git commit -m 'Add amazing feature'`
6. **Push to your fork**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Code Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings for functions and classes
- Write unit tests for new features

### TypeScript/React (Frontend)
- Use TypeScript for type safety
- Follow React best practices
- Use functional components and hooks
- Keep components small and focused

### Git Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Be descriptive but concise
- Reference issues when applicable: "Fix #123"

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Areas We Need Help

- [ ] Additional chess opening databases
- [ ] More training puzzles and tactics
- [ ] UI/UX improvements
- [ ] Performance optimizations
- [ ] Documentation and tutorials
- [ ] Multilingual support
- [ ] Mobile app development
- [ ] Additional LLM personas

## Questions?

Feel free to:
- Open a GitHub Discussion
- Create an issue with the `question` label
- Reach out to maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Prioritize the learning experience of users

Thank you for contributing! 🎉
