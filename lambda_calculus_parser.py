import re
import itertools

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
    
           

class Application(Node):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
        
    def __str__(self):
        return f'({self.func} {self.arg})'

    def __repr__(self):
        return f'Application(func={self.func!r}, arg={self.arg!r})'

    
class Macro(Node):
    def __init__(self, name):
        assert re.match(r'^[A-Z]+$', name)
        self.name = str(name)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'Macro({self.name!r})'
    
    
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

expr = parse("(f (L x. f))")
