Okay, here is the comprehensive documentation for the `pybitcask` repository, based on the provided information and adhering to the requested structure.

**Note:** As the repository structure provided only lists documentation and configuration files, and not the actual source code directories (`pybitcask/`, `tests/`), parts of this documentation, particularly concerning Core Components and specific Source File implementation details, are based on the information inferred from the README, `pyproject.toml`, and standard Bitcask architecture principles. A full analysis would require access to the source code files.

# pybitcask Documentation

## 1. Project Overview

### Purpose and Goals
*   **Primary Objectives:** To provide a pure Python implementation of the Bitcask key-value storage model, focusing on high write throughput and simplicity.
*   **Intended Use Cases:** Ideal for scenarios demanding fast key-value storage, such as log aggregation, event sourcing, real-time data collection (IoT), session storage, configuration management, and cache persistence. It's also suitable where data recovery from append-only logs is beneficial (e.g., audit trails, transaction logs).
*   **Target Audience:** Python developers needing a simple, persistent, disk-based key-value store with good write performance, particularly when the entire keyset can fit comfortably in memory.
*   **Business or Technical Problems Solved:** Addresses the need for a performant key-value store where write speed is critical and read access is primarily by key lookup. It offers a simpler alternative to more complex database systems for specific use cases.
*   **Unique Value Proposition:** Offers a straightforward implementation of the established Bitcask design in Python, emphasizing ease of use and integration into Python applications, leveraging an append-only log for durability and fast writes.

### Key Features
*   **Core Functionality:** Provides basic key-value operations (`put`, `get`, `delete`, `keys`).
*   **Append-Only Log Storage:** All writes append to the current data file, ensuring high write throughput and inherent data durability.
*   **In-Memory Index (KeyDir):** Maintains an index of all keys in memory, mapping keys to the location (file ID, offset, size) of their latest value on disk, enabling fast read operations.
*   **Thread-Safe Operations:** Designed to allow safe concurrent access from multiple threads (stated as single-writer, multiple-reader safe in limitations, implying internal locking).
*   **Data Persistence:** Data is stored durably on disk in segment files.
*   **Complex Data Type Support:** Allows storing complex Python objects by serializing them to JSON before storage (and deserializing upon retrieval).
*   **Tombstone-Based Deletion:** Deleting a key writes a special "tombstone" marker to the log file; the actual data removal requires a separate compaction process (currently noted as a future improvement).

### Technology Stack
*   **Programming Language:** Python (>= 3.8)
*   **Database and Storage:** Custom implementation using append-only data files on the local filesystem and an in-memory Python dictionary for the key index.
*   **External Services:** None directly required for core functionality.
*   **Key Dependencies (Core):** None explicitly listed in `pyproject.toml`'s main `dependencies`.
*   **Development and Deployment Tools:**
    *   Package Management: `uv` (recommended), `pip`
    *   Testing: `pytest`, `pytest-cov`
    *   Linting/Formatting: `ruff`, `black`, `isort`
    *   CI/Hooks: `pre-commit`

## 2. Repository Structure

### Directory Organization
*   **Root Directory:** Contains primary configuration, documentation, and helper scripts.
    *   `.pre-commit-config.yaml`: Configuration for pre-commit hooks.
    *   `BENCHMARKS.md`: (Assumed) Contains performance benchmark results.
    *   `COMPARISON.md`: (Assumed) Compares pybitcask to other key-value stores.
    *   `README.md`: Project overview, setup, usage examples, and design notes.
    *   `pyproject.toml`: Project metadata, dependencies, and tool configurations (PEP 517/518).
    *   `project-guardian.sh`: Convenience script for setting up the development environment.
*   **Source Directory (`pybitcask/` - Assumed):** *Location not listed in provided structure, but standard practice.* Contains the core implementation of the Bitcask engine.
*   **Tests Directory (`tests/` - Assumed):** *Location not listed, but specified in `pyproject.toml`.* Contains unit and integration tests for the `pybitcask` library.
*   **Data Directory (e.g., `iot_data/` in example):** Created at runtime by the `Bitcask` instance to store data files. Not part of the repository structure itself.

