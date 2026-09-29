from pathlib import Path

from storage.local import LocalStorage

storage = LocalStorage("./storage_data")

test_file = Path("test.txt")
test_file.write_text("Hello AI Drive")
storage.save(
    test_file,
    "test-file-123",
)

print(storage.exists("test-file-123"))
print(
    storage.get("test-file-123").read_text()
)

storage.delete("test-file-123")
print(storage.exists("test-file-123"))

test_file.unlink()