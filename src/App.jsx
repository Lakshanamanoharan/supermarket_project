import React, { useState, useRef, useEffect } from 'react';
import Cart from './components/Cart';
import VoiceOverlay from './components/VoiceOverlay';
import Receipt from './components/Receipt';
import './index.css';

// Generate a random session ID on load
const SESSION_ID = Math.random().toString(36).substring(7);

function App() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'வணக்கம்! நான் உங்கள் சூப்பர் மார்க்கெட் உதவியாளர். நான் உங்களுக்கு எப்படி உதவ முடியும்? \n (Hello! I am your supermarket assistant. How can I help you today?)', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  ]);
  const [cart, setCart] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [showVisualizer, setShowVisualizer] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [preferredLang, setPreferredLang] = useState('auto'); // auto, en, ta
  const [isTyping, setIsTyping] = useState(false);
  const [receiptData, setReceiptData] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messageEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const scrollToBottom = () => {
    messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      role: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: text,
          session_id: SESSION_ID,
          preferred_lang: preferredLang
        })
      });
      
      const data = await response.json();

      setIsTyping(false);

      const botMessage = {
        role: 'bot',
        text: data.text,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      if (data.cart) {
        setCart([...data.cart]);
      }
      
      if (data.action === 'checkout_success') {
        setReceiptData({
          receipt_items: data.receipt_items,
          total_amount: data.total_amount,
          delivery_mode: data.delivery_mode || 'pickup',
          delivery_address: data.delivery_address || ''
        });
      }

      // Feature 1: Trigger Text-to-Speech
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // Clear queued speech
        const plainText = data.text.replace(/[*_~`#>\-]/g, '');
        const utterance = new SpeechSynthesisUtterance(plainText);
        
        const voices = window.speechSynthesis.getVoices();
        
        let targetVoice = null;
        if (preferredLang === 'ta' || /[^\x00-\x7F]/.test(data.text)) {
          utterance.lang = 'ta-IN';
          targetVoice = voices.find(v => v.lang.includes('ta') || v.name.toLowerCase().includes('tamil'));
        } else {
          utterance.lang = 'en-US';
          targetVoice = voices.find(v => v.lang.includes('en-us') || v.lang.includes('en-US') || v.name.toLowerCase().includes('english'));
        }
        
        if (targetVoice) utterance.voice = targetVoice;
        
        utterance.rate = 1.0;
        utterance.pitch = 1.05;

        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        
        window.speechSynthesis.speak(utterance);
      }
      
    } catch (error) {
      console.error("Failed to connect to backend:", error);
      setIsTyping(false);
      setMessages(prev => [...prev, { role: 'bot', text: "Server is currently unreachable. Please try again later.", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
    }
  };

  const toggleVoice = () => {
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      setShowVisualizer(false);
    } else {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert("Speech recognition is not supported in your browser. Please use Chrome.");
        return;
      }

      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = preferredLang === 'ta' ? 'ta-IN' : 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
        setShowVisualizer(true);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        handleSend(transcript);
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        setIsRecording(false);
        setShowVisualizer(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
        setShowVisualizer(false);
      };

      recognitionRef.current = recognition;
      try {
        recognition.start();
      } catch (e) {
        console.error(e);
      }
    }
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  return (
    <div className="app-container">
      <div className="chat-section">
        <header className="chat-header">
          <div className="bot-info">
            <div className="bot-avatar">AI</div>
            <div>
              <h3>Supermarket Bot</h3>
              <div className="status-indicator">
                <span className="status-dot"></span>
                Online
              </div>
            </div>
          </div>
          <div className="header-actions">
            <select 
              className="lang-selector"
              value={preferredLang}
              onChange={(e) => setPreferredLang(e.target.value)}
            >
              <option value="auto">Auto-Detect Language</option>
              <option value="en">English (ஆங்கிலம்)</option>
              <option value="ta">Tamil (தமிழ்)</option>
            </select>
            <button className="voice-btn" onClick={() => alert('Call Started...')}>📞</button>
          </div>
        </header>

        <div className="info-banner">
          <span className="info-icon">💡</span>
          <span>
            {preferredLang === 'ta' 
              ? "குறிப்பு: பொருட்களைச் சேர்க்க 'add' (சேர்) அல்லது நீக்க 'remove' (நீக்கு) போன்ற வார்த்தைகளைப் பயன்படுத்தவும்."
              : "Tip: The agent understands keywords like 'add' or 'remove' to manage your cart."}
          </span>
        </div>


        <div className="message-list">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-text">{msg.text}</div>
              <div className="message-time">{msg.time}</div>
            </div>
          ))}
          {isTyping && (
            <div className="message bot typing-indicator">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          )}
          <div ref={messageEndRef} />
        </div>

        <div className="input-section">
          <input 
            type="text" 
            className="chat-input" 
            placeholder={preferredLang === 'ta' ? "உங்கள் ஆர்டரை இங்கே தட்டச்சு செய்யவும்..." : "Type your order here..."}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend(inputValue)}
          />
          {isSpeaking ? (
            <button 
              className="voice-btn recording stop-speech"
              onClick={stopSpeaking}
              title="Stop Audio"
            >
              🔇
            </button>
          ) : (
            <button 
              className={`voice-btn ${isRecording ? 'recording' : ''}`}
              onClick={toggleVoice}
              title="Voice Input"
            >
              {isRecording ? '⏹' : '🎤'}
            </button>
          )}
          <button 
            className="send-btn"
            onClick={() => handleSend(inputValue)}
            disabled={!inputValue.trim()}
          >
            ➤
          </button>
          <button 
            className={`voice-btn ${isRecording ? 'recording' : ''}`}
            onClick={toggleVoice}
            title="Voice Input"
          >
            {isRecording ? '⏹' : '🎤'}
          </button>
        </div>

        {showVisualizer && <VoiceOverlay onStop={toggleVoice} />}
      </div>

      <Cart cart={cart} onRemoveItem={(itemName) => handleSend(`remove ${itemName}`)} />
      
      {receiptData && <Receipt data={receiptData} onClose={() => setReceiptData(null)} />}
    </div>
  );
}

export default App;


