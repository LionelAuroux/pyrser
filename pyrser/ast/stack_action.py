from pyrser.ast.walk import *

class Checker:
    def __init__(self, hook_fun, user_data):
        # for events to throw at certain position
        self.dict_action = {}
        # block scope
        self.named_events = {}
        self.postpone_clean = {}
        # block/stmt scope
        self.captures = {}
        self.events = {}
        self.depths = {}
        self.sibling_depths = []

        self.childrelat = {}
        self.event_chr = {} #event childrelat

        # internal state
        self.current_node = None
        self.current_depth = None
        self.last_depth = None
        self.current_width = None
        self.last_width = None
        self.current_parent = None
        # user data
        self.hook_fun = hook_fun
        self.user_data = user_data

    def is_parentof(self, idparent, idchild) -> bool:
        def get_parent_of(childrelat, idchild):
            if idchild in self.childrelat:
                for parent in self.childrelat[idchild]:
                    print("CHECK")
                    yield parent
                    print("UP")
                    yield from get_parent_of(self.childrelat, parent)
            #elif idchild == self.current_parent:
            #    yield idchild
        print("ancestor %d parent of %d" % (idparent, idchild))
        if idparent == idchild:
            print("found")
            return True
        for parent in get_parent_of(self, idchild):
            print("check parent %d" % (parent))
            if parent == idparent:
                print("found")
                return True
        return False

    def check_event_and_action(self, cur_pos, lsevents, stack):
        class Abort(Exception):
            pass

        global pure_action_map
        for stmt in stack:
            for ids, stmt_pattern in stmt:
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
                                    #
                                    if ev.childrelat is not None:
                                        idchild = ev.childrelat[0]
                                        idparent = ev.childrelat[1]
                                        print("EV CHILD %d HAS PARENT %d" % (idchild, idparent))
                                        # literals have always the same id, so they have many parents
                                        if idchild not in self.childrelat:
                                            self.childrelat[idchild] = []
                                        # called many time for the same node (depend of stack)
                                        if idparent not in self.childrelat[idchild]:
                                            self.childrelat[idchild].append(idparent)
                                        self.current_parent = ev.childrelat[1]
                                    #
                                    res = ev.check_event(action, self)
                                    print("POS %d %s - %s" % (relat_loc, action[0], res))
                                    if not res:
                                        for all_loc in self.dict_action.keys():
                                            for k in list(self.dict_action[all_loc].keys()):
                                                del_id = (cur_pos, block_id, stmt_id, stackid)
                                                if k == del_id:
                                                    print("DEL %s" % repr(k))
                                                    print("\t%s" % repr(self.dict_action[all_loc][k]))
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
        if cur_pos in self.dict_action:
            self.current_node = lsevents[cur_pos].node
            self.current_depth = lsevents[cur_pos].depth
            self.current_width = lsevents[cur_pos].width
            if self.last_depth is not None and self.last_depth > self.current_depth:
                # go up,
                print("CHILD RELAT %s" % (self.childrelat))
                print("CURRENT PARENT %d" % (self.current_parent))
                pass
            if self.last_depth is not None and self.last_depth < self.current_depth:
                # go down, clean stored depths >= current_depth if any
                print("CHILD RELAT %s" % (self.childrelat))
                print("CURRENT PARENT %d" % (self.current_parent))
                pass
            self.last_depth = self.current_depth
            self.last_width = self.current_width
            for uid in sorted(self.dict_action[cur_pos].keys()):
                last_action = True
                for action in self.dict_action[cur_pos][uid]:
                    if last_action:
                        last_action = pure_action_map[action[0]](action, self, uid)
                        print("POS2 %d %s - %s" % (cur_pos, action[0], last_action))
                    if not last_action:
                        for all_loc in self.dict_action.keys():
                            for k in list(self.dict_action[all_loc].keys()):
                                if k == uid:
                                    print("DEL2 %s" % repr(k))
                                    if self.captures:
                                        print("CAPTURES? %s" % repr(self.captures))
                                    print("\t%s" % repr(self.dict_action[all_loc][k]))
                                    del self.dict_action[all_loc][k]

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
        chk.event_chr[evid] = []
    chk.events[evid].append(chk.current_depth)
    chk.events[evid].append(chk.current_depth)
    return True

