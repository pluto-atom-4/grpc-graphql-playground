package graph

import (
	"context"
	"fmt"

	"github.com/pluto-atom-4/grpc-graphql-playground/recommender/client"
)

// Resolver handles GraphQL queries and mutations
type Resolver struct {
	recommenderClient *client.Client
}

// NewResolver creates a new resolver with a gRPC client
func NewResolver(recommenderAddr string) (*Resolver, error) {
	grpcClient, err := client.NewClient(recommenderAddr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gRPC client: %w", err)
	}

	return &Resolver{
		recommenderClient: grpcClient,
	}, nil
}

// GetRecommendations resolves the recommendations query
func (r *Resolver) GetRecommendations(ctx context.Context, userID string, limit *int32) ([]*Destination, error) {
	limitVal := int32(10)
	if limit != nil && *limit > 0 {
		limitVal = *limit
	}

	pbDestinations, err := r.recommenderClient.GetRecommendations(ctx, userID, limitVal)
	if err != nil {
		return nil, fmt.Errorf("failed to get recommendations: %w", err)
	}

	destinations := make([]*Destination, len(pbDestinations))
	for i, pbDest := range pbDestinations {
		destinations[i] = &Destination{
			ID:      pbDest.Id,
			Name:    pbDest.Name,
			Region:  pbDest.Region,
			Country: pbDest.Country,
			Description: func() *string {
				if pbDest.Description != "" {
					return &pbDest.Description
				}
				return nil
			}(),
			Latitude: func() *float64 {
				if pbDest.Latitude != 0 {
					lat := float64(pbDest.Latitude)
					return &lat
				}
				return nil
			}(),
			Longitude: func() *float64 {
				if pbDest.Longitude != 0 {
					lon := float64(pbDest.Longitude)
					return &lon
				}
				return nil
			}(),
			Score: float64(pbDest.Score),
		}
	}

	return destinations, nil
}

// GetDestination resolves a single destination by ID
func (r *Resolver) GetDestination(ctx context.Context, id string) (*Destination, error) {
	// For MVP, fetch all recommendations and find by ID
	// In production, this would query a database directly
	allDests, err := r.GetRecommendations(ctx, "system", nil)
	if err != nil {
		return nil, err
	}

	for _, dest := range allDests {
		if dest.ID == id {
			return dest, nil
		}
	}

	return nil, nil // Not found
}

// GetDestinations resolves all destinations
func (r *Resolver) GetDestinations(ctx context.Context) ([]*Destination, error) {
	// For MVP, return top recommendations for "system" user
	return r.GetRecommendations(ctx, "system", func(i int32) *int32 { return &i }(100))
}

// RecordEvent resolves the recordEvent mutation
func (r *Resolver) RecordEvent(ctx context.Context, userID, destinationID, eventType string, rating *int32) (*EventResponse, error) {
	ratingVal := int32(0)
	if rating != nil {
		ratingVal = *rating
	}

	err := r.recommenderClient.RecordEvent(ctx, userID, destinationID, eventType, ratingVal, 0)
	if err != nil {
		return &EventResponse{
			Success: false,
			Message: fmt.Sprintf("failed to record event: %v", err),
		}, nil
	}

	return &EventResponse{
		Success: true,
		Message: "event recorded successfully",
	}, nil
}

// Close closes the resolver's gRPC connection
func (r *Resolver) Close() error {
	if r.recommenderClient != nil {
		return r.recommenderClient.Close()
	}
	return nil
}
