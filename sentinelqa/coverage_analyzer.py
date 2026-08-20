from __future__ import annotations
import ast
from pathlib import Path
from .models import CoverageReport, FunctionCoverage

class _FunctionCollector(ast.NodeVisitor):
    def __init__(self): self.functions=[]
    def visit_FunctionDef(self,node): self.functions.append(node.name); self.generic_visit(node)
    def visit_AsyncFunctionDef(self,node): self.functions.append(node.name); self.generic_visit(node)

class _CallCollector(ast.NodeVisitor):
    def __init__(self): self.calls=set()
    def visit_Call(self,node):
        if isinstance(node.func,ast.Name): self.calls.add(node.func.id)
        elif isinstance(node.func,ast.Attribute): self.calls.add(node.func.attr)
        self.generic_visit(node)

class CoverageAnalyzer:
    def analyze(self,src_dir:str|Path,tests_dir:str|Path)->CoverageReport:
        funcs=[]
        for path in Path(src_dir).rglob("*.py"):
            tree=ast.parse(path.read_text()); c=_FunctionCollector(); c.visit(tree); funcs.extend(c.functions)
        calls={}
        for path in Path(tests_dir).rglob("*.py"):
            tree=ast.parse(path.read_text()); c=_CallCollector(); c.visit(tree)
            for call in c.calls: calls.setdefault(call,[]).append(path.name)
        rows=[]
        for fn in sorted(set(funcs)):
            matches=sorted(set(calls.get(fn,[])))
            rows.append(FunctionCoverage(function=fn,covered=bool(matches),matching_tests=matches))
        total=len(rows); covered=sum(int(x.covered) for x in rows); pct=100*covered/total if total else 100
        return CoverageReport(total_functions=total,covered_functions=covered,coverage_percent=round(pct,2),functions=rows)
