import re

# ('=', 'rel', lhs, rhs)        - equality of type 'rel' relating Left-Hand-Side and Right-Hand-Side
# ('#', 'num')                  - numbers represented as strings to pass on maximum precision to sympy
# ('@', 'var')                  - variable name, can take forms: 'x', "x'", 'dx', '\partial x', 'x_2', '\partial x_{y_2}', "d\alpha_{x_{\beta''}'}'''"
# ('"', 'str')                  - string (for function parameters like '+' or '-')
# (',', (expr1, expr2, ...))    - comma expression (tuple)
# ('(', expr)                   - explicit parentheses
# ('|', expr)                   - absolute value
# ('-', expr)                   - negative of expression, negative numbers are represented with this at least initially
# ('!', expr)                   - factorial
# ('+', (expr1, expr2, ...))    - addition
# ('*', (expr1, expr2, ...))    - multiplication
# ('/', numer, denom)           - fraction numer(ator) / denom(inator)
# ('^', base, exp)              - power base ^ exp(onent)
# ('log', expr)                 - natural logarithm of expr
# ('log', expr, base)           - logarithm of expr in base
# ('sqrt', expr)                - square root of expr
# ('sqrt', expr, n)             - nth root of expr
# ('func', 'func', expr)        - sympy or regular python function 'func', will be called with sympy expression
# ('lim', expr, var, to)        - limit of expr when variable var approaches to from both positive and negative directions
# ('lim', expr, var, to, dir)   - limit of expr when variable var approaches to from direction dir which may be '+' or '-'
# ('sum', expr, var, from, to)  - summation of expr over variable var from from to to
# ('diff', expr, (var1, ...))   - differentiation of expr with respect to var1 and optional other vars
# ('intg', None, var)           - anti-derivative of 1 with respect to differential var ('dx', 'dy', etc ...)
# ('intg', expr, var)           - anti-derivative of expr with respect to differential var ('dx', 'dy', etc ...)
# ('intg', None, var, from, to) - definite integral of 1 with respect to differential var ('dx', 'dy', etc ...)
# ('intg', expr, var, from, to) - definite integral of expr with respect to differential var ('dx', 'dy', etc ...)

#...............................................................................................
class AST (tuple):
	def __new__ (cls, *args):
		op       = _AST_CLS2OP.get (cls)
		cls_args = tuple (AST (*arg) if arg.__class__ is tuple else arg for arg in args)

		if op:
			args = (op,) + cls_args

		elif args:
			args = cls_args
			cls2 = _AST_OP2CLS.get (args [0])

			if cls2:
				op       = args [0]
				cls      = cls2
				cls_args = cls_args [1:]

		self    = tuple.__new__ (cls, args)
		self.op = op

		if op:
			self._init (*cls_args)

		return self

	def __getattr__ (self, name): # calculate value for nonexistent self.name by calling self._name ()
		func                 = getattr (self, f'_{name}') if name [0] != '_' else None
		val                  = func and func ()
		self.__dict__ [name] = val

		return val

	def _is_neg (self):
		return \
				self.is_minus or \
				self.is_num and self.num [0] == '-' or \
				self.is_mul and self.muls [0].is_neg

	def _is_single_unit (self): # is single positive digit, fraction or single non-differential non-subscripted variable?
		if self.op == '/':
			return True

		if self.op == '#':
			return len (self.num) == 1

		return self.op == '@' and not AST_Var._rec_not_single.match (self.var)

	def neg (self, stack = False): # stack means stack negatives ('-', ('-', ('#', '-1')))
		if stack:
			return \
					AST ('-', self)            if not self.is_pos_num else \
					AST ('#', f'-{self.num}')

		else:
			return \
					self.minus                 if self.is_minus else \
					AST ('-', self)            if not self.is_num else \
					AST ('#', self.num [1:])   if self.num [0] == '-' else \
					AST ('#', f'-{self.num}')

	def strip_paren (self, count = None):
		count = 999999999 if count is None else count

		while self.op == '(' and count:
			self   = self.paren
			count -= 1

		return self

	def strip_minus (self, count = None):
		count = 999999999 if count is None else count

		while self.op == '-' and count:
			self   = self.minus
			count -= 1

		return self

	@staticmethod
	def is_int_text (text): # >= 0
		return AST_Num._rec_int.match (text)

	@staticmethod
	def flatcat (op, ast0, ast1): # ,,,/O.o\,,,~~
		if ast0.op == op:
			if ast1.op == op:
				return AST (op, ast0 [-1] + ast1 [-1])
			return AST (op, ast0 [-1] + (ast1,))
		elif ast1.op == op:
			return AST (op, (ast0,) + ast1 [-1])
		return AST (op, (ast0, ast1))

