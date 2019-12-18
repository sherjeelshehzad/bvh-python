#a (slight) rewrite of the BvhNode class to use a structure with less child objects
#so we can actually make this fast
import re
from copy import deepcopy

#from https://stackoverflow.com/a/19871956
#finds kv in node, where node is a nested dict/list structure
def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x
                

class BvhJoint:
    def __init__(self, value='', parent=None, children=[], channels=[], offsets=[], frames=[]):
        self.value = value
        self.children = children
        self.parent = parent
        if self.parent:
            self.parent.add_child(self)
        self.channels = channels
        self.offsets = offsets
        self.frames = frames
    def add_child(self,joint):
        joint.parent = self
        self.children.append(joint)
    
    @property
    def getChild(self):
        return self.children
    @property
    def getParent(self):
        return self.parent
    @property
    def getChannels(self):
        return self.channels
    @property
    def getOffsets(self):
        return self.offsets
    @property
    def getFrame(self,index):
        try:
            return self.frames[index]
        except IndexError:
            return []
    @property
    def getFrames(self):
        return self.frames
    
#a better solution is to just use a dict for Bvh so our lookups are fast
#in-progress rewrite of the original Bvh parser from 20tab/bvh-python
class BvhDict:
    #to avoid repetitiveness, create a static 'const' dict with all the properties we need
    #for each joint
    propertydict = {'type':'','parent':None,'children':[],'channels':[],'offsets':[],'frames':[]}
    def __init__(self, data):
        self.data = data
        self.dict = {}
        self.frames = []
        self.tokenise()
        
    def tokenise(self):
        first_round = []
        accumulator = ''
        for char in self.data:
            if char not in ('\n', '\r'):
                accumulator += char
            elif accumulator:
                first_round.append(re.split('\\s+', accumulator.strip()))
                accumulator = ''
        else:
            if accumulator:
                first_round.append(re.split('\\s+', accumulator.strip()))
                accumulator = ''
        frame_time_found = False
        node = None
        joint_stack = {}
        current_joint = ''
        #TODO: the proper way to do this seems to be to build the dictionary from
        #the inside out, so start at the innermost child and work backwards
        for item in first_round:
            if frame_time_found:
                self.frames.append(item)
                continue
            key = item[0]
            
            if key == '{':
                pass
            elif key == '}':
                pass
            else:
                if ((item[0] == 'ROOT') or (item[0] == 'JOINT')):
                    node = {item[1] : deepcopy(self.propertydict)}
                    self.dict[item[1]] = deepcopy(self.propertydict)
                    self.dict[item[1]]['type'] = item[0]
                elif item[0] == 'CHANNELS':
                    for subitem in item[2:]:
                        node['channels'].append(subitem)
                elif item[0] == 'OFFSET':
                    for subitem in item[1:]:
                        node['offsets'].append(subitem)
            if item[0] == 'Frame' and item[1] == 'Time:':
                frame_time_found = True
            
            