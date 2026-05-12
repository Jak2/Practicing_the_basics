#!/usr/bin/env python3
"""
sql_tree.py
===========
Scans the dev folder source tree and outputs all SQL queries
grouped by:
  - API route (HTTP method + path) for route/endpoint files
  - Class → method for service/helper files

Usage
-----
    # From repo root — scan the entire folder, print to terminal:
    python sql_tree.py

    # Scan a specific sub-directory:
    python sql_tree.py project/app/api/v2/security -o out.txt

    # Single file → file
    python sql_tree.py project/app/api/v2/jobs/cron_scheduler.py -o out.txt

    
    # Write to a file (UTF-8, box characters render correctly):
    python sql_tree.py -o sql_report.txt

    # Scan specific path and write to file:
    python sql_tree.py project/app/api/v2 -o sql_report.txt

    NOTE: Do NOT use  >  to redirect on Windows — PowerShell's > operator
    reads stdout through the OEM code page (CP437) which corrupts UTF-8
    box-drawing characters into gibberish like ΓöÇ. Use -o instead.


Output format
-------------
    [ROUTES]
    POST   /v2/cosmetics/{instance_id}/execute
      └─ execute_cosmetics()  [routes.py:82]
           ├─ [L 84] SELECT  →  SELECT makeup, touchup FROM dev_project...
           └─ (calls service — see cosmeticService below)

    [SERVICES]
    cosmeticService  [cosmetics/service.py]
      └─ execute_cosmetics()  [L 245]
           ├─ [L 247] SELECT  →  SELECT wi.instance_id, wi.current_makeup...
           ├─ [L 312] UPDATE  →  UPDATE dev_project.dev_instances...
           └─ [L 380] INSERT  →  INSERT INTO dev_project.cosmetic_execution_log...
"""

import io
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Argument parsing ──────────────────────────────────────────────────────────
# Usage:
#   python sql_tree.py                              → scan default root, print to terminal
#   python sql_tree.py <path>                       → scan specific dir/file, print to terminal
#   python sql_tree.py <path> -o report.txt         → scan and write to file (UTF-8, no mangling)
#   python sql_tree.py -o report.txt                → scan default root, write to file

_args   = sys.argv[1:]
_output = None

if "-o" in _args:
    idx     = _args.index("-o")
    _output = _args[idx + 1]
    _args   = [a for i, a in enumerate(_args) if i != idx and i != idx + 1]

ROOT = Path(_args[0] if _args else "dev/project/app")

# When writing to a file write UTF-8 directly — bypasses PowerShell's OEM
# code page mangling that happens with the > redirect operator.
# When printing to a terminal, also force UTF-8 so box-drawing chars show.
if _output:
    _out = open(_output, "w", encoding="utf-8")
else:
    _out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SKIP_DIRS  = {"__pycache__", ".git", "guide", "generated", "migrations"}
SKIP_FILES = {"__init__.py"}  # usually empty — remove if you want them

# ── Regex patterns ────────────────────────────────────────────────────────────

