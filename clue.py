#!/usr/bin/env python3
from logic_tree import *
from menu import Menu
import pickle
from itertools import product
from collections import Counter
from random import choice, shuffle

class Player:
    """ A class representing a player in the game Clue """

    def __init__(self, name, ncards, is_cpu, knowns=None):
        self.name = name
        self.ncards = ncards
        self.is_cpu = is_cpu
        self.hand = tree()
        self.true_hand = None
        if self.is_cpu:
            self.hand.add_neg(list(allcardset() - set(knowns)))
            for k in knowns:
                self.hand.add_pos([k])

    def print_hand(self):
        """ print the cards the player is known to have and not to have """
        pos = [ALLCARDS[num] for num in self.hand.pos_elements()]
        neg = [ALLCARDS[num] for num in self.hand.neg_elements()]
        posstr = 'In hand: {}'.format(', '.join(pos))
        negstr = 'Not in hand: {}'.format(', '.join(neg))
        print(self.name)
        if pos:
            print(posstr)
        if neg:
            print(negstr)

    # All queries and cards are indices into the ALLCARDS list
    def update_for_no(self, query):
        self.hand.add_neg(query)

    def update_for_yes(self, query):
        self.hand.add_pos(query)

    def update_for_card(self, card):
        self.hand.add_pos([card])

    def possibles(self):
        """ Nested list representing disjunctions """
        poss = self.hand.possibles()
        return [[ALLCARDS[n] for n in sub] for sub in poss]



# -----------
# UI Helpers
# -----------


def inp():
    return input("> ")


def get_bool(prompt, default=None):
    deftext = ' Y|n' if default == True \
        else ' y|N' if default==False else ' y|n'
    print(prompt + deftext)
    resp = inp()
    return True if resp.upper() == 'Y' or (resp=='' and default==True) \
        else False if resp.upper() == 'N' or (resp=='' and default==False) \
        else None


def get_string(prompt):
    print(prompt)
    return inp()


def get_int(prompt, allow_n=False, allowed=None):
    print(prompt)
    while True:
        resp = inp()
        if allow_n and resp.upper() == 'N':
            return False
        try:
            result = int(resp)
            if allowed and result not in allowed:
                pause("{} is not allowed".format(result))
                continue
            return result
        except(ValueError):
            pause("not a valid number")


def get_list(prompt, n, allowed=None):
    print(prompt)
    while True:
        resp = inp()
        result = resp.strip().split()
        if len(result) != n:
            pause("expected {} numbers".format(n))
            continue
        try:
            result = [int(x) for x in result]
            if allowed:
                if any(result[i] not in allowed[i] for i in range(n)):
                    pause("some numbers were out of range")
                    continue
            return result
        except(ValueError):
            pause("{} is not a valid list of numbers".format(result))
                


def sync_players(players):
    """ manually synchronize using the fact that if a player has a card,
        the others don't """
    for p, p1 in product(players, repeat=2):
            if p != p1:
                for n in (p.hand.pos_elements() - p1.hand.neg_elements()):
                    p1.hand.add_neg([n])


def base_to_zero(nums):
    return [n-1 for n in nums]

def indices_to_all(nums):
    """ change the indices of a zero-based query to index into ALLCARDS """
    s, w, r = nums
    return [s, w+NS, r+NS+NW]

def text_query(nums):
    """ get the names for a zero-based query """
    return [ALLCARDS[i] for i in nums]

def allcardset():
    """ a set containing all the cards """
    return set(range(len(ALLCARDS)))


def get_responders(players, suggester):
    """ get the responders (in the correct order) for the given suggester """
    si = players.index(suggester)
    return players[si+1:] + players[:si]


def pause(msg=None):
    if msg:
        print(msg)
    input("Press <Enter> to continue...")


def abort_suggestion(message):
    print("The current suggestion was aborted."
          + "Cause: " + message if message else "")
    pause()


def abort_add_player(message):
    print("Adding the player was aborted."
          + "Cause: " + message if message else "")
    pause()


def abort_delete_player(message):
    print("Deleting the player was aborted."
          + "Cause: " + message if message else "")
    pause()


