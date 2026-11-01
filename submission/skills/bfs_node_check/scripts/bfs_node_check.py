#!/usr/bin/env python3
"""Induced call subgraph around a symbol, with code for every node.

Usage: bfs_node_check.py <symbol> [--depth 1] [--side both] [--max-nodes 16] [--max-code-lines 40]

<symbol> may be a bare name (parse_header) or dotted (Class.method, pkg.mod.func);
the last component is matched.

  --depth 1|2      1 = direct callers + callees; 2 = one more ring (callers of
                   callers, callees of callees). Default 1.
  --side both|callers|callees   which direction(s) to expand. Default both.

Prints a JSON induced subgraph to stdout:
  nodes: [{name, file, line, end_line, kind, depth, code}]
  edges: [{from, to, type: "calls"}]

Every node carries its code, so the whole neighborhood can be reviewed in one
call. Pure stdlib; files that fail to parse are skipped.
"""
import ast
import json
import os
import sys

EXCLUDE_DIRS = {
    "tests", "test", "docs", "docs_src", "examples", "benchmarks",
    "build", "dist", ".git", "__pycache__", ".github", ".tox", "venv",
}

_SRC_CACHE = {}


def last_component(sym):
    return sym.replace("/", ".").strip().split(".")[-1]


def iter_py_files(root, limit=500):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                count += 1
                if count > limit:
                    return
                yield os.path.join(dirpath, fn)


def parse(path):
    if path not in _SRC_CACHE:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                _SRC_CACHE[path] = f.read()
        except OSError:
            _SRC_CACHE[path] = None
    src = _SRC_CACHE[path]
    if src is None:
        return None, None
    try:
        return ast.parse(src), src
    except (SyntaxError, ValueError):
        return None, None


def enclosing_funcs(tree):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append((node.name, node.lineno, getattr(node, "end_lineno", node.lineno)))
    return out


def innermost_enclosing(funcs, line):
    best = None
    for name, start, end in funcs:
        if start <= line <= end:
            if best is None or (end - start) <= (best[2] - best[1]):
                best = (name, start, end)
    return best


def snippet(src_lines, start, end, max_lines):
    start = max(1, start)
    end = min(len(src_lines), end)
    if end - start + 1 > max_lines:
        end = start + max_lines - 1
    return "\n".join(src_lines[start - 1:end])


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(json.dumps({"status": "error", "error": "usage: bfs_node_check.py <symbol> [--depth 1|2] [--side both|callers|callees] [--max-nodes N] [--max-code-lines N]"}))
        return
    symbol = args[0]
    depth = 1
    side = "both"
    max_nodes = 16
    max_code_lines = 40
    if "--depth" in args:
        i = args.index("--depth")
        if i + 1 < len(args):
            try:
                depth = min(2, max(1, int(args[i + 1])))
            except ValueError:
                pass
    if "--side" in args:
        i = args.index("--side")
        if i + 1 < len(args) and args[i + 1] in ("both", "callers", "callees"):
            side = args[i + 1]
    if "--max-nodes" in args:
        i = args.index("--max-nodes")
        if i + 1 < len(args):
            try:
                max_nodes = max(1, int(args[i + 1]))
            except ValueError:
                pass
    if "--max-code-lines" in args:
        i = args.index("--max-code-lines")
        if i + 1 < len(args):
            try:
                max_code_lines = max(5, int(args[i + 1]))
            except ValueError:
                pass

    target = last_component(symbol)
    root = "/workspace" if os.path.isdir("/workspace") else os.getcwd()
    files = list(iter_py_files(root))

    # Index the repo once: definitions and call sites per name.
    defs = {}      # name -> [(file, lineno, end_lineno, src_lines)]
    call_sites = {}  # name -> [(file, line, enclosing_name)]
    for path in files:
        tree, src = parse(path)
        if tree is None:
            continue
        rel = os.path.relpath(path, root)
        src_lines = src.splitlines()
        funcs = enclosing_funcs(tree)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defs.setdefault(node.name, []).append(
                    (rel, node.lineno, getattr(node, "end_lineno", node.lineno), src_lines))
            elif isinstance(node, ast.Call):
                fn = node.func
                name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else None)
                if name:
                    enc = innermost_enclosing(funcs, node.lineno)
                    call_sites.setdefault(name, []).append(
                        (rel, node.lineno, enc[0] if enc else None))

    nodes = {}   # (file, line) -> node dict
    edges = []   # {from, to, type}
    edge_seen = set()

    def add_edge(a, b):
        if (a, b) not in edge_seen:
            edge_seen.add((a, b))
            edges.append({"from": a, "to": b, "type": "calls"})

    def add_node(name, file, start, end, kind, src_lines, d):
        key = (file, start)
        if key in nodes or len(nodes) >= max_nodes:
            return False
        nodes[key] = {
            "name": name,
            "file": file,
            "line": start,
            "end_line": end,
            "kind": kind,
            "depth": d,
            "code": snippet(src_lines, start, end, max_code_lines),
        }
        return True

    def expand(name, d):
        """Add one ring around `name`: its callers and/or callees.
        Returns the names of newly added nodes (the next BFS frontier)."""
        added = []
        if side in ("both", "callers"):
            for (f, line, enc) in call_sites.get(name, []):
                if enc is None:
                    add_edge("<module:%s>" % f, name)
                    continue
                # find enc's definition to attach code
                for (ef, es, ee, elines) in defs.get(enc, []):
                    if ef == f:
                        add_edge(enc, name)
                        if add_node(enc, f, es, ee, "caller", elines, d):
                            added.append(enc)
                        break
        if side in ("both", "callees"):
            # callees of name = names called inside name's body
            for (f, es, ee, elines) in defs.get(name, []):
                tree, _src = parse(os.path.join(root, f))
                if tree is None:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name and node.lineno == es:
                        for sub in ast.walk(node):
                            if isinstance(sub, ast.Call):
                                fn = sub.func
                                cname = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else None)
                                if cname:
                                    add_edge(name, cname)
                                    for (cf, cs, ce, clines) in defs.get(cname, []):
                                        if add_node(cname, cf, cs, ce, "callee", clines, d):
                                            added.append(cname)
                        break
        return added

    # depth 0: the target definition
    for (f, es, ee, elines) in defs.get(target, []):
        add_node(target, f, es, ee, "definition", elines, 0)
        break

    frontier = [target]
    for d in range(1, depth + 1):
        if len(nodes) >= max_nodes:
            break
        next_frontier = []
        seen = set()
        for name in frontier:
            for new_name in expand(name, d):
                if new_name not in seen:
                    seen.add(new_name)
                    next_frontier.append(new_name)
        frontier = next_frontier
        if not frontier:
            break

    print(json.dumps({
        "status": "ok",
        "symbol": symbol,
        "matched_name": target,
        "depth": depth,
        "side": side,
        "nodes": list(nodes.values()),
        "edges": edges,
        "node_count": len(nodes),
        "note": "Induced call subgraph with code per node. depth=1: direct callers+callees; "
                "depth=2: one more ring. Cross-check with get_code_neighbors for import-aliased references.",
    }))


if __name__ == "__main__":
    main()