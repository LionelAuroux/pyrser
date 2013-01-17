from pyrser import node
from pyrser import parsing
from pyrser import trace
import pprint


class GenericHook(object):
##### Hooks:
    def true_hook(self, node_):
        """
        #true :
        Returns True.
        Usefull for to mock a hook for debug.
        """
        return True

    def false_hook(self, node_):
        """
        #false :
        Returns False.
        Usefull for to mock a hook for debug.
        """
        return False

    def dump_hook(self, node_):
        """
        #dump :
        Dump the content of the current node.
        """
        pprint.pprint(node_)
        return True

    def print_hook(self, node_, str_):
        """
        #print(str) :
        Print str.
        """
        print(str_)
        return True

    def id_hook(self, node_, name):
        """
        #id :
        Print id of the local node_.
        """
        print("[%s] - %s" % (name, id(node_)))
        return True

    def exit_hook(self, node_):
        """
        #exit :
        Exit the processus.
        """
        exit(1)

    def traceHook(self, node_):
        """
        Trace the function called until now.
        """
        trace.rule_stack_trace(self)
        return True

    def slideHook(self, node_, field, subkey=None):
        """
        #slide(field) :
        The whole content of node_ will be put in a new node, stored at field.
        """
        if subkey is not None:
            node_ = node_[subkey]
        node.slide(node_, field)
        return True

##### Wrappers:
    def _Wrapper(self, rule, node_):
        """
        @_ :
        The next node used as local for the following rules will be the
        current local node.
        """
        node.next_is(node_, node_)
        result = rule()
        node.next_clean(node_)
        return result

    def nextWrapper(self, rule, node_, field, clean=False):
        """
        @node.next(field) :
        The next node used as local for the following rules is created and
        added under the field key.
        If the rule wrapped fails the node will be delete.
        """
        node.next(node_, field)
        result = rule()
        if clean is True and result is False:
            del node_[field]
        node.next_clean(node_)
        return result

    def push_atWrapper(self, rule, node_, field):
        """
        @push_at(field) :
        The next node used as local is created and add to a list, at field
        if rule succeed.
        """
        sub_node = {}
        node.next_is(node_, sub_node)
        result = rule()

        if result is True:
            if field not in node_:
                node_[field] = []
            node_[field].append(sub_node)

        node.next_clean(node_)
        return result

    def push_capture_atWrapper(self, rule, node_, field, sCapture):
        """
        @push_capture_at(field, sCapture) :
        If the wrapped rule succeeds the captured text stored at sCapture key
        will be push at the field list.
        """
        node.next_is(node_, node_)
        result = rule()

        if result is True and sCapture in node_:
            if not field in node_:
                node_[field] = []
            node_[field].append(node_[sCapture])
            del node_[sCapture]

        node.next_clean(node_)
        return result

    def slideWrapper(self, rule, node_, field, subkey=None):
        """
        @slide(field) :
        If the rule succeed, the whole content of node_ will be put in a new
        node, stored at field.
        """
        result = rule()
        if result is True:
            if subkey is not None:
                node_ = node_[subkey]
            node.slide(node_, field)
        return result

    def continueWrapper(self, rule, node_, text=None):
        """
        @continue(text?) :
        This wrapper should be used to keep trace of errors.
        If the wrapped rule fail, an execution stack will be printed, an
        Exception raised and the processus will be exit.
        """
        trace_ = trace.set_stack_trace(self)
        result = rule()
        if result is False:
            trace.result_stack_trace(trace_)
            if text is not None:
                raise Exception(text)
                exit(1)
            raise Exception
            exit(1)
        return result

    def traceWrapper(self, rule, node_, name):
        """
        @trace(text?) :
        Print the rules, hooks and wrappers called by rule, and their result.
        """
        trace_ = trace.set_stack_trace(self)
        result = rule()
        trace.result_stack_trace(trace_)
        return result

    def consumedWrapper(self, rule, node_, name):
        """
        @consumed(name) :
        Will display the text consumed by rule if it succeeds.
        """
        parsing.Parsing.oBaseParser.setTag(name)
        result = rule()
        if result is True:
            print ("Consumed [%s] - %s" %
                  (name, parsing.Parsing.oBaseParser.getTag(name)))
        return result
