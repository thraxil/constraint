import operator


class Connector(object):
    def __init__(self, init_value=None):
        self.value = init_value
        self.constraints = set([])
        self.informant = None

    def has_value(self):
        return self.value is not None

    def get_value(self):
        return self.value

    def set_value(self, v, informant):
        if self.has_value():
            return
        self.value = v
        self.informant = informant
        for c in self.constraints:
            if c == informant:
                continue
            c.process_new_value()
        if self.value != v:
            # we set it, and they changed it
            print "contradiction!"

    def forget_value(self, retractor):
        if retractor != self.informant:
            return
        self.informant = None
        for c in self.constraints:
            if c == retractor:
                continue
            c.process_forget_value()

    def connect(self, constraint):
        self.constraints.add(constraint)
        if self.has_value():
            constraint.process_new_value()


class Constant(object):
    def __init__(self, v, connector):
        self.v = v
        self.connector = connector
        self.connector.set_value(self.v, self)

    def process_new_value(self):
        pass

    def process_forget_value(self):
        pass


class User(object):
    def process_new_value(self):
        pass

    def process_forget_value(self):
        pass


class Constraint(object):
    def __init__(self, inputs, output):
        self.inputs = inputs
        self.output = output
        for i in self.inputs:
            i.connect(self)
        self.output.connect(self)

    def process_forget_value(self):
        self.output.forget_value(self)
        for i in self.inputs:
            i.forget_value(self)

    def _collect_inputs(self):
        inputs = set(self.inputs)
        self.inputs_with_values = set(i for i in self.inputs if i.has_value())
        self.inputs_without = inputs - self.inputs_with_values
        self.input_values = [i.get_value() for i in self.inputs_with_values]

    def value(self):
        raise NotImplemented

    def invert_value(self):
        raise NotImplemented

    def shortcut_cond(self):
        return False

    def shortcut_value(self):
        raise NotImplemented

    def process_new_value(self):
        self._collect_inputs()
        if self.shortcut_cond():
            self.output.set_value(self.shortcut_value(), self)
        elif len(self.inputs_without) == 0:
            self.output.set_value(self.value(), self)
        elif len(self.inputs_without) == 1 and self.output.has_value():
            list(self.inputs_without)[0].set_value(
                self.invert_value(), self)


class Adder(Constraint):
    def value(self):
        return sum(self.input_values)

    def invert_value(self):
        return self.output.get_value() - self.value()


class Subtracter(Constraint):
    def value(self):
        # only defined for 2 inputs
        return self.input_values[0] - self.input_values[1]

    def invert_value(self):
        # trickier, since it matters *which* input we know
        if self.inputs[0].has_value():
            return self.inputs[0].get_value() - self.output.get_value()
        if self.inputs[1].has_value():
            return self.output.get_value() + self.inputs[1].get_value()


class Divider(Constraint):
    def value(self):
        # only defined for 2 inputs
        return self.input_values[0] / self.input_values[1]

    def invert_value(self):
        # trickier, since it matters *which* input we know
        if self.inputs[0].has_value():
            return self.inputs[0].get_value() / self.output.get_value()
        if self.inputs[1].has_value():
            return self.output.get_value() * self.inputs[1].get_value()


class Multiplier(Constraint):
    def value(self):
        return reduce(operator.mul, self.input_values, 1.)

    def invert_value(self):
        return self.output.get_value() / self.value()

    def shortcut_cond(self):
        return 0. in self.input_values

    def shortcut_value(self):
        return 0.


class CFConverter(object):
    def __init__(self, celsius, fahr):
        self.c = celsius
        self.f = fahr
        self.u = Connector()
        self.v = Connector()
        self.w = Connector()
        self.x = Connector()
        self.y = Connector()
        self.m1 = Multiplier([self.c, self.w], self.u)
        self.m2 = Multiplier([self.v, self.x], self.u)
        self.a = Adder([self.v, self.y], self.f)
        self.cw = Constant(9., self.w)
        self.cx = Constant(5., self.x)
        self.cy = Constant(32., self.y)


if __name__ == "__main__":
    c = Connector()
    f = Connector()
    cfc = CFConverter(c, f)

    f.set_value(32., User())
    print c.get_value()

    # 4 + x = 5 * y
    c1 = Connector()
    c2 = Connector()
    c3 = Connector()
    c4 = Connector()
    c5 = Connector()
    a1 = Adder([c1, c2], c3)
    m1 = Multiplier([c4, c5], c3)
    cons1 = Constant(4, c2)
    cons2 = Constant(5, c5)
    c4.set_value(7., User())
    print c1.get_value()
