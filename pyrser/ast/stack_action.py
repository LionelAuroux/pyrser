from pyrser.ast.walk import *

class Checker:
    def __init__(self, hook_fun, user_data):
        self.dict_action = {}
        self.states = {}
        self.events = {}
        self.depths = {}
        self.sibling_depths = []
        self.captures = {}
        self.current_node = None
        self.hook_fun = hook_fun
        self.user_data = user_data

    def check_event_and_action(self, cur_pos, lsevents, stack):
        class Abort(Exception):
            pass

        global pure_action_map
        for ids, stmt_pattern in stack:
            block_id, stmt_id = ids
            for stackid, action_stack in enumerate(stmt_pattern):
                idx_loc = 0
                try:
                    for action in action_stack:
                        relat_loc = cur_pos + idx_loc
                        #TODO: optimize
                        try:
                            ev = lsevents[relat_loc]
                            # thru events
                            if action[0] not in pure_action_map:
                                res = ev.check_event(action, self)
                                if not res:
                                    for all_loc in self.dict_action.keys():
                                        for k in list(self.dict_action[all_loc].keys()):
                                            del_id = (cur_pos, block_id, stmt_id, stackid)
                                            if k == del_id:
                                                del self.dict_action[all_loc][k]
                                    raise Abort()
                                idx_loc += 1
                        except IndexError as ev:
                            pass
                        except Abort as e:
                            raise e
                        except Exception as e:
                            raise TypeError("c'est la merde %s" % str(e))
                        # thru actions
                        if action[0] in pure_action_map:
                            # an action always after a thru events and attach to his position
                            relat_loc -= 1
                            uniq = (cur_pos, block_id, stmt_id, stackid)
                            if relat_loc not in self.dict_action:
                                self.dict_action[relat_loc] = {}
                            if uniq not in self.dict_action[relat_loc]:
                                self.dict_action[relat_loc][uniq] = []
                            self.dict_action[relat_loc][uniq].append(action)
                except Abort as e:
                    pass
        #if cur_pos not in self.dict_action:
        #    print("Nothing to do at %d" % cur_pos)
        if cur_pos in self.dict_action:
            self.current_node = lsevents[cur_pos].node
            self.current_depth = lsevents[cur_pos].depth
            for uid in sorted(self.dict_action[cur_pos].keys()):
                last_action = True
                for action in self.dict_action[cur_pos][uid]:
                    if last_action:
                        last_action = pure_action_map[action[0]](action, self, uid)
                    if not last_action:
                        for all_loc in self.dict_action.keys():
                            for k in list(self.dict_action[all_loc].keys()):
                                if k == uid:
                                    del self.dict_action[all_loc][k]

def match(tree, compile_psl, hooks, user_data):
    #TODO: not complete
    from pyrser.ast.walk import walk
    from pyrser.parsing.node import normalize

    tree = normalize(tree)
    stack = []
    for block in compile_psl:
        stack += [block.get_stack_action()]
    chk = Checker(hooks, user_data)
    res = False

    class FakeList:
        def __init__(self, gen):
            self.gen = gen

        def __iter__(self):
            self.cache = []
            self.idx = 0
            return self

        def __next__(self):
            ev = self.gen.send(None)
            self.cache.append(ev)
            self.idx += 1
            return ev

        def __getitem__(self, k):
            if k not in self.cache and k > self.idx:
                while self.idx < k:
                    self.cache.append(self.gen.send(None))
                    self.idx += 1
            return self.cache[k]

    #ls = FakeList(walk(tree))
    ls = get_events_list(tree)
    for idx, ev in enumerate(ls):
        chk.check_event_and_action(idx, ls, stack)

def get_events_list(tree) -> []:
    """
    For debug purpose: provide the list of all events of tree
    """
    from pyrser.ast.walk import walk

    res = []
    try:
        g = walk(tree)
        while True:
            ev = g.send(None)
            res.append(ev)
    except StopIteration as e:
        return res
    return None

##############

