import React from 'react';

const VoiceOverlay = ({ onStop }) => {
  return (
    <div className="visualizer-overlay">
      <div className="wave-container">
        {[...Array(8)].map((_, i) => (
          <div 
            key={i} 
            className="wave-bar" 
            style={{ animationDelay: `${i * 0.1}s` }}
          />
        ))}
      </div>
      <p style={{ marginTop: '1rem', letterSpacing: '2px', fontWeight: '500', marginBottom: '2rem' }}>
        LISTENING...
      </p>
      <button className="stop-voice-btn" onClick={onStop}>
        ⏹ Stop Recording
      </button>
    </div>
  );
};

export default VoiceOverlay;
