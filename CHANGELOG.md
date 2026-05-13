# Changelog

## [In Development] - Unreleased

<!--
Section Order:

### Added
### Fixed
### Changed
### Removed
-->

### Added

- Ninja API
  - API Schema Example
  - API Example
- Makefile System
- Applogger
- `retry_task_on_esi_error` context manager for Tasks
- Unified template settings
- CSS, JS Bundle Example
- Universal Updater

### Changed

- Updated pre-commit dependencies
- Dependency `allianceuth` set to `>=5`
- Dependency `django-esi` set to `>=9`
- Dependency `django-ninja` set to `>=1.5,<2`

### Removed

- `django-eveuniverse` dependency
- `allianceauth-app-utils` dependency
- `when_esi_is_available` decorator
- Admin View
- Unnecessary Stuff in `app_settings`

## [0.0.4] - 2025-09-03

### Added

- Admin Example View

### Changed

- Update Pre-Commit
- GitHub Workflow
- Prepared ESI Provider to new Guideline
- Updated pyproject
- Updated tox
- Updated npm
- Optimized AA Test Enviroment

### Fixed

- Template Path (`template` to `example`)

### Removed

- Cache Buster [Commit](https://github.com/Geuthur/aa-template/blob/4518910bc1a77b5323d5f5c91cad60f60b44b432/template/helpers/static_files.py)

## [0.0.3] - 2025-07-04

### Changed

- Refactor aa-example

## [0.0.2] - 2025-02-06

### Change

- Update AA to 4.6.1
- Update Pre Commit

### Added

- Translation
- Python 3.13 Support
- Cache Buster by [@ppfeufer](https://github.com/ppfeufer)

## [0.0.1] - 2024-08-xx

### Added

- Initial public release
