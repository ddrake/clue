from itertools import product

class atom:
    """ Represents an integer with an associated boolean value
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
        It is implemented as a list of sets, where each set
        represents a branch of a tree
    """

    def __init__(self):
        self.branches = []

    def add_pos(self, query):
        """ Add a query (tuple) positively to the tree.  This results in
            a copy of each existing branch for each atom in the disjunction.
            Multiple references to a given atom are created in the process.
        """
        self.branches = [b | set((atom(q, True),))
                             for b in self.branches for q in query] \
                        if self.branches else [set((atom(q, True),)) for q in query]
        self.prune()
        self.clean()

    def add_neg(self, query):
        """ Add a query (tuple) negatively to the tree.  A chain of negative
            atoms is created for the conjunction.  It is then and unioned 
            with each existing branch.
        """
        qset = set(atom(q, False) for q in query)
        self.branches = [b | qset for b in self.branches] \
                        if self.branches else [qset]
        self.prune()
        self.clean()

    def contr(self, branch):
        """ Check if a branch contains one or more logical contradictions.
            If so, the branch can be deleted from the tree.
        """
        yes = {a.num for a in branch if a.bval}
        no = {a.num for a in branch if not a.bval}
        return yes & no

    def prune(self):
        """ remove any branches with contradictions """
        self.branches = [b for b in self.branches if not self.contr(b)]

    def clean(self):
        """ Remove duplicate branches.  
        """
        self.branches = [set(b) for b in set([tuple(b) for b in self.branches])]

    #---------------------------
    # Information about the tree
    #---------------------------

    def print(self):
        for b in self.branches:
            print(sorted(list(b), key=lambda b: b.num))

    def common_elements(self):
        """ get a set of the atoms common to each branch """
        return set.intersection(*self.branches) if self.branches else {}

    def possibles(self):
        """ get a nested list representing the disjuctive part of the tree 
            bvals are not included since they will always be True
            inner and outer lists are sorted in ascending order
        """
        if not self.branches: return []
        ce = self.common_elements()
        diff = [b - ce for b in self.branches if b - ce]
        return sorted([sorted([a.num for a in sub]) for sub in diff])

    def simple(self):
        """ return a simple representation of the tree """
        return sorted(list(self.common_elements()), 
                key=lambda a: a.num) + self.possibles() \
                if self.branches else []

    def pos_elements(self):
        """ the common atoms with bval True """
        return {a.num for a in self.common_elements() if a.bval}

    def neg_elements(self):
        """ the common atoms with bval False """
        return {a.num for a in self.common_elements() if not a.bval}

    def contains_any(self, nums):
        """ compare the positive common atoms with the given enumerable 
            to see if any are included
        """
        return self.pos_elements() & set(nums)
