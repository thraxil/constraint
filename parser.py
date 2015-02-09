from pyparsing import (
    Literal, CaselessLiteral, Word, Combine, Group, Optional,
    ZeroOrMore, Forward, nums, alphas)
from constraint import (
    Adder, Multiplier, Connector, Constant,
    User, Subtracter, Divider)


class Variable(object):
    def __init__(self, v):
        self.name = v

    def __repr__(self):
        return "<" + self.name + ">"

    def vars(self):
        return {self.name: self}

    def build(self, connectors):
        return connectors[self.name]


def variable(strg, loc, toks):
    return Variable(toks[0])


class ConstantTerm(object):
    def __init__(self, v):
        self.value = float(v)

    def __repr__(self):
        return "%f" % self.value

    def vars(self):
        return {}

    def build(self, connectors):
        c = Connector()
        Constant(self.value, c)
        return c


def constant(strg, loc, toks):
    return ConstantTerm(toks[0])


ops = {
    "+": Adder,
    "*": Multiplier,
    "-": Subtracter,
    "/": Divider,
}

op_names = {
    "+": "Adder",
    "*": "Multiplier",
    "-": "Subtracter",
    "/": "Divider",
}


class ExpressionTerm(object):
    def __init__(self, e1, op, e2):
        self.e1 = e1
        self.op = op
        self.e2 = e2

    def __repr__(self):
        return "%s(%s, %s)" % (op_names[self.op], self.e1, self.e2)

    def vars(self):
        d = self.e1.vars()
        d.update(self.e2.vars())
        return d

    def build(self, connectors):
        i1 = self.e1.build(connectors)
        i2 = self.e2.build(connectors)
        output = Connector()
        ops[self.op]([i1, i2], output)
        return output


def expression(strg, loc, toks):
    if len(toks[0]) == 1:
        return toks[0]
    if len(toks[0]) == 3:
        return ExpressionTerm(toks[0][0], toks[0][1], toks[0][2])


class Equation(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return "EQN(%s, %s)" % (self.lhs, self.rhs)

    def vars(self):
        d = self.lhs.vars()
        d.update(self.rhs.vars())
        return d

    def build(self, connectors):
        lh_conn = self.lhs.build(connectors)
        rh_conn = self.rhs.build(connectors)
        # it's always safe to connect by adding 0'
        dummy_con = Connector()
        Constant(0.0, dummy_con)
        Adder([lh_conn, dummy_con], rh_conn)


def equation(strg, loc, toks):
    return Equation(toks[0], toks[2])


# -------------- The Grammar ------------

point = Literal(".")
e = CaselessLiteral("E")
fnumber = Combine(
    Word("+-" + nums, nums) +
    Optional(point + Optional(Word(nums))) +
    Optional(e + Word("+-" + nums, nums))).setParseAction(constant)
ident = Word(alphas, alphas + nums + "_$").setParseAction(variable)
plus = Literal("+")
minus = Literal("-")
mult = Literal("*")
div = Literal("/")
lpar = Literal("(").suppress()
rpar = Literal(")").suppress()
addop = plus | minus
multop = mult | div
pi = CaselessLiteral("PI")

expr = Forward()
atom = (pi | e | fnumber | ident | lpar + expr + rpar) | (lpar + expr + rpar)
term = Forward()
term << (atom + ZeroOrMore(multop + term))
expr << Group(term + ZeroOrMore(addop + term)).setParseAction(expression)
eqn = (expr + "=" + expr).setParseAction(equation)

# ----------------------------------------


def solve(equations, unknown, **values):
    connectors = dict()
    equations = [eqn.parseString(s).asList()[0] for s in equations]
    for e in equations:
        for v in e.vars().keys():
            if v not in connectors:
                connectors[v] = Connector()
    for e in equations:
        e.build(connectors)

    for k, v in values.items():
        connectors[k].set_value(v, User())
    return connectors[unknown].get_value()


if __name__ == "__main__":
    print solve(["F = m * a", "F = 10", "m=2.0"], "a")
    print solve(["F = m * a"], "F", a=3.0, m=2.0)
    print solve(["3 + x = 5 * y_2"], "y_2", x=17)
    print solve(["A - B = C", "A = 1", "B = 2"], "C")
    print solve(["A - B = C", "A = 10", "C = 2"], "B")
    print solve(["A - B = C", "B = 10", "C = 2"], "A")
    print solve(["X + 10 = 13"], "X")
    print solve(["A / B = C", "A = 1", "B = 2"], "C")
    print solve(["A / B = C", "A = 10", "C = 2"], "B")
    print solve(["A / B = C", "B = 10", "C = 2"], "A")
