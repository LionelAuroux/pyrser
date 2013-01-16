from pprint import pprint
import traceback
import jinja2


def jinja_getattr(self, sName):
    try:
        return self._TemplateReference__context[sName]
    except:
        print
        pprint(self._TemplateReference__context['tree'])
        raise Exception("Undefined macro : %s" % sName)


def c_ast_to_c(oTree, sTemplateName, sTemplateFolder="templates"):
    oEnv = jinja2.Environment(
        loader=jinja2.PackageLoader('cnorm_to_c', sTemplateFolder))
    oTemplate = oEnv.get_template(sTemplateName,
                                  globals={'getattr': jinja_getattr,
                                           'tree': oTree})
    try:
        sGeneratedCode = oTemplate.render(oTree)
    except jinja2.exceptions.UndefinedError as exception:
        raise Exception(
            "Something was possibly wrong with the tree. Check it and the traceback : %s." % exception)
        print
        pprint(oTree)
        print traceback.format_exc()
        exit(1)
    return sGeneratedCode
