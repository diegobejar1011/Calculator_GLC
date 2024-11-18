from flask import Flask, jsonify, render_template, request
from lark import Lark, Tree, Token

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
        return jsonify({'treeJson': treeJson})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000") 