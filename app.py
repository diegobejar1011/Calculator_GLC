from flask import Flask, jsonify, render_template, request
from lark import Lark, Tree, Token
import ply.lex as lex

app = Flask("Calculator")

grammar = """
?start: expr
?expr: term
     | expr "+" term   -> add
     | expr "-" term   -> sub
?term: factor
     | term "*" factor -> mul
     | term "/" factor -> div
?factor: NUMBER        -> number
       | "(" expr ")"  -> parens
NUMBER: /\d+(\.\d+)?/
%ignore " "            // Ignorar espacios en blanco
"""

parser = Lark(grammar, start='start', parser='lalr')

tokens = (
    'NUMBER',
    'DECIMAL',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE'
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

def t_DECIMAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Carácter no reconodico: {t.value[0]}")
    t.lexer.skip(1)
    
lexer = lex.lex()

def tokenize(expression):
    token_list = []
    int_count = 0
    operator_count = 0
    
    lexer.input(expression)
    for tok in lexer:
        token_list.append({
            'type': tok.type,
            'value': tok.value
        })
        if tok.type == 'NUMBER':
            int_count += 1
        elif tok.type in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']:
            operator_count += 1
            
    return {
        "tokens": token_list,
        "integer_count": int_count,
        "operator_count": operator_count
    }


def toJson(tree):
    rename_map = {
        "add": "+",
        "sub": "-",
        "mul": "*",
        "div": "/",
        "number": "n"
    }
    if isinstance(tree, Token):
        return {"name": tree.value} 
    elif isinstance(tree, Tree):
        node_name = rename_map.get(tree.data, tree.data)
        return {
            "name": node_name,
            "children": [toJson(child) for child in tree.children]
        }

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        expression = request.form['expression']
        tree = parser.parse(expression)
        treeJson = toJson(tree) 
        resolveLex = tokenize(expression)
        return jsonify({'treeJson': treeJson}, resolveLex)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000") 