package config

import (
	"fmt"
	"os"
)

type Config struct {
	HTTPPort                int
	RecommenderGRPCAddress string
	Environment            string
}

func LoadConfig() *Config {
	return &Config{
		HTTPPort:                8080,
		RecommenderGRPCAddress: getEnv("RECOMMENDER_GRPC_ADDR", "localhost:50051"),
		Environment:            getEnv("ENVIRONMENT", "development"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func (c *Config) String() string {
	return fmt.Sprintf(
		"Config{HTTPPort: %d, RecommenderGRPCAddress: %s, Environment: %s}",
		c.HTTPPort,
		c.RecommenderGRPCAddress,
		c.Environment,
	)
}
