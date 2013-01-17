from sys import settrace
from traceback import extract_stack


def rule_stack_trace(oInstance):
    """
    Trace the rules, hook and wrapper calls.
    """
    nDepth = 1
    for iCall in extract_stack():
        for iManglingEnd in ['Rule', 'Wrapper', 'Hook']:
            if iCall[2].endswith(iManglingEnd):
                sFile = iCall[0]
                if sFile == '<string>':
                    sFile = 'generated grammar'
                print("%s+|In %s line %s: %s::%s (%s)" %\
                    (nDepth * '-',
                      sFile,
                      iCall[1],
                      oInstance.__class__.__name__,
                      iCall[2],
                     iManglingEnd))
                if iManglingEnd == 'Rule':
                    nDepth += 1


def set_stack_trace(oInstance):
    oTrace = Trace(oInstance)
    settrace(oTrace)
    return oTrace


def result_stack_trace(oTrace):
    """
    Trace the rules, hook and wrapper calls with their result.
    """
    settrace(lambda x, y, z: None)
    for iCall in oTrace.lCalled:
        sFile = iCall['file']
        if sFile == '<string>':
            sFile = 'generated grammar'
        if not isinstance(iCall['return'], type(True)):
            iCall['return'] = None
        print("%s+|In %s line %s: %s::%s (%s) => [%s]"\
            % (iCall['depth'] * '-', sFile, iCall['line'], iCall['grammar'], iCall['name'], iCall['type'], iCall['return']))


class Trace(object):
    def __init__(self, oGrammar):
        self.lCalled = []
        self.nDepth = 1
        self.sGrammarName = oGrammar.__class__.__name__

    def __call__(self, oFrame, sEvent, oArg):
        sFuncName = oFrame.f_code.co_name
        for iManglingEnd in ['Rule', 'Wrapper', 'Hook']:
            if sFuncName.endswith(iManglingEnd):
                if sEvent == 'call':
                    self.lCalled.append({'name': sFuncName, 'depth': self.nDepth, 'grammar': self.sGrammarName, 'line': oFrame.f_lineno, 'file': oFrame.f_code.co_filename, 'type': iManglingEnd})
                    self.nDepth += 1
                elif sEvent == 'return':
                    nCount = len(self.lCalled) - 1
                    while nCount >= 0:
                        if self.lCalled[nCount]['name'] == sFuncName:
                            self.lCalled[nCount]['return'] = oArg
                        nCount -= 1
                    self.nDepth -= 1
                return self.__call__
