class atom:
    """
    a number with an associated boolean value
    """

    def __init__(self, num, bval):
        self.num = num
        self.bval = bval

    def __str__(self):
        return '{}{}'.format('' if self.bval else '~', self.num)

    def __repr__(self):
        return '({}, {})'.format(self.num, self.bval)

    def __eq__(self, other):
        return self.num == other.num and self.bval == other.bval

    def __hash__(self):
        return hash(str(self))


class tree:
    """ a logic tree customized for use by the clue solver
        it is implemented as a list of lists, where each list 
        represents a branch of a tree
    """

    def __init__(self):
        self.branches = []

    def add_pos(self, query):
        """ add a query (tuple) positively to the tree.  This adds branches
            intentionally creating duplicate references to atoms.
        """
        if self.branches:
            self.branches = [b + [atom(q, True)]
                             for b in self.branches for q in query]
        else:
            for q in query:
                self.branches.append([atom(q, True)])
        self.prune()
        self.clean()

    def add_neg(self, query):
        """ add a query (tuple) negatively to the tree
        """
        qlst = [atom(q, False) for q in query]
        if self.branches:
            for b in self.branches:
                for q in qlst:
                    b.append(q)
        else:
            self.branches.append(qlst)
        self.prune()
        self.clean()

    def test(self, branch):
        """ check if a branch contains logical contradictions and
            so can be deleted.
        """
        yes = set()
        no = set()
        for a in branch:
            if a.bval:
                yes.add(a.num)
            else:
                no.add(a.num)
        return len(yes & no)

    def prune(self):
        """ remove any branches with contradictions """
        self.branches = [b for b in self.branches if self.test(b) == 0]

    def print(self):
        for b in self.branches:
            print(b)

    def common_elements(self):
        """ get a list of the atoms common to each branch """
        if not self.branches:
            return {}
        else:
            lst = [set(b) for b in self.branches]
            isect = lst[0]
            for b in lst:
                isect = isect & b
            return isect

    def possibles(self):
        """ get a nested list representing the disjuctive part of the tree """
        if not self.branches:
            return []
        lst = [set(b) for b in self.branches]
        isect = self.common_elements()
        lst = [sorted(list(b-isect), key=lambda a: a.num)
               for b in lst if len(b-isect) > 0]
        return [[l.num for l in sub] for sub in lst]

    def simple(self):
        """ return a simple representation of the tree """
        if not self.branches:
            return self.branches
        lst = [set(b) for b in self.branches]
        isect = self.common_elements()
        difflst = [sorted(list(b-isect), key=lambda a: a.num)
                   for b in lst if len(b-isect) > 0]
        blst = sorted(list(isect), key=lambda a: a.num)
        return blst + difflst

    def clean(self):
        """ remove duplicates from branches
            exclude any branch that is a subset of another branch 
            and sort atoms in branches by number
        """
        lst = [set(b) for b in set([tuple(set(b)) for b in self.branches])]
        lenlst = len(lst)
        newlst = []
        for i in range(lenlst):
            exclude = False
            for j in range(lenlst):
                if j == i:
                    continue
                if lst[i].issubset(lst[j]):
                    exclude = True
                    break
            if not exclude:
                newlst.append(lst[i])
        newlst = [sorted(list(b), key=lambda a: a.num) for b in newlst]
        self.branches = newlst

    def pos_elements(self):
        """ the common atoms with bval True """
        return set([a.num for a in self.common_elements() if a.bval])

    def neg_elements(self):
        """ the common atoms with bval False """
        return set([a.num for a in self.common_elements() if not a.bval])

    def contains_any(self, nums):
        """ compare the positive common atoms with the given list 
            to see if any are included
        """
        return len(self.pos_elements() & set(nums)) > 0
