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

- Belt Respawn Timer
  - Belt timer display in Session view showing estimated respawn time
  - Persistent timer state across sessions8

### Changed

- pin `allianceauth` to `>=5.2`
- Update Authentication Foreign from AA v5.2

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

[0.0.1]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.1...v0.0.1 "v0.0.1"
[0.0.3]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.1...v0.0.3 "v0.0.3"
[0.0.4]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.3...v0.0.4 "v0.0.4"
[0.0.5]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.4...v0.0.5 "v0.0.5"
[0.0.6]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.5...v0.0.6 "v0.0.6"
[0.0.7]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.6...v0.0.7 "v0.0.7"
[0.0.8]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.7...v0.0.8 "v0.0.8"
[0.0.9]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.8...v0.0.9 "v0.0.9"
[in development]: https://github.com/Geuthur/aa-beltradar/compare/v0.0.9...HEAD "In Development"
