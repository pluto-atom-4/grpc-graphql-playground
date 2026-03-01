# This Project


## Recommender Service

Responsibilities: Kafka consumer that builds recommendations based on product/order events.


## Overview

Recommender (Python): Consumes Kafka events and builds product recommendations.
API Gateway (Go): A GraphQL service exposing a unified API for front-end clients.

### Tech Stack:

Front-end:
- NextJS, Typescript, GraphQL, gPRC as BFF

Back-end:

- Production: Python, Go, gRPC, Postgres,  Kafka
- Local Dev Env: Python, Go, gRPC, SQLite, Redpand


### Communication Overview
- API Gateway (GraphQL) talks to:
  - `Recommender client` → `Recommender server` (Go) → `Postgres (Replica)` + `Kafka`

### Event Flow:
- `Recommender` service is also a `Kafka` consumer, consuming Kafka events and updating internal state for recommendations.


References: 
- Building a Frontend (GraphQL) ↔ BFF (gRPC) ↔ Backend Stack with NestJS and Next.js at Zenn (https://zenn.dev/maronn/articles/nestjs-nextjs-grpc-graphql?locale=en)
- rasadov/EcommerceAPI at GitHub (https://github.com/rasadov/EcommerceAPI?tab=readme-ov-file)

---


## Implementation Ideas focusing on Front end

Add NodeJS Packages

```bash
npm i --save @grpc/grpc-js @grpc/proto-loader
```

NextJS factory 

```typescript
import { NestFactory } from '@nestjs/core';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { AppModule } from './app.module';
import * as path from 'path';
async function bootstrap() {
  const app = await NestFactory.createMicroservice<MicroserviceOptions>(
    AppModule,
    {
      transport: Transport.GRPC,
      options: {
        package: 'hero',
        protoPath: path.join(__dirname, 'hero/hero.proto'),
      },
    },
  );
  await app.listen();
}
bootstrap();
````

configure the compile option in `nest-cli.json`

```json
"assets": ["**/*.proto"],
"watchAssets": true
```


### type defintion file from prot file


```bash
npm install ts-proto
```

proto file

```golang
syntax = "proto3";
package hero;
service HeroesService {
  rpc FindOne (HeroById) returns (Hero) {}
}
message HeroById {
  int32 id = 1;
}
message Hero {
  int32 id = 1;
  string name = 2;
}
```

command to create type definition 

```bash
npx protoc --ts_proto_opt=nestJs=true --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. ./src/hero/hero.proto
```

The comnand outputs: `hero.ts`


```typescript
/* eslint-disable */
import { GrpcMethod, GrpcStreamMethod } from "@nestjs/microservices";
import { Observable } from "rxjs";
export const protobufPackage = "hero";
/** hero/hero.proto */
export interface HeroById {
  id: number;
}
export interface Hero {
  id: number;
  name: string;
}
export const HERO_PACKAGE_NAME = "hero";
export interface HeroesServiceClient {
  findOne(request: HeroById): Observable<Hero>;
}
export interface HeroesServiceController {
  findOne(request: HeroById): Promise<Hero> | Observable<Hero> | Hero;
}
export function HeroesServiceControllerMethods() {
  return function (constructor: Function) {
    const grpcMethods: string[] = ["findOne"];
    for (const method of grpcMethods) {
      const descriptor: any = Reflect.getOwnPropertyDescriptor(
        constructor.prototype,
        method
      );
      GrpcMethod("HeroesService", method)(
        constructor.prototype[method],
        method,
        descriptor
      );
    }
    const grpcStreamMethods: string[] = [];
    for (const method of grpcStreamMethods) {
      const descriptor: any = Reflect.getOwnPropertyDescriptor(
        constructor.prototype,
        method
      );
      GrpcStreamMethod("HeroesService", method)(
        constructor.prototype[method],
        method,
        descriptor
      );
    }
  };
}
export const HEROES_SERVICE_NAME = "HeroesService";
````

```typescript

/* eslint-disable */
import { GrpcMethod, GrpcStreamMethod } from "@nestjs/microservices";
import { Observable } from "rxjs";
export const protobufPackage = "hero";
/** hero/hero.proto */
export interface HeroById {
  id: number;
}
export interface Hero {
  id: number;
  name: string;
}
export const HERO_PACKAGE_NAME = "hero";
export interface HeroesServiceClient {
  findOne(request: HeroById): Observable<Hero>;
}
export interface HeroesServiceController {
  findOne(request: HeroById): Promise<Hero> | Observable<Hero> | Hero;
}
export function HeroesServiceControllerMethods() {
  return function (constructor: Function) {
    const grpcMethods: string[] = ["findOne"];
    for (const method of grpcMethods) {
      const descriptor: any = Reflect.getOwnPropertyDescriptor(
        constructor.prototype,
        method
      );
      GrpcMethod("HeroesService", method)(
        constructor.prototype[method],
        method,
        descriptor
      );
    }
    const grpcStreamMethods: string[] = [];
    for (const method of grpcStreamMethods) {
      const descriptor: any = Reflect.getOwnPropertyDescriptor(
        constructor.prototype,
        method
      );
      GrpcStreamMethod("HeroesService", method)(
        constructor.prototype[method],
        method,
        descriptor
      );
    }
  };
}
export const HEROES_SERVICE_NAME = "HeroesService";
```


### Front End BFF

`app.module.ts`:

```typescript
import { Module } from "@nestjs/common";
import { AppService } from "./app.service";
import { ClientsModule, Transport } from "@nestjs/microservices";
import { HERO_PACKAGE_NAME } from "./hero/hero";
import * as path from "path";
import { AppResolver } from "./app.resolver";
import { AppController } from "./app.controller";
@Module({
  imports: [
    ClientsModule.register([
      {
        name: HERO_PACKAGE_NAME,
        transport: Transport.GRPC,
        options: {
          url: "localhost:5000",
          package: HERO_PACKAGE_NAME,
          protoPath: path.join(__dirname, "hero/hero.proto"),
        },
      },
    ]),
  ],
  controllers: [AppController],
  providers: [AppService, AppResolver],
})
export class AppModule {}
```

`app.service,ta`:
```typescript
import { Inject, Injectable, OnModuleInit } from "@nestjs/common";
import {
  HEROES_SERVICE_NAME,
  HERO_PACKAGE_NAME,
  Hero,
  HeroesServiceClient,
} from "./hero/hero";
import { ClientGrpc } from "@nestjs/microservices";
import { Observable, lastValueFrom } from "rxjs";
import { adjustRpcResponse } from "./utils/convertObservableToPromise";

@Injectable()
export class AppService implements OnModuleInit {
  private heroesService: HeroesServiceClient;

  constructor(@Inject(HERO_PACKAGE_NAME) private client: ClientGrpc) {}

  onModuleInit() {
    this.heroesService =
      this.client.getService<HeroesServiceClient>(HEROES_SERVICE_NAME);
  }

  async getHero() {
    return await this.adjustRpcResponse<Hero>(
      this.heroesService.findOne({ id: 1 })
    );
  }

  private async adjustRpcResponse<T>(response: Observable<T>): Promise<T> {
    try {
      return await lastValueFrom(response);
    } catch (e) {
      throw e;
    }
  }
}
```

`app.controller.ts`:
```typescript
import { Controller, Get } from "@nestjs/common";
import { Observable } from "rxjs";
import { AppService } from "./app.service";
import { Hero } from "./hero/hero";
@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}
  @Get()
  call(): Observable<Hero> {
    return this.appService.getHero();
  }
}
```


### GraphQL (NestJS)

```bash
npm i @nestjs/graphql @nestjs/apollo @apollo/server graphql
```

`app.module.ts`:

```typescript
import { Module } from "@nestjs/common";
import { AppService } from "./app.service";
import { ClientsModule, Transport } from "@nestjs/microservices";
import { HERO_PACKAGE_NAME } from "./hero/hero";
import * as path from "path";
import { AppResolver } from "./app.resolver";
import { AppController } from "./app.controller";
import { GraphQLModule } from "@nestjs/graphql";
import { ApolloDriver, ApolloDriverConfig } from "@nestjs/apollo";
@Module({
  imports: [
    ClientsModule.register([
      {
        name: HERO_PACKAGE_NAME,
        transport: Transport.GRPC,
        options: {
          url: "localhost:5000",
          package: HERO_PACKAGE_NAME,
          protoPath: path.join(__dirname, "hero/hero.proto"),
        },
      },
    ]),
    GraphQLModule.forRoot<ApolloDriverConfig>({
      driver: ApolloDriver,
      autoSchemaFile: path.join(process.cwd(), "src/schema.gql"),
    }),
  ],
  controllers: [AppController],
  providers: [AppService, AppResolver],
})
export class AppModule {}
```

`app.model.ts`:
```typescript
import { Field, ObjectType } from "@nestjs/graphql";

@ObjectType()
export class AppModel {
  @Field((type) => Number)
  id: number;
  @Field((type) => String)
  name: string;
}
```

`app.resolver.ts`: 
```typescript
import { Query, Resolver } from "@nestjs/graphql";
import { AppModel } from "./app.model";
import { AppService } from "./app.service";
@Resolver((of) => AppModel)
export class AppResolver {
  constructor(private appService: AppService) {}
  @Query(() => AppModel, { name: "apps" })
  async getHero(): Promise<AppModel> {
    const hero = await this.appService.getHero();
    return { id: hero.id, name: hero.name };
  }
}
```

### Front end (NextJS)

```bash
npm create next-app frontend --typescript

# to obtain the data via GraphQL
npm install --save urql
```

`_app.tsx`:
```typescript
import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { Client, Provider, cacheExchange, fetchExchange } from "urql";
const client = new Client({
  url: "http://localhost:3000/graphql",
  exchanges: [cacheExchange, fetchExchange],
});
export default function App({ Component, pageProps }: AppProps) {
  return (
    <Provider value={client}>
      <Component {...pageProps} />
    </Provider>
  );
}
```

`index.tsx`:
```typescript
import { Inter } from "next/font/google";
import { gql, useQuery } from "urql";
const inter = Inter({ subsets: ["latin"] });
const heroQuery = gql`
  query heros {
    apps {
      id
      name
    }
  }
`;
const Home = () => {
  const [{ data }] = useQuery({ query: heroQuery });
  return (
    <main
      className={`flex min-h-screen flex-col items-center justify-between p-24 ${inter.className}`}
    >
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <p>id:{data?.apps.id}</p>
        <p>name:{data?.apps.name}</p>
      </div>
    </main>
  );
};
export default Home;
```

Configure to use reverce proxy

`next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/graphql",
        destination: `http://localhost:3003/graphql`,
      },
    ];
  },
};
module.exports = nextConfig;
```


### type definitions for Front end (NextJS)

```bash
npm i -S graphql
npm i -D typescript ts-node @graphql-codegen/cli
```

```log
質問①
? What type of application are you building? (Use arrow keys):(アプリケーション種類は何？)
→「Application built with React 」を選択します。