def action_set_named_event(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    evid = (action[1], block_id)
    chk.named_events[evid] = chk.current_depth
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

def action_check_clean_event_and(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    nb_match = []
    for ev in action[1]:
        evid = (ev, block_id, stmt_id)
        if evid in chk.events:
            # logically the first element is the deeper
            nb_match.append(chk.events[evid][0])
    # we unsure that all event come from the same depth and are all set (AND)
    if len(nb_match) == len(action[1]) and nb_match.count(nb_match[0]) == len(nb_match):
        for ev in action[1]:
            evid = (ev, block_id, stmt_id)
            chk.events[evid].pop(0)
            if not chk.events[evid]:
                del chk.events[evid]
        return True
    return False

def action_check_clean_event_or(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    nb_match = []
    for ev in action[1]:
        evid = (ev, block_id, stmt_id)
        if evid in chk.events:
            # logically the first element is the deeper
            nb_match.append((evid, chk.events[evid][0]))
    # we unsure that all event come from the same depth, but we don't car how many are set (OR)
    if sum(1 for y in nb_match if y[1] == nb_match[0][1]) == len(nb_match):
        for evid, _ in nb_match:
            chk.events[evid].pop(0)
            if not chk.events[evid]:
                del chk.events[evid]
        return True
    return False

def action_check_clean_event_xor(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    nb_match = []
    for ev in action[1]:
        evid = (ev, block_id, stmt_id)
        if evid in chk.events:
            # logically the first element is the deeper
            nb_match.append((evid, chk.events[evid][0]))
    # only one element is set (XOR)
    if len(nb_match) == 1:
        evid, _ = nb_match[0]
        chk.events[evid].pop(0)
        if not chk.events[evid]:
            del chk.events[evid]
        return True
    return False

def action_check_named_event(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    evid = (action[1], block_id)
    if evid in chk.named_events:
        if block_id not in chk.postpone_clean:
            chk.postpone_clean[block_id] = {}
        chk.postpone_clean[block_id][action[1]] = (chk.named_events[evid], evid)
        action_set_event((None, action[2]), chk, uid)
    return True

def action_postpone_clean_named_event(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    lsr = []
    if block_id in chk.postpone_clean:
        for it in chk.postpone_clean[block_id].values():
            if it[0] >= chk.current_depth:
                lsr.append(it)
    for it in lsr:
        del chk.named_events[it[1]]
        del chk.postpone_clean[block_id][it[1][0]]
        if not chk.postpone_clean[block_id]:
            del chk.postpone_clean[block_id]
    return True

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

def action_store_ancestor_depth(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    depthid = (action[1], block_id, stmt_id)
    if depthid not in chk.depths:
        chk.depths[depthid] = []
    chk.depths[depthid].append((chk.current_depth, id(chk.current_node)))
    return True

def action_check_ancestor_depth(action, chk, uid):
    cur_pos, block_id, stmt_id, stackid = uid
    depthid = (action[1], block_id, stmt_id)
    d = action[2]
    ismin = action[3]
    if depthid not in chk.depths:
        return False
    # check ancestor links
    print("CURRENT NODE %d" % id(chk.current_node))
    check = False
    for idx in range(len(chk.depths[depthid]) - 1, -1, -1):
        curdepth = chk.depths[depthid][idx]
        depth = curdepth[0]
        idnode = curdepth[1]
        print("ANCESTOR ID %d D %d" % (idnode, depth))
        if not chk.is_parentof(id(chk.current_node), idnode):
            continue
        print("ismin %s: %d - %d ?? %d" % (ismin, depth, chk.current_depth, d))
        if ismin:
            if depth - chk.current_depth >= d:
                check = True
                chk.depths[depthid].pop(idx)
                break
        elif depth  - chk.current_depth == d:
                check = True
                chk.depths[depthid].pop(idx)
                break
    if not chk.depths[depthid]:
        del chk.depths[depthid]
    return check

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
    print("CALL HOOK %s" % chk.captures)
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
    'check_clean_event_and': action_check_clean_event_and,
    'check_clean_event_or': action_check_clean_event_or,
    'check_clean_event_xor': action_check_clean_event_xor,
    'check_named_event': action_check_named_event,
    'postpone_clean_named_event': action_postpone_clean_named_event,
    'capture': action_capture,
    'capture_pair_first': action_capture_pair_first,
    'capture_pair_second': action_capture_pair_second,
    'store_ancestor_depth': action_store_ancestor_depth,
    'check_ancestor_depth': action_check_ancestor_depth,
    'store_sibling_depth': action_store_sibling_depth,
    'check_sibling_depth': action_check_sibling_depth,
    'hook': action_hook
}
