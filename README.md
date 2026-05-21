![Release](https://img.shields.io/pypi/v/aa-beltradar?label=release)
![Licence](https://img.shields.io/github/license/geuthur/aa-beltradar)
![Python](https://img.shields.io/pypi/pyversions/aa-beltradar)
![Django](https://img.shields.io/pypi/frameworkversions/django/aa-beltradar.svg?label=django)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/aa-beltradar/master.svg)](https://results.pre-commit.ci/latest/github/Geuthur/aa-beltradar/master)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checks](https://github.com/Geuthur/aa-beltradar/actions/workflows/autotester.yml/badge.svg)](https://github.com/Geuthur/aa-beltradar/actions/workflows/autotester.yml)
[![codecov](https://codecov.io/gh/Geuthur/aa-beltradar/graph/badge.svg?token=cwR63HffuI)](https://codecov.io/gh/Geuthur/aa-beltradar)
[![Translation status](https://weblate.geuthur.de/widget/allianceauth/aa-beltradar/svg-badge.svg)](https://weblate.geuthur.de/engage/allianceauth/)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W810Q5J4)

# AA Belt Radar module for AllianceAuth.<a name="aa-beltradar"></a>

A Belt Survey Analyser to track how fast you mine your belt.

______________________________________________________________________

- [AA Belt Radar](#aa-beltradar)
  - [Features](#features)
  - [Upcoming](#upcoming)
  - [Highlights](#highlights)
  - [Installation](#features)
    - [Step 1 - Install the Package](#step1)
    - [Step 2 - Configure Alliance Auth](#step2)
    - [Step 3 - Add the Scheduled Tasks and Settings](#step3)
    - [Step 4 - Migrate & Preload EVE SDE Data](#step4)
      - [Step 4.1 - Migrate App and collect static](#step41)
    - [Step 5 - Setting up Permissions](#step5)
    - [Step 6 - (Optional) Setting up Compatibilies](#step6)
  - [Translations](#translations)
  - [Contributing](#contributing)

## Features<a name="features"></a>

- Display estimated completion time for belt mining
- Show mining speed in m³/s
- Display remaining volume and belt size information
- Optional Share your Mining Session with others

## Upcoming<a name="upcoming"></a>

- Respawn Timer for Belts
- Graphical Upgrades
- Compressed Price

## Highlights<a name="highlights"></a>

![Image: Belt Radar Dashboard]

![Image: Belt Radar My Sessions]

![Image: Belt Radar View Session]

## Installation<a name="installation"></a>

> [!NOTE]
> AA Belt Radar needs at least Alliance Auth v5
> Please make sure to update your Alliance Auth before you install this APP

### Step 1 - Install the Package<a name="step1"></a>

Make sure you're in your virtual environment (venv) of your Alliance Auth then install the pakage.

```shell
pip install aa-beltradar
```

### Step 2 - Configure Alliance Auth<a name="step2"></a>

Configure your Alliance Auth settings (`local.py`) as follows:

```python
INSTALLED_APPS = [
    # other apps
    "eve_sde",  # only if it not already existing
    "beltradar",
    # other apps?
]

# This line is right below the `INSTALLED_APPS` list, if not already exist!
INSTALLED_APPS = ["modeltranslation"] + INSTALLED_APPS
```

### Step 3 - Add the Scheduled Tasks<a name="step3"></a>

To set up the Scheduled Tasks add following code to your `local.py`

```python
CELERYBEAT_SCHEDULE["AA Belt Radar :: Update Belt Radar"] = {
    "task": "beltradar.tasks.update_all_belt_radar",
    "schedule": 43200,
}
CELERYBEAT_SCHEDULE["AA Belt Radar :: Update Market Price"] = {
    "task": "beltradar.tasks.update_market_prices",
    "schedule": 86400,
}
```

### Step 3.1 - (Optional) Add own Logger File

To set up the Logger add following code to your `local.py`
Ensure that you have writing permission in logs folder.

```python
LOGGING["handlers"]["beltradar_file"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(BASE_DIR, "log/beltradar.log"),
    "formatter": "verbose",
    "maxBytes": 1024 * 1024 * 5,
    "backupCount": 5,
}
LOGGING["loggers"]["extensions.beltradar"] = {
    "handlers": ["beltradar_file"],
    "level": "DEBUG",
}
```

### Step 4 - Migrate & Preload EVE SDE Data<a name="step4"></a>

AA Skillfarm uses EVE SDE data to map IDs to names for EveTypes. You will need to preload some data from SDE once.

```shell
python manage.py migrate eve_sde
python manage.py esde_load_sde
```

### Step 4.1 - Migrate App and collect static<a name="step41">

Migrate the app and collect static.

```shell
python manage.py migrate beltradar
python manage.py aabeltradar_migrate_market_data
python manage.py collectstatic --noinput
```

### Step 5 - Setting up Permissions<a name="step5"></a>

With the Following IDs you can set up the permissions for the Belt Radar

| ID              | Description                       |                                                            |
| :-------------- | :-------------------------------- | :--------------------------------------------------------- |
| `basic_access`  | Can access the Belt Radar module  | All Members with the Permission can access the Belt Radar. |
| `manage_access` | Can Manage Belt Radar module      | Can manage Application                                     |
| `admin_access`  | Has access to all Survey Sessions | Can see all Survey Sessions                                |

### Step 6 - (Optional) Setting up Compatibilies<a name="step6"></a>

The Following Settings can be setting up in the `local.py`

| Setting Name                 | Descriptioon                                      | Default        |
| ---------------------------- | ------------------------------------------------- | -------------- |
| `BELT_RADAR_APP_NAME`        | Set the name of the APP                           | `"Belt Radar"` |
| `BELT_RADAR_TASK_TIME_LIMIT` | Defines the time (in seconds) a task will timeout | `1200`         |

## Translations<a name="translations"></a>

[![Translations](https://weblate.geuthur.de/widget/allianceauth/aa-beltradar/multi-auto.svg)](https://weblate.geuthur.de/engage/allianceauth/)

Help us translate this app into your language or improve existing translations. Join our team!"

## Contributing <a name="contributing"></a>

You want to improve the project?
Please ensure you read the [Contribution Guidelines]

<!-- MD Links -->

[contribution guidelines]: https://github.com/Geuthur/aa-beltradar/blob/master/CONTRIBUTING.md "Contribution Guidelines"
[image: belt radar dashboard]: https://raw.githubusercontent.com/Geuthur/aa-beltradar/master/docs/images/aa-beltradar-index.png "AA Belt Radar Dashboard"
[image: belt radar my sessions]: https://raw.githubusercontent.com/Geuthur/aa-beltradar/master/docs/images/aa-beltradar-my-sessions.png "AA Belt Radar (My Sessions)"
[image: belt radar view session]: https://raw.githubusercontent.com/Geuthur/aa-beltradar/master/docs/images/aa-beltradar-view-session.png "AA Belt Radar (View Session)"
