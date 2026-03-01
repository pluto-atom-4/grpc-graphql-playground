import React from 'react';

interface DestinationCardProps {
  destination: {
    id: string;
    name: string;
    region: string;
    country: string;
    description?: string;
    latitude?: number;
    longitude?: number;
    score: number;
  };
}

export default function DestinationCard({ destination }: DestinationCardProps) {
  const scorePercentage = Math.round(destination.score * 100);

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="p-6">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{destination.name}</h3>
            <p className="text-sm text-gray-600">{destination.region}, {destination.country}</p>
          </div>
          <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
            {scorePercentage}%
          </div>
        </div>

        {destination.description && (
          <p className="text-gray-700 text-sm mb-4 line-clamp-2">
            {destination.description}
          </p>
        )}

        {destination.latitude && destination.longitude && (
          <p className="text-xs text-gray-500 mb-4">
            📍 {destination.latitude.toFixed(2)}, {destination.longitude.toFixed(2)}
          </p>
        )}

        {/* Score indicator */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${scorePercentage}%` }}
          ></div>
        </div>

        <button className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium">
          Learn More
        </button>
      </div>
    </div>
  );
}
