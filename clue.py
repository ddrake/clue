from logic_tree import *
from menu import Menu

class Player:
    def __init__(self, name, ncards, is_cpu, knowns=None):
        self.name = name
        self.ncards = ncards
        self.is_cpu = is_cpu
        self.hand = tree()
        if self.is_cpu:
            self.hand.add_neg(list(allcardset() - set(knowns)))
            for k in knowns:
                self.hand.add_pos([k])

    def print_hand(self):
        pos = [ALLCARDS[num] for num in self.hand.pos_elements()]
        neg = [ALLCARDS[num] for num in self.hand.neg_elements()]
        posstr = 'In hand: {}'.format(', '.join(pos))
        negstr = 'Not in hand: {}'.format(', '.join(neg))
        print(self.name)
        if pos: print(posstr)
        if neg: print(negstr)
        
    def print_hand_tree(self):
        print(self.name)
        self.hand.print()

    def update_for_no(self, query):
        self.hand.add_neg(query)

    def update_for_yes(self, query):
        self.hand.add_pos(query)
    
    def update_for_card(self, card):
        self.hand.add_pos([card])

    def possibles(self):
        poss = self.hand.possibles()
        return [[ALLCARDS[n] for n in sub] for sub in poss]

#-----------
# UI Helpers
#-----------
def inp():
    return input("> ")

def get_bool(prompt):
    print(prompt + ' (y/n)')
    resp = inp()
    return True if resp.upper() == 'Y' else False if resp.upper() == 'N' else None

def get_string(prompt):
    print(prompt)
    return inp()

def get_int(prompt):
    print(prompt)
    while True:
        resp = inp()
        try:
            result = int(resp)
            return result
        except(ValueError):
            pass

def get_list(prompt, n):
    print(prompt)
    while True:
        resp = inp()
        result = resp.strip().split()
        if len(result) == n:
            try:
                result = [int(x) for x in result]
                return result
            except(ValueError):
                pass

def sync_players(players):
    for p in players:
        for p1 in players:
            if p != p1:
                for n in (p.hand.pos_elements() - p1.hand.neg_elements()):
                    p1.hand.add_neg([n])

def base_to_zero(nums):
    return [n-1 for n in nums]

def all_query(nums):
    s,w,r = nums
    return [ALLCARDS.index(SUSPECTS[s-1]), ALLCARDS.index(WEAPONS[w-1]), ALLCARDS.index(ROOMS[r-1])]

def allcardset():
    return set(range(len(ALLCARDS)))

def get_responders(players, suggester):
    si = players.index(suggester)
    return players[si+1:] + players[:si]

def add_suggestion(players):
    for i, p in enumerate(players):
        print(i+1, p.name)

    pnum = get_int("Enter player who suggested")
    print(pnum)
    try:
        suggester = players[pnum-1]
    except(IndexError) as err:
        return

    confirm = get_bool("Suggester is {}. OK?".format(suggester.name))
    if not confirm: return

    for i,s in enumerate(SUSPECTS):
        print(i+1, s)
    print()
    for i,w in enumerate(WEAPONS):
        print(i+1, w)
    print()
    for i,r in enumerate(ROOMS):
        print(i+1, r)
    numlist = get_list("Enter numbers for suggestion separated by spaces", 3)
    numquery = all_query(numlist)
    s,w,r = numlist
    query = [SUSPECTS[s-1], WEAPONS[w-1], ROOMS[r-1]]
    confirm = get_bool("Got {} OK?".format(query))
    if not confirm: return
    responders = get_responders(players, suggester)
    for player in responders:
        if player.is_cpu:
            if player.hand.contains_any(numquery):
                print("CPU showed a card")
                input("press <Enter>...")
                break
        else:
            print()
            print("Response from {}".format(player.name))
            if suggester.is_cpu:
                print_all_cards()
                print(query)
                cnum = get_int("Enter card shown or 0 if none")
                if cnum == 0:
                    player.update_for_no(numquery)
                else:
                    try:
                        card = ALLCARDS[cnum-1]
                    except(IndexError):
                        return
                    player.update_for_card(cnum-1)
                    break
            else:
                print(query)
                resp = get_int("Enter 1 if card was shown or 0 if not")
                if resp not in[0,1]: return
                if resp == 0:
                    player.update_for_no(numquery)
                else:
                    player.update_for_yes(numquery)
                    break

def add_player(players):
    name = get_string("Player name")
    ncards = get_int("Number of cards")
    is_cpu = False
    if len(players) == 0 or not any(p for p in players if p.is_cpu):
        is_cpu = get_bool("Is this player the CPU?")
        confirm = get_bool("Got {}, {} cards, {}. OK?"\
                .format(name, ncards, "CPU" if is_cpu else "not CPU"))
        if not confirm: return
    knowns = None
    if is_cpu:
        print_all_cards()
        result = get_list("Enter card numbers separated by spaces", ncards)
        try:
            knowns = [ALLCARDS[i-1] for i in result]
        except(IndexError):
            return
        confirm = get_bool("Got {}. OK?" \
                .format(knowns))
        if not confirm: return
        players.append(Player(name, ncards, is_cpu, base_to_zero(result)))
    else:
        players.append(Player(name, ncards, is_cpu))
    set_player_options(players)

