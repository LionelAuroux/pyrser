from expression import Expression
from statement import Statement
from declaration import Declaration

oRoot = {}
print Declaration().parse('int main(){}', oRoot, 'declaration')
