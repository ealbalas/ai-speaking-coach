'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import { 
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface AnalysisReportProps {
  report: {
    transcript: string;
    vocal_delivery: {
      speaking_rate: number;
      pitch_variance: number;
      long_pauses_count: number;
      pitch_over_time: number[];
      pace_over_time: number[];
    };
    content: {
      filler_word_counts: Record<string, number>;
      clarity_score: number;
      suggestions: string[];
      improved_sentence: string;
    };
  };
  onReset: () => void;
}

const AnalysisReport: React.FC<AnalysisReportProps> = ({ report, onReset }) => {
  // Chart Data and Options
  // These objects configure the appearance and data for the charts.
  const pitchData = {
    labels: report.vocal_delivery.pitch_over_time.map((_, index) => `Time ${index + 1}`),
    datasets: [
      {
        label: 'Pitch (Hz)',
        data: report.vocal_delivery.pitch_over_time,
        borderColor: 'rbg(75, 192, 192, 0.2)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
        fill: true,
      },
    ]
  };

  const paceData = {
    labels: report.vocal_delivery.pace_over_time.map((_, index) => `Interval ${index + 1}`),
    datasets: [
      {
        label: 'Pace (WPM)',
        data: report.vocal_delivery.pace_over_time,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const, labels: { color: '#ffffff' } },
      title: { display: true, font: { size: 18 }, color: '#ffffff' },
    },
    scales: {
      y: { beginAtZero: false, ticks: { color: '#ffffff' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
      x: { ticks: { color: '#ffffff' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }
    }
  };

  const pitchChartOptions = {...chartOptions, plugins: {...chartOptions.plugins, title: {...chartOptions.plugins.title, text: 'Pitch Variation Over Time'}}};
  const paceChartOptions = {...chartOptions, plugins: {...chartOptions.plugins, title: {...chartOptions.plugins.title, text: 'Speaking Pace Over Time'}}};

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-gray-800 rounded-lg shadow-lg text-white animate-fade-in">
      <h2 className="text-3xl font-bold mb-6 text-center">Analysis Report</h2>

      {/* --- Summary Cards --- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 text-center">
        <div className="bg-gray-700 p-4 rounded-lg">
          <div className="text-4xl font-bold">{Math.round(report.vocal_delivery.speaking_rate)}</div>
          <div className="text-sm text-gray-400">Avg. Words/Min</div>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
          <div className="text-4xl font-bold">{report.vocal_delivery.long_pauses_count}</div>
          <div className="text-sm text-gray-400">Long Pauses</div>
        </div>
         <div className="bg-gray-700 p-4 rounded-lg">
          <div className="text-4xl font-bold">{report.content.clarity_score}/10</div>
          <div className="text-sm text-gray-400">Clarity Score</div>
        </div>
      </div>

      {/* --- MISSING PART 3: Chart and Button JSX --- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-gray-700 p-4 rounded-lg">
            <Line options={pitchChartOptions} data={pitchData} />
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
            <Line options={paceChartOptions} data={paceData} />
        </div>
      </div>

      {/* --- Existing Report Sections --- */}
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-gray-300">Transcript</h3>
        <p className="bg-gray-700 p-4 rounded-lg text-gray-300 italic">&quot;{report.transcript}&quot;</p>
      </div>
      
      <div>
        <h3 className="text-xl font-semibold text-gray-300">Content Analysis</h3>
        <ul className="list-disc list-inside text-gray-400 space-y-2">
          <li>
            Filler Words:
            <ul className="list-disc list-inside ml-4 mt-1">
              {Object.entries(report.content.filler_word_counts).map(([word, count]) => (
                <li key={word}>{`${word}: ${count}`}</li>
              ))}
            </ul>
          </li>
          <li>Clarity Score: {report.content.clarity_score}/10</li>
          <li>Suggestions:
            <ul className="list-disc list-inside ml-4 mt-1">
              {report.content.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </li>
          <li>Improvement:
            <ul className="list-disc list-inside ml-4 mt-1">
              <li>{report.content.improved_sentence}</li>
            </ul>
          </li>
        </ul>
      </div>

      <div className="text-center mt-8">
        <button 
          onClick={onReset}
          className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75 transition-colors"
        >
          Start New Session
        </button>
      </div>
    </div>
  );
};

export default AnalysisReport;
