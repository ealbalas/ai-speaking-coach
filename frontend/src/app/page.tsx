'use client';

import { useState, useRef, FC, useEffect } from 'react';
import AnalysisReport from './AnalysisReport';

enum RecordingState {
  Idle,
  Recording,
  Stopped,
  Analyzing,
  Complete,
}

interface FeedbackMessage {
    id: number;
    text: string;
}

const Home: FC = () => {
  const [recordingState, setRecordingState] = useState<RecordingState>(RecordingState.Idle);
  const [statusMessage, setStatusMessage] = useState('Click "Start Recording" to begin.');
  const [analysisReport, setAnalysisReport] = useState<any>(null);
  const [realtimeFeedback, setRealtimeFeedback] = useState<FeedbackMessage[]>([]);
  
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  useEffect(() => {
    // Automatically remove feedback messages after a delay
    if (realtimeFeedback.length > 0) {
        const timer = setTimeout(() => {
            setRealtimeFeedback(fb => fb.slice(1));
        }, 5000); // Message disappears after 5 seconds
        return () => clearTimeout(timer);
    }
  }, [realtimeFeedback]);

  const addRealtimeFeedback = (text: string) => {
    const newMessage: FeedbackMessage = { id: Date.now(), text };
    setRealtimeFeedback(fb => [...fb, newMessage]);
  };

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
    setRealtimeFeedback([]);
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
          sessionIdRef.current = data.session_id;
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
          
          mediaRecorder.start(1000); // Send data every second
        } else if (data.type === 'FILLER_WORD') {
            addRealtimeFeedback(`Filler word detected: "${data.words.join(', ')}"`);
        }
      };

      socket.onclose = () => {
        setStatusMessage('Upload complete. Preparing analysis...');
        if (sessionIdRef.current) {
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
    setRealtimeFeedback([]);
    sessionIdRef.current = null;
  };
 
  if (recordingState === RecordingState.Complete && analysisReport) {
    return (
        <main className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-900">
            <AnalysisReport report={analysisReport} onReset={resetSession} />
        </main>
    );
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-900">
      <div className="w-full max-w-md text-center">
        <h1 className="text-4xl font-bold mb-4 text-white">AI Speaking Coach</h1>
        <p className="mb-6 text-gray-300 h-10">{statusMessage}</p>
        
        {/* Real-time Feedback Display */}
        <div className="h-24 mb-4">
            {realtimeFeedback.map((msg) => (
                <div key={msg.id} className="text-yellow-400 bg-gray-700 rounded-md p-2 shadow-lg animate-fadeIn">
                    {msg.text}
                </div>
            ))}
        </div>

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
            <div className="flex justify-center items-center text-blue-400">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {statusMessage}
             </div>
          )}
        </div>
      </div>
    </main>
  );
}

export default Home;
