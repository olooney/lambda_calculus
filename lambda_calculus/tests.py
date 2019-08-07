from .parser import parse, variable_names
from .ast import Variable

expr = parse(str(parse('((λ x. (x x)) (λ f. (Lambda x. ((Lx.x) x)) ))')))
print(expr)
print(repr(expr))

print("\nAlpha replacement Case 1")
expr = parse('(((x x) (y x)) (x y))')
print(expr)
print(expr.alpha_replace(Variable('x'), Variable('z')))

print("\nAlpha replacement Case 2")
expr = parse('(L x. y)')
print(expr)
print(expr.alpha_replace(Variable('y'), Variable('z')))

print("\nAlpha replacement Case 3")
expr = parse('(L x. (x y) )')
print(expr)
print(expr.alpha_replace(Variable('x'), Variable('t')))

print("\nUnsafe Substitution")
expr = parse("(L a. (x x))")
print(expr.substitute(Variable('x'), parse('(L z. z)')))

print("\nBeta Reduction Case 1")
expr = parse("((L x. (x x)) (L y. y))")
print(expr)
print(expr.beta_reduction())
print(expr.beta_reduction().beta_reduction())

print("\nBeta Reduction Case 2")
print(parse("((L x y z. (x y z)) a b c)"))
print(parse("((L x y z. (x y z)) a b c)").beta_reduction())
print(parse("((L x y z. (x y z)) a b c)").beta_reduction().beta_reduction())
print(parse("((L x y z. (x y z)) a b c)").beta_reduction().beta_reduction().beta_reduction())
