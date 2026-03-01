package client

import (
	"context"
	"fmt"

	pb "github.com/pluto-atom-4/grpc-graphql-playground/recommender/generated/pb"
	"google.golang.org/grpc"
)

// Client wraps the gRPC recommender service client
type Client struct {
	conn   *grpc.ClientConn
	client pb.RecommenderServiceClient
}

// NewClient creates a new recommender service client
func NewClient(addr string) (*Client, error) {
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		return nil, fmt.Errorf("failed to connect to recommender service: %w", err)
	}

	return &Client{
		conn:   conn,
		client: pb.NewRecommenderServiceClient(conn),
	}, nil
}

// GetRecommendations retrieves travel recommendations for a user
func (c *Client) GetRecommendations(ctx context.Context, userID string, limit int32) ([]*pb.Destination, error) {
	if limit <= 0 {
		limit = 10 // default limit
	}

	req := &pb.RecommendationRequest{
		UserId: userID,
		Limit:  limit,
	}

	resp, err := c.client.GetRecommendations(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("failed to get recommendations: %w", err)
	}

	return resp.Destinations, nil
}

// RecordEvent processes a user event (view, click, book, rate)
func (c *Client) RecordEvent(ctx context.Context, userID, destinationID, eventType string, rating int32, timestamp int64) error {
	req := &pb.EventRequest{
		UserId:        userID,
		DestinationId: destinationID,
		EventType:     eventType,
		Rating:        rating,
		Timestamp:     timestamp,
	}

	resp, err := c.client.RecordEvent(ctx, req)
	if err != nil {
		return fmt.Errorf("failed to record event: %w", err)
	}

	if !resp.Success {
		return fmt.Errorf("event recording failed: %s", resp.Message)
	}

	return nil
}

// Close closes the gRPC connection
func (c *Client) Close() error {
	if c.conn != nil {
		return c.conn.Close()
	}
	return nil
}