#...............................................................................................
class AST_Eq (AST):
	is_eq      = True

	SHORT2LONG = {'!=': '\\ne', '<=': '\\le', '>=': '\\ge'}
	LONG2SHORT = {'\\ne': '!=', '\\le': '<=', '\\ge': '>=', '==': '=', '\\neq': '!=', '\\lt': '<', '\\gt': '>'}

	def _init (self, rel, lhs, rhs):
		self.rel = rel # should be short form
		self.lhs = lhs
		self.rhs = rhs

	def _is_eq_eq (self):
		return self.rel == '='

class AST_Num (AST):
	is_num           = True

	_rec_int          = re.compile (r'^-?\d+$')
	_rec_pos_int      = re.compile (r'^\d+$')
	_rec_mant_and_exp = re.compile (r'^(-?\d*\.?\d*)[eE](?:(-\d+)|\+?(\d+))$')

	def _init (self, num):
		self.num = num

	def _is_pos_num (self):
		return self.num [0] != '-'

	def _is_neg_num (self):
		return self.num [0] == '-'

	def _is_pos_int (self):
		return AST_Num._rec_pos_int.match (self.num)

	def mant_and_exp (self):
		m = AST_Num._rec_mant_and_exp.match (self.num)

		return (self.num, None) if not m else (m.group (1) , m.group (2) or m.group (3))

class AST_Var (AST):
	is_var              = True

	LONG2SHORT          = {'\\pi': 'pi', '\\infty': 'oo', '\\text{True}': 'True', '\\text{False}': 'False', '\\text{undefined}': 'undefined'}
	SHORT2LONG          = {'pi': '\\pi', 'oo': '\\infty', 'True': '\\text{True}', 'False': '\\text{False}', 'undefined': '\\text{undefined}'}

	_rec_diff_start         = re.compile (r'^d(?=[^_])')
	_rec_part_start         = re.compile (r'^\\partial ')
	_rec_diff_or_part_start = re.compile (r'^(d(?=[^_])|\\partial )')
	_rec_diff_or_part_solo  = re.compile (r'^(?:d|\\partial)$')
	_rec_not_single         = re.compile (r'^(?:d.|\\partial |.+_)')

	def _init (self, var):
		self.var = var # should be long form

	def _is_null_var (self):
		return not self.var

	def _is_long_var (self):
		return self.var in AST_Var.LONG2SHORT

	def _is_differential (self):
		return AST_Var._rec_diff_start.match (self.var)

	def _is_partial (self):
		return AST_Var._rec_part_start.match (self.var)

	def _is_diff_or_part (self):
		return AST_Var._rec_diff_or_part_start.match (self.var)

	def _is_diff_or_part_solo (self):
		return AST.Var._rec_diff_or_part_solo.match (self.var)

	def diff_subvar (self):
		return AST ('@', AST.Var._rec_diff_or_part_start.sub ('', self.var))

	def as_differential (self): # var or diff or part var to diff var
		return AST ('@', f'd{AST_Var._rec_diff_or_part_start.sub ("", self.var)}') if self.var else self

	def as_partial (self): # var or diff or part var to diff var
		return AST ('@', f'\\partial {AST_Var._rec_diff_or_part_start.sub ("", self.var)}') if self.var else self

	def diff_or_part_start_text (self):
		m = AST_Var._rec_diff_or_part_start.match (self.var)

		return m.group (1) if m else ''

class AST_Str (AST):
	is_str = True

	def _init (self, str_):
		self.str_ = str_

class AST_Comma (AST):
	is_comma = True

	def _init (self, commas):
		self.commas = commas

class AST_Paren (AST):
	is_paren = True

	def _init (self, paren):
		self.paren = paren

