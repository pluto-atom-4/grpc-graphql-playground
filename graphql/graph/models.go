package graph

// Destination represents a travel destination
type Destination struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Region      string   `json:"region"`
	Country     string   `json:"country"`
	Description *string  `json:"description"`
	Latitude    *float64 `json:"latitude"`
	Longitude   *float64 `json:"longitude"`
	Score       float64  `json:"score"`
}

// EventResponse is the response from recording an event
type EventResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}
