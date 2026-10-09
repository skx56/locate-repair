# Locate and repair

Three synthetic defects. A localisation claim is accepted only when the file, the symbol, and the line all match. A repair is accepted only when the behavior tests pass.

This is not an agent task and not a tool trace. The grader checks a submitted location, then checks a patched file by running it.

| Task | Defect |
| --- | --- |
| `path-notes` | `read_note` joins a name onto the notes directory and will follow `..` |
| `customer-lookup` | `find_customer` puts the name into the SQL string, so `O'Brien` does not match |
| `export-cap` | `allow_export` treats a negative row count as allowed for a non-admin |

```bash
python3 -m unittest discover -s tests -v
python3 grade.py demo
```

`demo` exits 0 only when every gold location passes, a filename-only claim fails, every gold repair passes, and every original file fails.

Grade one claim or one patched file:

```bash
python3 grade.py locate path-notes tasks/path-notes/gold/location.json
python3 grade.py repair path-notes tasks/path-notes/gold/store.py
python3 grade.py repair path-notes tasks/path-notes/buggy/store.py
```

The repair command prints a reason and exits 1 when the tests fail.