# Route decorators:  @router.get("/path")  or  @app.post("/path")
RE_ROUTE = re.compile(
    r'@(?:router|app)\s*\.\s*(get|post|put|delete|patch|head|options)\s*\('
    r'\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)

# Function / method definition  (captures indentation + name)
RE_FUNC = re.compile(r'^( {0,99})(?:async\s+)?def\s+(\w+)\s*\(')

# Class definition
RE_CLASS = re.compile(r'^class\s+(\w+)')

# SQL type keyword at the start of a meaningful SQL statement
RE_SQL_TYPE = re.compile(
    r'^\s*(SELECT|INSERT\s+INTO|INSERT|UPDATE|DELETE\s+FROM|DELETE'
    r'|WITH|MERGE|CALL|EXECUTE|CREATE\s+TEMP|TRUNCATE)',
    re.IGNORECASE,
)

# A string qualifies as SQL only if it STARTS with a SQL DML/DDL keyword
# (after optional whitespace/newlines). This rejects docstrings that merely
# mention SQL words in prose.
RE_SQL_LEADING = re.compile(
    r'^\s*(SELECT|INSERT\s+INTO|INSERT|UPDATE\s+\w|DELETE\s+FROM|DELETE\b'
    r'|WITH\s+\w|MERGE\s+INTO|TRUNCATE\s+TABLE|CREATE\s+TEMP'
    r'|ALTER\s+TABLE|CALL\s+\w)',
    re.IGNORECASE,
)

# Triple-quote opening (with optional f / r prefix)
RE_TRIPLE_OPEN = re.compile(r'[frFR]{0,2}("""|\'\'\')(.*)')


# ── Data structures ───────────────────────────────────────────────────────────

class SqlQuery:
    __slots__ = ("line_no", "sql_type", "sql_lines")

    def __init__(self, line_no: int, text: str):
        self.line_no = line_no
        m = RE_SQL_TYPE.match(text.strip())
        self.sql_type = m.group(1).upper().replace("\n", " ") if m else "SQL"
        # Preserve original line structure: strip each line, drop blanks
        self.sql_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    def header(self) -> str:
        return f"[L{self.line_no:>4}] {self.sql_type}"


class FuncInfo:
    __slots__ = ("name", "line_no", "indent", "queries", "routes")

    def __init__(self, name: str, line_no: int, indent: int):
        self.name    = name
        self.line_no = line_no
        self.indent  = indent
        self.queries: list[SqlQuery] = []
        self.routes:  list[tuple]    = []   # (http_method, path)


class FileInfo:
    def __init__(self, path: Path):
        self.path      = path
        self.rel       = str(path.relative_to(ROOT))
        self.classes:  dict[str, list[FuncInfo]] = defaultdict(list)  # class → funcs
        self.functions: list[FuncInfo]            = []                 # module-level


# ── Parser ────────────────────────────────────────────────────────────────────

def _collect_triple_quote_string(lines: list[str], start_line: int,
                                  delim: str, tail: str) -> tuple[str, int]:
    """
    Starting from `start_line` with `tail` = content after the opening triple
    quote, collect lines until the closing delimiter.
    Returns (full_string, end_line_index).
    """
    parts = [tail]
    i = start_line + 1
    while i < len(lines):
        line = lines[i]
        close = line.find(delim)
        if close != -1:
            parts.append(line[:close])
            return "\n".join(parts), i
        parts.append(line)
        i += 1
    return "\n".join(parts), i  # unterminated — return what we have


def parse_file(path: Path) -> FileInfo:
    info      = FileInfo(path)
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return info

    lines      = src.splitlines()
    n          = len(lines)

    # State
    current_class: str | None          = None
    func_stack:    list[FuncInfo]      = []   # stack by indentation
    pending_routes: list[tuple]        = []   # decorators seen before a def

    i = 0
    while i < n:
        raw  = lines[i]
        line = raw.rstrip()

        # ── Class definition ──────────────────────────────────────────────
        cm = RE_CLASS.match(line)
        if cm:
            current_class = cm.group(1)
            func_stack.clear()
            i += 1
            continue

        # ── Route decorator ───────────────────────────────────────────────
        rm = RE_ROUTE.search(line)
        if rm:
            pending_routes.append((rm.group(1).upper(), rm.group(2)))
            i += 1
            continue

        # ── Function definition ───────────────────────────────────────────
        fm = RE_FUNC.match(line)
        if fm:
            indent   = len(fm.group(1))
            funcname = fm.group(2)

            # pop functions that are at the same or deeper indent (we left them)
            func_stack = [f for f in func_stack if f.indent < indent]

            fi = FuncInfo(funcname, i + 1, indent)
            if pending_routes:
                fi.routes = list(pending_routes)
                pending_routes.clear()
            else:
                pending_routes.clear()

            func_stack.append(fi)
            if current_class:
                info.classes[current_class].append(fi)
            else:
                info.functions.append(fi)

            i += 1
            continue

        # ── Clear pending routes if we hit something that is not a def ────
        stripped = line.strip()
        if stripped and not stripped.startswith("#") \
                    and not stripped.startswith("@") \
                    and not stripped.startswith(")") \
                    and not stripped.startswith("async"):
            # if pending_routes has content but we hit a non-def line,
            # the decorator was on a class, not a function — clear it
            # (be conservative: only clear on non-blank, non-decorator lines
            #  that look like statements)
            if pending_routes and not RE_FUNC.match(line) and not RE_CLASS.match(line):
                pass   # keep — multi-line decorator possible on next line

        # ── SQL string detection ──────────────────────────────────────────
        # Only consider triple-quoted strings that are:
        #   a) inside a text(""" ... """) call, OR
        #   b) assigned to a variable named query/sql/stmt/statement
        # This excludes docstrings (which follow def/class with no text( or =).
        tq = RE_TRIPLE_OPEN.search(line)
        if tq:
            before_quote = line[:line.index(tq.group(0))]
            is_sql_context = (
                re.search(r'\btext\s*\(\s*[frFR]{0,2}$', before_quote)
                or re.search(r'\b(?:query|sql|stmt|statement|q)\s*(?:\+?=)\s*[frFR]{0,2}$', before_quote)
                or re.search(r'\btext\s*\(', before_quote)   # text( anywhere before
                or re.search(r'=\s*[frFR]{0,2}$', before_quote)  # any assignment
            )
            if not is_sql_context:
                i += 1
                continue

            delim     = tq.group(1)
            tail      = tq.group(2)
            sql_text, end_i = _collect_triple_quote_string(lines, i, delim, tail)

            if RE_SQL_LEADING.search(sql_text):
                sq = SqlQuery(i + 1, sql_text)
                # Attach to innermost function on the stack
                if func_stack:
                    func_stack[-1].queries.append(sq)
                # module-level SQL outside any function is rare; skip it
                # (it's usually a constant or migration string, not a query path)
            i = end_i + 1
            continue

        i += 1

    return info


# ── Tree renderer ─────────────────────────────────────────────────────────────

BOX_BRANCH = "├─"
BOX_LAST   = "└─"
BOX_PIPE   = "│ "
BOX_SPACE  = "  "


def _render_queries(queries: list[SqlQuery], prefix: str) -> list[str]:
    out = []
    for idx, q in enumerate(queries):
        is_last   = idx == len(queries) - 1
        conn      = BOX_LAST if is_last else BOX_BRANCH
        cont_pipe = BOX_SPACE if is_last else BOX_PIPE   # vertical line under connector

        # Header line:  ├─ [L  51] SELECT
        out.append(f"{prefix}{conn} {q.header()}")

        # SQL body lines, each prefixed with │ or space to stay in the tree
        sql_indent = f"{prefix}{cont_pipe}    "
        for sql_line in q.sql_lines:
            out.append(f"{sql_indent}{sql_line}")

        # Blank separator between queries for readability
        out.append(f"{prefix}{cont_pipe}")

    return out


def render_file(info: FileInfo) -> list[str]:
    out   = []
    label = f"📄 {info.rel}"
    out.append(label)
    out.append("─" * min(len(label) + 2, 100))

    # ── Routes / module-level functions ──────────────────────────────────
    all_funcs = list(info.functions)
    for class_name, funcs in info.classes.items():
        all_funcs.extend(funcs)

    # Separate into routed vs non-routed
    routed     = [f for f in all_funcs if f.routes]
    non_routed = [f for f in all_funcs if not f.routes and f.queries]

    if routed:
        out.append("")
        out.append("  [ROUTES]")
        for f in routed:
            for method, path in f.routes:
                out.append(f"  {method:<7} {path}")
            out.append(f"    └─ {f.name}()  [line {f.line_no}]")
            if f.queries:
                out.extend(_render_queries(f.queries, "         "))
            else:
                out.append("         (no direct SQL — delegates to service)")

    if non_routed:
        out.append("")
        out.append("  [SERVICE / HELPERS]")
        # Group by class
        grouped: dict[str | None, list[FuncInfo]] = defaultdict(list)
        for class_name, funcs in info.classes.items():
            for f in funcs:
                if f.queries:
                    grouped[class_name].append(f)
        for f in info.functions:
            if f.queries:
                grouped[None].append(f)

        for class_name, funcs in grouped.items():
            if class_name:
                out.append(f"  class {class_name}")
            for idx, f in enumerate(funcs):
                conn = BOX_LAST if idx == len(funcs) - 1 else BOX_BRANCH
                label_f = f"{conn} {f.name}()  [line {f.line_no}]"
                prefix = "     " if class_name else "  "
                out.append(f"  {prefix}{label_f}")
                q_prefix = "     " + ("   " if class_name else "  ")
                out.extend(_render_queries(f.queries, f"  {q_prefix}"))

    return out


# ── Stats ─────────────────────────────────────────────────────────────────────

def _count(info: FileInfo) -> tuple[int, int, int]:
    """Returns (routes, functions_with_sql, total_queries)."""
    routes = sum(len(f.routes) for f in info.functions)
    for funcs in info.classes.values():
        routes += sum(len(f.routes) for f in funcs)

    all_funcs = list(info.functions)
    for funcs in info.classes.values():
        all_funcs.extend(funcs)

    funcs_with_sql = sum(1 for f in all_funcs if f.queries)
    total_q        = sum(len(f.queries) for f in all_funcs)
    return routes, funcs_with_sql, total_q


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    files: list[FileInfo] = []

    if ROOT.is_file():
        # Single file passed directly
        files.append(parse_file(ROOT))
    else:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in sorted(filenames):
                if fname in SKIP_FILES:
                    continue
                if not fname.endswith(".py"):
                    continue
                full = Path(dirpath) / fname
                info = parse_file(full)
                files.append(info)

    # Only print files that have something
    total_routes = total_funcs = total_queries = 0

    for info in files:
        r, f, q = _count(info)
        total_routes  += r
        total_funcs   += f
        total_queries += q

        if f == 0 and r == 0:
            continue  # nothing to show

        lines = render_file(info)
        _out.write("\n".join(lines) + "\n\n")

    # Summary
    _out.write("=" * 70 + "\n")
    _out.write(f"  Files scanned  : {len(files)}\n")
    _out.write(f"  Routes found   : {total_routes}\n")
    _out.write(f"  Functions w/SQL: {total_funcs}\n")
    _out.write(f"  SQL queries    : {total_queries}\n")
    _out.write("=" * 70 + "\n")

    if _output:
        _out.close()
        sys.stdout.write(f"Written to {_output}  ({total_queries} queries across {len(files)} files)\n")


if __name__ == "__main__":
    main()
