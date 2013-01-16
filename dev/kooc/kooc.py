from cnorm.declaration import CDeclaration
from pyrser.grammar import Grammar


class Kooc(CDeclaration):
    """
    type_specifier ::=   CDeclaration::type_specifier
                       | class_specifier
                       | callback
    ;

    class_specifier ::= "class" #type("__class__") [#identifier :type_specifier]?
                        [extend]?
                        '{'
                            [
                              [visibility ':']?
                              [
                                @push_at("declarations") declaration ';'
                              ]+
                              #visibility
                            ]+
                        '}'
    ;

    extend ::= [visibility]? #identifier [',' #identifier]*
    ;

    visibility ::= ["public" | "private" | "protected"] :visibility
    ;

    callback ::= "@callback" #identifier ';'
    ;
    """
    def __init__(self):
        CDeclaration.__init__(self)
        Kooc.__init__(self, CDeclaration, CDeclaration.__doc__, globals())