質問②
? Where is your schema?:(スキーマの定義はどこにありますか)
→スキーマファイルのパス(今回はbff内のsrc配下にあるschema.gql) or スキーマにアクセスできるURL(今回はhttp://localhot:3003/graphql)

質問③
Where are your operations and fragments?:(GraphQLのクエリなどを書いているファイルはどこにありますか？)
→GraphQLのクエリなどが記載されているパスを指定します。この記事では「pages/**/*.tsx」を指定します。

質問④
Where to write the output:(どこにコードを生成する？)
→任意のディレクトリを設定してください。この記事では「generate/」を指定しています。
→ディレクトリの最後に「/」を設定しないとコード生成時にエラーが発生するので、ご注意ください。

質問⑤
Do you want to generate an introspection file?
→これの意味はよく分からなかったので、好きなものを選んでください。

質問⑥
How to name the config file?:(コード生成の設定ファイル名は何にする？)
→ymlも行けますが、特にこだわりが無ければデフォルトのままで良いと思います。

質問⑦
What script in package.json should run the codegen?:(package.jsonでコード生成を起動するスクリプト名は何にする?)
→好きなものを選んでください。
```

Update `index.tsx`:
```typescript
import { graphql } from "@/generate";
import { HerosQuery } from "@/generate/graphql";
import { Inter } from "next/font/google";
import { useQuery } from "urql";
const inter = Inter({ subsets: ["latin"] });
const herosDocument = graphql(`
  query heros {
    apps {
      id
      name
    }
  }
`);
const Home = () => {
  const [{ data }] = useQuery<HerosQuery>({ query: herosDocument });
  return (
    <main
      className={`flex min-h-screen flex-col items-center justify-between p-24 ${inter.className}`}
    >
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <p>id:{data?.apps.id}</p>
        <p>name:{data?.apps.name}</p>
      </div>
    </main>
  );
};
export default Home;
```

Time spent: 25 min

### Sampel data for recomendation

Popular destinations in 2026

- Dolomites & Northern Italy / Milan & Dolomites (Italy)
- Washington, D.C. (USA)
- Warsaw (Poland)
- Peloponnese Peninsula (Greece)
- Antarctica
- Zanzibar (Tanzania)
- Nikko (Japan)
- Hudson Valley, New York (USA)
- Abu Dhabi (UAE)
- Sonoma, California (USA)
- Riviera Nayarit (Mexico)
- Park City, Utah (USA)
- Mallorca (Spain)
- Los Angeles, California (USA)
- Grenada (Caribbean)
- Emerald Coast, Florida (USA)
- Croatia

References:
- https://zenn.dev/maronn/articles/nestjs-nextjs-grpc-graphql
- https://eng.tourismandsocietytt.com/news-and-newsletter/2026/2026-january/ultimas-noticias/forbes-travel-guide-highlights-20-leading-international-destinations-for-20

---
## Ideas on implementaion backend API and GraphQL

Structure:
```
graphql
 cmd/graphql
   main.go
 config
   config.go
 generated
   generated.go
   gqlgen.yml
   modules_gen.go
 graph
   graph.go
   mutation.go
   query.go

recommender
  app
    db
      models.py
      session.py
    entry
      main.py
      sync.py
    services
      recommender.py
  client
      client.go
  config
      settings.py
  generated
    pb
      recommendaer.pb.go
      recommender_grpc.pb.go
      recommender_pb.2.py
      recommender_pb2.pyi
      recommender_pb2_grpc.py
  recommender.proto
  pyproject.toml
go.mod
go.sum
```

## Further considerations on architecture

### 1. Architectural Strategy

A common production-grade pattern involves:

- GraphQL Gateway: Acts as the primary entry point for the frontend, aggregating data from multiple microservices.
- gRPC (Internal): Used for high-performance, type-safe communication between the GraphQL Gateway and internal microservices.
- Kafka (Event Bus): Handles asynchronous tasks, event-driven state changes, and real-time data streaming between services.

### 2. Implementing the Frontend (API Layer)

The GraphQL Gateway Path 

1. Unified Schema: Define a GraphQL schema that represents your UI needs.
2. Resolvers to gRPC: Write resolvers in your GraphQL server (e.g., Apollo or gqlgen) that call internal gRPC services to fetch data.
3. Kafka Subscriptions: Use GraphQL Subscriptions to stream real-time updates from Kafka to the frontend via WebSockets.
4. Mutations to Kafka: When a user performs an action, the GraphQL mutation can either call a gRPC service or produce a message directly to a Kafka topic


### 3. Integrating Kafka for Real-Time Data

- Materialized Views: Have a service consume Kafka events and save them into a database (e.g., PostgreSQL or Redis). The frontend then queries this database via GraphQL.
- Direct Streaming: Use a "sidecar" or gateway service that consumes a Kafka topic and pushes the data to the frontend using GraphQL Subscriptions or gRPC Server Streaming (supported by gRPC-Web).
- Managed Solutions: Tools like Grafbase or Hasura can natively map Kafka topics into a GraphQL API, reducing manual boilerplate.


### 4. Implementation Checklist

- Define Contracts: Start with .proto files for gRPC and a .graphql schema for the frontend.
- Setup Proxy: If using gRPC-Web, configure an Envoy Proxy.
- Event Mapping: Decide if mutations should immediately return a result or just an "Accepted" status while the real work happens asynchronously in Kafka.
- Type Safety: Use tools like Buf to manage your Protobuf definitions across the stack. 

## gRPC, Kafka, and GraphQL, Go (Golang) over Ruby

### 1. Performance and Scalability

- Concurrency: Go’s goroutines are lightweight and designed for the high-concurrency demands of microservices. Ruby's Global Interpreter Lock (GIL) limits true parallel execution, making it struggle with the high-throughput requirements typical of Kafka and gRPC.
- Raw Speed: As a compiled language, Go is significantly faster (often 3x–10x) than Ruby, which is interpreted. In one case study, a Go-based API handled 100,000 requests per second where a Ruby version struggled at 10,000.
- Infrastructure Efficiency: Go applications typically consume much less CPU and memory than their Ruby counterparts for the same workload, leading to lower cloud costs. 

### 2. Ecosystem Support for the Stack

- gRPC Native Integration: gRPC was built with languages like Go in mind. Go has first-class support for protocol buffers and high-performance internal communication.
- Kafka Performance: While Ruby has Kafka gems (libraries), Go’s Kafka clients (like segmentio/kafka-go or confluent-kafka-go) are better at handling high-velocity data streams due to Go's non-blocking I/O.
- GraphQL Gateways: Go has mature, high-performance libraries like gqlgen or Apollo Federation support, which are ideal for building a unified GraphQL gateway that aggregates data from internal gRPC services. 

### 3. Maintainability and Deployment

- Type Safety: Go’s strict static typing and explicit error handling make it more reliable for complex distributed systems compared to Ruby’s dynamic nature, which can lead to runtime errors that are harder to debug.
- Deployment Simplicity: Go compiles into a single static binary with no external dependencies, making it much easier to deploy in Docker or Kubernetes compared to managing a Ruby environment with its various "gems" and interpreter versions. 

## Local development

### Redpanda (Kafka-Compatible)

- If you specifically want to keep the Kafka API and ecosystem but hate the setup, use Redpanda. 
Drop-in Replacement: It is fully compatible with Kafka clients but written in C++, meaning it has no JVM dependency and runs as a single binary.
- Developer Friendly: It is significantly easier to spin up locally via Docker than a full Kafka cluster. 


### SQLite

Choosing SQLite over Postgres for backend development offers several "profits" in terms of cost, speed, and simplicity, particularly for small-to-medium scale applications or the prototyping phase. 

### 1. Zero Infrastructure Costs & Maintenance

- No Dedicated Server: Unlike Postgres, which requires a separate server process (and often a paid managed service like AWS RDS), SQLite is a serverless library that reads/writes directly to a single file on disk.
- Reduced DevOps Workload: Because there is no server to configure, "babysit," or update, operational complexity is significantly lower.
- Lower Hosting Bills: You can run SQLite on the smallest, cheapest cloud instances (e.g., $5/month DigitalOcean or Hetzner) because it consumes minimal CPU and memory compared to the overhead of a Postgres instance. 

### 2. Elimination of Network Latency

- In-Process Execution: SQLite runs in the same process address space as your application. A database query is a simple function call rather than a message sent over a network (TCP/IP).
- Zero Round-Trip Time: By eliminating network round trips, SQLite can significantly outperform Postgres for read-heavy workloads or pages that require many small, sequential queries. 

#### 3. Accelerated Development Velocity

- Instant Setup: Local development starts immediately with no need to install Postgres, manage users/permissions, or run Docker.
- Simple Backups & Portability: Backing up or moving your database is as easy as copying the .sqlite file. This allows you to easily share a populated database with team members for debugging or testing.
- Testing Speed: You can use SQLite’s in-memory mode for automated tests, which is often much faster than spinning up a real Postgres instance for every test run. 

### 4. Technical Reliability for Specific Loads
ACID Compliance: Despite its size, SQLite is fully ACID-compliant. It ensures data integrity even during power failures or application crashes.
Handle Moderate Traffic: A well-configured SQLite database (using Write-Ahead Logging (WAL) mode) can handle hundreds of thousands of hits per day, making it more than sufficient for 80-90% of standard web applications. 

### When the "Profit" Disappears
The benefits of SQLite vanish if your app requires:
High Write Concurrency: SQLite only allows one writer at a time, which can create bottlenecks in apps with many simultaneous users making updates.
Advanced Features: Postgres offers superior support for complex data types (JSONB, Arrays), Full-Text Search, and geospatial data via PostGIS.

---
## Time spend:

- #1 : 30 min
- #2 : 25 min
- #3 : 10 min
- #4 : 20 min
- #5 : 20 min
- #6 : 20 min
- 