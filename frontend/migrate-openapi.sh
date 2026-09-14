#!/bin/bash
echo "Running OpenAPI TypeScript generation"
npx openapi-typescript ./src/openapi.json -o src/Api/OpenApi.ts
echo "OpenAPI TypeScript generation completed"