def print_all_cards():
    for i,c in enumerate(ALLCARDS):
        print(i+1, c)

def delete_player(players):
    confirm = get_bool("Are you sure you want to delete player {}" \
            .format(current_player.name))
    if not confirm: return
    players.remove(current_player)
    set_player_options(players)

def possible_solution(players):
    diff = possible_solution_nums(players)
    return [ALLCARDS[c] for c in diff]

def definite_solution(players):
    defs = definite_solution_nums(players)
    return [ALLCARDS[c] for c in defs]

def found_solution(players):
    return len(definite_solution(players)) == 3

def likely_solution(players):
    likes = likely_solution_nums(players)
    return sorted([(ALLCARDS[n], ct) for n, ct in likes], key=lambda tp: tp[1], reverse=True)

def print_possible_solution(players):
    print(possible_solution(players))
    input("press <Enter>...")

def print_definite_solution(players):
    print(definite_solution(players))
    input("press <Enter>...")

def print_likely_solution(players):
    print(likely_solution(players))
    input("press <Enter>...")

def print_player_possibles(players):
    for p in players:
        print(p.name)
        print(p.possibles())
        print()
    input("press <Enter>...")

def definite_solution_nums(players):
    none = [p.hand.neg_elements() for p in players]
    if none:
        nset = none[0]
        for s in none:
            nset = nset.intersection(s)
    return nset

def likely_solution_nums(players):
    not_in_hand = [p.hand.neg_elements() for p in players]
    d = {}
    for sub in not_in_hand:
        for n in sub:
            d.setdefault(n,[]).append(n)
    return [(k, len(v)) for k,v in d.items()]

def possible_solution_nums(players):
    knowns = [list(p.hand.pos_elements()) for p in players]
    knowns = set(k for lst in knowns for k in lst)
    return allcardset() - knowns

def player_hands(players):
    for player in players:
        player.print_hand()
        print()
    input("press <Enter>...")

def player_hand_trees(players):
    for player in players:
        print(player.hand.simple())
        print()
    input("press <Enter>...")

#----------------
# Menu Setup
#----------------
def set_main_options(players):
    m_main.title = "Clue"
    m_main.options = []
    m_main.add_option("Quit", m_main.close)
    m_main.add_option("Add Suggestion", lambda: add_suggestion(players))
    m_main.add_option("Sync Players", lambda: sync_players(players))
    m_main.add_option("Player hands", lambda: player_hands(players))
    m_main.add_option("Player possibles", lambda: print_player_possibles(players))
    m_main.add_option("Possible solution cards", lambda: print_possible_solution(players))
    m_main.add_option("Likely solution cards", lambda: print_likely_solution(players))
    m_main.add_option("Definite solution cards", lambda: print_definite_solution(players))
    m_main.add_option("Manage Players", m_player.open)
 
def set_player_options(players):
    m_player.options = []
    m_player.add_option("Return to Main Menu", m_player.close) 
    m_player.add_option("Add Player", lambda: add_player(players))
    for player in players:
        m_player.add_option(player.name, lambda p=player: set_player_open_del(p))

def set_player_del_options(players):
    m_player_del.options = []
    m_player_del.add_option("Return to Player List", \
            m_player_del.close)
    m_player_del.add_option("Delete", lambda: delete_player(players))

def set_player_open_del(player):
    global current_player
    current_player = player
    print(player.name)
    m_player_del.open()


#-------------
# Main Program
#-------------
SUSPECTS = ['Colonel Mustard','Mr. Green', 'Professor Plum', 
                'Miss Scarlet', 'Ms White', 'Mrs. Peacock']
WEAPONS = ['lead pipe', 'candlestick', 'rope', 'knife', 
                'wrench', 'pistol']
ROOMS = ['hall', 'conservatory', 'library', 'dining room', 
                'kitchen', 'billiard room', 'study', 'lounge','ball room']
ALLCARDS = SUSPECTS + WEAPONS + ROOMS

if __name__ == '__main__':
    players = [ Player('Dow',3,True,[0, 12, 19]), 
                Player('Tave',4,False), 
                Player('Osanna',3,False), 
                Player('Lucinda',4,False),
                Player('Nathan',4,False) ]

    current_player = None
    m_main = Menu(title = "Main Menu")
    m_player = Menu(title = "Manage Players")
    m_player_del = Menu(title = "Edit/Delete Player")
    set_main_options(players)
    set_player_options(players)
    set_player_del_options(players)
    m_main.open()

