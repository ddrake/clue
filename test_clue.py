from clue import *
from random import choice

def query_to_set(query):
    return set(indices_to_all(query))

def test_solve1():
    players = [ Player('Dow', 3, True,[0, 12, 19]), 
                Player('Tave', 4, False), 
                Player('Osanna', 3, False), 
                Player('Lucinda', 4, False),
                Player('Nathan', 4, False) ]
    solution = [4,4,6]
    true_hands = [set([0,12,19]), set([2,6,8,20]), set([3,11,17]), set([1,9,13,14]), set([5,7,15,16])]
    suggestions = [(0,(1,1,1)), (1,(2,2,2)), (2,(3,4,5)), (3,(3,5,2)), (4,(4,4,6)), (0,(4,4,6))]
    for i, item in enumerate(suggestions):
        pid, query = item
        qset = query_to_set(query)
        suggester = players[pid]
        responders = get_responders(players, suggester)
        for r in responders:
            idx = players.index(r)
            hand = true_hands[idx]
            isect = qset & hand
            if len(isect) == 0:
                r.update_for_no(qset)
            else:
                if suggester.is_cpu:
                    card = isect.pop()
                    r.update_for_card(card)
                else:
                    r.update_for_yes(qset)
                break
        if found_solution(players): break
    assert found_solution(players), "No solution found"
    assert i == 5

def test_solve2():
    players = [ Player('Dow', 3, True, [0, 12, 19]), 
                Player('Tave', 4, False), 
                Player('Osanna', 3, False), 
                Player('Lucinda', 4, False),
                Player('Nathan', 4, False) ]
    solution = [4,4,6]
    true_hands = [set([0,12,19]), set([2,6,8,20]), set([3,11,17]), set([1,9,13,14]), set([5,7,15,16])]
    suggestions = [(1,(5,5,8)), (2,(2,4,7)), (3,(5,2,3)), (4,(5,4,3)), (0,(3,2,2)), 
                   (1,(2,5,7)), (2,(5,5,5)), (3,(4,1,1)), (4,(4,3,4)), (0,(1,4,1)), 
                   (1,(1,3,6)), (2,(3,3,3)), (3,(4,1,4)), (4,(2,1,8)), (0,(5,3,7)),
                   (1,(4,3,6)), (2,(3,4,3)), (3,(4,3,6)), (4,(4,4,8)), (0,(5,4,6)),
                   (1,(4,3,6)), (2,(3,4,3)), (3,(4,1,6)), (4,(4,4,8)), (0,(4,3,7)),
                   (1,(2,4,6)), (2,(4,3,6)), (3,(0,4,4)), (4,(4,1,6)), (0,(1,4,6))]
    for i, item in enumerate(suggestions):
        pid, query = item
        qset = query_to_set(query)
        suggester = players[pid]
        responders = get_responders(players, suggester)
        for r in responders:
            idx = players.index(r)
            hand = true_hands[idx]
            isect = qset & hand
            if len(isect) == 0:
                r.update_for_no(qset)
            else:
                if suggester.is_cpu:
                    card = isect.pop()
                    r.update_for_card(card)
                else:
                    r.update_for_yes(qset)
                break
        if found_solution(players): break
    assert query == (4,1,6)
    assert definite_solution(players) == ['wrench', 'study', 'Ms White']
