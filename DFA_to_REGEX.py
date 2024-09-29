# folosesc tehnica de eliminat stari pt a converti DFA in EFA
# trebuie determinate toate drumurile de la starea initiala la cea finala pentru a construi o exp reg pt tot DFA-ul
def inputDataProcessingDFA():
    global no_states, Lstates, no_symbols, Lsymbols, initial_state, no_accepted_states, Laccepted_states, no_transitions, Ltransitions

    f = open("input.in")
    no_states = int(f.readline().strip()) # number (no.) of states
    Lstates = [int(x) for x in f.readline().strip().split()] # in ac mom nu conteaza nr de stari, din moment ce toate sunt scrise pe o linie
    no_symbols = int(f.readline().strip())
    Lsymbols = [ch for ch in f.readline().strip().split()] # implicit e un sir de caractere
    initial_state = int(f.readline().strip())
    no_accepted_states = int(f.readline().strip())
    Laccepted_states = [int(x) for x in f.readline().strip().split()]

    # anterior am incercat sa folosesc implementarea lui dict_transitions de la tema trecuta, dar am realizat ca pentru functia newDictionary nu merge implementarea deoarece exista posibilitatea ca dintr-o satre sa se ajunga in alta stare prin doua sau mai multe muchii, si nu pot sa identific simbolul de la "coada la cap"
    # deci pentru simplitate este indeajuns o lista list_transitions cu tupluri de forma (current_state, symbol, target_state)
    Ltransitions = list()
    no_transitions = int(f.readline().strip())
    for i in range(no_transitions):
        line_transition = f.readline().strip().split() # fiecare linie reprezinta de fapt o tranzitie vazuta ca un tuplu care poate fi despachetat, de forma (current_state, symbol, target_state)
        t_transition = (int(line_transition[0]), line_transition[1], int(line_transition[2]))
        Ltransitions.append(t_transition)

    print(no_states, Lstates, no_symbols, Lsymbols, initial_state, no_accepted_states, Laccepted_states, no_transitions, Ltransitions, sep="\n")
    f.close()

inputDataProcessingDFA()

# inainte de parcurgerea in sine trebuie verificate starea initiala si finala
def reconstructInitialFinalStatesLtransitions():
    global Lstates, initial_state, Laccepted_states, Ltransitions

    # daca starea initiala este si finala sau daca exista cel putin o alta stare care intra in cea initiala, trebuie adaugata o noua stare initiala si o λ-miscare catre fosta stare initiala
    ok_init = True # presupun ca e in regula
    if initial_state in Laccepted_states: # daca e stare initiala si finala in acelasi timp
        ok_init = False
    else: # continua verificarea
        for t_transition in Ltransitions:
            if initial_state == t_transition[2]:
                ok_init = False
                break
    if ok_init == False:
        # se adauga o noua stare initiala + lambda tranzitii
        prev_initial_state = initial_state
        initial_state = int(-1)
        Lstates.append(initial_state)
        new_transition = (initial_state, 'λ', prev_initial_state)
        Ltransitions.append(new_transition)

    # daca starea finala nu este unica sau daca exista cel putin o muchie care pleaca din starea finala, trebuie adaugata o noua stare finala spre care se duc muchii de la fostele stare/i finala/e
    ok_fin = True
    final_state = Laccepted_states[0]
    if len(Laccepted_states) != 1:  # daca starea finala nu e unica
        ok_fin = False
    else:  # daca starea finala e unica se verifica daca are succesori
        for t_transition in Ltransitions:
            if final_state == t_transition[0]:
                ok_fin = False
                break
    if ok_fin == False:
        # se adauga o noua stare finala + lambda tranzitii
        # nu am garantia ca exista o singura stare finala
        next_final_state = int(-2)
        for final_state in Laccepted_states:
            new_transition = (final_state, 'λ', next_final_state)
            Ltransitions.append(new_transition)
        Lstates.append(next_final_state)
        Laccepted_states = [next_final_state] # pt a te referi la starea finala => Laccepted_states[0]
    print(Ltransitions, initial_state, Laccepted_states[0])

reconstructInitialFinalStatesLtransitions()

