# AA Belt Radar module for AllianceAuth.<a name="aa-beltradar"></a>

> [!WARNING]
> Before you create Models, etc remove the 0001_initial.py from migrations folder if you dont have created own one.

A Belt Survey Analyser to track how fast you mine your belt.

______________________________________________________________________

- [AA Belt Radar](#aa-beltradar)
  - [Features](#features)
  - [Upcoming](#upcoming)
  - [Installation](#features)
    - [Step 1 - Install the Package](#step1)
    - [Step 2 - Configure Alliance Auth](#step2)
    - [Step 3 - Add the Scheduled Tasks and Settings](#step3)
    - [Step 4 - Migration to AA](#step4)
    - [Step 5 - Setting up Permissions](#step5)
    - [Step 6 - (Optional) Setting up Compatibilies](#step6)
  - [Highlights](#highlights)

## Features<a name="features"></a>

## Upcoming<a name="upcoming"></a>

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

- Add `'beltradar',` to `INSTALLED_APPS`

### Step 3 - Add the Scheduled Tasks<a name="step3"></a>

To set up the Scheduled Tasks add following code to your `local.py`

```python
CELERYBEAT_SCHEDULE["AA Belt Radar :: Belt Radar"] = {
    "task": "beltradar.tasks.example_task",
    "schedule": crontab(minute=0, hour="*/1"),
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

### Step 4 - Migration to AA<a name="step4"></a>

Migrate the app and collect static.

```shell
python manage.py migrate beltradar
python manage.py collectstatic --noinput
```

### Step 5 - Setting up Permissions<a name="step5"></a>

With the Following IDs you can set up the permissions for the Belt Radar

| ID              | Description                      |                                                            |
| :-------------- | :------------------------------- | :--------------------------------------------------------- |
| `basic_access`  | Can access the Belt Radar module | All Members with the Permission can access the Belt Radar. |
| `manage_access` | Can Manage Belt Radar module     | Can manage Application                                     |

### Step 6 - (Optional) Setting up Compatibilies<a name="step6"></a>

The Following Settings can be setting up in the `local.py`

- BELTRADAR_APP_NAME: `"YOURNAME"` - Set the name of the APP
- BELTRADAR_TASKS_TIME_LIMIT: `7200` - Defines the time (in seconds) a task will timeout

## Highlights<a name="highlights"></a>

> [!NOTE]
> Contributing
> You want to improve the project?
> Just Make a [Pull Request](https://github.com/Geuthur/aa-beltradar/pulls) with the Guidelines.
> We Using pre-commit
