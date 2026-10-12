# Author: Utkarsh Gupta
# License: GPL v3
"""
Whether an equation GeoAI wrote is mathematically the same as the method's, not just spelled the same.

The model may legitimately rewrite the method's equation: substitute an intermediate quantity
(G = rho Vs^2 with rho = gamma/g becomes G = gamma/g Vs^2), reorder factors, or use \\times for \\cdot. A text
comparison flags all of those. Here both sides are parsed from a small LaTeX subset into expression trees (no
eval), the method's own definitions are substituted in, and the two right-hand sides are evaluated at several
random positive values of the remaining symbols. Equal at every point -> the same equation.

Anything outside the subset (sums, integrals, cases, unknown commands) makes the parse fail; callers then fall
back to the text comparison, so this only ever removes false alarms.
"""
import math
import random
import re
from typing import Dict, List, Optional, Tuple

# A node is ("num", value) | ("sym", name) | (op, left, right) for + - * / ^ | ("neg", x) | ("fn", name, x).
Node = tuple

_GREEK = {"alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta", "vartheta", "iota",
          "kappa", "lambda", "mu", "nu", "xi", "pi", "rho", "sigma", "tau", "upsilon", "phi", "varphi", "chi", "psi",
          "omega", "Gamma", "Delta", "Theta", "Lambda", "Xi", "Sigma", "Phi", "Psi", "Omega"}
_FUNCS = {"sqrt": math.sqrt, "ln": math.log, "log": math.log10, "exp": math.exp, "sin": math.sin, "cos": math.cos,
          "tan": math.tan, "tanh": math.tanh, "sinh": math.sinh, "cosh": math.cosh, "arctan": math.atan}


class ParseError(ValueError):
    pass


def _clean(tex: str) -> str:
    t = tex.replace("\\left", "").replace("\\right", "").replace("\\displaystyle", "")
    t = re.sub(r"\\(?:text|mathrm|operatorname|mathit|mathbf)\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\[,;:! ]|~", " ", t)
    t = t.replace("\\cdot", "*").replace("\\times", "*").replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    return t.strip().rstrip(".,;")


def _tokens(tex: str) -> List[str]:
    out: List[str] = []
    i = 0
    while i < len(tex):
        c = tex[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or (c == "." and i + 1 < len(tex) and tex[i + 1].isdigit()):
            m = re.match(r"\d*\.?\d+(?:[eE][-+]?\d+)?", tex[i:])
            out.append(m.group())
            i += len(m.group())
        elif c == "\\":
            m = re.match(r"\\[A-Za-z]+", tex[i:])
            if not m:
                raise ParseError(tex[i:i + 2])
            out.append(m.group())
            i += len(m.group())
        elif c.isalpha():
            out.append(c)
            i += 1
        elif c in "+-*/^_(){}[]'":
            out.append(c)
            i += 1
        else:
            raise ParseError(c)
    return out


class _Parser:
    """expr := term (('+'|'-') term)* ; term := factor (('*'|'/')? factor)* ; factor := '-' factor | power."""

    def __init__(self, tokens: List[str]):
        self.t = tokens
        self.i = 0

    def peek(self) -> Optional[str]:
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self, expected: Optional[str] = None) -> str:
        tok = self.peek()
        if tok is None or (expected is not None and tok != expected):
            raise ParseError(f"expected {expected!r}, got {tok!r}")
        self.i += 1
        return tok

    def expr(self) -> Node:
        node = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            node = (op, node, self.term())
        return node

    def term(self) -> Node:
        node = self.factor()
        while True:
            tok = self.peek()
            if tok in ("*", "/"):
                self.take()
                node = (tok, node, self.factor())
            elif tok is not None and tok not in ("+", "-", ")", "}", "]", "="):
                node = ("*", node, self.factor())  # implicit product: "\rho V_s^2"
            else:
                return node

    def factor(self) -> Node:
        if self.peek() == "-":
            self.take()
            return ("neg", self.factor())
        if self.peek() == "+":
            self.take()
            return self.factor()
        return self.power()

    def power(self) -> Node:
        base = self.atom()
        if self.peek() == "^":
            self.take()
            return ("^", base, self.group_or_atom())
        return base

    def group_or_atom(self) -> Node:
        if self.peek() == "{":
            self.take("{")
            node = self.expr()
            self.take("}")
            return node
        if self.peek() == "-":
            self.take()
            return ("neg", self.atom())
        return self.atom()

    def subscript(self) -> str:
        """The text of a subscript, as part of a symbol's name (G_{max} -> "G_max")."""
        if self.peek() == "{":
            self.take("{")
            depth, parts = 1, []
            while depth:
                tok = self.take()
                depth += tok == "{"
                depth -= tok == "}"
                if depth:
                    parts.append(tok.lstrip("\\"))
            return "".join(parts)
        return self.take().lstrip("\\")

    def symbol(self, name: str) -> Node:
        while self.peek() in ("_", "'"):
            if self.take() == "_":
                name += "_" + self.subscript()
            else:
                name += "_prime"
        return ("sym", name)

    def atom(self) -> Node:
        tok = self.take()
        if re.fullmatch(r"\d*\.?\d+(?:[eE][-+]?\d+)?", tok):
            return ("num", float(tok))
        if tok in ("(", "{", "["):
            close = {"(": ")", "{": "}", "[": "]"}[tok]
            node = self.expr()
            self.take(close)
            return node
        if tok == "\\frac":
            num = self.group_or_atom()
            den = self.group_or_atom()
            return ("/", num, den)
        if tok == "\\sqrt":
            if self.peek() == "[":
                self.take("[")
                n = self.expr()
                self.take("]")
                return ("^", self.group_or_atom(), ("/", ("num", 1.0), n))
            return ("fn", "sqrt", self.group_or_atom())
        if tok == "\\pi":
            return ("num", math.pi)
        if tok.startswith("\\") and tok[1:] in _FUNCS:
            return ("fn", tok[1:], self.power())
        if tok.startswith("\\") and tok[1:] in _GREEK:
            return self.symbol(tok[1:])
        if len(tok) == 1 and tok.isalpha():
            return self.symbol(tok)
        raise ParseError(tok)


