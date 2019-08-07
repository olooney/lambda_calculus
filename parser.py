import re
import itertools
from string import ascii_lowercase as variable_names

from ast import Node, Abstraction, Application, Variable, Macro

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
    
def consume_expected(tokens, expected):
    close_paren = next(tokens)
    assert close_paren == expected, "expected: " + repr(expected)


def parse_expr(tokens):
    token = next(tokens)
    if token == '(': 
        # both abstraction or application start with '('.
        # peek ahead to decide which we have.
        next_token = tokens.peek()        
        if next_token == 'λ':
            return parse_abstraction(tokens)
        else:
            return parse_application(tokens)
    else:
        if token in (')', 'λ', '.'):
            print('invalid token:', token)
        
        # must be a macro (uppercase) or variable (lowercase.) 
        if token == token.upper():
            return Macro(token)
        else:
            return Variable(token)

def parse_abstraction(tokens):
    # abstraction: "(λ v. b)"
    
    stack = []
    
    consume_expected(tokens, 'λ')
    
    while tokens.peek() != '.':
        stack.append(Variable(next(tokens)))
        
    assert stack, "lambda abstractions must have at least one variable."
    
    consume_expected(tokens, '.')
    body = parse_expr(tokens)
    consume_expected(tokens, ')')
    
    while stack:
        body = Abstraction(stack.pop(), body)

    return body


def parse_application(tokens):
    # application: "(f a)"
    
    func = parse_expr(tokens)
    arg = parse_expr(tokens)

    while tokens.peek() != ')':
        # three or more letters in a row.
        # use left associative application.
        func = Application(func, arg)
        arg = parse_expr(tokens)

    consume_expected(tokens, ')')

    return Application(func, arg)

        
def parse(string):
    tokens = peekable(tokenize(string))
    expr = parse_expr(tokens)
    
    for token in tokens:
        raise ValueError("token stream not exhausted: " + str(token))
        
    return expr
