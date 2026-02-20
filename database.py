import json
from pathlib import Path
from typing import Any
import threading


class Database:
    """
    Thread-safe JSON database manager.

    This class provides a simple key-value storage backed by a JSON file,
    ensuring safe concurrent access using reentrant locks and atomic writes.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the JSON database.

        Parameters
        ----------
        file_path : str
            Path to the JSON file used for persistent storage.
        """
        self.file_path = Path(file_path)
        self._lock = threading.RLock()
        self._ensure_directory_exists()
        self.data = self.load_data()

    def _ensure_directory_exists(self) -> None:
        """
        Ensure that the parent directory of the database file exists.

        Creates the directory tree if it does not already exist.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> dict:
        """
        Load data from the JSON file.

        Returns
        -------
        dict
            The parsed JSON data, or an empty dictionary if the file does not exist
            or contains invalid JSON.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(
                f"Warning: Invalid JSON file at {self.file_path}. "
                "Starting with empty data."
            )
            return {}

    def _save_data(self) -> None:
        """
        Persist the in-memory data to disk using an atomic write strategy.

        Writes to a temporary file first and then replaces the original file
        to reduce the risk of data corruption.

        Raises
        ------
        IOError
            If an error occurs while writing the file.
        """
        with self._lock:
            try:
                # Write to a temporary file first for safety
                temp_path = self.file_path.with_suffix(".tmp")
                with open(temp_path, "w", encoding="utf-8") as file:
                    json.dump(self.data, file, indent=4, ensure_ascii=False)

                # Atomically replace the original file
                temp_path.replace(self.file_path)
            except IOError as e:
                raise IOError(f"Failed to save data to {self.file_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from the database.

        Parameters
        ----------
        key : str
            Key to retrieve.
        default : Any, optional
            Default value returned if the key does not exist.

        Returns
        -------
        Any
            The stored value associated with the key, or `default` if the key is not found.
        """
        with self._lock:
            return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the database and persist it to disk.

        Parameters
        ----------
        key : str
            Key to set.
        value : Any
            Value to store.
        """
        with self._lock:
            self.data[key] = value
            self._save_data()

    def delete(self, key: str) -> bool:
        """
        Delete a key from the database.

        Parameters
        ----------
        key : str
            Key to delete.

        Returns
        -------
        bool
            True if the key existed and was deleted, False otherwise.
        """
        with self._lock:
            if key in self.data:
                del self.data[key]
                self._save_data()
                return True
            return False

    def clear(self) -> None:
        """
        Remove all entries from the database and persist the change.
        """
        with self._lock:
            self.data.clear()
            self._save_data()

    def exists(self, key: str) -> bool:
        """
        Check whether a key exists in the database.

        Parameters
        ----------
        key : str
            Key to check.

        Returns
        -------
        bool
            True if the key exists, False otherwise.
        """
        with self._lock:
            return key in self.data

    def update(self, updates: dict) -> None:
        """
        Update multiple key-value pairs at once and persist the changes.

        Parameters
        ----------
        updates : dict
            Dictionary containing key-value pairs to update.
        """
        with self._lock:
            self.data.update(updates)
            self._save_data()

    def get_all(self) -> dict:
        """
        Return a shallow copy of all stored data.

        Returns
        -------
        dict
            A copy of the internal data dictionary.
        """
        with self._lock:
            return self.data.copy()


# Example usage
# if __name__ == "__main__":
#     settings_database = Database(file_path="./storage/data/settings.json")

#     # Use the database
#     settings_database.set("theme", "dark")
#     settings_database.set("language", "en-us")

#     print(settings_database.get("theme"))      # dark
#     print(settings_database.exists("theme"))   # True
#     print(settings_database.get_all())         # {'theme': 'dark', 'language': 'en-us'}