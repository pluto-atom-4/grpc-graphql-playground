package graph

import (
	"github.com/graphql-go/graphql"
)

// BuildSchema creates the GraphQL schema
func BuildSchema(resolver *Resolver) (graphql.Schema, error) {
	// Define the Destination type
	destinationType := graphql.NewObject(graphql.ObjectConfig{
		Name: "Destination",
		Fields: graphql.Fields{
			"id": &graphql.Field{
				Type: graphql.NewNonNull(graphql.String),
			},
			"name": &graphql.Field{
				Type: graphql.NewNonNull(graphql.String),
			},
			"region": &graphql.Field{
				Type: graphql.NewNonNull(graphql.String),
			},
			"country": &graphql.Field{
				Type: graphql.NewNonNull(graphql.String),
			},
			"description": &graphql.Field{
				Type: graphql.String,
			},
			"latitude": &graphql.Field{
				Type: graphql.Float,
			},
			"longitude": &graphql.Field{
				Type: graphql.Float,
			},
			"score": &graphql.Field{
				Type: graphql.NewNonNull(graphql.Float),
			},
		},
	})

	// Define the EventResponse type
	eventResponseType := graphql.NewObject(graphql.ObjectConfig{
		Name: "EventResponse",
		Fields: graphql.Fields{
			"success": &graphql.Field{
				Type: graphql.NewNonNull(graphql.Boolean),
			},
			"message": &graphql.Field{
				Type: graphql.NewNonNull(graphql.String),
			},
		},
	})

	// Define Query
	queryType := graphql.NewObject(graphql.ObjectConfig{
		Name: "Query",
		Fields: graphql.Fields{
			"recommendations": &graphql.Field{
				Type: graphql.NewNonNull(graphql.NewList(graphql.NewNonNull(destinationType))),
				Args: graphql.FieldConfigArgument{
					"userId": &graphql.ArgumentConfig{
						Type: graphql.NewNonNull(graphql.String),
					},
					"limit": &graphql.ArgumentConfig{
						Type:         graphql.Int,
						DefaultValue: 10,
					},
				},
				Resolve: func(p graphql.ResolveParams) (interface{}, error) {
					userID := p.Args["userId"].(string)
					var limit *int32
					if l, ok := p.Args["limit"]; ok {
						if lVal, ok := l.(int); ok {
							lInt32 := int32(lVal)
							limit = &lInt32
						}
					}
					return resolver.GetRecommendations(p.Context, userID, limit)
				},
			},
			"destination": &graphql.Field{
				Type: destinationType,
				Args: graphql.FieldConfigArgument{
					"id": &graphql.ArgumentConfig{
						Type: graphql.NewNonNull(graphql.String),
					},
				},
				Resolve: func(p graphql.ResolveParams) (interface{}, error) {
					id := p.Args["id"].(string)
					return resolver.GetDestination(p.Context, id)
				},
			},
			"destinations": &graphql.Field{
				Type: graphql.NewNonNull(graphql.NewList(graphql.NewNonNull(destinationType))),
				Resolve: func(p graphql.ResolveParams) (interface{}, error) {
					return resolver.GetDestinations(p.Context)
				},
			},
		},
	})

	// Define Mutation
	mutationType := graphql.NewObject(graphql.ObjectConfig{
		Name: "Mutation",
		Fields: graphql.Fields{
			"recordEvent": &graphql.Field{
				Type: graphql.NewNonNull(eventResponseType),
				Args: graphql.FieldConfigArgument{
					"userId": &graphql.ArgumentConfig{
						Type: graphql.NewNonNull(graphql.String),
					},
					"destinationId": &graphql.ArgumentConfig{
						Type: graphql.NewNonNull(graphql.String),
					},
					"eventType": &graphql.ArgumentConfig{
						Type: graphql.NewNonNull(graphql.String),
					},
					"rating": &graphql.ArgumentConfig{
						Type: graphql.Int,
					},
				},
				Resolve: func(p graphql.ResolveParams) (interface{}, error) {
					userID := p.Args["userId"].(string)
					destID := p.Args["destinationId"].(string)
					eventType := p.Args["eventType"].(string)

					var rating *int32
					if r, ok := p.Args["rating"]; ok {
						if rVal, ok := r.(int); ok {
							rInt32 := int32(rVal)
							rating = &rInt32
						}
					}

					return resolver.RecordEvent(p.Context, userID, destID, eventType, rating)
				},
			},
		},
	})

	// Create and return the schema
	schema, err := graphql.NewSchema(graphql.SchemaConfig{
		Query:    queryType,
		Mutation: mutationType,
	})

	return schema, err
}
