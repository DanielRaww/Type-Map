# Daniel Raw & Abigail Daniel
# March 28, 2019
# Project 4: type.py

""" type.py implements a static type checker for Gee language.
This subset, tipe, contains the type of each statement,
checks the validty of the type and adds it in to the type map dictionary
that contains {variable : type}. """


import re, sys, string

debug = False
dict = { }
tokens = [ ]
tm = { }


# Class of StatementList: maintain a list of Statement objects

class StatementList( object ):
	def __init__(self):
		self.statementList = []

	def addStatement(self, statement):
		self.statementList.append(statement)

	def __str__(self):
		printStr = ''
		for statement in self.statementList:
			printStr += str(statement)
		return printStr

	def meaning(self, state):
		for section in self.statementList:
			section.meaning(state)
		return state

#iterates through each statement in statementList and calls tipe()
	def tipe (self, tm):
		for statement in self.statementList:
			statement.tipe(tm)
		return tm

# Statement class and subclasses

class Statement( object ):
	def __str__(self):
		return ""


class Assignment( Statement ):
	def __init__(self, identifier, expression):
		self.identifier = str(identifier)
		self.expression = expression

	def __str__(self):
		return "= " + self.identifier + " " + str(self.expression) + "\n"

	def meaning(self, state):
		state[self.identifier] = self.expression.meaning(state)
		return state

# calls tipe() on expression
	def tipe(self, tm):
		tp = self.expression.tipe(tm)
#if empty, gives error
		if tp == "":
			error("Type Error: variable undefined")
#if not in tm, adds it with type as value
		if self.identifier not in tm:
			tm[self.identifier] = tp
			print(str(self.identifier) + " " + str(tp))

		else:
#if tupe does not match, gives error
			if tm[self.identifier] != tp:
				error("Type Error: " + str(tm[self.identifier]) + " = " + tp + "!")



class WhileStatement( Statement ):
	def __init__(self, expression, block):
		self.expression = expression
		self.block = block

	def __str__(self):
		return "while " + str(self.expression) + "\n" + str(self.block) + "endwhile\n"

	def meaning(self, state):
		while self.expression.meaning(state) == True:
			self.block.meaning(state)
		return state

#calls tipe() on expression and block
	def tipe (self, tm):
		self.expression.tipe(tm)
		self.block.tipe(tm)

class IfStatement( Statement ):
	def __init__(self, expression, ifBlock, elseBlock):
		self.expression = expression
		self.ifBlock = ifBlock
		self.elseBlock = elseBlock

	def __str__(self):
		return "if " + str(self.expression) + "\n" + str(self.ifBlock) + "else\n" + str(self.elseBlock) + "endif\n"

	def meaning(self, state):
		if self.expression.meaning(state) == True:
			self.ifBlock.meaning(state)
			return state
		elif self.elseBlock is not '':
			self.elseBlock.meaning(state)
			return state
		return state

#calls tipe() on self, if it is empty gives error
	def tipe(self, tm):
		tp = self.expression.tipe(tm)
		if tp == "":
			error("Type Error: variable undefined")


# Expression class and subclasses

class Expression( object ):
	def __str__(self):
		return ""


class BinaryExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right

	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)

	def meaning(self,state):
        #obtains left and right expressions
		left = self.left.meaning(state)
		right = self.right.meaning(state)

        #returns operations on left and right
		if self.op == '+':
			return left + right
		elif self.op == '-':
			return left - right
		elif self.op == '*':
			return left * right
		elif self.op == '/':
			return left / right

        #evaulates relationals for left and right expressions
		elif re.match(Lexer.relational, self.op):
			switcher = {
			">": left > right,
			"<": left < right,
			">=": left >= right,
			"<=:": left <= right,
			"==": left == right,
			"!=": left != right,
			}
			return switcher.get(self.op, "invalid relation")

        #evaluates and & or for left and right expressions
		elif self.op in ["and", "or"]:
			switcher = {
			"and": left and right,
			"or": left or right
			}
			return switcher.get(self.op, "invalid relation")

#calls tipe() on left and right expressions
	def tipe(self, tm):
		left = self.left.tipe(tm)
		right = self.right.tipe(tm)

#if arithmetic operations are used, and tipe is not number, gives Error
#else returns number
		if self.op == "+" or self.op == "-" or self.op == "/" or self.op == "*":
			if left != "number" or right != "number":
				error("Type Error: " + str(left) + " = " + str(right) + "!")
			return "number"

#if relational operators are used, and tipes of left ane right are not equal, gives Error
#else returns boolean
		if self.op == "==" or self.op == ">=" or self.op == "<=" or self.op == "!=" or self.op == ">" or self.op == "<":
			if left != right:
				error("Type Error: " + str(left) + " = " + str(right) + "!")
			return "boolean"

