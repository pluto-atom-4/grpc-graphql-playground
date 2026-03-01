package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/pluto-atom-4/grpc-graphql-playground/graphql/config"
)

func main() {
	cfg := config.LoadConfig()
	log.Printf("Starting GraphQL gateway with config: %v", cfg)

	// For MVP, return a simple health check and GraphQL introspection endpoint
	http.HandleFunc("/graphql", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		// TODO: Implement actual GraphQL handling with gqlgen
		fmt.Fprintf(w, `{"data":null,"errors":[{"message":"GraphQL not yet implemented"}]}`)
	})

	http.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"status":"healthy"}`)
	})

	addr := fmt.Sprintf(":%d", cfg.HTTPPort)
	log.Printf("GraphQL gateway listening on http://localhost%s/graphql", addr)
	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatalf("Failed to start HTTP server: %v", err)
	}
}
