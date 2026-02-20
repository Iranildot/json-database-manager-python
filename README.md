# Database Usage Example

This document provides a practical example of how to use the `Database` class for managing
application settings and user preferences using a JSON file with thread-safe access.

## Installation

Make sure you have your `database.py` file available in your project:

```bash
project/
├── database.py
└── main.py
```

## Example: Managing Application Settings

```python
from database import Database


def main():
    # Initialize the database (JSON file will be created automatically if it does not exist)
    settings_db = Database(file_path="./storage/data/settings.json")

    # Save application settings
    settings_db.set("theme", "dark")
    settings_db.set("language", "en-us")
    settings_db.set("window_size", {"width": 1280, "height": 800})
    settings_db.set("recent_files", [])

    # Read values
    theme = settings_db.get("theme", default="light")
    language = settings_db.get("language", default="en-us")
    window_size = settings_db.get("window_size", default={"width": 1024, "height": 768})

    print("Theme:", theme)
    print("Language:", language)
    print("Window size:", window_size)

    # Update multiple values at once
    settings_db.update({
        "theme": "light",
        "auto_save": True,
    })

    # Work with collections
    recent_files = settings_db.get("recent_files", [])
    recent_files.append("/home/user/Documents/report.pdf")
    recent_files.append("/home/user/Documents/notes.txt")
    settings_db.set("recent_files", recent_files)

    # Conditional logic
    if not settings_db.exists("onboarding_completed"):
        print("First run detected. Showing onboarding...")
        settings_db.set("onboarding_completed", True)

    # Remove a setting
    settings_db.delete("auto_save")

    # Read everything (e.g., for debugging or exporting)
    all_settings = settings_db.get_all()
    print("All settings:", all_settings)


if __name__ == "__main__":
    main()
```

## Typical Use Cases

- User preferences (theme, language, layout)
- Application configuration files
- Feature flags
- Simple local cache
- Desktop apps using Tkinter / CustomTkinter

## Notes

- The database automatically creates directories if they do not exist.
- Writes are atomic to reduce the risk of file corruption.
- The implementation is thread-safe for concurrent access.