class AST_Abs (AST):
	is_abs = True

	def _init (self, abs):
		self.abs = abs

class AST_Minus (AST):
	is_minus = True

	def _init (self, minus):
		self.minus = minus

class AST_Fact (AST):
	is_fact = True

	def _init (self, fact):
		self.fact = fact

class AST_Add (AST):
	is_add = True

	def _init (self, adds):
		self.adds = adds

class AST_Mul (AST):
	is_mul = True

	def _init (self, muls):
		self.muls = muls

class AST_Div (AST):
	is_div = True

	def _init (self, numer, denom):
		self.numer = numer
		self.denom = denom

class AST_Pow (AST):
	is_pow = True

	def _init (self, base, exp):
		self.base = base
		self.exp  = exp

class AST_Log (AST):
	is_log = True

	def _init (self, log, base = None):
		self.log  = log
		self.base = base

class AST_Sqrt (AST):
	is_sqrt = True

	def _init (self, rad, idx = None):
		self.rad = rad
		self.idx = idx

class AST_Func (AST):
	is_func = True

	PY_ONLY = set ('''
		?
		Abs
		Derivative
		Integral
		Limit
		Piecewise
		Sum
		abs
		expand
		factor
		factorial
		series
		simplify
		'''.strip ().split ())

	PY_AND_TEX = set ('''
		arg
		exp
		ln
		'''.strip ().split ())

	PY_ALL = PY_ONLY | PY_AND_TEX
	ALIAS  = {'?': 'N'}

	_rec_trigh             = re.compile (r'^a?(?:sin|cos|tan|csc|sec|cot)h?$')
	_rec_trigh_noninv_func = re.compile (r'^(?:sin|cos|tan|csc|sec|cot)h?$')

	def _init (self, func, arg):
		self.func = func
		self.arg  = arg

	def _is_trigh_func (self):
		return AST_Func._rec_trigh.match (self.func)

	def _is_trigh_func_noninv_func (self):
		return AST_Func._rec_trigh_noninv_func.match (self.func)

class AST_Lim (AST):
	is_lim = True

	def _init (self, lim, var, to, dir = None):
		self.lim = lim
		self.var = var
		self.to  = to
		self.dir = dir

class AST_Sum (AST):
	is_sum = True

	def _init (self, sum, var, from_, to):
		self.sum   = sum
		self.var   = var
		self.from_ = from_
		self.to    = to

class AST_Diff (AST):
	is_diff = True

	def _init (self, diff, vars):
		self.diff = diff
		self.vars = vars

class AST_Intg (AST):
	is_intg = True

	def _init (self, intg, var, from_ = None, to = None):
		self.intg  = intg
		self.var   = var
		self.from_ = from_
		self.to    = to

#...............................................................................................
_AST_OP2CLS = {
	'=': AST_Eq,
	'#': AST_Num,
	'@': AST_Var,
	'"': AST_Str,
	',': AST_Comma,
	'(': AST_Paren,
	'|': AST_Abs,
	'-': AST_Minus,
	'!': AST_Fact,
	'+': AST_Add,
	'*': AST_Mul,
	'/': AST_Div,
	'^': AST_Pow,
	'log': AST_Log,
	'sqrt': AST_Sqrt,
	'func': AST_Func,
	'lim': AST_Lim,
	'sum': AST_Sum,
	'diff': AST_Diff,
	'intg': AST_Intg,
}

_AST_CLS2OP = dict ((b, a) for (a, b) in _AST_OP2CLS.items ())

for cls in _AST_CLS2OP:
	setattr (AST, cls.__name__ [4:], cls)

AST.Zero      = AST ('#', '0')
AST.One       = AST ('#', '1')
AST.NegOne    = AST ('#', '-1')
AST.VarNull   = AST ('@', '')
AST.I         = AST ('@', 'i')
AST.E         = AST ('@', 'e')
AST.Pi        = AST ('@', '\\pi')
AST.Infty     = AST ('@', '\\infty')
AST.True_     = AST ('@', '\\text{True}')
AST.False_    = AST ('@', '\\text{False}')
AST.Undefined = AST ('@', '\\text{undefined}')

# if __name__ == '__main__':
# 	print (AST_Str ('a').is_str)