#if and or or are used and left and right are not boolean, gives error
#else returns number
		if self.op == "and" or self.op == "or":
			if left != "boolean" or right != "boolean":
				error("Type Error: " + str(left) + " = " + str(right) + "!") #Not sure what to return
			return "number"



class Number( Expression ):
	def __init__(self, value):
		self.number = int(value)

	def __str__(self):
		return str(self.number)

	def meaning(self, state):
        #gets integer value of a number
        #incase its written as a string
		return int(self.number)

#returns number as tipe for a number
	def tipe(self,tm):
		return "number"

class VarRef( Expression ):
	def __init__(self, value):
		self.relation = value

	def __str__(self):
		return str(self.relation)

	def meaning(self, state):
        #returns relation as a key in state dictionary
		return (state[self.relation])

#if value of varref not in tm, gives Error
#else returns key
	def tipe(self, tm):
		if self.relation not in tm:
			error("Type Error: " +  str(self.relation) + " referenced before defined!")
		return tm[self.relation]



class String( Expression ):
	def __init__(self, value):
		self.string = value

	def __str__(self):
		return str(self.string)

	def meaning(self):
        #returns the string
		return self.string

# Lexer, a private class that represents lists of tokens from a Gee

class Lexer :
	special = r"\(|\)|\[|\]|,|:|;|@|~|;|\$"
	relational = "<=?|>=?|==?|!="
	arithmetic = "\+|\-|\*|/"
	#char = r"'."
	string = r"'[^']*'" + "|" + r'"[^"]*"'
	number = r"\-?\d+(?:\.\d+)?"
	literal = string + "|" + number
	#idStart = r"a-zA-Z"
	#idChar = idStart + r"0-9"
	#identifier = "[" + idStart + "][" + idChar + "]*"
	identifier = "[a-zA-Z]\w*"
	lexRules = literal + "|" + special + "|" + relational + "|" + arithmetic + "|" + identifier


	def __init__( self, text ) :
		self.tokens = re.findall( Lexer.lexRules, text )
		self.position = 0
		self.indent = [ 0 ]

	def peek( self ) :
		if self.position < len(self.tokens) :
			return self.tokens[ self.position ]
		else :
			return None

	def next( self ) :
		self.position = self.position + 1
		return self.peek( )

	def __str__( self ) :
		return "<Lexer at " + str(self.position) + " in " + str(self.tokens) + ">"



def parse( text ) :
	global tokens
	tokens = Lexer( text )
	stmtlist = parseStmtList( )
	return stmtlist

#def type(stateList):
#	""" type function creates a dictionary that calls tipe() on the dicionary
#	and prints dictionary tm in correct format """

#	tmdict = {}
#	tm_dict = stateList.tipe(tmdict)
#	for key, value in tm_dict.items():
#		print( str(key) + " " + str(value))
#	return


def state(stateList):
    """state function creates a dictionary for the state
    and calls meaning() and semantic_format() on it"""

    statedict = {} #state dictionary
    state_dict = stateList.meaning(statedict) #calls meaning on dictionary
    semantics_final = semantic_format(state_dict) #calls on semantic to format output
    print(semantics_final) #prints output
    return


def semantic_format(statedict):
    """semantic format function creates {<ident, state>} format for output"""

    final = "" #empty string
    for k, v in statedict.items(): #for each key and its value in state dictionary
        final += ", <" +str(k) + ", " + str(v) + ">" #add ", <key, value>" to string
    final = final[2:] #omits first space and comma
    return "{" + final +"}" #returns string with brackets


def parseStmtList(  ):
	""" stmtList =  {  statement  } """

	tok = tokens.peek( )
	statementList = StatementList()
	while tok not in [None ,"~"]: #have to account for undent that signals an end of block
		statement = parseStatement()
		statementList.addStatement(statement)
		tok = tokens.peek()
	return statementList


def parseStatement():
	"""statement = ifStatement |  whileStatement  |  assignment"""

	tok = tokens.peek()
	if debug: print ("Statement: ", tok)
	if tok == "if":
		return parseIfStmt()
	elif tok == "while":
		return parseWhileStmt()
	elif re.match(Lexer.identifier, tok):
		return parseAssignment()
	error("error msg: statement")
	return


def parseAssignment():
	"""assign = ident "=" expression  eoln"""

	identifier = tokens.peek()
	if debug: print ("Assign statement: ", left)
	if tokens.next() != "=":
		error("error msg: assignment")
	tokens.next()
	exp = expression()
	tok = tokens.peek()
	if tok != ";":
		error("error msg: assignment")
	tokens.next()
	return Assignment(identifier, exp)


def parseIfStmt():
	"""ifStatement = "if" expression block   [ "else" block ] """

	tok = tokens.next()
	if debug: print ("If statement: ", tok)
	expr = expression()
	ifBlock = parseBlock()
	elseBlock = ''
	if tokens.peek() == "else":
		tok = tokens.next()
		if debug: print ("Else statement: ", tok)
		elseBlock = parseBlock()
	return IfStatement(expr, ifBlock, elseBlock)