def parse(tex: str) -> Node:
    p = _Parser(_tokens(_clean(tex)))
    node = p.expr()
    if p.peek() is not None:
        raise ParseError(f"unexpected {p.peek()!r}")
    return node


def parse_equation(line: str) -> Optional[Tuple[str, Node]]:
    """(lhs symbol name, rhs tree) for "X = ..." with a single symbol on the left; None otherwise."""
    if line.count("=") != 1:
        return None
    lhs, rhs = line.split("=")
    try:
        left = parse(lhs)
        right = parse(rhs)
    except ParseError:
        return None
    return (left[1], right) if left[0] == "sym" else None


def symbols_in(node: Node, out: set) -> set:
    """The symbol names in a tree, added to `out`."""
    if node[0] == "sym":
        out.add(node[1])
    elif node[0] in ("neg", "fn"):
        symbols_in(node[-1], out)
    elif node[0] != "num":
        symbols_in(node[1], out)
        symbols_in(node[2], out)
    return out


def _expand(node: Node, defs: Dict[str, Node], depth: int = 0) -> Node:
    """Replace defined symbols by their definitions (rho -> gamma / g), recursively."""
    if depth > 10:
        raise ParseError("circular definitions")
    if node[0] == "sym":
        return _expand(defs[node[1]], defs, depth + 1) if node[1] in defs else node
    if node[0] == "num":
        return node
    if node[0] == "neg":
        return ("neg", _expand(node[1], defs, depth))
    if node[0] == "fn":
        return ("fn", node[1], _expand(node[2], defs, depth))
    return (node[0], _expand(node[1], defs, depth), _expand(node[2], defs, depth))


def _eval(node: Node, env: Dict[str, float]) -> float:
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "sym":
        return env[node[1]]
    if kind == "neg":
        return -_eval(node[1], env)
    if kind == "fn":
        return _FUNCS[node[1]](_eval(node[2], env))
    a, b = _eval(node[1], env), _eval(node[2], env)
    return {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b else math.inf, "^": a ** b}[kind]


def same_expression(a: Node, b: Node, trials: int = 5) -> bool:
    """Equal at several random positive points (seeded, so the check is deterministic)."""
    names = sorted(symbols_in(a, set()) | symbols_in(b, set()))
    rng = random.Random(1234)
    for _ in range(trials):
        env = {n: rng.uniform(0.5, 3.0) for n in names}
        try:
            x, y = _eval(a, env), _eval(b, env)
        except (ValueError, OverflowError, ZeroDivisionError, KeyError, TypeError):
            return False
        if isinstance(x, complex) or isinstance(y, complex) or not math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12):
            return False
    return True


def equations(lines: List[str]) -> Dict[str, List[Node]]:
    """{lhs: [rhs, ...]} of the lines that parse as "symbol = expression", in order (an answer often writes the
    same left-hand side twice: symbolically, then with the numbers substituted)."""
    out: Dict[str, List[Node]] = {}
    for line in lines:
        eq = parse_equation(line)
        if eq:
            out.setdefault(eq[0], []).append(eq[1])
    return out


def equivalent_line(method_line: str, method_defs: Dict[str, Node], written: Dict[str, List[Node]]) -> Optional[bool]:
    """
    Whether the answer writes the method's line `X = f(...)` in an equivalent form: some written `X = g(...)` with
    g == f once both are expanded with the method's definitions (and the answer's own symbolic ones). None when it
    cannot be decided (the line does not parse, or the answer has no equation for X).
    """
    eq = parse_equation(method_line)
    if not eq or eq[0] not in written:
        return None
    lhs, rhs = eq
    # The answer's own definitions: its first right-hand side with symbols in it (not a numeric substitution).
    own = {k: next((n for n in v if symbols_in(n, set())), v[0]) for k, v in written.items()}
    defs = {k: v for k, v in {**own, **method_defs}.items() if k != lhs}
    try:
        target = _expand(rhs, defs)
        return any(same_expression(target, _expand(candidate, defs)) for candidate in written[lhs])
    except ParseError:
        return None
