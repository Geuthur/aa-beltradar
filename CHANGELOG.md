# Changelog

## [In Development] - Unreleased

<!--
> [!NOTE]
>

> [!TIP]
>

> [!IMPORTANT]
>

> [!WARNING]
>

> [!CAUTION]
>

Section Order:

### Added
### Fixed
### Changed

- A test now checks that every permission string used in the code (`has_perm`, `permission_required`, `permissions_required`) matches a codename defined in `General.Meta.permissions` with the correct app label, so copy errors like `taxsystem.admin_access` are caught. The permissions stay defined in `General` as a plain list of `(codename, text)` tuples and are checked directly through Django.
-->

<!-- AI Changes -->

### Fixed

- Tests no longer share the Redis cache with other processes. `testauth/settings/local.py` gives each test run its own random cache `KEY_PREFIX`. Before, ESI responses cached by a running testauth instance on the same Redis (e.g. `GET /markets/prices`) were returned instead of the pook responses, and the market price tests in `test_managers.py` failed until the cache entry expired. Redis stays the cache backend because Alliance Auth needs `django_redis`.

### Changed

- `UserSettings.user` is now a `OneToOneField` instead of a nullable `ForeignKey`, as in the repository template. Before, a user could end up with several settings rows and `UserSettings.objects.get_or_create(user=...)` raised `MultipleObjectsReturned`. The data migration `0014_remove_invalid_usersettings` keeps only the newest settings row per user (highest ID) and deletes rows without a user; `0015_alter_usersettings_user` then changes the field (migration required).
- The `AppLogger` is created only once in `beltradar/providers.py`. `api/session.py`, `api/helpers/charts.py`, `decorators.py`, `managers.py`, `models/beltradar.py`, `tasks.py` and `thirdparty/discord.py` import it with `from beltradar.providers import logger` instead of building their own. `api/helpers/actions.py`, `api/helpers/core.py`, `api/snapshot.py`, `api/timer.py`, `forms.py` and `views.py` created a logger they never used; it is removed there. Log records now carry the logger name `beltradar.providers` instead of the module name; the `[Belt Radar]` prefix is unchanged.

<!-- Your changes go here -->

## [2.1.0] - 2026-11-10

### Added

- Updated translations from Weblate.

### Fixed

- Admin access to all survey sessions and belt timers (`visible_to` and `manage_to`) now checks `beltradar.admin_access` instead of `taxsystem.admin_access`, which was a copy error from aa-taxsystem. Users with `beltradar.admin_access` now get the admin view as intended.
- Re-applied the real Weblate translations (about 21 to 24 per language, plus `cs` and `sk`) that were lost when the bundled package translations emptied the pre-filled values, so Weblate can rebase its branch again. Untranslated strings stay empty.
- Market price update no longer fails or stores `0.00` when an ESI entry has no `adjusted_price`; `EveMarketPrice.adjusted_price` is now nullable (migration required)
- Market price update no longer aborts when ESI returns a type missing from the local SDE; these types are skipped and logged as a warning, all other prices are still stored.
- Fixed `make coverage` exiting with 0 when tests failed. The reports are still created, and the target now exits with the status of the test run, or with the status of `coverage report` if the tests passed.
- Bumped the dev dependency `brace-expansion` in the root `package-lock.json` from 5.0.9 to 5.0.12 to close a Dependabot security alert (affected: >= 4.0.0, < 5.0.12). Only the lockfile changed.

### Changed

