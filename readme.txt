=====================================================================
                    mlcheck.py (v0.5) - HTML/XML Validator
=====================================================================

Author : Igor Brzezek
GitHub : github.com/igorbrzezek
Email  : igor.brzezek@gmail.com
License: MIT

---------------------------------------------------------------------
1. PURPOSE
---------------------------------------------------------------------

Script `mlcheck.py` (MarkupLanguageChecker) is a command-line tool for validating the syntax of HTML and XML files. 

It is designed to quickly find common syntax errors, such as:
- Mismatched or unclosed tags.
- Incorrect tag nesting order (e.g., <b><i></b></i>).
- Malformed XML structure.

It can be used to check a single file or to scan entire directories of project files at once.

---------------------------------------------------------------------
2. FEATURES
---------------------------------------------------------------------

- **Dual-Mode Validation:** Supports both HTML and XML validation with auto-detection.
- **Smart HTML Parsing:** Correctly handles "void" elements (like <br>, <img>, <meta>) that don't need a closing tag.
- **Context-Aware:** Understands raw text contexts (like <pre>, <code>, <script>, <style>) and will not parse their contents as HTML, preventing false positives from code snippets.
- **Encoding Detection:** Automatically handles files in UTF-8 or Latin-1 (fallback) to prevent UnicodeDecodeErrors.
- **Batch Scanning:** Can scan an entire directory for all HTML (`.html`, `.htm`) or XML (`.xml`) files.
- **Recursive Mode:** Can scan all subdirectories for matching files.
- **Detailed Statistics:** Provides summaries of tags found, errors found, files scanned, and files with errors.
- **Specific Schemas:** Supports special validation for known formats (e.g., Moodle XML).
- **Optional Coloring:** Uses 'colorama' (if installed) to highlight errors, but runs perfectly without it.

---------------------------------------------------------------------
3. REQUIREMENTS
---------------------------------------------------------------------

- **Python 3.x**
- **colorama** (Optional): Required *only* if you want to use the `--color` option. The script will run without it and simply disable coloring. You can install it via pip:
  `pip install colorama`

---------------------------------------------------------------------
4. USAGE & COMMAND-LINE OPTIONS
---------------------------------------------------------------------

The script is run from the command line:

    python mlcheck.py -i <path> [options]


---
Main Input Options
---

  -i INPUT, --input INPUT
    Path to the input file (default mode) or directory (in --all mode). This argument is required for any validation.

---
Batch Scanning Options
---

  --all {x|h}
    Enables batch scanning mode. This tells the script to treat the `-i` path as a directory and scan files within it. You must specify the type of file to scan for:
    - `h`: Scan for HTML files (.html, .htm)
    - `x`: Scan for XML files (.xml)

  -r, --recursive
    Enables recursive scanning. This option only works when used with `--all`. The script will search the input directory and all of its subdirectories.

---
Validation and Output Options
---

  --stat
    Show detailed statistics.
    - In single-file mode: Shows total tags, total errors, detected format, and encoding.
    - In batch mode: Hides per-file stats but shows a summary for each directory (in recursive mode) and a final global summary of all files scanned.

  --color
    Enable colored output for errors and summaries. Requires the 'colorama' library to be installed. If not installed, a warning will be shown and color will be disabled.

  --format {moodlemc}
    Use a specific validation schema for an XML file. Currently supports:
    - `moodlemc`: Validates basic structure for Moodle multichoice XML quiz files.

  --informat {XML|HTML}
    Force the validator to treat the input file as a specific format, overriding the automatic detection.

  -v, --version
    Show the script's version number and exit.

  -h
    Show the short help message. This displays the metadata and all available options *without* the usage examples.

  --help
    Show the full help message. This displays the metadata, all options, AND the usage examples at the bottom.


---------------------------------------------------------------------
5. EXAMPLES
---------------------------------------------------------------------

1. Validate a single HTML file:
   ---------------------------------
   python mlcheck.py -i my_page.html

2. Validate a single file with detailed statistics:
   ---------------------------------
   python mlcheck.py -i my_page.html --stat

3. Validate a Moodle XML file and show stats:
   ---------------------------------
   python mlcheck.py -i quiz.xml --stat --format moodlemc

4. Scan all HTML files in the current directory and show a summary:
   ---------------------------------
   python mlcheck.py -i . --all h --stat

5. Recursively scan all XML files in a 'projects' directory with color:
   ---------------------------------
   python mlcheck.py -i ./projects --all x -r --stat --color
