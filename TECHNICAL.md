# 🔧 Technical Documentation

## Project Structure & Architecture

### Directory Structure
```
/app/
├── backend/                    # FastAPI Python backend
│   ├── server.py              # Main API server with dual-AI integration
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables (API keys)
├── frontend/                  # React.js frontend
│   ├── src/
│   │   ├── App.js            # Main React component with game logic
│   │   ├── App.css           # Tailwind CSS with detective theme
│   │   ├── index.js          # React entry point
│   │   └── index.css         # Global styles
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Tailwind configuration
│   └── .env                  # Frontend environment variables
├── tests/                    # Test files
├── scripts/                  # Utility scripts
└── README.md                 # Main documentation
```

## API Documentation

### Core Endpoints

#### Case Management
- `POST /api/generate-case` - Generate new mystery case
- `GET /api/cases/{case_id}` - Retrieve case details
- `GET /api/case-scenes/{case_id}` - Get visual scenes for case

#### Character Interaction
- `POST /api/question-character` - Question suspects (returns potential new characters and visual scenes)
- `POST /api/generate-dynamic-character` - Generate new character from mention

#### Evidence Analysis
- `POST /api/analyze-evidence` - Submit theory for Claude analysis

#### Visual Generation
- `POST /api/generate-visual-scene` - Generate scene from context

#### Health Check
- `GET /api/health` - API health status

### Data Models

#### DetectiveCase
```python
class DetectiveCase(BaseModel):
    id: str
    title: str
    setting: str
    crime_scene_description: str
    crime_scene_image_url: Optional[str]
    victim_name: str
    characters: List[Character]
    evidence: List[Evidence]
    visual_scenes: List[VisualScene]
    solution: str
    created_at: datetime
    difficulty: str = "medium"
```

#### Character
```python
class Character(BaseModel):
    id: str
    name: str
    description: str
    background: str
    alibi: str
    motive: Optional[str]
    is_culprit: bool = False
```

#### VisualScene
```python
class VisualScene(BaseModel):
    id: str
    title: str
    description: str
    image_url: str
    generated_from: str  # "crime_scene", "testimony", "evidence_analysis"
    context: str
    character_involved: Optional[str]
    timestamp: datetime
```

## AI Integration Architecture

### Dual-AI System Design

#### DualAIDetectiveService Class
The core service that orchestrates both AI systems:

```python
class DualAIDetectiveService:
    def __init__(self):
        self.storyteller_ai = None  # OpenAI - for creative content
        self.logic_ai = None        # Claude - for logical analysis
```

#### AI System Responsibilities

**OpenAI GPT-4 (Storyteller AI)**
- Mystery case generation
- Character personality development
- Natural language dialogue
- Creative scene descriptions
- Dynamic character generation from mentions

**Anthropic Claude (Logic AI)**
- Evidence relationship analysis
- Logical consistency checking
- Deductive reasoning assistance
- Character mention detection
- Theory validation

### Visual Generation Pipeline

1. **Trigger Detection**: System identifies visual descriptions in testimony
2. **Prompt Generation**: OpenAI creates detailed image generation prompt
3. **Image Generation**: FAL.AI generates high-quality scene image
4. **Storage**: Image URL stored in database and linked to case
5. **Frontend Update**: Auto-refresh mechanism displays new images

## Frontend Architecture

### React Component Structure
- **App.js**: Main game component with state management
- **State Management**: React hooks for game state, conversations, evidence
- **API Integration**: Fetch calls to backend with error handling
- **Auto-refresh**: Periodic checking for new visual content

### Key Frontend Features

#### Dynamic Character Discovery
```javascript
// Handle new character discovery from API response
if (data.new_characters_discovered && data.new_characters_discovered.length > 0) {
    setCurrentCase(prev => ({
        ...prev,
        characters: [...prev.characters, ...data.new_characters_discovered.map(discovery => discovery.character)]
    }));
}
```

#### Visual Scene Management
```javascript
// Auto-refresh for crime scene images
useEffect(() => {
    if (currentCase?.id && !currentCase.crime_scene_image_url) {
        const interval = setInterval(refreshCaseData, 10000);
        return () => clearInterval(interval);
    }
}, [currentCase?.id, currentCase?.crime_scene_image_url]);
```