### File Conventions
*   **Naming:** Python modules and packages follow PEP 8 (lowercase_with_underscores). Test files follow the `*_test.py` pattern (`pytest` convention).
*   **Organization:** Code is expected to be organized within the `pybitcask` package. Tests reside in the `tests` directory.
*   **Configuration:** Project configuration centralized in `pyproject.toml`. Pre-commit hooks configured in `.pre-commit-config.yaml`.
*   **Documentation:** Primary documentation in `README.md`. Specific topics like benchmarks and comparisons have dedicated Markdown files (`BENCHMARKS.md`, `COMPARISON.md`). Docstrings within the code are expected (enforced by `ruff`'s `D` rules).

## 3. Core Components
*(Based on Bitcask architecture and README information, as source code is not provided)*

### Main Modules
*   **`pybitcask` (Package Root):** Likely exposes the main `Bitcask` class for public use.
*   **`bitcask` (e.g., `pybitcask/bitcask.py` - Assumed):** Contains the main `Bitcask` class orchestrating reads, writes, deletes, and managing data files and the KeyDir.
*   **`data_file` (e.g., `pybitcask/data_file.py` - Assumed):** Manages reading from and writing to individual append-only data segment files. Handles file rotation (creating new segments when the active one reaches a size limit). Encapsulates the on-disk entry format (CRC, timestamp, key size, value size, key, value - *Assumed Standard Bitcask Format*).
*   **`key_dir` (e.g., `pybitcask/key_dir.py` - Assumed):** Implements the in-memory hash map (likely a Python `dict`) storing the mapping from keys to their disk location (`file_id`, `value_offset`, `value_size`, `timestamp`). Responsible for loading the index from data files on startup.
*   **`entry` (e.g., `pybitcask/entry.py` - Assumed):** Defines the structure and serialization/deserialization logic for log entries written to data files.

### Key Classes and Functions
*   **`Bitcask(data_dir)`:**
    *   Purpose: The main public interface to the key-value store.
    *   `__init__(self, data_dir)`: Initializes the store, creates the data directory if needed, loads the KeyDir by scanning existing data files, and opens the active data file for writing.
    *   `put(self, key, value)`: Serializes the value (using JSON by default), creates a log entry, appends it to the active data file, and updates the KeyDir with the new location. Handles file rotation if the active file exceeds a size threshold.
    *   `get(self, key)`: Looks up the key in the KeyDir. If found, reads the value from the specified location in the corresponding data file and deserializes it. Returns `None` or raises `KeyError` if not found.
    *   `delete(self, key)`: Writes a special "tombstone" entry for the key to the active data file and removes the key from the in-memory KeyDir.
    *   `keys(self)`: Returns an iterable or list of all current keys stored in the KeyDir.
    *   `close(self)`: Closes the active data file handle.
*   **(Internal Functions/Methods - Assumed):**
    *   `_load_keydir()`: Scans all data files on startup to rebuild the in-memory KeyDir.
    *   `_write_entry()`: Handles the low-level logic of writing a serialized entry to the data file.
    *   `_read_value()`: Handles the low-level logic of reading a value from a specific offset in a data file.

### Data Structures
*   **On-Disk Data Files (Segments):** Append-only files containing sequences of log entries. Each entry typically includes metadata (CRC, timestamp, key size, value size) and the key/value data. Older files are read-only.
*   **In-Memory Index (KeyDir):** A Python dictionary (`dict`) mapping `key` (string or bytes) to `(file_id, value_offset, value_size, timestamp)`. This structure allows O(1) average-case lookup time for key locations.
*   **Log Entry Format:** [Assumed Standard Bitcask Format] `CRC (4 bytes) | Timestamp (4 or 8 bytes) | Key Size (4 bytes) | Value Size (4 bytes) | Key (variable) | Value (variable)`
*   **Tombstone:** A special value written during a `delete` operation to mark a key as deleted in the log file.

## 4. Key Files Analysis

### Documentation Files
*   **`README.md`:** Provides a comprehensive introduction, feature list, installation instructions (`uv`-focused), quick start script (`project-guardian.sh`), usage examples (IoT scenario), scaling considerations, limitations, and future improvement plans. Serves as the primary entry point for understanding the project.
*   **`BENCHMARKS.md`:** (Presence inferred) Expected to contain performance metrics for operations like `put`, `get`, possibly comparing different scenarios or configurations. Dependencies listed in `pyproject.toml` (`lmdb`, `matplotlib`, `pandas`, `seaborn`, `psutil`, `tabulate`) support this.
*   **`COMPARISON.md`:** (Presence inferred) Likely provides a qualitative or quantitative comparison of `pybitcask` against other key-value storage solutions (e.g., `dbm`, `leveldb`, `redis`), highlighting trade-offs.
*   **`CONTRIBUTING.md`:** *Not listed.* A standard file outlining how developers can contribute (issue reporting, pull requests, coding standards) would be beneficial.
*   **`CHANGELOG.md`:** *Not listed.* A file tracking version history and changes would improve maintainability and user understanding.
*   **`LICENSE`:** *Not listed as a separate file.* The license (`MIT`) is specified within `pyproject.toml`. Including a `LICENSE` file is standard practice.

### Configuration Files
*   **`.pre-commit-config.yaml`:** Configures pre-commit hooks to automatically run tools like `ruff`, `black`, and `isort` before commits are finalized, ensuring code quality and consistency.
*   **`pyproject.toml`:** Central PEP 517/518 configuration file. Defines:
    *   Project metadata (name, version, description, authors, license).
    *   Core dependencies (currently none specified).
    *   Optional dependencies for different environments (`test`, `benchmark`, `dev`).
    *   Python version requirement (`>=3.8`).
    *   Tool configurations (`pytest`, `ruff`, `isort`).

### Source Files
*(Analysis based on assumptions and README example)*
*   **Main Entry Point (`pybitcask/__init__.py` - Assumed):** Likely imports and exposes the public `Bitcask` class from its implementation module.
*   **Core Logic (`pybitcask/bitcask.py`, `pybitcask/data_file.py`, etc. - Assumed):** Contain the implementation of the `Bitcask` class, data file handling, KeyDir management, and entry serialization/deserialization as described in "Core Components".
*   **Utility Functions (`pybitcask/utils.py` - Possible):** May contain helper functions for file operations, serialization, or other common tasks.
*   **Test Suites (`tests/*_test.py`):** Contain `pytest`-based tests covering the functionality of the `Bitcask` class and its components (e.g., putting/getting values, deleting, handling edge cases, persistence across restarts).
*   **Examples:** The README provides an `IoTDataStore` class example demonstrating how to use `pybitcask` for a specific use case. More examples could reside in an `examples/` directory.

## 5. Dependencies and Requirements

### External Dependencies
*   **Core Runtime:** None specified. The implementation aims to be self-contained using Python's standard library.
*   **Serialization:** Implicitly uses `json` from the standard library based on the README example.
*   **Optional (`test`):** `pytest`, `pytest-cov`
*   **Optional (`benchmark`):** `lmdb`, `matplotlib`, `pandas`, `seaborn`, `psutil`, `tabulate`
*   **Optional (`dev`):** `ruff`, `black`, `isort` (and tools installed via `pre-commit`)
*   **Version Compatibility:** Requires Python version 3.8 or higher. Compatibility details for optional dependencies are managed via `uv` or `pip`.
*   **Security Considerations:** As there are no core external dependencies, the primary security concerns relate to file system permissions for the data directory and the potential vulnerabilities if a different, less safe serialization format (like `pickle`) were used instead of JSON.

### Development Setup
*   **Requirements:** Git, Python >= 3.8, `uv` (recommended installer).
*   **Setup Steps:**
    1.  `git clone https://github.com/agaonker/pybitcask.git`
    2.  `cd pybitcask`
    3.  `./project-guardian.sh` (Recommended Quick Start) OR Manually:
        *   Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
        *   Create venv: `uv venv .venv`
        *   Activate venv: `source .venv/bin/activate`
        *   Install: `uv pip install -e ".[dev,test,benchmark]"` (Install all optional groups)
        *   Setup hooks: `pre-commit install`
*   **IDE/Tooling:** Any standard Python IDE (VS Code, PyCharm) will work. Integration with `ruff`, `black`, `isort`, and `pytest` is recommended.
*   **Testing:** Run tests using `pytest tests/ -v`.

### Runtime Requirements
*   **System:** Python >= 3.8 interpreter. Sufficient disk space for data files (append-only nature means space usage grows over time until compaction is implemented). Operating system with standard file system support (Linux, macOS, Windows).
*   **Memory:** Sufficient RAM to hold the entire set of keys (the KeyDir) in memory. This is a critical constraint noted in the README.
*   **Performance:** Write performance is generally high due to append-only writes. Read performance is high (O(1) average) if the key exists. Performance depends heavily on disk I/O speed and available memory.
*   **Scaling:** Limited to vertical scaling (more RAM, faster disk) by default. Horizontal scaling requires manual sharding (strategies suggested in README). Concurrency is limited (single writer).
*   **Monitoring:** No built-in monitoring. Users should monitor disk space usage and application memory footprint.

## 6. Architecture and Design

### System Architecture
*   **High-Level Design:** Follows the classic Bitcask architecture:
    1.  **Write Path:** Data is appended to the currently active data file (segment). The in-memory index (KeyDir) is then updated with the new key's location.
    2.  **Read Path:** The key is looked up in the KeyDir. If found, the location points to a specific offset in a (possibly inactive) data file, from which the value is read directly.
    3.  **Deletion:** A tombstone record is appended, and the key is removed from the KeyDir.
    4.  **Startup:** The KeyDir is rebuilt by scanning all data files in the data directory sequentially.
*   **Component Interaction:** The `Bitcask` class acts as a facade, coordinating interactions between the `KeyDir` (in-memory state) and `DataFile` components (disk persistence).
*   **Data Flow:** Client -> `Bitcask` API (`put`/`get`/`delete`) -> `KeyDir` (for lookups/updates) and/or `DataFile` (for reads/writes).
*   **Error Handling:** Expected to handle file I/O errors (disk full, permissions). Data integrity likely relies on CRC checks within log entries [Assumed]. Application-level errors (e.g., key not found) are handled via return values or exceptions.

### Design Patterns
*   **Append-Only Log:** Core pattern for achieving high write throughput and durability.
*   **In-Memory Index / Hash Map:** Used for fast key lookups (Key-Value Store pattern).
*   **Facade:** The `Bitcask` class provides a simplified interface over the underlying storage mechanism (KeyDir, DataFiles).
*   **Segmented Log:** Data is stored in multiple files (segments), with only the latest being active for writes.
*   **Tombstone:** Used for marking deletions without rewriting files immediately.
*   **Thread Safety:** Likely uses locking (e.g., `threading.Lock` or `RWLock`) to manage concurrent access, especially around writes and KeyDir updates [Inferred from "Thread-safe" claim].

### Scalability and Performance
*   **Scaling Strategies:**
    *   Vertical: Increase RAM (for larger KeyDir), use faster storage (SSD). Limited by single-machine resources.
    *   Horizontal: Not natively supported. Requires application-level sharding (partitioning keys across multiple `pybitcask` instances), as suggested in the README.
*   **Limitations:**
    *   Memory: KeyDir must fit in RAM.
    *   Disk Space: Grows continuously without compaction.
    *   Concurrency: Single writer thread limits write throughput scaling. Multiple readers are supported.
    *   Querying: Only key lookups are efficient; scans (`keys()`) can be slow, and range/secondary index queries are not supported.
*   **Performance Optimization:**
    *   Append-only writes minimize disk head seeks.
    *   In-memory index ensures fast reads.
    *   Future improvements (compaction, batch operations, async I/O) listed in README would further enhance performance.
*   **Monitoring:** Focus on RAM usage (KeyDir size) and disk usage (data file growth).

## 7. Development Guidelines

### Code Style and Standards
*   **Conventions:** Adheres to PEP 8 (enforced by `black` and `ruff`). Naming conventions (`N`) and docstrings (`D`) checked by `ruff`. Imports sorted by `isort`.
*   **Documentation:** Docstrings are expected. `README.md` provides user-facing documentation.
*   **Testing:** `pytest` is used for testing. `pytest-cov` suggests test coverage is tracked. Tests should cover core functionality, edge cases, and persistence.
*   **Review Process:** Pre-commit hooks enforce style and quality before code is committed. Pull requests on GitHub (implied standard workflow) would likely be used for code reviews.

### Development Workflow
*   **Branching:** Assumed standard practice (e.g., Gitflow, GitHub Flow - feature branches off `main`/`master`).
*   **CI/CD:** No explicit CI/CD pipeline configured in provided files, but `pre-commit` provides local CI checks. GitHub Actions could be easily added for automated testing/linting on pushes/PRs.
*   **Release Management:** No process defined. Typically involves tagging releases on Git and potentially publishing to PyPI (though not configured in `pyproject.toml`).
*   **Quality Assurance:** Relies on automated tests (`pytest`) and static analysis/linting (`ruff`, `black`, `isort`) enforced via `pre-commit`.

### Best Practices
*   **Security:**
    *   Ensure appropriate file permissions on the data directory.
    *   Use JSON serialization as default (safer than `pickle`). Be cautious if allowing custom serializers.
*   **Performance:**
    *   Be mindful of the memory footprint (KeyDir size).
    *   Implement compaction (currently a future improvement) for long-running deployments to reclaim disk space and potentially improve read performance by removing stale data.
    *   Consider batching writes if the application pattern allows (future improvement).
*   **Error Handling:**
    *   Handle potential `IOError` during file operations.
    *   Check return values or handle exceptions for operations like `get` (key not found).
    *   Ensure proper resource cleanup (e.g., closing file handles, perhaps via context managers `__enter__`/`__exit__` on the `Bitcask` class).
*   **Logging:** Consider adding standard Python `logging` for operational insights, especially for file operations, startup (KeyDir loading), and potential errors.