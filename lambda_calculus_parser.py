import re
import itertools
from string import ascii_lowercase as variable_names
from copy import copy

lambda_calculus_tokens = re.compile(r'\(|\)|\.|Lambda|L|λ|[A-Z]+|[a-z][a-z0-9_]*')


def tokenize(formula):
    for match in lambda_calculus_tokens.finditer(formula):
        token = match.group(0)
        if token in ('L', 'Lambda', 'λ'):
            token = 'λ'
        yield token


class peekable(object):
    def __init__(self, it):
        self._it = iter(it)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._it)

    def peek(self, default=None, _chain=itertools.chain):
        it = self._it
        try:
            v = next(self._it)
            self._it = _chain((v,), it)
            return v
        except StopIteration:
            return default


# Abstract Base Class for parse tree nodes
class Node:
    pass

        
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
    
    def beta_reduce(self):
        assert isinstance(self.func, Abstraction)
        return self.func.body.substitute(self.func.variable, self.arg)
            
    
class Macro(Node):
    def __init__(self, name):
        assert re.match(r'^[A-Z]+$', name)
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
        assert re.match(r'^[a-z][a-z0-9_]*$', name)
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
        
    
def consume_expected(tokens, expected):
    close_paren = next(tokens)
    assert close_paren == expected


def parse_token_stream(tokens):
    token = next(tokens)
    if token == '(':
        next_token = tokens.peek()
        if next_token == 'λ':
            next(tokens) # consume the λ token
            variable = Variable(next(tokens))
            consume_expected(tokens, '.')
            body = parse_token_stream(tokens)
            consume_expected(tokens, ')')
            return Abstraction(variable, body)
        else:
            func = parse_token_stream(tokens)
            args = parse_token_stream(tokens)
            consume_expected(tokens, ')')            
            return Application(func, args)
    else:
        assert token not in (')', 'λ', '.')
        if token == token.upper():
            return Macro(token)
        else:
            return Variable(token)


def parse(string):
    return parse_token_stream(peekable(tokenize(string)))


expr = parse(str(parse('((λ x. (x x)) (λ f. (Lambda x. ((Lx.x) x)) ))')))
print(expr)
print(repr(expr))

expr = parse("(λ f. (L x. (f (f z)) ))")

expr = parse('(((x x) (y x)) (x y))')
print(expr)
print(expr.alpha_replace(Variable('x'), Variable('z')))

expr = parse('(L x. y)')
print(expr)
print(expr.alpha_replace(Variable('y'), Variable('z')))

expr = parse('(L x. (x y) )')
print(expr)
print(expr.alpha_replace(Variable('x'), Variable('t')))

expr = parse("(L a. (x x))")
print(expr.substitute(Variable('x'), parse('(L z. z)')))

expr = parse("((L x. (x x)) (L y. y))")
print(expr)
print(expr.beta_reduce())
print(expr.beta_reduce().beta_reduce())

