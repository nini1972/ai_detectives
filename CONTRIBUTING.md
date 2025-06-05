# 🤝 Contributing to Dual-AI Detective Game

Thank you for your interest in contributing to the world's first dual-AI detective game! This project represents a breakthrough in AI-powered gaming.

## 🎯 Project Overview

This is a revolutionary detective game that combines:
- **OpenAI GPT-4** for creative storytelling
- **Anthropic Claude** for logical analysis
- **FAL.AI** for visual scene generation
- **Dynamic character discovery** through conversation
- **Real-time visual testimony** generation

## 🧬 Generated Code Notice

**Important**: This project was primarily generated using AI assistance (Claude-3.5-Sonnet) with human guidance and iteration. When contributing:

1. **Understand the AI-generated patterns** in the existing code
2. **Maintain consistency** with the established architecture
3. **Document any major changes** to the AI-integration patterns
4. **Test thoroughly** as AI-generated code may have unexpected behaviors

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB
- API keys for OpenAI, Anthropic, and FAL.AI

### Quick Setup
```bash
# Clone and setup
git clone <repository-url>
cd dual-ai-detective
chmod +x setup.sh
./setup.sh

# Follow the prompts to configure API keys
```

### Manual Setup
See [README.md](README.md) for detailed manual setup instructions.

## 🏗️ Architecture Overview

### Backend (`/backend/server.py`)
- **FastAPI** server with async support
- **DualAIDetectiveService** class managing both AI systems
- **MongoDB** for data persistence
- **Visual generation pipeline** with FAL.AI

### Frontend (`/frontend/src/App.js`)
- **React** with hooks for state management
- **Auto-refresh mechanism** for visual content
- **Real-time notifications** for discoveries
- **Save/load system** with localStorage

## 🎯 Areas for Contribution

### 1. 🤖 AI Integration Enhancements
- **New AI Services**: Integration with additional AI providers
- **Prompt Engineering**: Improved prompts for better responses
- **Context Management**: Better conversation history handling
- **Error Handling**: More robust AI service failure handling

### 2. 🎨 Visual Improvements
- **UI/UX Design**: Enhanced visual design and user experience
- **Animation**: Smooth transitions and loading animations
- **Responsive Design**: Better mobile and tablet support
- **Accessibility**: Screen reader support and keyboard navigation

### 3. 🎮 Game Mechanics
- **New Investigation Tools**: Timeline builders, relationship maps
- **Difficulty Levels**: Adaptive complexity systems
- **Achievement System**: Progress tracking and rewards
- **Tutorial System**: Guided introduction for new players

### 4. 🔧 Technical Improvements
- **Performance**: Database optimization, caching strategies
- **Testing**: Comprehensive test coverage
- **Security**: Input validation, rate limiting
- **Monitoring**: Logging, metrics, error tracking

### 5. 📱 Platform Extensions
- **Mobile App**: Native iOS/Android applications
- **PWA Features**: Offline support, push notifications
- **Browser Extensions**: Quick case access tools
- **API Documentation**: OpenAPI/Swagger improvements

## 🔍 Code Review Guidelines

### AI-Generated Code Considerations
When reviewing AI-generated code:

1. **Logic Verification**: Ensure AI logic flows make sense
2. **Error Handling**: Check for edge cases AI might miss
3. **Performance**: Look for inefficient patterns
4. **Security**: Validate input sanitization and API key handling
5. **Maintainability**: Ensure code is readable and well-structured

### Review Checklist
- [ ] Code follows existing patterns and conventions
- [ ] AI integrations are properly tested
- [ ] Error handling is comprehensive
- [ ] Performance impact is considered
- [ ] Documentation is updated
- [ ] Tests are included (where applicable)

## 🧪 Testing Strategy

### Backend Testing
```bash
cd backend
python backend_test.py
```

### Frontend Testing
```bash
cd frontend
yarn test
```

### Integration Testing
- Test complete game flow from case generation to solving
- Verify AI service integrations
- Test visual generation pipeline
- Validate save/load functionality

### Manual Testing Scenarios
1. **Case Generation**: Generate multiple cases, verify uniqueness
2. **Character Discovery**: Question suspects to trigger new character creation
3. **Visual Generation**: Test testimony-to-image conversion
4. **Error Handling**: Test with invalid inputs and service failures

## 📝 Commit Guidelines

### Commit Message Format
```
type(scope): brief description

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples
```
feat(ai): add new character personality generation system
fix(visual): resolve image loading race condition
docs(readme): update setup instructions
```

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues
2. Verify the bug with latest code
3. Test with fresh environment setup

### Bug Report Template
```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Browser: [e.g., Chrome 96]
- Node.js version: [e.g., 18.0.0]
- Python version: [e.g., 3.11.0]

## Additional Context
- Console errors
- Screenshots
- API response logs
```

## 💡 Feature Requests

### Feature Request Template
```markdown
## Feature Description
Brief description of the proposed feature

## Problem/Use Case
What problem does this solve?

## Proposed Solution
How should this feature work?

## Technical Considerations
- AI integration requirements
- Performance implications
- UI/UX considerations

## Alternative Solutions
Other ways to address this need
```

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation

## 📞 Getting Help

### Development Questions
- Create an issue with the `question` label
- Include relevant code snippets and context

### AI Integration Questions
- Provide details about which AI service (OpenAI/Anthropic/FAL.AI)
- Include API request/response examples
- Share relevant error messages

## 🔐 Security

### Reporting Security Issues
- Email security issues privately (don't create public issues)
- Include detailed reproduction steps
- Provide impact assessment

### Security Guidelines
- Never commit API keys
- Validate all user inputs
- Use environment variables for sensitive data
- Follow OWASP guidelines for web security

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## 🎮 Community

Join our community of developers pushing the boundaries of AI-powered gaming:
- Share your detective game ideas
- Collaborate on AI integration improvements
- Help test new features
- Contribute to documentation

---

**Thank you for contributing to the future of AI-powered detective gaming!** 🕵️‍♂️