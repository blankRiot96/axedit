import ast

src = """

def foo():
    '''asldka;lsdk'''
"""

print(ast.dump(ast.parse(src), indent=4))