- Language files hold only real translations as Weblate writes them, missing keys fall back to English. `i18next-scanner` now maintains only `frontend/i18n/en/translation.json`; the empty placeholder values were removed from all other languages.
- Removed the unused property `EveMarketPrice.get_compressed_price`.
- Replaced `pook` with `pookx` in the test dependencies.
- Test factories for Alliance Auth (`UserFactory`, `EveCharacterFactory`, `add_character_to_user`, ...) now come only from `aa-evesde-factory`; the repo keeps just its own `UserMainFactory` and the Belt Radar model factories. Fixed the import section order of the test data module.
- Tables migrated to TanStack Table v9.
- Updated `vitest` and `@vitest/coverage-v8` to 5.0.5 (includes the security fix in `@vitest/mocker`).
- The ESI client now loads a bundled OpenAPI spec (`beltradar/openapi_2026-08-18.json`) instead of downloading it at runtime.
- Updated the ESI compatibility date from `2025-12-16` to `2026-08-18`.
- Removed the unused forms `UserSettingsForm`, `DeleteSnapshotForm`, `DeleteSessionForm`, `ModifySessionForm`, `DeleteBeltTimerForm`, `CreateTimerForm` and `ModifyBeltTimerForm`.
- Test base classes in `beltradar/tests/__init__.py` now match the repository template: `BeltRadarTestCase` was renamed to `AuthTestCase`.
- `aa-geuthur-react` raised to `^1.3.0`. The package bundles its own translations and registers them with i18next through `AaReactProvider`, so `Main.tsx` lists only the namespace `translation`, the copies under `beltradar/static/beltradar/i18n/<lng>/aa-geuthur-react.json` are removed and `make react-copy-translations` no longer copies them. Untranslated strings in `frontend/i18n/<lng>/translation.json` are empty instead of English (`i18next-scanner` writes the key as value only for `en`); `returnEmptyString: false` shows the English fallback at runtime. Translate on Weblate as before.
- The React frontend now uses the shared npm package [aa-geuthur-react](https://github.com/Geuthur/aa-geuthur-react) (1.2.0) instead of its own copies of the table, modal, loader, header, menu and util modules. The app structure follows the repository template (`Main.tsx`, `Routing.tsx`, `constants.ts`), the pages are wrapped by `AuthBase` of the package (`aa-react container`, 640 to 1280 px, `fluidOnSmallScreens` on phones), the navigation menu is the menu of the package, and the stylesheet and the ESLint import rule come from the package. Visible differences: the table footer of the package (page size, status and paging next to each other), flat section headers in the session view, and spinner and error icons in package size.
- API: the menu, user and settings endpoints follow the contract of `aa-geuthur-react`. `view/menu/` is now `menu/` and delivers `left_links` and `right_links` (the `modals` stay), `view/user/` is now `user/` and additionally delivers `corporation_id`, `corporation_name`, `alliance_id`, `alliance_name` and `is_admin` (the superuser flag; `notification` was removed), and `modify/user/settings/` was replaced by `GET settings/` and `PUT settings/` with a JSON body `{"disable_notifications": bool}`. The data endpoints (`view/session/...`, `view/public-sessions/` and so on) are unchanged.

### Removed

- CI: dropped the obsolete `libbz2-dev` install step.

## [2.0.1] - 2026-10-18

### Changed

- Replaced `<main>` and `<section>` layout elements with `react-bootstrap` `Card` and theme-compatible containers across all pages, headers, dashboards, and session components.
- Added comprehensive CSS design tokens and theme overrides in `index.css` and `beltradar.css` for full Flatly and Darkly Alliance Auth compatibility.

## [2.0.0] - 2026-10-06

> [!CAUTION]
> Please note that this release involves structural changes.
> All Survey Entries and Sessions will be removed.

### Added

- Survey snapshots can now be created and managed with raw Survey Scanner data via a dedicated modal.
- Snapshot selector and action buttons for managing mining survey snapshots in the session view.
- Dynamic belt size selection in the belt timer creation form based on the selected belt type.
- User settings page with notification preferences.
- Belt timer creation and deletion functionality directly in the session view header and dashboard.
- Automatic locale detection matching Django's language settings for date, time, and duration formatting.

### Changed

- Modernized user interface using the Alliance Auth design system (`aa-panel`, `aa-table`, and status badges).
- Session view refreshes automatically every 30 seconds with a live status indicator.
- Belt timers are now automatically created once only 10% of the initial belt volume remains.
- Redesigned User Settings page with modern panel styling.
- Standalone belt timers can now be edited with dynamic ETA recalculation, while session-linked timers support visibility toggling (`is_public`).
- Updated and expanded German translations across all forms and views.

### Fixed

- Mining speed per snapshot was calculated against the first snapshot instead of the directly preceding one.
- Session speed, ETA and income calculations were distorted by pauses between snapshots; they are now calculated based on active mining intervals.
- Fixed inaccurate belt type and size resolution in the session view.
- Prevented duplicate session data reloads.

## [1.0.1] - 2026-09-05

## [1.0.0] - 2026-09-05

> [!CAUTION]
> Please note that this release involves structural changes.
> All Survey Entries and Sessions will be removed.

### Fixed

- Session management icons with permission checks for modify and delete actions
- TrafficContainer Error Response
- AttributeError if User has no Main Character
- Permission Issues

### Added

- Session and BeltTimer modification functionality, including forms and modals
- Public Icon in Session Views
- "is_public" field for Session Model
- Dynamic Belt & Snapshot Management
- Belt Timer Creation Triggered by 4 Submitted Surveys (Auto Timer)
- `BeltSurveySnapshot` Model
- BeltTimer Filter for expired timers
- Belt Type & Belt Size Expection
- Bootstrap5 Tooltip to Progress Bar
- "Export to CSV" function

### Changed

- Public Session will only display if `is_public` is `true`
- Create Timer & Session now are interactive
- Optimized DataTables CSS
- Refactor Belt Radar Models & Managers
- Convert Raw Numbers to Int for better readability
- ETA will display 'Done' if it is in the past
- permission checks to return None for not found cases and update related error handling in API endpoints
- Belt Respawn Timers Can Now Be Created Without a Session Assignment

## [0.5.1] - 2026-08-08

### Added

- Traffic Chart

### Changed

- Moved Chart Generation from API Endpoint to Helper Function

## [0.5.0] - 2026-08-05

### Added

- `dhook-lite` dependency
- Discord Webhook support for Belt Timer Respawn
  - `BELT_RADAR_WEBHOOK_URL` Setting for Webhook Support

### Changed

- `DownTimeError` Will no longer send out warning logs
- Refactor templates & url viewnames
- Added `User` Field in Belt Timer Model
- Optimized JS Function `updateBeltSizeChoices`
- Belt Timer no longer assign to a session
- Renamed `All Sessions` to `Belt Radar`
- Renamed `My Sessions` to `My Belt Radar`
- Refactor `BeltSurveySession`
- Moved "Estimated Finish" time to ETA:

### Removed

- `session` field from Belt Timer Model

## [0.2.0] - 2026-08-02

### Added

- Belt Respawn Timer
  - Belt timer display in Session view showing estimated respawn time
  - Persistent timer state across sessions
  - Optional Discord Notification (default: true) can be disabled by user
- User Settings
  - Turnable Notification

### Changed

- pin `allianceauth` to `>=5.2`
- Update Authentication Foreign from AA v5.2
- `update_all_belt_radar` task interval from 12 Hours to 10 Minutes

## [0.1.0] - 2026-07-13

### Fixed

- Delete Session redirect
- 1406, "Data too long for column 'public_id' at row 1"
- Delete Session in "All Sessions" View

### Changed

- public_id has been shortened to 12 letters

## [0.0.9] - 2026-06-10

### Added

- Validate required fields in the survey form

### Changed

- Enhance survey form validation

## [0.0.8] - 2026-06-03

### Added

- User Sessions View
- Python 3.13 Support
- Compatibility to Alliance Auth v5

### Fixed

- Users not seeing Sessions from other users with permission

### Changed

- Enhance market price update task with retry mechanism

### Removed

- Compatibility to Alliance Auth v4

## [0.0.7] - 2026-05-25

### Added

- EveMarketPrice Model
- Update Market Price Task
- API Response Handling for Modals
- Shake Animation for Errors
- Custom AllianceAuth’s fetchGet & fetchPost implementations and added unified error response handling.
- Migration for EveMarketPrice

### Changed

- Unified Timestamp per Snapshot
- Optimized Charts
- Add Survey button now loads data interactively without page reload
- Performance Optimation for "Add Survey"
- Add Survey Button minimized and moved to Survey Table

### Fixed

- BS5 Tooltip in EvE Render Function
- Decimal Issue
- Empty Session Name

### Removed

- Add Survey view is now handled via modal

## [0.0.6] - 2026-05-17

### Added

- Back to Session button in "Add Survey" view
- many propterties for `BeltSurveySession`
- Loading Animation for new Data in "View Session"
- ApexCharts v5.12.0 for visualisation of Mining Data

### Changed

- Moved `mining_stats` function to managers
- Optimized Stats Calculation
- Optimized CSS

### Fixed

- Error Handling in API
- `get_owner_or_none` Error
- DataTable Issues
- Wrong deletion for "Delete Snapshot" button

## [0.0.5] - 2026-05-16

### Added

- `last_entry`, `last_entry_snapshot` to `BeltSurveySession` Model

### Changed

- Refine ore data parsing logic and improve error handling
- View Session now display only last Snapshot

### Fixed

- MultipleObjectsReturned in `get_owner_or_none`
- Overlapping Snapshot Hash

### Removed

- `latest_entries` from `BeltSurveySession` Model

## [0.0.4] - 2026-05-16

### Added

- Translation Files

## [0.0.3] - 2026-05-16

### Added

- Display estimated completion time for belt mining
- Display remaining volume and belt size information
- Show mining speed in m³/s
- Permission System to view and manage Survey Sessions
- Prepared Task Function

## [0.0.1] - 2026-05-14

### Added

- Initial public release

<!-- Links -->

[0.0.1]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.1...v0.0.1 "v0.0.1"
[0.0.3]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.1...v0.0.3 "v0.0.3"
[0.0.4]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.3...v0.0.4 "v0.0.4"
[0.0.5]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.4...v0.0.5 "v0.0.5"
[0.0.6]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.5...v0.0.6 "v0.0.6"
[0.0.7]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.6...v0.0.7 "v0.0.7"
[0.0.8]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.7...v0.0.8 "v0.0.8"
[0.0.9]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.8...v0.0.9 "v0.0.9"
[0.1.0]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.9...v0.1.0 "v0.1.0"
[0.2.0]: https://github.com/Geuthur/aa-beltradar/compare/v0.1.0...v0.2.0 "v0.2.0"
[0.5.0]: https://github.com/Geuthur/aa-beltradar/compare/v0.2.0...v0.5.0 "v0.5.0"
[0.5.1]: https://github.com/Geuthur/aa-beltradar/compare/v0.5.0...v0.5.1 "v0.5.1"
[1.0.0]: https://github.com/Geuthur/aa-beltradar/compare/v0.5.1...v1.0.0 "v1.0.0"
[1.0.1]: https://github.com/Geuthur/aa-beltradar/compare/v1.0.0...v1.0.1 "v1.0.1"
[2.0.0]: https://github.com/Geuthur/aa-beltradar/compare/v1.0.1...v2.0.0 "v2.0.0"
[2.0.1]: https://github.com/Geuthur/aa-beltradar/compare/v2.0.0...v2.0.1 "v2.0.1"
[2.1.0]: https://github.com/Geuthur/aa-beltradar/compare/v2.0.1...v2.1.0 "v2.1.0"
[in development]: https://github.com/Geuthur/aa-beltradar/compare/v2.1.0...HEAD "In Development"