#### Save/Load System
- **localStorage**: Client-side game state persistence
- **Complete State Saving**: Cases, conversations, notes, evidence selections
- **Session Management**: Restore exact game state across browser sessions

## Database Design

### MongoDB Collections

#### Cases Collection
```json
{
    "id": "uuid",
    "title": "string",
    "setting": "string",
    "crime_scene_description": "string",
    "crime_scene_image_url": "string",
    "victim_name": "string",
    "characters": [Character],
    "evidence": [Evidence],
    "visual_scenes": [VisualScene],
    "solution": "string",
    "created_at": "datetime"
}
```

## Environment Configuration

### Backend Environment Variables
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="detective_game"
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
FAL_KEY="fal-..."
```

### Frontend Environment Variables
```bash
REACT_APP_BACKEND_URL="https://domain.com"
```

## Deployment Architecture

### Kubernetes Configuration
- **Frontend Pod**: Nginx serving React build
- **Backend Pod**: FastAPI with Uvicorn
- **MongoDB Pod**: Persistent volume for data storage
- **Supervisor**: Process management and auto-restart

### Service Configuration
```bash
# Service control commands
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
sudo supervisorctl restart all
```

### URL Routing
- **Frontend Routes**: Direct to port 3000
- **API Routes**: `/api/*` redirected to backend port 8001
- **Ingress Rules**: Kubernetes handles traffic routing

## Performance Optimization

### Backend Optimizations
- **Async Operations**: All AI calls are asynchronous
- **Background Processing**: Crime scene generation doesn't block case creation
- **Error Handling**: Comprehensive try-catch with fallback responses
- **Connection Pooling**: MongoDB Motor driver for efficient connections

### Frontend Optimizations
- **State Management**: Efficient React hooks preventing unnecessary re-renders
- **Auto-refresh**: Smart polling that stops when image is found
- **Image Loading**: Error handling and loading states for visual content
- **Responsive Design**: Tailwind CSS for optimal mobile experience

## Security Considerations

### API Key Management
- Environment variables only
- Never exposed in frontend code
- Separate keys for different services

### Input Validation
- Pydantic models for request validation
- SQL injection prevention through MongoDB
- XSS protection in React components

### Error Handling
- No sensitive information in error messages
- Graceful degradation when AI services fail
- Comprehensive logging for debugging

## Testing Strategy

### Backend Testing
- API endpoint testing with curl commands
- AI integration testing with mock responses
- Database operation testing
- Error condition testing

### Frontend Testing
- Component rendering tests
- State management tests
- API integration tests
- User interaction flow tests

### Integration Testing
- End-to-end game flow testing
- AI service integration testing
- Visual generation pipeline testing
- Save/load functionality testing

## Monitoring & Logging

### Backend Logging
```python
# Supervisor logs location
/var/log/supervisor/backend.*.log
```

### Performance Metrics
- API response times
- AI service costs per request
- Image generation success rates
- User engagement metrics

## Troubleshooting Guide

### Common Issues

#### Case Generation Stuck
- Check AI API keys and balances
- Verify MongoDB connection
- Check supervisor logs for errors

#### Images Not Appearing
- Verify FAL.AI balance and API key
- Check auto-refresh mechanism
- Manually refresh case data

#### Character Questioning Fails
- Validate character and case IDs
- Check OpenAI API status
- Verify request payload format

### Debug Commands
```bash
# Check service status
sudo supervisorctl status

# View backend logs
tail -f /var/log/supervisor/backend.*.log

# Test API health
curl https://domain.com/api/health

# Test case generation
curl -X POST https://domain.com/api/generate-case
```

## Future Technical Enhancements

### Scalability Improvements
- Redis caching for frequently accessed data
- CDN integration for image delivery
- Horizontal scaling for AI services
- Load balancing for multiple backend instances

### Advanced Features
- WebSocket integration for real-time updates
- Advanced image generation with consistent character appearance
- Voice synthesis for character dialogue
- Mobile-responsive progressive web app

### Performance Optimizations
- Image compression and optimization
- Lazy loading for visual content
- Service worker for offline functionality
- Database indexing for faster queries