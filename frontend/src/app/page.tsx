'use client';

import { useState } from 'react';
import DestinationCard from '@/components/DestinationCard';

interface Destination {
  id: string;
  name: string;
  region: string;
  country: string;
  description?: string;
  latitude?: number;
  longitude?: number;
  score: number;
}

export default function Home() {
  const [userId, setUserId] = useState('');
  const [recommendations, setRecommendations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId.trim()) {
      setError('Please enter a user ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const query = `
        query GetRecommendations($userId: String!, $limit: Int) {
          recommendations(userId: $userId, limit: $limit) {
            id
            name
            region
            country
            description
            latitude
            longitude
            score
          }
        }
      `;

      const response = await fetch('/graphql', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          variables: { userId, limit: 10 },
        }),
      });

      const data = await response.json();

      if (data.errors) {
        setError(data.errors[0]?.message || 'Failed to fetch recommendations');
      } else if (data.data?.recommendations) {
        setRecommendations(data.data.recommendations);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Search Form */}
      <form onSubmit={fetchRecommendations} className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">Find Recommendations</h2>
        <div className="flex gap-4">
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter your user ID"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading...' : 'Get Recommendations'}
          </button>
        </div>
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
            {error}
          </div>
        )}
      </form>

      {/* Recommendations Grid */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Recommended Destinations ({recommendations.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((destination) => (
              <DestinationCard key={destination.id} destination={destination} />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {recommendations.length === 0 && !loading && !error && (
        <div className="text-center py-12 bg-white shadow rounded-lg">
          <p className="text-gray-500">Enter your user ID to see personalized travel recommendations</p>
        </div>
      )}
    </div>
  );
}
