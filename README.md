
# mlcheck.py

**Version:** 0.2  
**Author:** Igor Brzeżek  
**Email:** igor.brzezek@gmail.com
**License:** MIT  
**GitHub:** [github.com/igorbrzezek](https://github.com/igorbrzezek)

## Overview

`mlcheck.py` is a command-line tool for validating **HTML** and **XML** files, with special support for **Moodle multichoice XML format**. It checks for structural correctness, tag mismatches, and missing required elements. It can operate on single files or scan entire directories (recursively if needed).

## Features

- Detects file format (HTML or XML) automatically or via override.
- Validates HTML structure including void elements and raw context tags.
- Validates Moodle multichoice XML files for required tags.
- Batch scanning of directories with optional recursion.
- Colored output (requires `colorama`).
- Detailed statistics (tag count, error count).
- Custom help system with examples.

## Requirements

- Python 3.6+
- Optional: `colorama` for colored output (`pip install colorama`)

## Usage

```bash
python mlcheck.py -i <file_or_directory> [options]
```

### Examples

1. **Validate a single HTML file:**
   ```bash
   python mlcheck.py -i file.html
   ```

2. **Validate a Moodle XML file with statistics:**
   ```bash
   python mlcheck.py -i file.xml --stat --format moodlemc
   ```

3. **Scan all HTML files in the current directory:**
   ```bash
   python mlcheck.py -i . --all h --stat
   ```

4. **Recursively scan all XML files in a directory:**
   ```bash
   python mlcheck.py -i ./projects --all x -r --stat
   ```

## Options

| Option           | Description |
|------------------|-------------|
| `-i`, `--input`  | Path to input file or directory (required unless using help). |
| `--all [x|h]`    | Scan all XML (`x`) or HTML (`h`) files in a directory. |
| `-r`, `--recursive` | Recursively scan subdirectories (requires `--all`). |
| `--stat`         | Show detailed statistics. |
| `--color`        | Enable colored output (requires `colorama`). |
| `--format moodlemc` | Use Moodle multichoice schema for XML validation. |
| `--informat [XML|HTML]` | Force validation as specific format. |
| `-h`             | Show short help message. |
| `--help`         | Show full help message with examples. |
| `-v`, `--version`| Show version information. |

## Output

- Lists errors with line and column numbers.
- Indicates unmatched or superfluous tags.
- Displays summary statistics when `--stat` is used.

## License

This project is licensed under the MIT License.
