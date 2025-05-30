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
  const [savedGames, setSavedGames] = useState([]);
  const [showSaveLoad, setShowSaveLoad] = useState(false);
  const [newCharacterNotifications, setNewCharacterNotifications] = useState([]);

  // Load saved games from localStorage on component mount
  useEffect(() => {
    const saved = localStorage.getItem('detective_saved_games');
    if (saved) {
      try {
        const parsedSaves = JSON.parse(saved);
        setSavedGames(parsedSaves);
      } catch (error) {
        console.error('Error parsing saved games:', error);
        localStorage.removeItem('detective_saved_games'); // Clear corrupted data
      }
    }
  }, []);

  // Save current game state
  const saveGame = (saveName) => {
    if (!currentCase) {
      alert('No active case to save!');
      return;
    }

    try {
      const gameData = {
        id: Date.now().toString(),
        name: saveName || `Case: ${currentCase.title}`,
        timestamp: new Date().toLocaleString(),
        currentCase,
        sessionId,
        conversations,
        investigationNotes,
        selectedEvidence,
        theory,
        analysis,
        gameState
      };

      const updatedSaves = [...savedGames, gameData];
      
      // Update localStorage first
      localStorage.setItem('detective_saved_games', JSON.stringify(updatedSaves));
      
      // Then update state
      setSavedGames(updatedSaves);
      
      alert(`✅ Game saved successfully as: ${gameData.name}`);
      setShowSaveLoad(false);
      
      console.log('Game saved:', gameData.name);
      console.log('Total saves:', updatedSaves.length);
    } catch (error) {
      console.error('Error saving game:', error);
      alert('❌ Failed to save game. Please try again.');
    }
  };

  // Load a saved game
  const loadGame = (saveData) => {
    try {
      setCurrentCase(saveData.currentCase);
      setSessionId(saveData.sessionId);
      setConversations(saveData.conversations || {});
      setInvestigationNotes(saveData.investigationNotes || '');
      setSelectedEvidence(saveData.selectedEvidence || []);
      setTheory(saveData.theory || '');
      setAnalysis(saveData.analysis || '');
      setGameState(saveData.gameState || 'playing');
      setShowSaveLoad(false);
      
      alert(`✅ Loaded: ${saveData.name}`);
      console.log('Game loaded:', saveData.name);
    } catch (error) {
      console.error('Error loading game:', error);
      alert('❌ Failed to load game. Please try again.');
    }
  };

  // Delete a saved game
  const deleteSave = (saveId) => {
    if (window.confirm('Are you sure you want to delete this saved game?')) {
      try {
        const updatedSaves = savedGames.filter(save => save.id !== saveId);
        localStorage.setItem('detective_saved_games', JSON.stringify(updatedSaves));
        setSavedGames(updatedSaves);
        console.log('Game deleted, remaining saves:', updatedSaves.length);
      } catch (error) {
        console.error('Error deleting save:', error);
        alert('❌ Failed to delete save. Please try again.');
      }
    }
  };

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
      
      // Handle dynamic character discovery
      if (data.new_characters_discovered && data.new_characters_discovered.length > 0) {
        console.log('New characters discovered:', data.new_characters_discovered);
        
        // Update the current case with new characters
        setCurrentCase(prev => ({
          ...prev,
          characters: [...prev.characters, ...data.new_characters_discovered.map(discovery => discovery.character)]
        }));
        
        // Show notifications for new characters
        const notifications = data.new_characters_discovered.map(discovery => ({
          id: Date.now() + Math.random(),
          character: discovery.character,
          discoveredThrough: discovery.discovered_through,
          context: discovery.context,
          timestamp: Date.now()
        }));
        
        console.log('Setting notifications:', notifications);
        setNewCharacterNotifications(prev => [...prev, ...notifications]);
        
        // Auto-dismiss notifications after 10 seconds
        setTimeout(() => {
          setNewCharacterNotifications(prev => 
            prev.filter(notification => 
              !notifications.some(newNotif => newNotif.id === notification.id)
            )
          );
        }, 10000);
      }
      
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
        <div className="relative z-10 container mx-auto px-4 py-8 min-h-screen">
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
            
            <div className="flex gap-4 mt-6 justify-center">
              <button
                onClick={() => setShowSaveLoad(true)}
                className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
              >
                💾 Load Saved Game
              </button>
            </div>
            
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
        
        {/* Save/Load Modal for Homepage */}
        {showSaveLoad && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <h2 className="text-3xl font-bold text-white mb-6 flex items-center">
                💾 Load Saved Games
              </h2>
              
              {/* Load Saved Games */}
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-blue-300 mb-3">Your Saved Investigations</h3>
                {savedGames.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-400 text-lg mb-4">No saved games found.</p>
                    <p className="text-gray-500 text-sm">Start a new investigation and save your progress to see saved games here.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {savedGames.map((save) => (
                      <div key={save.id} className="bg-blue-500/20 rounded-lg p-4 flex justify-between items-center">
                        <div>
                          <h4 className="text-white font-semibold">{save.name}</h4>
                          <p className="text-gray-300 text-sm">Saved: {save.timestamp}</p>
                          <p className="text-blue-300 text-xs">
                            Progress: {Object.keys(save.conversations).length} conversations, 
                            {save.investigationNotes.length} chars in notes
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => loadGame(save)}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-3 rounded transition-colors text-sm"
                          >
                            📂 Load
                          </button>
                          <button
                            onClick={() => deleteSave(save.id)}
                            className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-3 rounded transition-colors text-sm"
                          >
                            🗑️ Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Close Modal */}
              <div className="flex justify-end">
                <button
                  onClick={() => setShowSaveLoad(false)}
                  className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                >
                  ❌ Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (gameState === 'analysis') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900">
        <div className="container mx-auto px-4 py-8 min-h-screen">
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
      <div className="container mx-auto px-4 py-8 min-h-screen">
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
              onClick={() => setShowSaveLoad(true)}
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
            >
              💾 Save/Load Game
            </button>
            <button
              onClick={() => setShowContextPanel(!showContextPanel)}
              className={`font-bold py-2 px-4 rounded-lg transition-colors ${
                showContextPanel 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white' 
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
            {/* New Character Discovery Notifications */}
            {newCharacterNotifications.length > 0 && (
              <div className="space-y-3">
                {newCharacterNotifications.map((notification) => (
                  <div 
                    key={notification.id}
                    className="bg-yellow-500/20 border-l-4 border-yellow-500 rounded-lg p-4 animate-fadeInUp"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-semibold text-yellow-300 mb-2 flex items-center">
                          🔍 New Lead Discovered!
                        </h3>
                        <p className="text-white mb-2">
                          <strong>{notification.discoveredThrough}</strong> mentioned: <strong>{notification.character.name}</strong>
                        </p>
                        <p className="text-yellow-200 text-sm italic">"{notification.context}"</p>
                        <p className="text-gray-300 text-sm mt-2">
                          {notification.character.name} is now available for questioning below.
                        </p>
                      </div>
                      <button
                        onClick={() => setNewCharacterNotifications(prev => 
                          prev.filter(n => n.id !== notification.id)
                        )}
                        className="text-yellow-400 hover:text-yellow-300 text-xl"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

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
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                👥 Suspects & Persons of Interest
                <span className="ml-3 text-sm bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                  {currentCase.characters.length} Total
                </span>
              </h2>
              <div className="grid gap-4">
                {currentCase.characters.map((character) => {
                  const isNewCharacter = newCharacterNotifications.some(n => n.character.id === character.id);
                  
                  return (
                    <div 
                      key={character.id}
                      className={`bg-orange-500/20 rounded-lg p-4 cursor-pointer transition-all ${
                        activeCharacter?.id === character.id ? 'ring-2 ring-orange-400 bg-orange-500/30' : 'hover:bg-orange-500/30'
                      } ${isNewCharacter ? 'ring-2 ring-yellow-400 animate-pulse' : ''}`}
                      onClick={() => setActiveCharacter(character)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-semibold text-orange-300">{character.name}</h3>
                        {character.is_dynamic && (
                          <span className="text-xs bg-yellow-500 text-black px-2 py-1 rounded font-bold">
                            NEW LEAD
                          </span>
                        )}
                      </div>
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
                );
                })}
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
      
      {/* Save/Load Modal */}
      {showSaveLoad && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-3xl font-bold text-white mb-6 flex items-center">
              💾 Save & Load Games
            </h2>
            
            {/* Save Current Game */}
            {currentCase && (
              <div className="mb-6 bg-green-500/20 rounded-lg p-4">
                <h3 className="text-xl font-semibold text-green-300 mb-3">Save Current Investigation</h3>
                <p className="text-gray-300 text-sm mb-3">Current case: {currentCase.title}</p>
                <button
                  onClick={() => {
                    const defaultName = `${currentCase.title} - ${new Date().toLocaleDateString()}`;
                    const saveName = window.prompt('Enter a name for this save:', defaultName);
                    if (saveName && saveName.trim()) {
                      saveGame(saveName.trim());
                    }
                  }}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                >
                  💾 Save Current Progress
                </button>
              </div>
            )}
            
            {/* Load Saved Games */}
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-blue-300 mb-3">Load Saved Games</h3>
              {savedGames.length === 0 ? (
                <p className="text-gray-400 text-sm">No saved games found.</p>
              ) : (
                <div className="space-y-3">
                  {savedGames.map((save) => (
                    <div key={save.id} className="bg-blue-500/20 rounded-lg p-4 flex justify-between items-center">
                      <div>
                        <h4 className="text-white font-semibold">{save.name}</h4>
                        <p className="text-gray-300 text-sm">Saved: {save.timestamp}</p>
                        <p className="text-blue-300 text-xs">
                          Progress: {Object.keys(save.conversations).length} conversations, 
                          {save.investigationNotes.length} chars in notes
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => loadGame(save)}
                          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-3 rounded transition-colors text-sm"
                        >
                          📂 Load
                        </button>
                        <button
                          onClick={() => deleteSave(save.id)}
                          className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-3 rounded transition-colors text-sm"
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Close Modal */}
            <div className="flex justify-end">
              <button
                onClick={() => setShowSaveLoad(false)}
                className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
              >
                ❌ Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;