def parseWhileStmt():

	"""whileStatement = "while"  expression  block"""
	tok = tokens.next()
	if debug: print ("While statement: ", tok)
	expr = expression()
	block = parseBlock()
	return WhileStatement(expr, block)


def parseBlock():
	"""block = ":" eoln indent stmtList undent"""

	tok = tokens.peek()
	if debug: print ("Block: ", tok)
	# Check to make sure each of the appropriate terminal tokens exist and are in the right place
	if tok != ":":
		error("error msg: block")
	tok = tokens.next()
	if tok != ";":
		error("error msg: block")
	tok = tokens.next()
	if tok != "@":
		error("error msg: block")
	tok = tokens.next()
	stmtList = parseStmtList()
	if tokens.peek() != "~":
		error("error msg: block")
	tokens.next()
	return stmtList


def expression():
	"""expression = andExpr { "or" andExpr }"""

	tok = tokens.peek( )
	if debug: print ("expression: ", tok)
	left = andExpr( )
	tok = tokens.peek( )
	while tok == "or":
		tokens.next()
		right = andExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def andExpr():
	"""andExpr    = relationalExpr { "and" relationalExpr }"""
	tok = tokens.peek( )
	if debug: print ("andExpr: ", tok)
	left = relationalExpr( )
	tok = tokens.peek( )
	while tok == "and":
		tokens.next()
		right = relationalExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def relationalExpr():
	"""relationalExpr = addExpr [ relation addExpr ]"""

	tok = tokens.peek( )
	if debug: print ("relationalExpr: ", tok)
	left = addExpr( )
	tok = tokens.peek( )
	while re.match(Lexer.relational, tok):
		tokens.next()
		right = addExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def addExpr( ):
	""" addExpr    = term { ('+' | '-') term } """
	tok = tokens.peek( )
	if debug: print ("addExpr: ", tok)
	left = term( )
	tok = tokens.peek( )
	while tok == "+" or tok == "-":
		tokens.next()
		right = term( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def term( ):
	""" term    = factor { ('*' | '/') factor } """

	tok = tokens.peek( )
	if debug: print ("Term: ", tok)
	left = factor( )
	tok = tokens.peek( )
	while tok == "*" or tok == "/":
		tokens.next()
		right = factor( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def factor( ):
	"""factor  = number | string | ident |  "(" expression ")" """

	tok = tokens.peek( )
	if debug: print ("Factor: ", tok)
	if re.match(Lexer.number, tok):
		expr = Number(tok)
		tokens.next( )
		return expr
	elif re.match(Lexer.string, tok):
		expr = String(tok)
		tokens.next()
		return expr
	elif re.match(Lexer.identifier, tok):
		expr = VarRef(tok)
		tokens.next()
		return expr
	if tok == "(":
		tokens.next( )  # or match( tok )
		expr = expression( )
		tokens.peek( )
		tok = match(")")
		return expr
	error("error msg: factor()")
	return


def match(matchtok):
	tok = tokens.peek( )
	if (tok != matchtok): error("error msg: match()")
	tokens.next( )
	return tok

def error( msg ):
	sys.exit(msg)

def mklines(filename):
	inn = open(filename, "r")
	lines = [ ]
	pos = [0]
	ct = 0
	file = ""
	for line in inn:
		file += line
		ct += 1
		line = line.rstrip( )+";"
		line = delComment(line)
		if len(line) == 0 or line == ";": continue
		indent = chkIndent(line)
		line = line.lstrip( )
		if indent > pos[-1]:
			pos.append(indent)
			line = '@' + line
		elif indent < pos[-1]:
			while indent < pos[-1]:
				del(pos[-1])
				line = '~' + line
		#print (ct, "\t", line)
		lines.append(line)
	# print len(pos)
	undent = ""
	#print(file)
	for i in pos[1:]:
		undent += "~"
	lines.append(undent)
	inn.close()
	return lines

def chkIndent(line):
	ct = 0
	for ch in line:
		if ch != " ": return ct
		ct += 1
	return ct

def delComment(line):
	pos = line.find("#")
	if pos > -1:
		line = line[0:pos]
		line = line.rstrip()
	return line




def main():
	global debug


	ct = 0

	for opt in sys.argv[1:]:

		if opt[0] != "-": break

		ct = ct + 1

		if opt == "-d": debug = True

	if len(sys.argv) < 2+ct:

		print ("Usage:  %s filename" % sys.argv[0])

		return


	original = parse("".join(mklines(sys.argv[1+ct])))

	#calls type on parsed grammar
	tm_dict = {}
	type = original.tipe(tm_dict)
	return



main()
