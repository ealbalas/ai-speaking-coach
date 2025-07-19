'use client';

import { useState, useRef } from 'react';
import AnalysisReport from './AnalysisReport';

enum RecordingState {
  Idle,
  Recording,
  Stopped,
  Analyzing,
  Complete,
}

export default function Home() {
  const [recordingState, setRecordingState] = useState<RecordingState>(RecordingState.Idle);
  const [statusMessage, setStatusMessage] = useState('Click "Start Recording" to begin.');
  const [analysisReport, setAnalysisReport] = useState<any>(null);
  
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const sessionIdRef = useRef<string | null>(null); // Use a ref for the session ID

  const fetchAnalysis = async (id: string) => {
    setRecordingState(RecordingState.Analyzing);
    setStatusMessage('Analyzing your speech...');
    try {
      const response = await fetch(`http://localhost:8000/analysis/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch analysis.');
      }
      const report = await response.json();
      setAnalysisReport(report);
      setRecordingState(RecordingState.Complete);
      setStatusMessage('Analysis complete!');
    } catch (error) {
      console.error('Error fetching analysis:', error);
      setStatusMessage('Failed to get analysis. Please try again.');
      setRecordingState(RecordingState.Idle);
    }
  };

  const startRecording = async () => {
    setAnalysisReport(null);
    sessionIdRef.current = null;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setStatusMessage('Microphone access granted. Connecting to server...');
      
      const socket = new WebSocket('ws://localhost:8000/ws');
      socketRef.current = socket;

      socket.onopen = () => {
        setStatusMessage('Connected. Waiting for session ID...');
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.session_id) {
          sessionIdRef.current = data.session_id; // Store session ID in the ref
          setStatusMessage('Session started. Recording...');
          setRecordingState(RecordingState.Recording);

          const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
          mediaRecorderRef.current = mediaRecorder;

          mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
              socket.send(event.data);
            }
          };

          mediaRecorder.onstop = () => {
            if (socket.readyState === WebSocket.OPEN) {
              socket.close();
            }
            stream.getTracks().forEach(track => track.stop());
            setStatusMessage('Recording stopped. Uploading audio...');
            setRecordingState(RecordingState.Stopped);
          };
          
          mediaRecorder.start(1000);
        }
      };

      socket.onclose = () => {
        setStatusMessage('Upload complete. Preparing analysis...');
        if (sessionIdRef.current) { // Read session ID from the ref
          fetchAnalysis(sessionIdRef.current);
        } else {
            setStatusMessage('Could not get session ID. Please try again.');
            setRecordingState(RecordingState.Idle);
        }
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

  const resetSession = () => {
    setRecordingState(RecordingState.Idle);
    setStatusMessage('Click "Start Recording" to begin.');
    setAnalysisReport(null);
    sessionIdRef.current = null;
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
          {(recordingState === RecordingState.Stopped || recordingState === RecordingState.Analyzing) && (
            <p className="text-yellow-400 animate-pulse">{statusMessage}</p>
          )}
          {recordingState === RecordingState.Complete && (
             <button
             onClick={resetSession}
             className="w-full px-6 py-3 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75 transition-colors"
           >
             Start New Session
           </button>
          )}
        </div>
        {analysisReport && <AnalysisReport report={analysisReport} />}
      </div>
    </main>
  );
}