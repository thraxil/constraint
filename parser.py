from pyparsing import (
    Literal, CaselessLiteral, Word, Combine, Group, Optional,
    ZeroOrMore, Forward, nums, alphas)


class Variable(object):
    def __init__(self, v):
        self.name = v

    def __repr__(self):
        return "<" + self.name + ">"


class Constant(object):
    def __init__(self, v):
        self.value = float(v)

    def __repr__(self):
        return "%f" % self.value


def variable(strg, loc, toks):
    return Variable(toks[0])

def constant(strg, loc, toks):
    return Constant(toks[0])

def expression(strg, loc, toks):
    if len(toks[0]) == 3:
        if toks[0][1] == "+":
            return "Adder(%s, %s)" % (toks[0][0], toks[0][2])
        if toks[0][1] == "*":
            return "Multiplier(%s, %s)" % (toks[0][0], toks[0][2])

class Equation(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return "EQN(%s, %s)" % (self.lhs, self.rhs)

def equation(strg, loc, toks):
    lhs = toks[0]
    rhs = toks[2]
    return Equation(lhs, rhs)
    

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
atom = (
    (pi | e | fnumber | ident | lpar + expr + rpar)
    | (lpar + expr + rpar)
)
term = Forward()
term << atom + ZeroOrMore(multop + term)
expr << Group(term + ZeroOrMore(addop + term)).setParseAction(expression)
eqn = (expr + "=" + expr).setParseAction(equation)

if __name__ == "__main__":
    print expr.parseString("9")
    print "---"
    print expr.parseString("-9")
    print "---"
    print expr.parseString("-9 + 1")
    print "---"
    print expr.parseString("-9 + -1")
    print "---"
    print expr.parseString("-9 + 1 + 2")
    print "---"
    print expr.parseString("-9 + (1.3 + 5)")
    print "---"
    print expr.parseString("-9 + (a + 5)")
    print "---"
    print expr.parseString("-9 + (b + 5) + a * 5")
    print "---"
    print eqn.parseString("F = m * a")
    print "---"
    print eqn.parseString("3 + x = 5 * y_2")
