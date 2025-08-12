import React, { useState, useEffect } from "react";

function LoadingComponent() {
  const [frame, setFrame] = useState(0);
  
  const frames = [
    "[ * * * ]",
    "[ > * * ]", 
    "[ * > * ]",
    "[ * * > ]",
    "[ * * < ]",
    "[ * < * ]",
    "[ < * * ]"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setFrame(prev => (prev + 1) % frames.length);
    }, 200);
    
    return () => clearInterval(interval);
  }, [frames.length]);

  return (
    <div style={{ fontFamily: 'monospace', textAlign: 'center', padding: '20px' }}>
      <div>Loading awesome data...</div>
      <div style={{ marginTop: '10px', fontSize: '14px' }}>
        {frames[frame]}
      </div>
    </div>
  );
}

export default LoadingComponent;
