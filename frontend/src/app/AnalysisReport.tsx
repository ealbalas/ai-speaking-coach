'use client';

import React from 'react';

interface AnalysisReportProps {
  report: {
    transcript: string;
    vocal_delivery: {
      speaking_rate: number;
      pitch_variance: number;
      long_pauses_count: number;
    };
    content: {
      filler_word_counts: Record<string, number>;
      clarity_score: number;
      suggestions: string[];
    };
  };
}

const AnalysisReport: React.FC<AnalysisReportProps> = ({ report }) => {
  return (
    <div className="mt-6 w-full text-left p-6 bg-gray-800 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-white">Analysis Report</h2>
      
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-gray-300">Transcript</h3>
        <p className="text-gray-400">{report.transcript}</p>
      </div>

      <div className="mb-4">
        <h3 className="text-xl font-semibold text-gray-300">Vocal Delivery</h3>
        <ul className="list-disc list-inside text-gray-400">
          <li>Speaking Rate: {report.vocal_delivery.speaking_rate.toFixed(2)} WPM</li>
          <li>Pitch Variance: {report.vocal_delivery.pitch_variance.toFixed(2)}</li>
          <li>Long Pauses: {report.vocal_delivery.long_pauses_count}</li>
        </ul>
      </div>

      <div>
        <h3 className="text-xl font-semibold text-gray-300">Content Analysis</h3>
        <ul className="list-disc list-inside text-gray-400">
          <li>Clarity Score: {report.content.clarity_score}/10</li>
          <li>Filler Words:
            <ul className="list-disc list-inside ml-4">
              {Object.entries(report.content.filler_word_counts).map(([word, count]) => (
                <li key={word}>{word}: {count}</li>
              ))}
            </ul>
          </li>
          <li>Suggestions:
            <ul className="list-disc list-inside ml-4">
              {report.content.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default AnalysisReport;
