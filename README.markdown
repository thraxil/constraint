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