def print_cards_in_categories():
    """ used to ask the CPU player to enter a query
        containing one of each kind.  Note: the indices
        are into the individual lists, not ALLCARDS
    """
    for i, s in enumerate(SUSPECTS):
        print(i+1, s)
    print()
    for i, w in enumerate(WEAPONS):
        print(i+1, w)
    print()
    for i, r in enumerate(ROOMS):
        print(i+1, r)


def print_all_cards():
    """ used to ask the CPU player to enter a card """
    for i, c in enumerate(ALLCARDS):
        print(i+1, c)

def print_query_cards(query):
    for c in query:
        print(c+1, ALLCARDS[c])

def get_suggester(players):
    for i, p in enumerate(players):
        print(i+1, p.name)
    pnum = get_int("Enter the player who made the suggestion", 
            allowed=range(1,len(players)+1))
    return players[pnum-1]

def confirm_suggester(suggester):
    confirm = get_bool("Suggester is {}. OK?".format(suggester.name), 
            default=True)
    if not confirm:
        abort_suggestion("User cancelled")
    return confirm


def get_suggestion():
    print_cards_in_categories()
    numlist = get_list("Enter numbers for suggestion separated by spaces", 3, 
            allowed=[range(1, NS+1), range(1, NW+1), range(1, NR+1)])
    numquery = indices_to_all(base_to_zero(numlist))
    return numquery


def confirm_suggestion(query):
    confirm = get_bool("Suggestion is {}. OK?".format(query), default=True)
    if not confirm:
        abort_suggestion("User cancelled")
    return confirm


def get_response_cpu_suggested(numquery):
    print_query_cards(numquery)
    cnum = get_int("Enter card shown or 'n' if none", allow_n=True, 
            allowed=[n+1 for n in numquery])
    return cnum


def confirm_response_cpu_suggested(card, pname):
    if card == False:
        confirm = get_bool("{} did not show a card. OK?".format(pname), 
                default=True)
    else:
        confirm = get_bool(
            "{} showed {}.  OK?".format(pname, ALLCARDS[card-1]), 
            default=True)
    if not confirm:
        abort_suggestion("User cancelled")
    return confirm


def get_response_other_suggested(query):
    print(query)
    resp = get_bool("Was a card shown?")
    return resp


def confirm_response_other_suggested(resp, pname):
    confirm = get_bool("{} {} a card. OK?"
                       .format(pname, 'showed' if resp else 'did not show'),
                       defaut = True)
    if not confirm:
        abort_suggestion("User cancelled")
    return confirm


def add_suggestion(players):
    """ Enter a suggestion made by a player
        along with the responses of the other players
    """
    suggester = get_suggester(players)
    if not suggester:
        return
    if not confirm_suggester(suggester):
        return

    numquery = get_suggestion()
    textquery = text_query(numquery)
    if not confirm_suggestion(textquery):
        return

    responders = get_responders(players, suggester)
    for player in responders:
        if player.is_cpu:
            if player.hand.contains_any(numquery):
                pause("CPU showed a card")
                break
        else:
            print()
            print("Response from {}".format(player.name))
            if suggester.is_cpu:
                card = get_response_cpu_suggested(numquery)
                if not confirm_response_cpu_suggested(card, player.name):
                    return
                if card == False:
                    player.update_for_no(numquery)
                elif card > 0:
                    player.update_for_card(card-1)
                    break
                else:
                    return
            else:
                resp = get_response_other_suggested(textquery)
                if resp:
                    player.update_for_yes(numquery)
                    break
                else:
                    player.update_for_no(numquery)


