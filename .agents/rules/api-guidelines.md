# API & OpenAPI Guidelines

When working on backend communication and frontend API integration in this repository, strictly adhere to the following rules:

## 1. Always use `openapi-fetch` (Never `axios` for API calls)

- All API requests to backend endpoints must use `openapi-fetch` (`apiClient` exported from `@/Api/Api`).
- Do **not** use `axios` for API calls or endpoints. `apiClient` already handles CSRF tokens (`X-CSRFToken`), credentials, base URLs, and TypeScript types.

## 2. OpenAPI Generation via `make react-openapi`

- Whenever TypeScript API types in `src/Api/OpenApi.ts` need to be refreshed or updated after changes to OpenAPI endpoints, use the command:
  ```bash
  make react-openapi
  ```
  This command will automatically:
  1. Export the OpenAPI schema directly from Django Ninja (`export_openapi_schema --api beltradar.api.api`) to `frontend/src/openapi.json`.
  1. Generate the updated TypeScript types in `frontend/src/Api/OpenApi.ts`.
- Alternatively, `make react-export-openapi` exports only the schema, and `npm run generate-api` (inside `frontend/`) generates only the TypeScript types.
