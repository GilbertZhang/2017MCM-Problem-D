import sympy as sy
from scipy.optimize import minimize

class Least_Square:
    def __init__(self,lambdaA,square):
        self.lambdaA = lambdaA
        self.square = square

    def eval_fn(self,formula, **kwargs):
        expr = sy.sympify(formula)
        return expr.evalf(subs = kwargs)

    # def min_lambda(self,formula,actual,expect):
    #     for i in actual:


a = Least_Square(1,2)
print a.poisson_process(5)
print a.eval_fn(x=2,y=2,z=1,formula="x+2*y/z")
