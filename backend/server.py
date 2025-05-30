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

    async def question_character(self, case_id: str, character_name: str, question: str, session_id: str) -> dict:
        """Have a character respond to questioning using Storyteller AI and detect new character mentions"""
        await self.initialize_storyteller(session_id)
        await self.initialize_logic_ai(session_id)
        
        # Get case details from database
        case = await db.cases.find_one({"id": case_id})
        if not case:
            return {"error": "Case information not available."}
        
        # Find the character details
        character = None
        for char in case["characters"]:
            if char["name"] == character_name:
                character = char
                break
        
        if not character:
            return {"error": "Character not found."}
        
        # Get all existing character names for context
        existing_names = [char["name"] for char in case["characters"]]
        
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
- Other people involved: {', '.join(existing_names)}

The detective is asking you: "{question}"

IMPORTANT: You may naturally mention other people who could be relevant to the investigation - staff members, visitors, family, neighbors, etc. Be realistic about who might have been around or involved.

Respond in character with:
- Personality consistent with your background and description
- Show appropriate emotions (nervousness if guilty, concern if innocent)
- Provide helpful information but with realistic evasions if you're hiding something
- Stay true to your alibi and background
- If you're the culprit, be subtle - don't confess easily but show slight nervousness
- If innocent, be helpful but may have your own concerns or secrets
- Naturally mention other people if relevant (e.g., "The gardener was acting strange that day" or "I saw the cook leaving early")

Keep responses conversational, realistic, and under 150 words. Make it feel like a real interrogation."""

        response = await self.storyteller_ai.send_message(UserMessage(text=prompt))
        
        # Now detect if any new characters were mentioned
        detection_prompt = f"""Analyze the following conversation for mentions of NEW people who could potentially be questioned in this detective investigation.

CONVERSATION:
Detective: "{question}"
{character_name}: "{response}"

EXISTING CHARACTERS (do not include these): {', '.join(existing_names)}

Look for mentions of:
- Staff members (gardener, cook, maid, butler, driver, etc.)
- Visitors or guests
- Neighbors or locals
- Family members not yet listed
- Service people (delivery person, mailman, doctor, etc.)
- Anyone else who might have been present or relevant

For each NEW person mentioned, extract:
1. Their role/title (e.g., "gardener", "cook", "delivery person")
2. Any descriptive context from the conversation

Return a JSON array of new characters found:
[
  {
    "role": "role/title",
    "context": "what was said about them"
  }
]

If no new people are mentioned, return an empty array: []

Return ONLY the JSON array, nothing else."""

        mentions_response = await self.logic_ai.send_message(UserMessage(text=detection_prompt))
        
        # Parse the mentions
        try:
            import json
            new_mentions = json.loads(mentions_response.strip())
        except:
            new_mentions = []
        
        return {
            "response": response,
            "new_character_mentions": new_mentions
        }

    async def generate_dynamic_character(self, case_id: str, role: str, context: str, session_id: str) -> Character:
        """Generate a new character based on a mention in conversation"""
        await self.initialize_storyteller(session_id)
        await self.initialize_logic_ai(session_id)
        
        # Get case details
        case = await db.cases.find_one({"id": case_id})
        if not case:
            return None
            
        prompt = f"""Create a new character for the detective mystery "{case['title']}" based on this mention:

CASE CONTEXT:
- Title: {case['title']}
- Setting: {case['setting']}
- Victim: {case['victim_name']}
- Crime scene: {case['crime_scene_description']}

CHARACTER MENTION:
- Role: {role}
- Context: {context}

Create a detailed character with:
1. A realistic name that fits the setting/time period
2. Physical description appropriate for their role
3. Background and how they relate to the case/location
4. A believable alibi for the time of the crime
5. A potential motive (even if weak) that could make them a person of interest
6. Make them a viable suspect but not obviously guilty

Return ONLY a JSON object with this structure:
{{
  "name": "Full Name",
  "description": "Brief physical description and personality",
  "background": "Their role, history, and connection to the case",
  "alibi": "What they claim they were doing during the crime",
  "motive": "Potential reason they might be involved (or 'No clear motive')"
}}"""

        response = await self.storyteller_ai.send_message(UserMessage(text=prompt))
        
        # Parse the character data
        try:
            import json
            char_data = json.loads(response.strip())
            
            # Validate with Logic AI
            validation_prompt = f"""Review this dynamically generated character for logical consistency:

CASE: {case['title']}
SETTING: {case['setting']}
NEW CHARACTER: {json.dumps(char_data, indent=2)}
ORIGINAL MENTION: "{context}"

Check:
1. Does the character fit the setting and time period?
2. Is their background realistic for their role?
3. Does their alibi make sense?
4. Is their potential motive believable?
5. Do they add value to the investigation?

If valid, respond with: VALID
If issues found, suggest improvements in this format: 
ISSUES: [list problems]
SUGGESTIONS: [improvements]"""

            validation = await self.logic_ai.send_message(UserMessage(text=validation_prompt))
            
            if "VALID" in validation:
                character = Character(
                    id=str(uuid.uuid4()),
                    name=char_data["name"],
                    description=char_data["description"],
                    background=char_data["background"],
                    alibi=char_data["alibi"],
                    motive=char_data.get("motive"),
                    is_culprit=False  # Dynamic characters are never the original culprit
                )
                return character
            else:
                print(f"Character validation failed: {validation}")
                return None
                
        except Exception as e:
            print(f"Error generating dynamic character: {e}")
            return None

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
        
        # Generate response using AI and detect new character mentions
        session_id = str(uuid.uuid4())
        result = await ai_service.question_character(
            request.case_id, 
            character["name"], 
            request.question,
            session_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        response_data = {
            "character_name": character["name"], 
            "response": result["response"],
            "new_characters_discovered": []
        }
        
        # Process any new character mentions
        if result["new_character_mentions"]:
            for mention in result["new_character_mentions"]:
                # Generate the new character
                new_character = await ai_service.generate_dynamic_character(
                    request.case_id,
                    mention["role"],
                    mention["context"],
                    session_id
                )
                
                if new_character:
                    # Add to case in database
                    await db.cases.update_one(
                        {"id": request.case_id},
                        {"$push": {"characters": new_character.model_dump()}}
                    )
                    
                    response_data["new_characters_discovered"].append({
                        "character": new_character.model_dump(),
                        "discovered_through": character["name"],
                        "context": mention["context"]
                    })
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to question character: {str(e)}")

@app.post("/api/generate-dynamic-character")
async def generate_dynamic_character_endpoint(case_id: str, role: str, context: str):
    """Generate a new character based on a mention"""
    try:
        session_id = str(uuid.uuid4())
        character = await ai_service.generate_dynamic_character(case_id, role, context, session_id)
        
        if character:
            # Add to case in database
            await db.cases.update_one(
                {"id": case_id},
                {"$push": {"characters": character.model_dump()}}
            )
            return {"character": character.model_dump()}
        else:
            raise HTTPException(status_code=500, detail="Failed to generate character")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dynamic character: {str(e)}")

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