def action_set_event(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    evid = (action[1], block_id, stmt_id)
    if evid not in chk.events:
        chk.events[evid] = []
    chk.events[evid].append(chk.current_depth)
    return True

def action_set_named_event(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    evid = (action[1], block_id, stmt_id)
    if evid not in chk.events:
        chk.events[evid] = []
    chk.events[evid].append(chk.current_depth)
    return True

def action_check_attr_len(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    if hasattr(chk.current_node, '__dict__') and len(vars(chk.current_node)) == action[1]:
        return True
    return False

def action_check_len(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    if hasattr(chk.current_node, '__len__') and len(chk.current_node) == action[1]:
        return True
    return False

def action_no_event(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    if len(chk.events) == 0:
        return True
    return False

def action_check_event(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    nb_match = []
    for ev in action[1]:
        evid = (ev, block_id, stmt_id)
        if evid in chk.events:
            nb_match.append(chk.events[evid][0])
    if len(nb_match) == len(action[1]) and nb_match.count(nb_match[0]) == len(nb_match):
        return True
    return False

def action_check_clean_event(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    nb_match = []
    for ev in action[1]:
        evid = (ev, block_id, stmt_id)
        if evid in chk.events:
            # logically the first element is the deeper
            nb_match.append(chk.events[evid][0])
    # we unsure that all event come from the same depth
    if len(nb_match) == len(action[1]) and nb_match.count(nb_match[0]) == len(nb_match):
        for ev in action[1]:
            evid = (ev, block_id, stmt_id)
            chk.events[evid].pop(0)
            if len(chk.events[evid]) == 0:
                del chk.events[evid]
        return True
    return False

def action_capture(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    if block_id not in chk.captures:
        chk.captures[block_id] = {}
    if stmt_id not in chk.captures[block_id]:
        chk.captures[block_id][stmt_id] = {}
    chk.captures[block_id][stmt_id][action[1]] = chk.current_node
    return True

def action_capture_pair_first(action, chk, uid):
    # nearest so called after action_capture_pair_second
    cur_pos, block_id, stmt_id, stackid = uid
    if block_id not in chk.captures:
        return False
    if stmt_id not in chk.captures[block_id]:
        return False
    node = chk.captures[block_id][stmt_id][action[1]][-1]
    pair = (chk.first, node)
    if pair in chk.captures[block_id][stmt_id][action[1]]:
        return True
    chk.captures[block_id][stmt_id][action[1]][-1] = pair
    return True

def action_capture_pair_second(action, chk, uid):
    # deepest so called before action_capture_pair_first
    cur_pos, block_id, stmt_id, stackid = uid
    if block_id not in chk.captures:
        chk.captures[block_id] = {}
    if stmt_id not in chk.captures[block_id]:
        chk.captures[block_id][stmt_id] = {}
    if action[1] not in chk.captures[block_id][stmt_id]:
        chk.captures[block_id][stmt_id][action[1]] = []
    chk.captures[block_id][stmt_id][action[1]].append(chk.current_node)
    return True

def action_store_depth(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    depthid = (action[1], block_id, stmt_id)
    chk.depths[depthid] = chk.current_depth
    return True

def action_check_depth(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    depthid = (action[1], block_id, stmt_id)
    d = action[2]
    ismin = action[3]
    if depthid not in chk.depths:
        return False
    if ismin:
        if chk.depths[depthid] - chk.current_depth >= d:
            del chk.depths[depthid]
            return True
    else:
        if chk.depths[depthid]  - chk.current_depth == d:
            del chk.depths[depthid]
            return True
    return False

def action_store_sibling_depth(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    sibling_depthid = (action[1], block_id, stmt_id, chk.current_depth)
    chk.sibling_depths.append(sibling_depthid)
    return True

def action_check_sibling_depth(action, chk, uid):
    def match_list(ls, pattern):
        return [it for it in ls if len([it2 is None or (type(it2) is list and it[idx] in it2) or it[idx] == it2 for idx, it2 in enumerate(pattern)]) == len(it)]
    cur_pos, block_id, stmt_id, stackid = uid
    sibling_pattern = (action[1], block_id, stmt_id, None)
    # get all matching depths tuples
    lsres = match_list(chk.sibling_depths, sibling_pattern)
    # get sublist of continuous regd of depth matching action[1]
    continuous_sublist = []
    for idx in range(len(lsres)):
        if lsres[idx][0] == action[1][0]:
            subl = lsres[idx:idx + len(action[1])]
            if [it[0] for it in subl] == action[1]:
                subdepth = [it[3] for it in subl]
                if subdepth.count(subdepth[0]) == len(subdepth):
                    continuous_sublist.append(subl)
    if len(continuous_sublist) > 0:
        # clean sibling_depths
        for it in continuous_sublist:
            for it2 in it:
                chk.sibling_depths.remove(it2)
        return True
    return False

def action_hook(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    funname = action[1]
    if funname not in chk.hook_fun:
        raise TypeError("Can't find %s in Checker" % funname)
    capt_dict = {}
    if block_id in chk.captures and stmt_id in chk.captures[block_id]:
        capt_dict = chk.captures[block_id][stmt_id]
    chk.hook_fun[funname](capt_dict, chk.user_data)
    return True

pure_action_map = {
    'set_event': action_set_event,
    'set_named_event': action_set_named_event,
    'check_attr_len': action_check_attr_len,
    'check_len': action_check_len,
    'no_event': action_no_event,
    'check_event': action_check_event,
    'check_clean_event': action_check_clean_event,
    'capture': action_capture,
    'capture_pair_first': action_capture_pair_first,
    'capture_pair_second': action_capture_pair_second,
    'store_depth': action_store_depth,
    'check_depth': action_check_depth,
    'store_sibling_depth': action_store_sibling_depth,
    'check_sibling_depth': action_check_sibling_depth,
    'hook': action_hook
}
