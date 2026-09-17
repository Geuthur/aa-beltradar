# Makefile fragment for React-related tasks

# React Fast Build (Local tsc & vite build without supervisor/collectstatic)
.PHONY: react-build
react-build:
	@echo "Building React frontend"
	@cd $(REACT__EXECUTABLE) && npm run build
	@echo "React build completed"

# React Dev Server
.PHONY: react-dev
react-dev:
	@echo "Starting React development server"
	@cd $(REACT__EXECUTABLE) && npm run dev

# React Test Build
.PHONY: react-test-build
react-test-build: check-python-venv check-myauth-path
	@echo "Running React test build"
	@cd $(REACT__EXECUTABLE) && $(REACT__TEST_BUILD_SCRIPT)
	@echo "React test build completed"

# React Release Build
.PHONY: react-release
react-release: check-python-venv check-myauth-path
	@echo "Running React release build"
	@cd $(REACT__EXECUTABLE) && $(REACT__RELEASE_BUILD_SCRIPT)
	@echo "React release build completed"

# Export OpenAPI Schema from Django Ninja
.PHONY: react-export-openapi
react-export-openapi: check-python-venv check-myauth-path
	@echo "Exporting OpenAPI schema from Django Ninja"
	@$(PYTHON__EXECUTABLE) $(DJANGO__MYAUTH_PATH)/manage.py shell -c \
		"import json; from pathlib import Path; from django.utils.module_loading import import_string; from ninja.responses import NinjaJSONEncoder; api = import_string('$(GENERAL__PACKAGE).api.api'); Path('$(REACT__EXECUTABLE)/src/openapi.json').write_text(json.dumps(api.get_openapi_schema(), cls=NinjaJSONEncoder, indent=2), encoding='utf-8')"
	@echo "OpenAPI schema exported to $(REACT__EXECUTABLE)/src/openapi.json"

# React OpenAPI Migration (exports schema from Django Ninja and generates TypeScript types)
.PHONY: react-openapi
react-openapi: check-python-venv check-myauth-path react-export-openapi
	@echo "Starting React OpenAPI TypeScript generation"
	@cd $(REACT__EXECUTABLE) && $(REACT__OPENAPI_SCRIPT)
	@echo "React OpenAPI migration completed"

# React Translations Scanner
.PHONY: react-translations
react-translations:
	@echo "Scanning and building React translations"
	@cd $(REACT__EXECUTABLE) && npm run buildTranslations
	@echo "React translations completed"

# React ESLint with auto-fix
.PHONY: react-eslint
react-eslint:
	@echo "Running React ESLint check with auto-fix"
	@cd $(REACT__EXECUTABLE) && npx eslint . --fix
	@echo "React ESLint check completed"

# React Lint (read-only verification)
.PHONY: react-lint
react-lint:
	@echo "Running React lint verification"
	@cd $(REACT__EXECUTABLE) && npm run lint
	@echo "React lint verification completed"

# React Automated Tests
.PHONY: react-test
react-test:
	@echo "Running React tests"
	@cd $(REACT__EXECUTABLE) && npm test
	@echo "React tests completed"

# React Clean Build Artifacts
.PHONY: react-clean
react-clean:
	@echo "Cleaning React build artifacts"
	@rm -rf $(REACT__EXECUTABLE)/build
	@echo "React clean completed"

# Help Message
.PHONY: help
help::
	@echo "  $(TEXT_UNDERLINE)React:$(TEXT_UNDERLINE_END)"
	@echo "    react-build         Run fast React build (tsc + vite)"
	@echo "    react-dev           Start React development server"
	@echo "    react-test-build    Run full React test build (build, collectstatic, restart supervisor)"
	@echo "    react-release       Run full React release build (build, i18n, collectstatic)"
	@echo "    react-export-openapi Export OpenAPI schema directly from Django Ninja"
	@echo "    react-openapi       Export schema and generate OpenAPI TypeScript types"
	@echo "    react-translations  Scan and extract i18n translations"
	@echo "    react-eslint        Run React ESLint check with auto-fix"
	@echo "    react-lint          Run React ESLint lint verification (read-only)"
	@echo "    react-test          Run React unit tests with Vitest"
	@echo "    react-clean         Clean React build folder"
	@echo ""
