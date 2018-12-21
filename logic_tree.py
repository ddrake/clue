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
    """ A logic tree customized for use by the clue solver.
        It is implemented as a list of lists, where each list 
        represents a branch of a tree
    """

    def __init__(self):
        self.branches = []

    def branches_as_sets(self):
        return [set(b) for b in self.branches]

    def add_pos(self, query):
        """ add a query (tuple) positively to the tree.  This adds a branch
            for each disjunction, intentionally creating duplicate 
            references to atoms.
        """
        self.branches = [b + [atom(q, True)]
                             for b in self.branches for q in query] \
                        if self.branches else [[atom(q, True)] for q in query]
        self.prune()
        self.clean()

    def add_neg(self, query):
        """ add a query (tuple) negatively to the tree
        """
        qlist = [atom(q, False) for q in query]
        self.branches = [b + qlist for b in self.branches] \
                        if self.branches else [qlist]
        self.prune()
        self.clean()

    def contr(self, branch):
        """ check if a branch contains logical contradictions and
            so can be deleted.
        """
        yes = {a.num for a in branch if a.bval}
        no = {a.num for a in branch if not a.bval}
        return len(yes & no)

    def prune(self):
        """ remove any branches with contradictions """
        self.branches = [b for b in self.branches if self.contr(b) == 0]

    def clean(self):
        """ remove duplicates from branches
            exclude any branch that is a subset of another branch 
            and sort atoms in branches by number
        """
        lst = [set(b) for b in set([tuple(set(b)) for b in self.branches])]
        newlst = []
        for i in range(len(lst)):
            exclude = False
            for j in range(len(lst)):
                if lst[i] < lst[j]:
                    exclude = True
                    break
            if not exclude:
                newlst.append(lst[i])
        self.branches = [sorted(list(b), key=lambda a: a.num) for b in newlst]

    #---------------------------
    # Information about the tree
    #---------------------------

    def print(self):
        for b in self.branches:
            print(b)

    def common_elements(self):
        """ get a set of the atoms common to each branch """
        return set.intersection(*self.branches_as_sets()) \
                if self.branches else {}

    def possibles(self):
        """ get a nested list representing the disjuctive part of the tree 
            bvals are not included since they will always be True
        """
        if not self.branches: return []
        ce = self.common_elements()
        diff = [b - ce for b in self.branches_as_sets() if len(b - ce) > 0]
        return sorted([sorted([a.num for a in sub]) for sub in diff])

    def simple(self):
        """ return a simple representation of the tree """
        return sorted(list(self.common_elements()), 
                key=lambda a: a.num) + self.possibles() \
                if self.branches else []

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
