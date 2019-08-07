def zero(f, x):
    return x

def one(f, x):
    return f(x)

def two(f, x):
    return f(f(x))

def three(f, x):
    return f(f(f(x)))

def pred(n):
    def n_minus_one(f, x):

        # Uses the pair as a shift-register so we can throw away one application of f.
        # accepts a pair as an argument and returns a pair.
        def f_delayed(pair):
            # unpack the pair
            a, b = pair
            
            return (
                b,   # shift the second item to the first slot unchanged.
                f(b) # apply the function f to the second element, once.
            )
        
        # instead of calling n(f, x) directly, we instead pass in f_delayed as a wrapper.
        # However, it expects a pair, so we construct the pair (x, x) as an initial value.
        # Using x for both slots will allow it to work correctly even for the case n == zero.
        final_pair = n(f_delayed, (x, x))
        
        # f_delayed returned a pair, but we're supposed to return a value, so we take
        # only the first item, which will contain contain f^{n-1}(x). 
        return final_pair[0]
    
    return n_minus_one

print( pred(zero)(lambda x:x+1, 0) )
print( pred(one)(lambda x:x+1, 0) )
print( pred(two)(lambda x:x+1, 0) )
print( pred(three)(lambda x:x+1, 0) )
