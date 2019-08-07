Lambda Calculus
---------------

Parse, validate, and "run" lambda expressions.

    from lambda_calculus.parser import parse

    wff = parse("((λ x . (x x)) (λ y . y))"
    print(wff.beta_reduction())

prints:

    ((λ y . y) (λ y . y))

