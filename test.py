import shutil
import tempfile
import threading
import unittest
from pathlib import Path

from json_database_manager import JSONDatabaseManager  # ajuste o import para o nome do seu arquivo


class TestJSONDatabaseManager(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory and database file for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_db.json"
        self.db = JSONDatabaseManager(str(self.db_path))

    def tearDown(self):
        """Remove temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_load_empty(self):
        """JSONDatabaseManager should start empty if file does not exist."""
        self.assertEqual(self.db.get_all(), {})

    def test_set_and_get(self):
        """Should store and retrieve values correctly."""
        self.db.set("theme", "dark")
        self.assertEqual(self.db.get("theme"), "dark")

    def test_get_default_value(self):
        """Should return default value if key does not exist."""
        self.assertEqual(self.db.get("missing", "default"), "default")

    def test_exists(self):
        """Should correctly report key existence."""
        self.db.set("language", "en")
        self.assertTrue(self.db.exists("language"))
        self.assertFalse(self.db.exists("missing"))

    def test_delete_existing_key(self):
        """Should delete existing key and return True."""
        self.db.set("key", "value")
        result = self.db.delete("key")
        self.assertTrue(result)
        self.assertFalse(self.db.exists("key"))

    def test_delete_missing_key(self):
        """Should return False when deleting non-existing key."""
        result = self.db.delete("missing")
        self.assertFalse(result)

    def test_update_multiple_values(self):
        """Should update multiple values at once."""
        self.db.update({"a": 1, "b": 2})
        self.assertEqual(self.db.get("a"), 1)
        self.assertEqual(self.db.get("b"), 2)

    def test_clear_database(self):
        """Should remove all entries."""
        self.db.set("a", 1)
        self.db.set("b", 2)
        self.db.clear()
        self.assertEqual(self.db.get_all(), {})

    def test_persistence_on_disk(self):
        """Data should persist after reloading the database."""
        self.db.set("theme", "dark")
        self.db.set("volume", 80)

        # Reload database from disk
        new_db = JSONDatabaseManager(str(self.db_path))
        self.assertEqual(new_db.get("theme"), "dark")
        self.assertEqual(new_db.get("volume"), 80)

    def test_invalid_json_file_recovery(self):
        """Should recover gracefully from invalid JSON file."""
        # Write invalid JSON manually
        self.db_path.write_text("{ invalid json", encoding="utf-8")

        new_db = JSONDatabaseManager(str(self.db_path))
        self.assertEqual(new_db.get_all(), {})

    def test_thread_safety_basic(self):
        """Basic thread-safety test with concurrent writes."""
        def worker(i):
            self.db.set(f"key_{i}", i)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for i in range(20):
            self.assertEqual(self.db.get(f"key_{i}"), i)


if __name__ == "__main__":
    unittest.main()