def automate(players, test_data=None, display=False):
    """ Play a game automatically with provided data or random data for testing
        
        INPUTS
        players - a list of player objects
        data - a tuple of the following items:
            true_hands - a list of tuples of indices into ALLCARDS
                ordered the same as the players list
                with the length of each tuple corresponding to player's ncards
            true_solution - a three-tuple of indices into the three category lists
                representing a suspect, a weapon and a room
            suggestions - a list of three-tuples of indices into the three category
                lists representing a suspect a weapon and a room

        OUTPUTS
        computed_solution, true_solution, suggestions_made
    """
    def get_query_triple():
        return (choice(range(NS)), choice(range(NW)), choice(range(NR)))

    def deal():
        true_solution = get_query_triple()
        ac = set(range(NS+NW+NR))
        ac -= set(indices_to_all(true_solution))
        ac = list(ac)
        shuffle(ac)
        for p in players:
            p.true_hand = ac[:p.ncards]
            ac = ac[p.ncards:]
            assert len(p.true_hand) == p.ncards
        return true_solution
        
    if test_data:
        true_hands, true_solution, suggestions = test_data
        for player, true_hand in zip(players, true_hands):
            player.true_hand = true_hand
    else:
        true_solution = deal()
        suggestions = [(i % len(players), get_query_triple()) for i in range(100)]
        if display: 
            print("True solution")
            pause(str([SUSPECTS[true_solution[0]],
                       WEAPONS[true_solution[1]],
                       ROOMS[true_solution[2]]]))

    for i, item in enumerate(suggestions):
        pid, query = item
        qset = set(indices_to_all(query))
        suggester = players[pid]
        if display: 
            print()
            pause("{}. {} suggested {}.".format(i+1, suggester.name, text_query(qset)))
        responders = get_responders(players, suggester)
        for r in responders:
            isect = qset & set(r.true_hand)
            if len(isect) == 0:
                r.update_for_no(qset)
                if display: 
                    pause("{} had none.".format(r.name))
            else:
                if suggester.is_cpu:
                    card = isect.pop()
                    r.update_for_card(card)
                    if display: 
                        pause("{} showed {}.".format(r.name, ALLCARDS[card]))
                else:
                    r.update_for_yes(qset)
                    if display: 
                        pause("{} showed a card.".format(r.name))
                break
        if found_solution(players): break
    return true_solution, definite_solution_nums(players), suggestions[:i+1]


def get_player(players):
    name = get_string("Player name")
    ncards = get_int("Number of cards", allowed=range(1,10))
    is_cpu = False
    if len(players) == 0 or not any(p for p in players if p.is_cpu):
        is_cpu = get_bool("Is this player the CPU?")
    return name, ncards, is_cpu


def confirm_player(name, ncards, is_cpu):
    confirm = get_bool("Player is {}, {} cards, {}. OK?"
                       .format(name, ncards, "CPU" if is_cpu else "not CPU"),
                       default=True)
    if not confirm:
        abort_add_player("User cancelled")
    return confirm


def get_cpu_player_cards(ncards):
    print_all_cards()
    result = get_list("Enter card numbers separated by spaces", ncards,
            allowed=[range(1, len(ALLCARDS)+1)]*ncards)
    if any(i for i in result if i <= 0 or i > len(ALLCARDS)):
        return None
    return result


def confirm_cpu_player_cards(cards):
    knowns = [ALLCARDS[i-1] for i in cards]
    confirm = get_bool("Cards {}. OK?".format(knowns), default=True)
    if not confirm:
        abort_add_player("User cancelled")
    return confirm


def add_player(players):
    """ add a player to the game """
    name, ncards, is_cpu = get_player(players)
    if not confirm_player(name, ncards, is_cpu):
        return
    knowns = None
    if is_cpu:
        cards = get_cpu_player_cards(ncards)
        if not cards:
            return
        if not confirm_cpu_player_cards(cards):
            return
        players.append(Player(name, ncards, is_cpu, base_to_zero(cards)))
    else:
        players.append(Player(name, ncards, is_cpu))
    set_player_options(players)
    set_main_options(players)
    set_player_del_options(players)


def delete_player(players):
    """ delete a player """
    confirm = get_bool("Are you sure you want to delete player {}"
                       .format(current_player.name), default=True)
    if not confirm:
        abort_delete_player("User cancelled")
        return
    players.remove(current_player)
    set_player_options(players)
    set_main_options(players)
    set_player_del_options(players)
    m_player_del.close()

# ----------------------------------------
# Info about solutions and player's hands
# ----------------------------------------


def print_definite_solution(players):
    print(definite_solution(players))
    pause()


