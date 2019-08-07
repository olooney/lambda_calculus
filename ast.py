import re
from copy import copy

# Abstract Base Class for parse tree nodes
class Node:
    def beta_reduction(self):
        return copy(self)

        
class Abstraction(Node):
    def __init__(self, variable, body):
        self.variable = variable
        self.body = body
        
    def __str__(self):
        return f'(λ {self.variable} . {self.body})'

    def __repr__(self):
        return f'Abstraction(variable={self.variable!r}, body={self.body!r})'

    def mentioned(self):
        return self.variable.mentioned().union(self.body.mentioned())
    
    def alpha_replace(self, old, new):
        if old == self.variable or new == self.variable:
            used = self.mentioned().union(set([old.name, new.name]))
            available = [name for name in variable_names if name not in used and name > self.variable.name]
            if not available:
                available = [ name for name in variable_names if name not in used ]
            new_variable = Variable(available[0])
            conflict_free_body = self.body.alpha_replace(self.variable, new_variable)
            print(conflict_free_body)
            new_body = conflict_free_body.alpha_replace(old, new)
        else:
            new_variable = copy(self.variable)
            new_body = self.body.alpha_replace(old, new)
        return Abstraction(new_variable, new_body)
    
    def substitute(self, old, replacement):
        assert self.variable != old
        return Abstraction(self.variable, self.body.substitute(old, replacement))
    
    def beta_reduction(self):
        return Abstraction(
                copy(self.variable),
                self.body.beta_reduction())

            
class Application(Node):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
        
    def __str__(self):
        return f'({self.func} {self.arg})'

    def __repr__(self):
        return f'Application(func={self.func!r}, arg={self.arg!r})'
    
    def mentioned(self):
        return self.func.mentioned().union(self.arg.mentioned())
    
    def alpha_replace(self, old, new):
        return Application(
            self.func.alpha_replace(old, new),
            self.arg.alpha_replace(old, new))

    def substitute(self, old, replacement):
        return Application(
            self.func.substitute(old, replacement),
            self.arg.substitute(old, replacement))
    
    def beta_reduction(self):
        if isinstance(self.func, Abstraction):
            return self.func.body.substitute(self.func.variable, self.arg)
        else:
            return Application(
                self.func.beta_reduction(),
                self.arg.beta_reduction())
            
    
class Macro(Node):
    def __init__(self, name):
        assert re.match(r'^[A-Z]+$', name), "malformed macro name: " + repr(name)
        self.name = str(name)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'Macro({self.name!r})'
    
    def mentioned(self):
        return False
    
    def alpha_replace(self, old, new):
        return copy(self)
    
    def substitute(self, old, replacement):
        return copy(self)
    
 
class Variable(Node):
    def __init__(self, name):
        assert re.match(r'^[a-z][a-z0-9_]*$', name), "malformed variable name: " + repr(name)
        self.name = str(name)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Variable({self.name!r})'
    
    def __eq__(self, other):
        return \
            isinstance(other, Variable) and \
            self.name == other.name

    def mentioned(self):
        return set(self.name)
    
    def alpha_replace(self, old, new):
        if self == old:
            return Variable(new.name)
        else:
            return Variable(self.name)
    
    def substitute(self, old, replacement):
        if self == old:
            return copy(replacement)
        else:
            return copy(self)