def newDictionary():
    global Ltransitions, dict_transitions

    dict_transitions = dict()
    for t_transition in Ltransitions:
        current_state, symbol, target_state = t_transition
        if current_state not in dict_transitions.keys():
            dict_transitions[current_state] = dict()
        if symbol not in dict_transitions[current_state]:
            dict_transitions[current_state][symbol] = [target_state]
        else:
            dict_transitions[current_state][symbol].append(target_state) # lista de target states
    dict_transitions[Laccepted_states[0]] = dict() # starea finala nu va avea nicio muchie care iese din ea, deci se atribuie un dictionar imbricat vid
    print(dict_transitions)

newDictionary()

def DFA_to_RE():
    global Lstates, initial_state, Laccepted_states, dict_transitions, regex

    Lvalid_states = list()
    for state in Lstates:
        if state != initial_state and state != Laccepted_states[0] and state in dict_transitions.keys():
            Lvalid_states.append(state)
    while len(Lvalid_states) > 0:
        current_state = Lvalid_states[0]
        Lvalid_states.remove(current_state)

        Lprev = list() # lista formata din tupluri de forma (prev_state, exp, current_state)
        Lnext= list() # lista formata din tupluri de forma (current_state, exp, next_state)
        Lself = list() # lista formata din tupluri de forma (current_state, exp, current_state)
        # construirea efectiva a listelor
        for state in dict_transitions.keys():
            for symbol, Ltarget_states in dict_transitions[state].items():
                for target_state in Ltarget_states:
                    t_transition = (state, symbol, target_state)
                    if state == target_state and state == current_state:
                        Lself.append(t_transition)
                    elif state != target_state and state == current_state:
                        Lnext.append(t_transition)
                    elif current_state == target_state and state != current_state:
                        Lprev.append(t_transition)
        print(Lprev, Lself, Lnext, sep='\n', end='\n\n')

        # eliminare tranzitii inainte de modificarea Lprev
        for state, symbol, target_state in Lprev:
            dict_transitions[state][symbol].remove(target_state)
            # daca lungimea listei asociate unui simbol este 0, se elimina cheia (symbol) a dictionarului imbricat pt ca ar insemna ca au fost procesate toate tranzitiile care au acel simbol
            if len(dict_transitions[state][symbol]) == 0:
                del dict_transitions[state][symbol]
            if len(dict_transitions[state]) == 0:
                del dict_transitions[state] # nu se elimina inregistrarea in dictionar pentru -2 sau vechea stare finala datorita parcurgerii folosind current_state
            print(f"Eliminare tranzitie ({state}, {symbol}, {target_state}):")
            print(dict_transitions)
        del dict_transitions[current_state]

        # construirea noilor muchii si introd in dict_transitions
        exp_curr_curr = ''
        Lself_nolambda = list() # doar simbolul in loc de tuplul tranzitie se va retine in lista, pt a face join intre simboluri
        for t_transition in Lself:
            symbol = t_transition[1]
            if symbol != 'λ':
                Lself_nolambda.append(symbol)
        if len(Lself_nolambda) > 0:
            exp_curr_curr = '|'.join(Lself_nolambda)
        for t_transition_prev_curr in Lprev:
            prev_state, exp_prev_curr = t_transition_prev_curr[0], t_transition_prev_curr[1]
            for t_transition_curr_next in Lnext:
                exp_curr_next, next_state = t_transition_curr_next[1], t_transition_curr_next[2]
                if exp_curr_curr != '':
                    new_exp = f"{exp_prev_curr}({exp_curr_curr})*{exp_curr_next}"
                else:
                    new_exp = f"{exp_prev_curr}{exp_curr_curr}{exp_curr_next}"
                Lnew_exp = list()
                for symbol in new_exp: # eliminare lambda la concatenare
                    if symbol != 'λ':
                        Lnew_exp.append(symbol)
                new_exp = ''.join(Lnew_exp)
                print(f"Valoarea expresiei finale: {new_exp}")

                # adaugare tranzitie noua dictionar pentru a putea reuni exp de la starea initiala la cea finala
                if prev_state not in dict_transitions:
                    dict_transitions[prev_state] = dict()
                if new_exp not in dict_transitions[prev_state]:
                    dict_transitions[prev_state][new_exp] = list()
                dict_transitions[prev_state][new_exp].append(next_state)
                print("Dictionarul dupa adaugarea noii stari:", dict_transitions)

        Lregex = []
        if initial_state in dict_transitions:
            for exp, Ltarget_states in dict_transitions[initial_state].items():
                if Laccepted_states[0] in Ltarget_states:
                    Lregex.append(exp)
            regex = '|'.join(Lregex)

DFA_to_RE()
print(regex)