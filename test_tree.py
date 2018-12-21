from logic_tree import *

def test_add_both():
    t = tree()
    t.add_pos((1,2,3))
    t.add_pos((4,5,6))
    t.add_neg((1,5,6))
    common = t.common_elements()
    possibles = t.possibles()

    assert atom(1, False) in common
    assert atom(4, True) in common
    assert atom(5, False) in common
    assert atom(6, False) in common
    assert [3] in possibles
    assert [2] in possibles

def test_more_complicated():
    t = tree()
    t.add_pos((1,2,3))
    t.add_pos((4,5,6))
    t.add_neg((1,5,6))
    t.add_pos((2,8,4))
    common = t.common_elements()
    possibles = t.possibles()

    assert atom(1, False) in common
    assert atom(4, True) in common
    assert atom(5, False) in common
    assert atom(6, False) in common
    assert [2, 8] in possibles
    assert [3, 8] in possibles
    assert [2, 3] in possibles
