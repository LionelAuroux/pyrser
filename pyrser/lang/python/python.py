python =\
    {
        'builtins':
        {'identifier': 'readIdentifier', 'num': 'readInteger', 'string': 'readCString', 'cchar': 'readCChar', 'char': 'readAChar', 'space': 'readWs', 'end': 'readUntilEOF', 'empty': 'readEOF', 'super': 'super', 'false': 'false', 'readThisChar': 'readChar', 'readThisText': 'readText', 'range': 'readRange', 'notIgnore': 'notIgnore', 'resetIgnore': 'resetIgnore'},

        'not': {'!': 'negation', '~': 'complement'},

        'multiplier': {'?': 'zeroOrOne', '+': 'oneOrN', '*': 'zeroOrN', '[]': 'expression', '{}': 'n'},

        'keyword': {'and': 'and', 'object': 'self'},
        'accessOperator': '.',
        'alt': 'alt',
        'baseParserMethod': 'Parsing.oBaseParser',
        'indent': 15,
        'file_extension': '.py'
    }

from imp import load_source


def pythonPostGeneration(sModuleName, sFile, sToFile, sGrammar, oInstance):
    #	    try:
    oModule = load_source(sModuleName, sToFile)
#	    except:
#	      self.error(\
#		'Generated source is wrong, please report on redmine.lse.epita.fr')
#	      exit(0)

    if sGrammar != None:
        try:
            oClass = getattr(oModule, sGrammar)
            return oClass
        except:
            oInstance.error('No grammar called "%s" in %s' % (sGrammar, sFile))
            exit(0)
    return oModule
