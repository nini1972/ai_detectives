import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [currentCase, setCurrentCase] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeCharacter, setActiveCharacter] = useState(null);
  const [question, setQuestion] = useState('');
  const [conversations, setConversations] = useState({});
  const [selectedEvidence, setSelectedEvidence] = useState([]);
  const [theory, setTheory] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [gameState, setGameState] = useState('menu'); // menu, playing, analysis
  const [investigationNotes, setInvestigationNotes] = useState('');
  const [showContextPanel, setShowContextPanel] = useState(false);

  const generateNewCase = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/generate-case`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate case');
      }
      
      const data = await response.json();
      setCurrentCase(data.case);
      setSessionId(data.session_id);
      setGameState('playing');
      setConversations({});
      setSelectedEvidence([]);
      setTheory('');
      setAnalysis('');
      setInvestigationNotes('');
      setShowContextPanel(false);
    } catch (error) {
      console.error('Error generating case:', error);
      alert('Failed to generate new case. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const questionCharacter = async () => {
    if (!question.trim() || !activeCharacter) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/question-character`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: currentCase.id,
          character_id: activeCharacter.id,
          question: question.trim()
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to question character');
      }
      
      const data = await response.json();
      
      // Add to conversations
      const charId = activeCharacter.id;
      setConversations(prev => ({
        ...prev,
        [charId]: [
          ...(prev[charId] || []),
          {
            question: question.trim(),
            response: data.response,
            timestamp: new Date().toLocaleTimeString()
          }
        ]
      }));
      
      setQuestion('');
    } catch (error) {
      console.error('Error questioning character:', error);
      alert('Failed to question character. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeEvidence = async () => {
    if (!theory.trim() || selectedEvidence.length === 0) {
      alert('Please select evidence and provide a theory to analyze.');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/analyze-evidence`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: currentCase.id,
          evidence_ids: selectedEvidence,
          theory: theory.trim()
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze evidence');
      }
      
      const data = await response.json();
      setAnalysis(data.analysis);
      setGameState('analysis');
    } catch (error) {
      console.error('Error analyzing evidence:', error);
      alert('Failed to analyze evidence. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleEvidenceSelection = (evidenceId) => {
    setSelectedEvidence(prev => 
      prev.includes(evidenceId) 
        ? prev.filter(id => id !== evidenceId)
        : [...prev, evidenceId]
    );
  };

  if (gameState === 'menu' || !currentCase) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 relative overflow-hidden">
        {/* Hero Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{
            backgroundImage: 'url(https://images.unsplash.com/photo-1652985808809-08b53267628b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwyfHxub2lyJTIwZGV0ZWN0aXZlfGVufDB8fHx8MTc0ODU5MDIxOHww&ixlib=rb-4.1.0&q=85)'
          }}
        />
        <div className="relative z-10 container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-6xl font-bold text-white mb-4 tracking-wide gradient-text">
              🕵️ DUAL-AI DETECTIVE
            </h1>
            <p className="text-xl text-blue-200 mb-8 max-w-3xl mx-auto">
              Experience the world's first detective game powered by TWO AI systems working together. 
              OpenAI creates the story, Claude analyzes the logic. Every case is unique.
            </p>
            
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 max-w-4xl mx-auto mb-8 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-6">🚀 Revolutionary Features</h2>
              <div className="grid md:grid-cols-2 gap-6 text-left">
                <div className="bg-blue-500/20 rounded-lg p-4 hover-glow">
                  <h3 className="text-lg font-semibold text-blue-300 mb-2">🎭 Storyteller AI (OpenAI)</h3>
                  <p className="text-blue-100">Creates rich narratives, develops characters, and brings suspects to life in natural conversations</p>
                </div>
                <div className="bg-purple-500/20 rounded-lg p-4 hover-glow">
                  <h3 className="text-lg font-semibold text-purple-300 mb-2">🧠 Logic AI (Claude)</h3>
                  <p className="text-purple-100">Analyzes evidence, detects contradictions, and provides logical deduction assistance</p>
                </div>
                <div className="bg-green-500/20 rounded-lg p-4 hover-glow">
                  <h3 className="text-lg font-semibold text-green-300 mb-2">🎲 Dynamic Cases</h3>
                  <p className="text-green-100">Every mystery is procedurally generated with unique characters, evidence, and solutions</p>
                </div>
                <div className="bg-orange-500/20 rounded-lg p-4 hover-glow">
                  <h3 className="text-lg font-semibold text-orange-300 mb-2">💬 Natural Investigation</h3>
                  <p className="text-orange-100">Ask suspects anything using natural language - no limited dialogue trees</p>
                </div>
              </div>
            </div>
            
            <button
              onClick={generateNewCase}
              disabled={loading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-4 px-8 rounded-xl text-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 btn-primary shadow-lg relative overflow-hidden"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <div className="loading-spinner mr-3"></div>
                  🔮 Dual-AI Creating Your Mystery...
                </span>
              ) : '🎯 Start New Investigation'}
            </button>
            
            {loading && (
              <div className="mt-6 bg-blue-500/20 backdrop-blur-md rounded-lg p-6 border border-blue-400/30">
                <div className="text-center">
                  <div className="loading-spinner mx-auto mb-4"></div>
                  <h3 className="text-xl font-semibold text-blue-300 mb-2">🤖 Dual-AI System Working...</h3>
                  <div className="space-y-2 text-blue-200">
                    <p>🎭 <strong>Storyteller AI (OpenAI)</strong> is crafting your unique mystery...</p>
                    <p>🧠 <strong>Logic AI (Claude)</strong> is ensuring all clues connect perfectly...</p>
                    <p className="text-sm text-blue-300 mt-3">This may take 10-30 seconds for the best experience</p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="mt-12 text-center">
              <h3 className="text-lg font-semibold text-white mb-4">🎮 What Makes This Special?</h3>
              <div className="flex justify-center space-x-8 text-sm">
                <div className="ai-badge storyteller">
                  <span>🎭</span> Storyteller AI
                </div>
                <div className="text-white">+</div>
                <div className="ai-badge logic">
                  <span>🧠</span> Logic AI
                </div>
                <div className="text-white">=</div>
                <div className="text-yellow-300 font-bold">Revolutionary Experience</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (gameState === 'analysis') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-8">
            <h2 className="text-3xl font-bold text-white mb-6 flex items-center">
              🧠 Logic AI Analysis
            </h2>
            
            <div className="bg-purple-500/20 rounded-lg p-6 mb-6">
              <h3 className="text-xl font-semibold text-purple-300 mb-3">Your Theory:</h3>
              <p className="text-white bg-black/20 rounded p-3">{theory}</p>
            </div>
            
            <div className="bg-blue-500/20 rounded-lg p-6 mb-6">
              <h3 className="text-xl font-semibold text-blue-300 mb-3">Claude's Analysis:</h3>
              <div className="text-white whitespace-pre-wrap bg-black/20 rounded p-4">
                {analysis}
              </div>
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={() => setGameState('playing')}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
              >
                ← Continue Investigation
              </button>
              <button
                onClick={() => setGameState('menu')}
                className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
              >
                🏠 New Case
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-orange-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">{currentCase.title}</h1>
          <p className="text-orange-200 text-lg">{currentCase.setting}</p>
          <div className="flex justify-center gap-4 mt-4">
            <button
              onClick={() => setGameState('menu')}
              className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
            >
              🏠 New Case
            </button>
            <button
              onClick={() => setShowContextPanel(!showContextPanel)}
              className={`font-bold py-2 px-4 rounded-lg transition-colors ${
                showContextPanel 
                  ? 'bg-green-600 hover:bg-green-700 text-white' 
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {showContextPanel ? '📋 Hide Detective Info' : '📋 Show Detective Info'}
            </button>
          </div>
        </div>

        {/* Context Panel - Shows all case info for reference while questioning */}
        {showContextPanel && (
          <div className="mb-8 bg-gray-800/50 backdrop-blur-md rounded-xl p-6 border border-gray-600">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
              📋 Detective Reference Panel
            </h2>
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Quick Suspect Reference */}
              <div>
                <h3 className="text-lg font-semibold text-blue-300 mb-3">👥 All Suspects</h3>
                <div className="space-y-2 text-sm">
                  {currentCase.characters.map((char) => (
                    <div key={char.id} className="bg-blue-500/10 rounded p-2">
                      <strong className="text-blue-300">{char.name}</strong>: {char.description}
                      {char.motive && <div className="text-red-300">Motive: {char.motive}</div>}
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Quick Evidence Reference */}
              <div>
                <h3 className="text-lg font-semibold text-green-300 mb-3">🔍 All Evidence</h3>
                <div className="space-y-2 text-sm">
                  {currentCase.evidence.map((ev) => (
                    <div key={ev.id} className="bg-green-500/10 rounded p-2">
                      <strong className="text-green-300">{ev.name}</strong>: {ev.description}
                      <div className="text-gray-300">Found: {ev.location_found}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Crime Scene & Characters */}
          <div className="lg:col-span-2 space-y-6">
            {/* Crime Scene */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                🕵️ Crime Scene
              </h2>
              <div className="bg-red-500/20 rounded-lg p-4 mb-4">
                <h3 className="text-lg font-semibold text-red-300 mb-2">Victim: {currentCase.victim_name}</h3>
                <p className="text-white">{currentCase.crime_scene_description}</p>
              </div>
            </div>

            {/* Characters */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
              <h2 className="text-2xl font-bold text-white mb-4">👥 Suspects</h2>
              <div className="grid gap-4">
                {currentCase.characters.map((character) => (
                  <div 
                    key={character.id}
                    className={`bg-orange-500/20 rounded-lg p-4 cursor-pointer transition-all ${
                      activeCharacter?.id === character.id ? 'ring-2 ring-orange-400 bg-orange-500/30' : 'hover:bg-orange-500/30'
                    }`}
                    onClick={() => {
                      console.log('Character clicked:', character.name);
                      setActiveCharacter(character);
                      console.log('Active character set to:', character);
                    }}
                  >
                    <h3 className="text-lg font-semibold text-orange-300 mb-2">{character.name}</h3>
                    <p className="text-white text-sm mb-2">{character.description}</p>
                    <p className="text-orange-200 text-xs"><strong>Background:</strong> {character.background}</p>
                    <p className="text-orange-200 text-xs"><strong>Alibi:</strong> {character.alibi}</p>
                    {character.motive && (
                      <p className="text-red-300 text-xs mt-2"><strong>Possible Motive:</strong> {character.motive}</p>
                    )}
                    
                    {/* Question Interface - appears only for selected character */}
                    {activeCharacter?.id === character.id && (
                      <div className="mt-4 bg-black/30 rounded-lg p-4 border border-orange-400/30">
                        <h4 className="text-md font-semibold text-white mb-3 flex items-center">
                          💬 Question {character.name}
                        </h4>
                        <div className="flex gap-3 mb-4">
                          <input
                            type="text"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            placeholder="Ask anything... (e.g., 'Where were you at 9pm?' or 'What did you think of the victim?')"
                            className="flex-1 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-gray-400 text-sm"
                            onKeyPress={(e) => e.key === 'Enter' && questionCharacter()}
                          />
                          <button
                            onClick={questionCharacter}
                            disabled={loading || !question.trim()}
                            className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 text-sm"
                          >
                            {loading ? '💭' : 'Ask'}
                          </button>
                        </div>
                        
                        {/* Show conversation history for this character */}
                        {conversations[character.id] && conversations[character.id].length > 0 && (
                          <div className="space-y-2">
                            <h5 className="text-sm font-semibold text-orange-300">Conversation:</h5>
                            {conversations[character.id].map((conv, idx) => (
                              <div key={idx} className="bg-black/40 rounded p-3 text-sm">
                                <p className="text-yellow-300 mb-1"><strong>You:</strong> {conv.question}</p>
                                <p className="text-white"><strong>{character.name}:</strong> {conv.response}</p>
                                <p className="text-gray-400 text-xs mt-1">{conv.timestamp}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Evidence & Analysis Panel */}
          <div className="space-y-6">
            {/* Detective Notebook */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                📝 Detective Notebook
              </h2>
              <p className="text-gray-300 text-sm mb-3">
                Keep track of your findings, suspicions, and connections. This is your private notepad.
              </p>
              <textarea
                value={investigationNotes}
                onChange={(e) => setInvestigationNotes(e.target.value)}
                placeholder="Write your investigation notes here...
Example:
- Lady Margaret seemed nervous when asked about the insurance
- Dr. Harrison had access to the poison
- The butler was acting suspicious..."
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-3 text-white placeholder-gray-400 text-sm h-40 resize-none"
              />
              <div className="flex justify-between items-center mt-3">
                <span className="text-xs text-gray-400">
                  {investigationNotes.length} characters
                </span>
                <button
                  onClick={() => setInvestigationNotes('')}
                  className="text-xs text-red-300 hover:text-red-400 transition-colors"
                >
                  Clear Notes
                </button>
              </div>
            </div>

            {/* Evidence */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
              <h2 className="text-2xl font-bold text-white mb-4">🔍 Evidence Board</h2>
              <p className="text-gray-300 text-sm mb-3">
                Click evidence to add to your theory analysis. Selected items will be highlighted.
              </p>
              <div className="space-y-3">
                {currentCase.evidence.map((evidence) => (
                  <div 
                    key={evidence.id}
                    className={`bg-blue-500/20 rounded-lg p-3 cursor-pointer transition-all ${
                      selectedEvidence.includes(evidence.id) ? 'ring-2 ring-blue-400 bg-blue-500/30' : 'hover:bg-blue-500/30'
                    }`}
                    onClick={() => toggleEvidenceSelection(evidence.id)}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <h3 className="text-md font-semibold text-blue-300">{evidence.name}</h3>
                      {selectedEvidence.includes(evidence.id) && (
                        <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">SELECTED</span>
                      )}
                    </div>
                    <p className="text-white text-sm mb-1">{evidence.description}</p>
                    <p className="text-blue-200 text-xs"><strong>Found:</strong> {evidence.location_found}</p>
                    <p className="text-blue-200 text-xs"><strong>Significance:</strong> {evidence.significance}</p>
                    {evidence.is_key_evidence && (
                      <span className="inline-block mt-2 bg-yellow-500 text-black text-xs px-2 py-1 rounded">
                        KEY EVIDENCE
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Theory Analysis */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6">
              <h2 className="text-xl font-bold text-white mb-4">🧠 Final Theory Analysis</h2>
              <p className="text-gray-300 text-sm mb-3">
                When you're ready to test a complete theory, describe who did it and why. Claude will analyze the logic.
              </p>
              
              {selectedEvidence.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-blue-300 mb-2">Selected Evidence:</h3>
                  <div className="text-xs text-blue-200 bg-blue-500/10 rounded p-2">
                    {selectedEvidence.map(id => {
                      const evidence = currentCase.evidence.find(e => e.id === id);
                      return evidence ? evidence.name : '';
                    }).join(', ')}
                  </div>
                </div>
              )}
              
              <textarea
                value={theory}
                onChange={(e) => setTheory(e.target.value)}
                placeholder="My theory is that [suspect name] committed the murder because...

Include:
- Who did it
- How they did it  
- Why they did it
- How the evidence supports this"
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-gray-400 text-sm h-32 mb-4"
              />
              
              <button
                onClick={analyzeEvidence}
                disabled={loading || !theory.trim() || selectedEvidence.length === 0}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? '🧠 Claude is Analyzing...' : '🔍 Analyze Theory with Logic AI'}
              </button>
              
              <p className="text-xs text-gray-400 mt-2">
                💡 Tip: Select evidence and write a complete theory for best analysis results
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;