def print_likely_solution(players):
    print(likely_solution(players))
    pause()


def print_player_possibles(players):
    for p in players:
        print(p.name)
        print(p.possibles())
        print()
    pause()


def definite_solution(players):
    """ The solution to the game """
    defs = definite_solution_nums(players)
    return [ALLCARDS[c] for c in defs]


def found_solution(players):
    """ Indicate the game was solved """
    return len(definite_solution(players)) == 3


def likely_solution(players):
    """ Return tuples of cards with the
        number of players who don't have them
    """
    likes = likely_solution_nums(players)
    return sorted([(ALLCARDS[n], ct) for n, ct in likes],
                  key=lambda tp: tp[1], reverse=True)


def definite_solution_nums(players):
    likes = likely_solution_nums(players)
    if len(likes) == 3:
        return [k for k, v in likes]
    else:
        none = [p.hand.neg_elements() for p in players]
        return set.intersection(*none)

def likely_solution_nums(players):
    not_in_hand = Counter(n for p in players for n in p.hand.neg_elements())
    knowns = set(n for p in players for n in p.hand.pos_elements())
    return [(k,v) for k, v in not_in_hand.items() if k not in knowns]

def player_hands(players):
    for player in players:
        player.print_hand()
        print()
    pause()

def save_players(players):
    with open('clue.pkl', 'wb') as f:
        pickle.dump(players, f)
        pause('Saved to file')

def load_players():
    with open('clue.pkl', 'rb') as f:
        players = pickle.load(f)
        set_player_options(players)
        set_main_options(players)
        set_player_del_options(players)
        m_player_del.close()
        pause('Loaded from file')
# ----------
# Menu Setup
# ----------


def set_main_options(players):
    m_main.title = "Clue"
    m_main.options = []
    m_main.add_option("Quit", m_main.close)
    m_main.add_option("Save", lambda: save_players(players))
    m_main.add_option("Load", lambda: load_players())
    if players:
        m_main.add_option("Add Suggestion", lambda: add_suggestion(players))
        m_main.add_option("Sync Players", lambda: sync_players(players))
        m_main.add_option("Player hands", lambda: player_hands(players))
        m_main.add_option("Player possibles",
                          lambda: print_player_possibles(players))
        m_main.add_option("Likely solution cards",
                          lambda: print_likely_solution(players))
        m_main.add_option("Definite solution cards",
                          lambda: print_definite_solution(players))
        m_main.add_option("Automate",
                          lambda: automate(players, display=True))
    m_main.add_option("Manage Players", m_player.open)


def set_player_options(players):
    m_player.options = []
    m_player.add_option("Return to Main Menu", m_player.close)
    m_player.add_option("Add Player", lambda: add_player(players))
    for player in players:
        m_player.add_option(
            player.name, lambda p=player: set_player_open_del(p))


def set_player_del_options(players):
    m_player_del.options = []
    m_player_del.add_option("Return to Player List",
                            m_player_del.close)
    m_player_del.add_option("Delete", lambda: delete_player(players))


def set_player_open_del(player):
    global current_player
    current_player = player
    print(player.name)
    m_player_del.open()

# -------------
# Main Program
# -------------
SUSPECTS = ['Colonel Mustard', 'Mr. Green', 'Professor Plum',
            'Miss Scarlet', 'Ms White', 'Mrs. Peacock']
WEAPONS = ['lead pipe', 'candlestick', 'rope', 'knife',
           'wrench', 'pistol']
ROOMS = ['hall', 'conservatory', 'library', 'dining room',
         'kitchen', 'billiard room', 'study', 'lounge', 'ball room']
ALLCARDS = SUSPECTS + WEAPONS + ROOMS

NS, NW, NR = len(SUSPECTS), len(WEAPONS), len(ROOMS)

if __name__ == '__main__':
    players = []
    current_player = None
    m_main = Menu(title="Main Menu")
    m_player = Menu(title="Manage Players")
    m_player_del = Menu(title="Edit/Delete Player")
    set_main_options(players)
    set_player_options(players)
    set_player_del_options(players)
    m_main.open()
