import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import DestinationCard from '../src/components/DestinationCard';

describe('DestinationCard Component', () => {
  const mockDestination = {
    id: 'paris_001',
    name: 'Paris',
    region: 'Île-de-France',
    country: 'France',
    description: 'City of Light',
    latitude: 48.8566,
    longitude: 2.3522,
    score: 0.95,
  };

  it('should render destination name', () => {
    render(<DestinationCard destination={mockDestination} />);
    expect(screen.getByText('Paris')).toBeInTheDocument();
  });

  it('should render region and country', () => {
    render(<DestinationCard destination={mockDestination} />);
    expect(screen.getByText(/Île-de-France.*France/)).toBeInTheDocument();
  });

  it('should render description', () => {
    render(<DestinationCard destination={mockDestination} />);
    expect(screen.getByText('City of Light')).toBeInTheDocument();
  });

  it('should render coordinates', () => {
    render(<DestinationCard destination={mockDestination} />);
    expect(screen.getByText(/48.86.*2.35/)).toBeInTheDocument();
  });

  it('should render score as percentage', () => {
    render(<DestinationCard destination={mockDestination} />);
    expect(screen.getByText('95%')).toBeInTheDocument();
  });

  it('should render Learn More button', () => {
    render(<DestinationCard destination={mockDestination} />);
    const button = screen.getByRole('button', { name: /Learn More/ });
    expect(button).toBeInTheDocument();
  });

  it('should handle missing optional fields', () => {
    const minimalDestination = {
      id: 'dest_1',
      name: 'Destination',
      region: 'Region',
      country: 'Country',
      score: 0.5,
    };

    render(<DestinationCard destination={minimalDestination} />);
    expect(screen.getByText('Destination')).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('should render score indicator bar', () => {
    const { container } = render(<DestinationCard destination={mockDestination} />);
    const scoreBar = container.querySelector('.bg-blue-600');
    expect(scoreBar).toBeInTheDocument();
    // Check width is set to score percentage
    const width = scoreBar?.getAttribute('style');
    expect(width).toContain('95');
  });

  it('should handle different score values', () => {
    const lowScoreDestination = {
      ...mockDestination,
      score: 0.25,
    };

    render(<DestinationCard destination={lowScoreDestination} />);
    expect(screen.getByText('25%')).toBeInTheDocument();
  });

  it('should cap score at 100%', () => {
    const highScoreDestination = {
      ...mockDestination,
      score: 1.5, // Score over 1.0
    };

    render(<DestinationCard destination={highScoreDestination} />);
    // Should cap at 100% or handle gracefully
    const percentageText = screen.getByText(/\d+%/);
    const percentage = parseInt(percentageText.textContent || '0');
    expect(percentage).toBeLessThanOrEqual(100);
  });
});
