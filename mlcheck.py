#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Metadata
AUTHOR = "Igor Brzezek"
VERSION = "0.2"
DATE = "2025-10-24"
GITHUB = "github/igorbrzezek"
LICENSE = "MIT"

import argparse
import sys
import os
import datetime
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

# --- Dummy color objects (for optional colorama) ---
class DummyColor:
    def __getattr__(self, name):
        return ""

Fore = DummyColor()
Style = DummyColor()
# -------------------------------------

# Definition of HTML void elements
HTML_VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}

# Helper function to detect file format
def detect_format(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(200).lower()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin1') as f:
            content = f.read(200).lower()

    if '<html' in content:
        return 'HTML'
    elif '<quiz' in content or '<question' in content:
        return 'XML'
    else:
        return 'Unknown'

# HTML parser class
class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags_stack = []
        self.errors = []
        self.tags_count = 0 
        self.void_elements = HTML_VOID_ELEMENTS 
        self.raw_context_tags = {'pre', 'code', 'script', 'style'}
        self.is_in_raw_context = False

    def handle_starttag(self, tag, attrs):
        self.tags_count += 1
        
        if self.is_in_raw_context:
            return  

        if tag in self.raw_context_tags:
            self.is_in_raw_context = True
            
        if tag not in self.void_elements:
            self.tags_stack.append(tag)

    def handle_endtag(self, tag):
        if self.is_in_raw_context and tag not in self.raw_context_tags:
            return

        if tag in self.raw_context_tags:
            self.is_in_raw_context = False
        
        if tag in self.void_elements:
            self.errors.append((self.getpos(), f"Superfluous closing tag for void element: </{tag}>"))
            return
        
        if not self.tags_stack:
            self.errors.append((self.getpos(), f"Unmatched closing tag: {tag} (stack is empty)"))
        elif self.tags_stack[-1] == tag:
            self.tags_stack.pop()
        else:
            expected_tag = self.tags_stack[-1]
            self.errors.append((self.getpos(), f"Mismatched closing tag: expected </{expected_tag}> but got </{tag}>"))

    def error(self, message):
        self.errors.append((self.getpos(), message))


# Moodle multichoice validator
def validate_moodle_mc(root):
    errors = []
    questions = root.findall(".//question[@type='multichoice']")
    for q in questions:
        if q.find('name') is None:
            errors.append((q.sourceline, "Missing <name> tag in multichoice question"))
        if q.find('questiontext') is None:
            errors.append((q.sourceline, "Missing <questiontext> tag in multichoice question"))
        answers = q.findall('answer')
        if not answers:
            errors.append((q.sourceline, "No <answer> tags found in multichoice question"))
    return errors

# Main validation function
def validate_file(file_path, file_format, schema_option, color, stat, is_batch_mode=False):
    errors = []
    stats = {'tags': 0, 'errors': 0}
    file_encoding = 'unknown'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        file_encoding = 'utf-8'
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin1') as f:
            content = f.read()
        file_encoding = 'latin1'
    except Exception as e:
        print(f"Critical error reading {file_path}: {e}")
        return {'tags': 0, 'errors': 1} 

    if file_format == 'HTML':
        parser = MyHTMLParser()
        parser.feed(content)
        errors = parser.errors
        if parser.tags_stack:
            for unclosed_tag in reversed(parser.tags_stack):
                errors.append(((0, 0), f"Unclosed tag: {unclosed_tag}"))
        stats['tags'] = parser.tags_count
        stats['errors'] = len(errors)

    elif file_format == 'XML':
        try:
            root = ET.fromstring(content) 
            stats['tags'] = len(list(root.iter()))
            if schema_option == 'moodlemc':
                errors = validate_moodle_mc(root)
            stats['errors'] = len(errors)
        except ET.ParseError as e:
            position = e.position
            errors.append((position, str(e)))
            stats['errors'] = 1
    
    # --- Output (Modified) ---
    if errors:
        if is_batch_mode:
            print(f"\n--- Errors Found in: {Fore.YELLOW}{file_path}{Style.RESET_ALL} ---")
        else:
            print("--- Errors Found ---")
            
        for err in errors:
            pos, msg = err
            line, col = pos if isinstance(pos, tuple) else (pos, 0)
            output = f"Error at line {line}, column {col}: {msg}"
            print(Fore.RED + output if color else output)
    else:
        if not is_batch_mode:
            print(Fore.GREEN + "No errors found. File is valid." if color else "No errors found. File is valid.")

    if stat:
        if not is_batch_mode:
            print(f"\n--- Statistics (Format: {Fore.CYAN}{file_format}{Style.RESET_ALL}, Encoding: {Fore.CYAN}{file_encoding}{Style.RESET_ALL}) ---")
            print(f"Total tags (approx.): {stats['tags']}, Total errors: {stats['errors']}")

    return stats

# --- NEW MAIN FUNCTION ---
def main():
    
    # --- START OF MODIFIED ARGPARSE BLOCK ---
    parser = argparse.ArgumentParser(
        add_help=False, # ZMIANA: Wyłącz domyślną pomoc
        description=f"""
mlcheck.py (v{VERSION}) - HTML and XML Validator.
Author: {AUTHOR}
GitHub: {GITHUB}
License: {LICENSE}
""",
        epilog="""EXAMPLES:

        1. Validate a single file:
           %(prog)s -i file.html

        2. Validate a Moodle XML file with stats:
           %(prog)s -i file.xml --stat --format moodlemc

        3. Scan all HTML files in the current directory:
           %(prog)s -i . --all h --stat

        4. Recursively scan all XML files in the 'projects' directory:
           %(prog)s -i ./projects --all x -r --stat
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Group 1: Main Input Options
    input_group = parser.add_argument_group('Main Input Options')
    input_group.add_argument(
        '-i', '--input',
        # ZMIANA: -i nie jest już 'required', ponieważ -h/--help musi działać bez -i
        required=False, 
        help='Path to the input file (default mode) or directory (in --all mode).'
    )

    # Group 2: Batch Scanning Options
    batch_group = parser.add_argument_group('Batch Scanning Options')
    batch_group.add_argument(
        '--all',
        choices=['x', 'h'],
        help='Scan all files. Requires type: "x" (XML) or "h" (HTML). Treats -i as a directory.'
    )
    batch_group.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Scan recursively (searches subdirectories). Only works with --all.'
    )

    # Group 3: Validation and Output Options
    output_group = parser.add_argument_group('Validation and Output Options')
    
    # ZMIANA: Ręczna definicja -h i --help
    output_group.add_argument(
        '-h',
        action='store_true',
        help='Show this short help message (without examples) and exit.'
    )
    output_group.add_argument(
        '--help',
        action='store_true',
        help='Show the full help message (with examples) and exit.'
    )
    # -------------------------------------

    output_group.add_argument(
        '--stat',
        action='store_true',
        help='Show detailed statistics (tag count, error count). In --all mode, shows a summary for each directory and a global summary.'
    )
    output_group.add_argument(
        '--color',
        action='store_true',
        help='Enable colored error output (requires colorama).'
    )
    output_group.add_argument(
        '--format',
        choices=['moodlemc'],
        help='Use a specific validation schema (e.g., "moodlemc" for Moodle XML).'
    )
    output_group.add_argument(
        '--informat',
        choices=['XML', 'HTML'],
        help='Force validation as a specific type (overrides auto-detection).'
    )
    output_group.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {VERSION}'
    )

    args = parser.parse_args()
    
    # --- ZMIANA: Ręczna obsługa pomocy ---
    if args.h:
        # Drukuj pomoc BEZ epilogu (przykładów)
        formatter = parser._get_formatter()
        formatter.add_text(parser.description)
        formatter.add_usage(parser.usage, parser._actions, parser._mutually_exclusive_groups)
        for action_group in parser._action_groups:
             formatter.start_section(action_group.title)
             formatter.add_text(action_group.description)
             formatter.add_arguments(action_group._group_actions)
             formatter.end_section()
        print(formatter.format_help())
        sys.exit()

    if args.help:
        # Drukuj pełną pomoc (z epilogiem)
        parser.print_help() 
        sys.exit()
    # --- KONIEC ZMIANY ---

    # --- Conditional Color Init ---
    global Fore, Style 
    
    if args.color:
        try:
            from colorama import init, Fore as ColoramaFore, Style as ColoramaStyle
            init(autoreset=True)
            Fore = ColoramaFore
            Style = ColoramaStyle
        except ImportError:
            print("Warning: --color option specified, but 'colorama' library not found.")
            print("Please install it: pip install colorama")
            args.color = False 
    # --- END ---
    
    
    # --- Path and argument validation ---
    
    # ZMIANA: Sprawdź, czy -i istnieje, dopiero jeśli -h/--help nie zostały podane
    if not args.input:
        print("Error: Input path not specified. Use -i <path>.")
        parser.print_usage() # Pokaż krótkie użycie
        sys.exit(1)
        
    if not os.path.exists(args.input):
        print(f"Error: Input path does not exist: {args.input}")
        sys.exit(1)
        
    if args.recursive and not args.all:
        print("Error: -r (recursive) option requires --all [x|h] to be specified.")
        sys.exit(1)

    # --- Logic: Batch Scan vs. Single File ---

    if args.all:
        # --- BATCH SCAN MODE ---
        if not os.path.isdir(args.input):
            print(f"Error: --all mode requires --input to be a directory.")
            sys.exit(1)
        
        if args.all == 'h':
            extensions = ('.html', '.htm')
            scan_format = 'HTML'
        else: # args.all == 'x'
            extensions = ('.xml',)
            scan_format = 'XML'
        
        print(f"Starting scan for {scan_format} files in '{args.input}' (Recursive: {args.recursive})...\n")
        
        global_summary = {'files_scanned': 0, 'files_with_errors': 0, 'total_errors': 0, 'total_tags': 0}
        
        if args.recursive:
            # -- Recursive Scan --
            for dirpath, dirnames, filenames in os.walk(args.input, topdown=True):
                dir_summary = {'files_scanned': 0, 'files_with_errors': 0, 'total_errors': 0}
                files_in_this_dir = []
                
                for f in filenames:
                    if f.lower().endswith(extensions):
                        files_in_this_dir.append(os.path.join(dirpath, f))
                
                if not files_in_this_dir:
                    continue

                if args.stat: 
                    print(f"--- Scanning Directory: {Fore.CYAN}{dirpath}{Style.RESET_ALL}" if args.color else f"--- Scanning Directory: {dirpath} ---")
                
                for file_path in files_in_this_dir:
                    file_format = args.informat if args.informat else scan_format
                    try:
                        stats = validate_file(file_path, file_format, args.format, args.color, args.stat, is_batch_mode=True)
                        
                        dir_summary['files_scanned'] += 1
                        dir_summary['total_errors'] += stats['errors']
                        if stats['errors'] > 0:
                            dir_summary['files_with_errors'] += 1
                        
                        global_summary['files_scanned'] += 1
                        global_summary['total_tags'] += stats['tags']
                        global_summary['total_errors'] += stats['errors']
                        if stats['errors'] > 0:
                            global_summary['files_with_errors'] += 1
                            
                    except Exception as e:
                        print(f"CRITICAL ERROR scanning {file_path}: {e}")
                
                if args.stat and dir_summary['files_scanned'] > 0:
                    print(f"--- Directory Summary ({dirpath}):")
                    print(f"  Files Scanned: {dir_summary['files_scanned']}")
                    print(f"  Files with Errors: {Fore.RED if dir_summary['files_with_errors'] > 0 else Fore.GREEN}{dir_summary['files_with_errors']}{Style.RESET_ALL}" if args.color else f"  Files with Errors: {dir_summary['files_with_errors']}")
                    print(f"  Total Errors Found: {dir_summary['total_errors']}\n")

        else:
            # -- Non-Recursive (Flat) Scan --
            files_to_scan = []
            for f in os.listdir(args.input):
                full_path = os.path.join(args.input, f)
                if os.path.isfile(full_path) and f.lower().endswith(extensions):
                    files_to_scan.append(full_path)
            
            if not files_to_scan:
                print("No matching files found in this directory.")
            
            for file_path in files_to_scan:
                file_format = args.informat if args.informat else scan_format
                try:
                    stats = validate_file(file_path, file_format, args.format, args.color, args.stat, is_batch_mode=True)
                    global_summary['files_scanned'] += 1
                    global_summary['total_tags'] += stats['tags']
                    global_summary['total_errors'] += stats['errors']
                    if stats['errors'] > 0:
                        global_summary['files_with_errors'] += 1
                except Exception as e:
                    print(f"CRITICAL ERROR scanning {file_path}: {e}")

        # --- Print global summary (if --stat) ---
        if args.stat and global_summary['files_scanned'] > 0:
            print(f"\n=================================================")
            print(f"--- {Fore.GREEN}GLOBAL SCAN SUMMARY{Style.RESET_ALL} ---" if args.color else "--- GLOBAL SCAN SUMMARY ---")
            print(f"Total Files Scanned:       {global_summary['files_scanned']}")
            print(f"Total Tags Found:          {global_summary['total_tags']}")
            print(f"Total Files with Errors:   {Fore.RED if global_summary['files_with_errors'] > 0 else Fore.GREEN}{global_summary['files_with_errors']}{Style.RESET_ALL}" if args.color else f"Total Files with Errors:   {global_summary['files_with_errors']}")
            print(f"Total Errors Found:        {global_summary['total_errors']}")
            print(f"=================================================")
        elif global_summary['files_scanned'] == 0:
             print("No matching files found to scan.")

    else:
        # --- SINGLE FILE MODE (Old behavior) ---
        if os.path.isdir(args.input):
            print(f"Error: Input path is a directory. To scan a directory, use --all [x|h].")
            sys.exit(1)
        
        file_format = args.informat if args.informat else detect_format(args.input)
        if file_format == 'Unknown':
            print(f"Warning: Could not determine file type for {args.input}. Forcing XML.")
            file_format = 'XML'
            
        validate_file(args.input, file_format, args.format, args.color, args.stat, is_batch_mode=False)


# Run the main function
if __name__ == "__main__":
    main()