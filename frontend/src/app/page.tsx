'use client';

import { useState, useEffect, useRef } from 'react';

export default function Home() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<string[]>([]);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to the WebSocket server
    socketRef.current = new WebSocket('ws://localhost:8000/ws');

    const socket = socketRef.current;

    socket.onopen = () => {
      console.log('WebSocket connected');
      setMessages(prev => [...prev, 'Connected to server.']);
    };

    socket.onmessage = (event) => {
      setMessages(prev => [...prev, event.data]);
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
      setMessages(prev => [...prev, 'Disconnected from server.']);
    };

    // Clean up the connection when the component unmounts
    return () => {
      socket.close();
    };
  }, []);

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (socketRef.current && message) {
      socketRef.current.send(message);
      setMessage('');
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-4xl font-bold mb-4">AI Speaking Coach</h1>
      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-6">
        <div className="mb-4 h-64 overflow-y-auto border rounded p-2">
          <ul>
            {messages.map((msg, index) => (
              <li key={index}>{msg}</li>
            ))}
          </ul>
        </div>
        <form onSubmit={sendMessage}>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="Type a message..."
          />
          <button type="submit" className="w-full mt-2 p-2 bg-blue-500 text-white rounded">
            Send
          </button>
        </form>
      </div>
    </main>
  );
}
