from __future__ import unicode_literals

class TClass:
    '''
    Represents an taxonomic class
    '''

    def __init__(self, name, level=0, father=None, children=[]):
        assert(isinstance(name,unicode))
        self.name = name
        self.level = level #depth in taxonomy
        if not (father == None):
            assert(isinstance(father, TClass))
        self.father = father
        self.children = children
        self.instances = set()


    def __repr__(self):
        return self.name.split('/')[-1][:-1] + ' ({0})'.format(self.level)


    def add_child(self, child):
        assert(isinstance(child, TClass))
        for c in self.children:
            if c.name==child.name:
                print('WARNING: child "{0}" already present at "{1}"'.format(
                    child.name, self.name))

        self.children.append(child)

class Instance:
    '''
    Represents an instance of the taxonomy
    '''

    def __init__(self, uri=''):
        self.uri = uri #e.g. <http://dbpedia.org/page/Apple>


class Taxonomy:
    '''
    Wrap a taxonomy
    '''

    def __init__(self, root=TClass('<http://dbpedia.org/ontology/Thing>')):
        assert(isinstance(root,TClass))
        self.depth = 0
        self.root = root
        self.classes = {root:TClass(root.name)} #name:object


    def __repr__(self):
        children = self.root.children
        res = self._gen_child_repr([self.root])
        return res


    def _gen_child_repr(self, classes):
        '''
        Recursively generate the representation of children in the taxonomy
        '''
        res = ''
        if classes == []:
            return res

        for cls in classes:
            res += (" " * (cls.level * 2)) + cls.name + '\n'
            res += self._gen_child_repr(cls.children)
        return res


    def add_class(self, cls):
        assert(isinstance(cls, TClass))
        if cls.name in self.classes:
            print('WARNING: class {} already present'.format(cls.name))
        self.classes[cls.name] = cls
        if cls.level > self.depth:
            self.depth = cls.level
