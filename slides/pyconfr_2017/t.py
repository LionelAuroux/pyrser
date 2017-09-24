
import ast
class Allnames(ast.NodeVisitor):
    def visit_Module(self, node):
        self.names = {}
        self.generic_visit(node)
        print(sorted(self.names.keys()))

    def visit_Name(self, node):
        self.names[node.id] = node

x = Allnames()
t = ast.parse('d[x] += v[y, x]')
x.visit(t)
