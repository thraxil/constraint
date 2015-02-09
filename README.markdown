One of the weird things about most programming languages that confuse
newcomers to programming is that `=` represents assignment, not
equality.

`F = m * a` or `V = I * R` might be valid statements to a programmer,
but they lack some of the richness and utility that we're accustomed
to coming from mathematics or science. In a programming context, those
statements specify a one-way relationship. If you know the value of
`m` and `a`, the computer will tell you the value of `F`. A physicist
gets more use out of them. With that formula, if a physicist knows
`F` and `m`, they can easily find the value of `a`. If they know `F`
and `a`, they can find `m`. For a computer program to do the same, the
programmer must explicitly specify every option that they might want
to solve for.

This library addresses this issue (for a subclass of basic equation/formula
types). It is based on and extends a simple constraint propagation
technique described in [Section 3.3.5](http://mitpress.mit.edu/sicp/full-text/book/book-Z-H-22.html#%_sec_3.3.5) of
[SICP](http://mitpress.mit.edu/sicp/).

## Basic Structure

The approach is to decompose equations into networks of "connectors"
which may or may not have values and "primitive constraints" that
specify simple relationships between the connectors.

Eg, an "adder" constraint that specifies `A + B = C` would be
represented like:

![adder](images/adder.jpg)

Similar to a circuit diagram, these components are connected to each
other to form more complicated relationships. Eg, `(A + B) * D = C`
can be made by combining an adder and a multiplier:

![more complicated](images/aplusbtimesd.jpg)

An even more complicated formula, like the conversion between
Fahrenheit and Celsius, `9C = 5(F - 32)` could be represented as:

![celsius to fahrenheit](images/temp_conv.jpg)

The system starts out with all connectors having no value. When the
value on a connector is set, it propagates that value to the
constraints that are connected to that connector. Each of those
constraints, if it now has enough inputs and outputs that have values
that it can assign a value to the remaining input/output, does
that. These values propagate from component to component through the
system until everything is set.

## Working with the components

You can build these networks directly. For `F = m * a`:

    >>> from constraint import *
    >>> user = User() # explain this later
    >>> F = Connector()
    >>> m = Connector()
    >>> a = Connector()
    >>> Multiplier([m, a], F)
    >>> F.has_value()
    False
    >>> F.set_value(10., user)
    >>> m.set_value(5., user)
    >>> a.has_value()
    True
    >>> a.get_value()
    2.0

More complicated ones with intermediate connectors take a bit more
work. For temperature conversion:

    >>> c = Connector()
    >>> f = Connector()
    >>> u = Connector()
    >>> v = Connector()
    >>> w = Connector()
    >>> x = Connector()
    >>> y = Connector()
    >>> Multiplier([c, w], u)
    >>> Multiplier([v, x], u)
    >>> Adder([v, y], f)
    >>> cw = Constant(9., w)
    >>> cx = Constant(5., x)
    >>> cy = Constant(32., y)
    >>> c.set_value(20., user)
    >>> f.get_value()
    68.0

You can look at the implementations of `Adder`, `Multiplier`, etc to
see how to create your own constraint types.

## Parser

(you'll need pyparsing installed for this part)

That quickly becomes tedious and error-prone, so I wrote a parser to
parse basic equation/formula expressions and build the networks
automatically. The main function `solve()`, takes a list of equations,
and the name of the variable that you want to solve for and returns
the result:

    >>> from parser import solve
    >>> solve(["F = m * a", "F = 10", "m=2.0"], "a")
    5.0
    >>> solve(["F = m * a"], "F", a=3.0, m=2.0)
    6.0
    >>> solve(["X + 10 = 13"], "X")
    3.0

## Limitations

This is mostly just a fun experiment and proof of concept for me. I
wouldn't expect it to actually do anything serious for you (stick to
Mathematica or something if you really need to solve equations).

The nature of the approach has some basic limitations:

* each component must be
  [injective](http://en.wikipedia.org/wiki/Injective_function) if you
  expect it to work both ways. This rules out quite a few functions
  (eg `square()` isn't injective unless you limit it to `>= 0`).
* It won't actually solve anything that would require
  substitution. Eg, `solve(["X + 10 = Y", "Y * 2 = X"], "X")` won't
  give you results.

I've implemented virtually no error checking or robustness. If you
give it an invalid constraint graph, it will give you an invalid
answer (at best).

I very rarely write parsers, so this one is ugly and extremely
limited. You may need to group expressions with parenthesis like 
`A + (B + C)` instead of `A + B + C`, etc.
