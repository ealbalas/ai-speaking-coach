'use client';

import { useState, useRef } from 'react';

enum RecordingState {
  Idle,
  Recording,
  Stopped,
}

export default function Home() {
  const [recordingState, setRecordingState] = useState<RecordingState>(RecordingState.Idle);
  const [statusMessage, setStatusMessage] = useState('Click "Start Recording" to begin.');
  
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setStatusMessage('Microphone access granted. Connecting to server...');
      
      const socket = new WebSocket('ws://localhost:8000/ws');
      socketRef.current = socket;

      socket.onopen = () => {
        setStatusMessage('Connected. Starting recording...');
        setRecordingState(RecordingState.Recording);

        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
            socket.send(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          // When recording stops, close the WebSocket connection from the client side.
          // This will trigger the backend to save the file.
          if (socket.readyState === WebSocket.OPEN) {
            socket.close();
          }
          stream.getTracks().forEach(track => track.stop()); // Stop microphone access
          setStatusMessage('Recording stopped. Audio sent to server for processing.');
          setRecordingState(RecordingState.Stopped);
        };
        
        // Send audio in chunks every second
        mediaRecorder.start(1000); 
      };

      socket.onclose = () => {
        setStatusMessage('Connection closed. Ready to start a new session.');
        setRecordingState(RecordingState.Idle);
      };

      socket.onerror = (error) => {
        console.error('WebSocket Error:', error);
        setStatusMessage('Connection error. Please try again.');
        setRecordingState(RecordingState.Idle);
      };

    } catch (error) {
      console.error('Error getting user media:', error);
      setStatusMessage('Could not access microphone. Please check permissions and try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-900">
      <div className="w-full max-w-md text-center">
        <h1 className="text-4xl font-bold mb-4 text-white">AI Speaking Coach</h1>
        <p className="mb-6 text-gray-300">{statusMessage}</p>
        <div className="bg-gray-800 rounded-lg shadow-md p-6">
          {recordingState === RecordingState.Idle && (
            <button
              onClick={startRecording}
              className="w-full px-6 py-3 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75 transition-colors"
            >
              Start Recording
            </button>
          )}
          {recordingState === RecordingState.Recording && (
            <button
              onClick={stopRecording}
              className="w-full px-6 py-3 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-opacity-75 transition-colors"
            >
              Stop Recording
            </button>
          )}
            {recordingState === RecordingState.Stopped && (
              <p className="text-green-400">Session complete!</p>
            )}
        </div>
      </div>
    </main>
  );
