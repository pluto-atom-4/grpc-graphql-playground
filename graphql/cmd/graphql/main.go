package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/graphql-go/graphql"
	"github.com/pluto-atom-4/grpc-graphql-playground/graphql/config"
	"github.com/pluto-atom-4/grpc-graphql-playground/graphql/graph"
)

var gqlSchema graphql.Schema

func init() {
	cfg := config.LoadConfig()

	// Create resolver with gRPC client
	resolver, err := graph.NewResolver(cfg.RecommenderGRPCAddress)
	if err != nil {
		log.Fatalf("Failed to create resolver: %v", err)
	}

	// Build GraphQL schema
	var schemaErr error
	gqlSchema, schemaErr = graph.BuildSchema(resolver)
	if schemaErr != nil {
		log.Fatalf("Failed to build GraphQL schema: %v", schemaErr)
	}
}

func main() {
	cfg := config.LoadConfig()
	log.Printf("Starting GraphQL gateway with config: %v", cfg)

	// GraphQL query endpoint
	http.HandleFunc("/graphql", handleGraphQL)

	// Health check
	http.HandleFunc("/healthz", handleHealth)

	addr := fmt.Sprintf(":%d", cfg.HTTPPort)
	log.Printf("GraphQL gateway listening on http://localhost%s/graphql", addr)
	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatalf("Failed to start HTTP server: %v", err)
	}
}

func handleGraphQL(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Query         string                 `json:"query"`
		OperationName string                 `json:"operationName"`
		Variables     map[string]interface{} `json:"variables"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"errors": []string{err.Error()},
		})
		return
	}

	// Execute GraphQL query
	result := graphql.Do(graphql.Params{
		Schema:         gqlSchema,
		RequestString:  req.Query,
		VariableValues: req.Variables,
		OperationName:  req.OperationName,
		Context:        r.Context(),
	})

	if len(result.Errors) > 0 {
		w.WriteHeader(http.StatusBadRequest)
	}

	json.NewEncoder(w).Encode(result)
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"status":"healthy"}`)
}
