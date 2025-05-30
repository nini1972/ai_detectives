from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
mongo_url = os.environ.get("MONGO_URL")
db_name = os.environ.get("DB_NAME")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# AI API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Data models
class Character(BaseModel):
    id: str
    name: str
    description: str
    background: str
    alibi: str
    motive: Optional[str] = None
    is_culprit: bool = False

class Evidence(BaseModel):
    id: str
    name: str
    description: str
    location_found: str
    significance: str
    is_key_evidence: bool = False

class DetectiveCase(BaseModel):
    id: str
    title: str
    setting: str
    crime_scene_description: str
    victim_name: str
    characters: List[Character]
    evidence: List[Evidence]
    solution: str
    created_at: datetime
    difficulty: str = "medium"

class QuestionRequest(BaseModel):
    case_id: str
    character_id: str
    question: str

class AnalysisRequest(BaseModel):
    case_id: str
    evidence_ids: List[str]
    theory: str

# AI Service Class
class DualAIDetectiveService:
    def __init__(self):
        self.storyteller_ai = None  # OpenAI - for creative content
        self.logic_ai = None        # Claude - for logical analysis
    
    async def initialize_storyteller(self, session_id: str):
        """Initialize OpenAI for creative storytelling"""
        self.storyteller_ai = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"storyteller_{session_id}",
            system_message="""You are the Storyteller AI in a revolutionary dual-AI detective game. Your role is to create rich, immersive mystery narratives with compelling characters and atmospheric descriptions.

Your responsibilities:
- Generate detailed character personalities, backgrounds, and dialogue
- Create atmospheric crime scene descriptions
- Develop realistic motives and alibis
- Craft engaging narrative elements
- Respond in character when suspects are questioned

Always maintain narrative consistency and create content that feels like a premium detective novel."""
        ).with_model("openai", "gpt-4.1")
    
    async def initialize_logic_ai(self, session_id: str):
        """Initialize Claude for logical analysis"""
        self.logic_ai = LlmChat(
            api_key=ANTHROPIC_API_KEY,
            session_id=f"logic_{session_id}",
            system_message="""You are the Logic AI in a revolutionary dual-AI detective game. Your role is to provide logical analysis, maintain case consistency, and help players with deductive reasoning.

Your responsibilities:
- Analyze evidence relationships and logical connections
- Detect contradictions in testimonies or theories
- Provide structured case summaries and timelines
- Offer logical deduction guidance
- Maintain factual consistency throughout the investigation

Always think step-by-step and provide clear, logical reasoning for your conclusions."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")

    async def generate_mystery_case(self, session_id: str) -> DetectiveCase:
        """Generate a complete mystery case using the Storyteller AI"""
        await self.initialize_storyteller(session_id)
        
        prompt = """Generate a complete detective mystery case with the following structure:

Create a JSON response with:
1. Case title and setting (location, time period)
2. Victim name and basic crime scene description
3. 4-5 characters with detailed backgrounds, motives, and alibis
4. 6-8 pieces of evidence with descriptions and significance
5. The complete solution explaining who did it and how

Make it challenging but solvable. Include red herrings and multiple suspects with believable motives. Set it in an interesting location like a mansion, cruise ship, or exclusive resort.

Return ONLY valid JSON with this exact structure:
{
  "title": "...",
  "setting": "...",
  "crime_scene_description": "...",
  "victim_name": "...",
  "characters": [
    {
      "name": "...",
      "description": "...",
      "background": "...",
      "alibi": "...",
      "motive": "...",
      "is_culprit": false
    }
  ],
  "evidence": [
    {
      "name": "...",
      "description": "...",
      "location_found": "...",
      "significance": "...",
      "is_key_evidence": false
    }
  ],
  "solution": "..."
}"""

        response = await self.storyteller_ai.send_message(UserMessage(text=prompt))
        
        # Parse the response and create case
        import json
        try:
            case_data = json.loads(response)
            
            # Add IDs and process data
            case_id = str(uuid.uuid4())
            characters = []
            for char in case_data.get("characters", []):
                characters.append(Character(
                    id=str(uuid.uuid4()),
                    name=char["name"],
                    description=char["description"],
                    background=char["background"],
                    alibi=char["alibi"],
                    motive=char.get("motive"),
                    is_culprit=char.get("is_culprit", False)
                ))
            
            evidence = []
            for ev in case_data.get("evidence", []):
                evidence.append(Evidence(
                    id=str(uuid.uuid4()),
                    name=ev["name"],
                    description=ev["description"],
                    location_found=ev["location_found"],
                    significance=ev["significance"],
                    is_key_evidence=ev.get("is_key_evidence", False)
                ))
            
            case = DetectiveCase(
                id=case_id,
                title=case_data["title"],
                setting=case_data["setting"],
                crime_scene_description=case_data["crime_scene_description"],
                victim_name=case_data["victim_name"],
                characters=characters,
                evidence=evidence,
                solution=case_data["solution"],
                created_at=datetime.now()
            )
            
            return case
            
        except json.JSONDecodeError:
            # Fallback case if JSON parsing fails
            return self._create_fallback_case()
    
    def _create_fallback_case(self) -> DetectiveCase:
        """Create a fallback mystery case"""
        case_id = str(uuid.uuid4())
        return DetectiveCase(
            id=case_id,
            title="Murder at Blackwood Manor",
            setting="A Victorian mansion during a thunderstorm in 1920s England",
            crime_scene_description="Lord Blackwood found dead in his locked study, a glass of brandy spilled beside him",
            victim_name="Lord Blackwood",
            characters=[
                Character(
                    id=str(uuid.uuid4()),
                    name="Lady Margaret Blackwood",
                    description="The victim's wife, elegant but cold",
                    background="Married Lord Blackwood for his fortune 10 years ago",
                    alibi="Claims she was reading in her bedroom",
                    motive="Stands to inherit everything",
                    is_culprit=False
                ),
                Character(
                    id=str(uuid.uuid4()),
                    name="Dr. Harrison",
                    description="The family physician and old friend",
                    background="Has been treating the family for 20 years",
                    alibi="Was examining medical equipment in his room",
                    motive="Lord Blackwood discovered Dr. Harrison's gambling debts",
                    is_culprit=True
                )
            ],
            evidence=[
                Evidence(
                    id=str(uuid.uuid4()),
                    name="Poisoned Brandy Glass",
                    description="A crystal glass with traces of cyanide",
                    location_found="Lord Blackwood's study desk",
                    significance="The murder weapon",
                    is_key_evidence=True
                ),
                Evidence(
                    id=str(uuid.uuid4()),
                    name="Medical Bag",
                    description="Dr. Harrison's bag with missing cyanide vial",
                    location_found="Dr. Harrison's guest room",
                    significance="Contains the poison used in the murder",
                    is_key_evidence=True
                )
            ],
            solution="Dr. Harrison poisoned Lord Blackwood's brandy with cyanide to prevent exposure of his gambling debts",
            created_at=datetime.now()
        )

    async def question_character(self, case_id: str, character_name: str, question: str, session_id: str) -> str:
        """Have a character respond to questioning using Storyteller AI"""
        await self.initialize_storyteller(session_id)
        
        # Get case details from database
        case = await db.cases.find_one({"id": case_id})
        if not case:
            return "Error: Case information not available."
        
        # Find the character details
        character = None
        for char in case["characters"]:
            if char["name"] == character_name:
                character = char
                break
        
        if not character:
            return "Error: Character not found."
        
        prompt = f"""You are roleplaying as {character_name} in the detective mystery "{case['title']}".

CHARACTER CONTEXT:
- Name: {character['name']}
- Description: {character['description']}
- Background: {character['background']}
- Your alibi: {character['alibi']}
- Possible motive: {character.get('motive', 'No clear motive')}
- Are you the culprit: {'Yes' if character.get('is_culprit', False) else 'No'}

CASE CONTEXT:
- Victim: {case['victim_name']}
- Setting: {case['setting']}
- Crime scene: {case['crime_scene_description']}

The detective is asking you: "{question}"

Respond in character with:
- Personality consistent with your background and description
- Show appropriate emotions (nervousness if guilty, concern if innocent)
- Provide helpful information but with realistic evasions if you're hiding something
- Stay true to your alibi and background
- If you're the culprit, be subtle - don't confess easily but show slight nervousness
- If innocent, be helpful but may have your own concerns or secrets

Keep responses conversational, realistic, and under 150 words. Make it feel like a real interrogation."""

        response = await self.storyteller_ai.send_message(UserMessage(text=prompt))
        return response

    async def analyze_evidence(self, case_id: str, evidence_list: List[str], theory: str, session_id: str) -> str:
        """Analyze evidence and theory using Logic AI"""
        await self.initialize_logic_ai(session_id)
        
        # Get case details from database
        case = await db.cases.find_one({"id": case_id})
        if not case:
            return "Error: Case not found for analysis."
        
        # Get full evidence details
        evidence_details = []
        for evidence_id in evidence_list:
            for evidence in case["evidence"]:
                if evidence["id"] == evidence_id:
                    evidence_details.append(f"- {evidence['name']}: {evidence['description']} (Found: {evidence['location_found']}, Significance: {evidence['significance']})")
                    break
        
        evidence_text = "\n".join(evidence_details) if evidence_details else "No specific evidence selected"
        
        prompt = f"""Analyze the following detective theory and evidence for the case "{case['title']}":

CASE CONTEXT:
- Victim: {case['victim_name']}
- Setting: {case['setting']}
- Crime Scene: {case['crime_scene_description']}

DETECTIVE'S THEORY:
{theory}

EVIDENCE BEING CONSIDERED:
{evidence_text}

AVAILABLE CHARACTERS:
{', '.join([char['name'] + ' (' + char['description'] + ')' for char in case['characters']])}

Provide a logical analysis including:
1. **Strengths of this theory** - What evidence supports it?
2. **Weaknesses or gaps** - What doesn't add up or what's missing?
3. **Evidence relationships** - How do the selected pieces connect?
4. **Additional investigation needed** - What questions or evidence would strengthen/weaken this theory?
5. **Alternative explanations** - Other possible scenarios to consider
6. **Logical consistency check** - Does the timeline and evidence chain make sense?

Provide a thorough but focused analysis that helps guide the investigation."""

        response = await self.logic_ai.send_message(UserMessage(text=prompt))
        return response

# Initialize AI service
ai_service = DualAIDetectiveService()

@app.get("/")
async def root():
    return {"message": "Dual-AI Detective Game API", "status": "active"}

@app.post("/api/generate-case")
async def generate_case():
    """Generate a new mystery case"""
    try:
        session_id = str(uuid.uuid4())
        case = await ai_service.generate_mystery_case(session_id)
        
        # Store in database
        await db.cases.insert_one(case.model_dump())
        
        # Return case without solution
        case_response = case.model_copy()
        case_response.solution = "Hidden until case is solved"
        
        return {"case": case_response, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate case: {str(e)}")

@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    """Get a specific case"""
    try:
        case = await db.cases.find_one({"id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Remove MongoDB ObjectId and solution from response
        if "_id" in case:
            del case["_id"]
        
        # Convert any ObjectId to string to ensure JSON serialization
        def convert_objectid(obj):
            from bson import ObjectId
            if isinstance(obj, dict):
                return {k: convert_objectid(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_objectid(item) for item in obj]
            elif isinstance(obj, ObjectId):
                return str(obj)
            else:
                return obj
        
        case = convert_objectid(case)
        case["solution"] = "Hidden until case is solved"
        
        return {"case": case}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve case: {str(e)}")

@app.post("/api/question-character")
async def question_character(request: QuestionRequest):
    """Question a character in the case"""
    try:
        # Get case data
        case = await db.cases.find_one({"id": request.case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Find character
        character = None
        for char in case["characters"]:
            if char["id"] == request.character_id:
                character = char
                break
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Generate response using AI
        session_id = str(uuid.uuid4())
        response = await ai_service.question_character(
            request.case_id, 
            character["name"], 
            request.question,
            session_id
        )
        
        return {"character_name": character["name"], "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to question character: {str(e)}")

@app.post("/api/analyze-evidence")
async def analyze_evidence(request: AnalysisRequest):
    """Analyze evidence and theory using Logic AI"""
    try:
        session_id = str(uuid.uuid4())
        analysis = await ai_service.analyze_evidence(
            request.case_id,
            request.evidence_ids,
            request.theory,
            session_id
        )
        
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze evidence: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "ai_services": "dual-ai-active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)