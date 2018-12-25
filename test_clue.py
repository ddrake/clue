from clue import *

def test_solve1():
    players = [ Player('Dow', 3, True,[0, 12, 19]), 
                Player('Tave', 4, False), 
                Player('Osanna', 3, False), 
                Player('Lucinda', 4, False),
                Player('Nathan', 4, False) ]
    true_solution = [4,4,6]
    true_hands = [set([0,12,19]), set([2,6,8,20]), set([3,11,17]), set([1,9,13,14]), set([5,7,15,16])]
    suggestions = [(0,(1,1,1)), (1,(2,2,2)), (2,(3,4,5)), (3,(3,5,2)), (4,(4,4,6)), (0,(4,4,6))]
    computed_solution, _, suggestions_made = \
            automate(players, test_data=(true_hands, true_solution, suggestions))

    assert found_solution(players), "No solution found"
    assert len(suggestions_made) == 6
    assert computed_solution == true_solution

def test_solve2():
    players = [ Player('Dow', 3, True, [0, 12, 19]), 
                Player('Tave', 4, False), 
                Player('Osanna', 3, False), 
                Player('Lucinda', 4, False),
                Player('Nathan', 4, False) ]
    true_solution = [4,4,6]
    true_hands = [set([0,12,19]), set([2,6,8,20]), set([3,11,17]), set([1,9,13,14]), set([5,7,15,16])]
    suggestions = [(1,(5,5,8)), (2,(2,4,7)), (3,(5,2,3)), (4,(5,4,3)), (0,(3,2,2)), 
                   (1,(2,5,7)), (2,(5,5,5)), (3,(4,1,1)), (4,(4,3,4)), (0,(1,4,1)), 
                   (1,(1,3,6)), (2,(3,3,3)), (3,(4,1,4)), (4,(2,1,8)), (0,(5,3,7)),
                   (1,(4,3,6)), (2,(3,4,3)), (3,(4,3,6)), (4,(4,4,8)), (0,(5,4,6)),
                   (1,(4,3,6)), (2,(3,4,3)), (3,(4,1,6)), (4,(4,4,8)), (0,(4,3,7)),
                   (1,(2,4,6)), (2,(4,3,6)), (3,(0,4,4)), (4,(4,1,6)), (0,(1,4,6))]
    computed_solution, _, suggestions_made = \
            automate(players, test_data=(true_hands, true_solution, suggestions))

    assert computed_solution == true_solution
