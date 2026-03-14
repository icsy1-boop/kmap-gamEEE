# Boolean expression minimalization using Quine-McCluskey algorithm & Petrick's method
# https://en.wikipedia.org/wiki/Quine-McCluskey_algorithm
# https://en.wikipedia.org/wiki/Petrick%27s_method

# TODO:
#  - [DONE] Include answer checker
#  - Create randomizer for easy, medium, and hard questions
#  - [DONE] Change minimizePrimeImplicants result to list of list of set for literals, just make a separate print function for readability
#  - check randomizer if its all 1's or 0's 
#  - [DONE?] add checks for inputs in checkAnswer

import copy, random, numpy as np, numpy.random as npr, re

if __name__ == "__main__":
    import group_generator as gg
else:
    import kmap.group_generator as gg
    

def randomizeQuestion(difficulty: int, num_dc_override: int | None = None) -> tuple[int, str, list[int], list[int]]:
    
    """
    Generates a random question by giving a list of minterms/maxterms and don't cares.

    What makes a K-Map easy or difficult to solve? The following are used as a starting point in this function: 
    - Number of variables
    - Number of groups (POS/SOP terms in final expression) and size of groups
    - number of overlapping groups

    With this, `randomizeQuestion()` defines the following difficulties:
    ### Easy
    - Expressions only up to 4 variables
    - Up to 3 groups in minimal expression
    - None or 1 overlapping group
    
    :param difficulty: Difficulty of question to be generated. Possible values: 1 = easy, 2 = medium, 3 = hard, 4 = random.
    :type difficulty: int
    :param num_dc_override: Override for number of don't cares. Use 0 to disable don't cares.
    :type num_dc_override: int | None

    :rtype: tuple[ num_var, form, terms, dont_cares ]
    :returns: `randomizeQuestion()` returns a tuple of the following arguments needed for `getPrimeImplicants()` and `minimizePrimeImplicants()`.
    
    :returns num_var: `int`, number of variables in boolean expression
    :returns form: `"min"` or `"max"`, determines if the given terms are minterms or maxterms. Defaults to `"min"`.
    :returns terms: `list[int]`, list of given min/maxterms as integers
    :returns dont_cares: `list[int]`, list of don't cares. Defaults to an empty list.
    
    """
    terms = []
    dont_cares = []

    if difficulty == 1:
        # For easy difficulty:
        # - Expressions only up to 3 terms
        # - Either 2, 3, 4 variables with p = [0.3, 0.4, 0.3] respectively
        # - No multiple answers (hopefully?)
        # - Mostly SOP
        # - No don't cares

        # Set number of variables, groups, and form
        num_var = npr.choice([2, 3], p = [0.5, 0.5])
        num_groups = random.randint(1, 2 if num_var == 2 else 3)
        form = npr.choice(["min", "max"], p = [0.7, 0.3])
        # set dont cares
        num_dc = 0
        if num_dc_override is not None:
            num_dc = max(0, min(int(num_dc_override), (2**num_var) - 1))
        dc_in = 0
        dc_out = num_dc - dc_in
        s_o_probs = [0.5, 0.5]
        
    elif difficulty == 2:
        # For medium difficulty:
        # - 3 or 4 variables with p = [0.25, 0.75]
        # - Expressions from 3 to 4 terms
        # - 50/50 SOP/POS
        # - Up to 2 don't cares

        # Set number of variables, groups, and form
        num_var = npr.choice([3, 4], p = [0.3, 0.7])
        num_groups = random.randint(2, 2**(num_var-1))
        form = npr.choice(["min", "max"], p = [0.5, 0.5])
        # set dont cares
        num_dc = random.randint(0, 6)
        if num_dc_override is not None:
            num_dc = max(0, min(int(num_dc_override), (2**num_var) - 1))
        dc_in = num_dc
        dc_out = num_dc - dc_in
        s_o_probs = [0.5, 0.5]

    elif difficulty == 3:
        # For hard difficulty:
        # - 4 or 5 variables with p = [0.7, 0.3]
        # - Groups up to 4 - 6 terms (or as much as possible)
        # - 30/70 SOP/POS
        # - Up to 6 don't cares
        
        # Set number of variables, groups, and formsss
        num_var = npr.choice([5, 6], p = [0.5, 0.5])
        num_groups = random.randint(3, 2**(num_var-1))
        form = npr.choice(["min", "max"], p = [0.6, 0.4])
        # set dont cares
        num_dc = random.randint(1, 10)
        if num_dc_override is not None:
            num_dc = max(0, min(int(num_dc_override), (2**num_var) - 1))
        dc_in = random.randint(0, num_dc)
        dc_out = num_dc - dc_in
        s_o_probs = [0.5, 0.5]
    
    elif difficulty == 4:
        # TODO: Fix random difficulty, DO NOT USE FOR ACTUAL QUESTIONS UNTIL FIXED
        num_var = random.randint(4, 6)
        terms = sorted(npr.choice(range(2**num_var), size=random.randint(int((2**num_var)/8), int((2**num_var)/2)), replace=False).tolist())
        num_dc = random.randint(0, 3)
        if num_dc_override is not None:
            num_dc = max(0, min(int(num_dc_override), (2**num_var) - 1))
        if num_dc != 0:
            dont_cares = sorted(npr.choice(terms, size=min(num_dc, len(terms)-1), replace=False).tolist())
            for dc in dont_cares:
                terms.remove(dc)
        form = random.choice(["min", "max"])

    separate_groups = []
    overlapping_groups = []
    possible_s_groups = gg.generateGroups(num_var)
    orig_groups = copy.deepcopy(possible_s_groups)
    possible_o_groups = [[] for _ in range(num_var)]
    dont_cares = []

    # Group picker proper
    while num_groups > 0:
        # Stop if no more possible choices
        if len(possible_s_groups) == 0 and all(len(group_sizes) == 0 for group_sizes in possible_o_groups):
            break
        
        # Choose group type
        if len(possible_s_groups) == 0 and any(len(group_sizes) > 0 for group_sizes in possible_o_groups):
            c_type = "overlapping"
        elif all(len(group_sizes) == 0 for group_sizes in possible_o_groups) or (len(separate_groups) == 0 and len(overlapping_groups) == 0):
            c_type = "separate"
        else:
            c_type = npr.choice(["separate", "overlapping"], p=s_o_probs) 

        # Group type setter
        if c_type == "separate":
            chosen_group_set = separate_groups
            possible_group_set = possible_s_groups
        else:
            chosen_group_set = overlapping_groups
            possible_group_set = possible_o_groups
        
        # randomly choose in possible groups
        while True:
            c_group_size = random.randint(0, len(possible_group_set) - 1)
            if len(possible_group_set[c_group_size]) > 0:
                break
        c_group_idx = random.randint(0, len(possible_group_set[c_group_size])-1)
        chosen_group = possible_group_set[c_group_size][c_group_idx]
        # print(chosen_group)

        # add to group set and remove from possible choices
        chosen_group_set.append(chosen_group)
        possible_group_set[c_group_size].remove(chosen_group)
        if c_type == "overlapping":
            for group in separate_groups:
                if any([term in chosen_group for term in group]):
                    separate_groups.remove(group)
                    overlapping_groups.append(group)

        # Remove unusable groups
        to_be_removed = []
        can_be_overlapped = []
        for other_group, o_group_size in [(group, group_size) for group_size in range(len(possible_s_groups)) for group in possible_s_groups[group_size]] + [(group, group_size) for group_size in range(len(possible_o_groups)) for group in possible_o_groups[group_size]]:
            if all([term in chosen_group for term in other_group]): # remove sub groups (also current group)
                to_be_removed.append((o_group_size, other_group))
            elif all([term in other_group for term in chosen_group]):  # remove parent groups
                to_be_removed.append((o_group_size, other_group))
            elif any([term in chosen_group for term in other_group]): # remove overlapping groups
                to_be_removed.append((o_group_size, other_group))
                can_be_overlapped.append((o_group_size, other_group))
            else: # remove forming groups (groups that will be formed by combining current and other group)
                curr_terms = set([term for group in separate_groups for term in group] + [term for group in overlapping_groups for term in group] )
                new_terms = copy.deepcopy(curr_terms)
                new_terms.update(set([term for term in other_group]))
                


                # Check if adding current group will form a new group
                unused_groups = [g for gs in orig_groups for g in gs]
                for g in [g for g in separate_groups] + [g for g in overlapping_groups]:
                    unused_groups.remove(g)
                for g in unused_groups:
                    if  ((any([term not in other_group for term in g]) and 
                            any([term not in curr_terms for term in g]) and 
                            all([term in new_terms for term in g])) or
                            all([term in new_terms for term in range(2**num_var)])):
                        # possible_groups[o_group_size].remove(other_group)
                        to_be_removed.append((o_group_size, other_group))
                        for gs2, g2 in [(possible_s_groups.index(gs), g3) for gs in possible_s_groups for g3 in gs] + [(possible_o_groups.index(gs),g4) for gs in possible_o_groups for g4 in gs]:
                            if all(term in g for term in g2):
                                to_be_removed.append((gs2, g2))
                        break
                
                # Check if adding current group will remove an existing group
                for g in separate_groups + overlapping_groups:
                    new_terms_2 = [term for group in separate_groups for term in group] + [term for group in overlapping_groups for term in group] 
                    for term in g:
                        new_terms_2.remove(term)
                    for term in other_group:
                        new_terms_2.append(term)
                    new_terms_2 = set(new_terms_2)    
                    if all([term in new_terms_2 for term in curr_terms]):
                        to_be_removed.append((o_group_size, other_group))
                        break

        # Update possible groups by removing all to be removed groups
        for size, term in to_be_removed:
            if len(possible_s_groups) - 1 >= size:
                if term in possible_s_groups[size]:
                    possible_s_groups[size].remove(term)
            if len(possible_o_groups) - 1 >= size:
                if term in possible_o_groups[size]:
                    possible_o_groups[size].remove(term)

        # Update possible overlapping groups
        for size, term in can_be_overlapped:
            if term not in possible_o_groups[size]:
                possible_o_groups[size].append(term)


        # Clean up possible groups by removing empty group sizes
        possible_s_groups = list(filter(lambda group_size: len(group_size) > 0, possible_s_groups))

        num_groups -= 1

    final_terms = list(set([int(term) for group in separate_groups for term in group] + [int(term) for group in overlapping_groups for term in group]))

    possible_dc = [(group, group_size) for group_size in range(len(possible_s_groups)) for group in possible_s_groups[group_size]]
    possible_dc += [(group, group_size) for group_size in range(len(possible_o_groups)) for group in possible_o_groups[group_size]]
    dc_out_arr = []
    if len(possible_dc) > 0:
        dc_out_arr = random.choice(possible_dc)
        dc_out_arr = list(filter(lambda term: term not in terms, dc_out_arr[0]))
    
    groups = separate_groups + overlapping_groups

    for _ in range(dc_out):
        if len(dc_out_arr) == 0:
            break
        dc = random.choice(dc_out_arr)
        dc_out_arr.remove(dc)
        dont_cares.append(int(dc))
    dc_in = num_dc - len(dont_cares)
    for _ in range(dc_in):
        if len(final_terms) == 0:
            break
        can_dc_terms = [[x in group for group in groups].count(True) >= 2 for x in final_terms]
        if can_dc_terms.count(True) == 0:
            break
        else:
            dc_idx = random.choice([i for i, val in enumerate(can_dc_terms) if val])
            dc = final_terms[dc_idx]
            final_terms.pop(dc_idx)
            dont_cares.append(int(dc)) 
                
        # for x in range(3):
        #     dc = random.choice(final_terms)
        #     if [dc in group for group in groups].count(True) >= 2:
        #         break
        #     else:
        #         continue         
        # else:
        #     break
               
         

    # 0 - non cut group
    # 1 - group divided into left/right
    # 2 - group divided into top/bottom
    # 3 - group divided into 4


    _, terms = gg.generateTerms(num_var)

    
    groupings = [] # [group #, type of group, kind of anchor element (0, 1, 2, 3 for top left/right, bottom left/right), index row, index col, size of vertical, size of horizontal]
    for i in range(len(groups)):
        group = groups[i]
        group_indices = []
        # transforming them into coordinates.
        for term in group:
            group_indices.extend(list(zip(*np.where(terms == term))))

        if len(group_indices[0]) == 3:
            group_indices = [(r, c, l) for (l, r, c) in group_indices]
        elif len(group_indices[0]) == 4:
            group_indices = [(r, c, lr, lc) for (lr, lc, r, c) in group_indices]

        # inside the group, make a subgroup based on their layer
        overall_group_indices = []
        if num_var == 6:
            overall_group_indices = [[group for group in group_indices if group[2] * 2 + group[3] == i] for i in range(4)]      
        elif num_var == 5:
            overall_group_indices = [[group for group in group_indices if group[2] == i] for i in range(2)]
        else:
            overall_group_indices = [group_indices]

        for layer_idx, group_indices in enumerate(overall_group_indices):
            if len(group_indices) == 0:
                continue

            row_indices =  sorted(list(set([group[0] for group in group_indices])))
            col_indices = sorted(list(set([group[1] for group in group_indices])))

            group_type = 0
            if any(row_index not in row_indices for row_index in range(min(row_indices), max(row_indices) + 1)):
                group_type = 2
            if any(col_index not in col_indices for col_index in range(min(col_indices), max(col_indices) + 1)):
                if group_type == 2:
                    group_type = 3
                else:
                    group_type = 1

            if group_type == 0:
                groupings.append([i, 0, 0, int(min(group_indices)[0]), int(min(group_indices)[1]), len(row_indices), len(col_indices), layer_idx])
            elif group_type == 1:
                groupings.append([i, 1, 0, int(min(group_indices)[0]), int(min(group_indices)[1]), len(row_indices), len(col_indices)/2, layer_idx])
                groupings.append([i, 1, 1, int(min(group_indices)[0]), int(max(group_indices)[1]), len(row_indices), len(col_indices)/2, layer_idx])
            elif group_type == 2:
                groupings.append([i, 2, 0, int(min(group_indices)[0]), int(min(group_indices)[1]), len(row_indices) / 2, len(col_indices), layer_idx])
                groupings.append([i, 2, 1, int(max(group_indices)[0]), int(min(group_indices)[1]), len(row_indices) / 2, len(col_indices), layer_idx])
            elif group_type == 3:
                groupings.append([i, 3, 3, int(min(group_indices)[0]), int(min(group_indices)[1]), 1, 1, layer_idx])
                groupings.append([i, 3, 2, int(min(row_indices)), int(max(col_indices)), 1, 1, layer_idx])
                groupings.append([i, 3, 1, int(max(row_indices)), int(min(col_indices)), 1, 1, layer_idx])
                groupings.append([i, 3, 0, int(max(group_indices)[0]), int(max(group_indices)[1]), 1, 1, layer_idx])


    return num_var, form, final_terms, dont_cares, groupings


def _apply_term_letter_mapping(num_var: int) -> list[str]:
    terms = [chr(65 + x) for x in range(num_var)]
    if num_var == 2:
        terms[0], terms[1] = terms[1], terms[0]
    elif num_var == 3:
        terms[0], terms[1], terms[2] = terms[2], terms[0], terms[1]
    elif num_var == 4:
        terms[0:2], terms[2:4] = terms[2:4], terms[0:2]
    elif num_var == 5:
        terms[1:3], terms[3:5] = terms[3:5], terms[1:3]
    elif num_var == 6:
        terms[0], terms[1], terms[2:4], terms[4:6] = terms[1], terms[0], terms[4:6], terms[2:4]
    return terms


def _implicant_to_literal_set(num_var: int, implicant: str, form_terms: str = "min") -> set[str]:
    mapped_terms = _apply_term_letter_mapping(num_var)
    literals = set()
    for idx, ch in enumerate(implicant):
        if ch == "-":
            continue
        if form_terms == "min":
            literals.add(mapped_terms[idx] if ch == "1" else mapped_terms[idx] + "'")
        else:
            literals.add(mapped_terms[idx] + "'" if ch == "1" else mapped_terms[idx])
    return literals


def _groups_to_groupings(num_var: int, groups: list[set[int]]) -> list[list[int]]:
    _, terms = gg.generateTerms(num_var)
    groupings = []
    for i in range(len(groups)):
        group = groups[i]
        group_indices = []
        for term in group:
            group_indices.extend(list(zip(*np.where(terms == term))))

        if len(group_indices) == 0:
            continue

        if len(group_indices[0]) == 3:
            group_indices = [(r, c, l) for (l, r, c) in group_indices]
        elif len(group_indices[0]) == 4:
            group_indices = [(r, c, lr, lc) for (lr, lc, r, c) in group_indices]

        overall_group_indices = []
        if num_var == 6:
            overall_group_indices = [[group for group in group_indices if group[2] * 2 + group[3] == i] for i in range(4)]
        elif num_var == 5:
            overall_group_indices = [[group for group in group_indices if group[2] == i] for i in range(2)]
        else:
            overall_group_indices = [group_indices]

        for layer_idx, group_indices in enumerate(overall_group_indices):
            if len(group_indices) == 0:
                continue

            row_indices = sorted(list(set([group[0] for group in group_indices])))
            col_indices = sorted(list(set([group[1] for group in group_indices])))

            group_type = 0
            if any(row_index not in row_indices for row_index in range(min(row_indices), max(row_indices) + 1)):
                group_type = 2
            if any(col_index not in col_indices for col_index in range(min(col_indices), max(col_indices) + 1)):
                if group_type == 2:
                    group_type = 3
                else:
                    group_type = 1

            if group_type == 0:
                groupings.append([i, 0, 0, int(min(group_indices)[0]), int(min(group_indices)[1]), len(row_indices), len(col_indices), layer_idx])
            elif group_type == 1:
                groupings.append([i, 1, 0, int(min(group_indices)[0]), int(min(group_indices)[1]), len(row_indices), len(col_indices)/2, layer_idx])
                groupings.append([i, 1, 1, int(min(group_indices)[0]), int(max(group_indices)[1]), len(row_indices), len(col_indices)/2, layer_idx])
            elif group_type == 2:
                groupings.append([i, 2, 0, int(min(group_indices)[0]), int(min(group_indices)[1]), len(row_indices) / 2, len(col_indices), layer_idx])
                groupings.append([i, 2, 1, int(max(group_indices)[0]), int(min(group_indices)[1]), len(row_indices) / 2, len(col_indices), layer_idx])
            elif group_type == 3:
                groupings.append([i, 3, 3, int(min(group_indices)[0]), int(min(group_indices)[1]), 1, 1, layer_idx])
                groupings.append([i, 3, 2, int(min(row_indices)), int(max(col_indices)), 1, 1, layer_idx])
                groupings.append([i, 3, 1, int(max(row_indices)), int(min(col_indices)), 1, 1, layer_idx])
                groupings.append([i, 3, 0, int(max(group_indices)[0]), int(max(group_indices)[1]), 1, 1, layer_idx])

    return groupings


def tutorial_solve(num_var: int, terms: list[int], dont_cares: list[int], form_terms: str = "min"):
    if form_terms == "min":
        if len(terms) == 0:
            return {"expression": "0", "groupings": []}
        if len(terms) + len(dont_cares) >= 2**num_var:
            return {"expression": "1", "groupings": []}
    else:
        if len(terms) == 0:
            return {"expression": "1", "groupings": []}
        if len(terms) + len(dont_cares) >= 2**num_var:
            return {"expression": "0", "groupings": []}

    prime_implicants = getPrimeImplicants(num_var=num_var, terms=terms, dont_cares=dont_cares, form_terms=form_terms)
    minimal_expressions = minimizePrimeImplicants(num_var=num_var, terms=terms, prime_implicants=prime_implicants, form_terms=form_terms)

    if len(minimal_expressions) == 0:
        return {"expression": "", "groupings": []}

    chosen_expression = minimal_expressions[0]
    expression_str = stringifyExpression(expression=chosen_expression, form_answer=form_terms)

    literal_sets = [set(expr) for expr in chosen_expression]
    implicants_by_literals = {frozenset(_implicant_to_literal_set(num_var, pi, form_terms)): pi for pi in prime_implicants}

    chosen_implicants = []
    for lit_set in literal_sets:
        pi = implicants_by_literals.get(frozenset(lit_set))
        if pi:
            chosen_implicants.append(pi)

    groups = []
    for pi in chosen_implicants:
        covered = set()
        for i in range(2**num_var):
            bits = bin(i).lstrip("0b").rjust(num_var, "0")
            if all(p == "-" or p == b for p, b in zip(pi, bits)):
                covered.add(i)
        if len(covered) > 0:
            groups.append(covered)

    groupings = _groups_to_groupings(num_var, groups)
    return {"expression": expression_str, "groupings": groupings}



def getPrimeImplicants(num_var: int, 
                       terms: list[int], 
                       dont_cares: list[int] = [],  
                       form_terms: str = "min",
                       ) -> list[str]:
    """
    Accepts a list of minterms or maxterms (as integers) and returns a list of prime implicants.

    :param num_var: Number of variables in boolean expression
    :type num_var: int
    :param terms: List of given min/maxterms as integers
    :type terms: list[int]
    :param dont_cares: List of don't cares. Defaults to an empty list.
    :type dont_cares: list[int], optional
    :param form_terms: `"min"` or `"max"`, determines if the given terms are minterms or maxterms. Defaults to `"min"`.
    :type form_terms: str, optional


    :return prime_implicants: List of binary strings of prime implicants with don't care digits as '-'.
    """
    prime_implicants = []
    merged_terms = [[] for _ in range(num_var + 1)] # Running group for number of 1's/0's in terms

    # Start to group terms with how many 1's/0's they have
    for term in list(map(lambda t: bin(t).lstrip("0b").rjust(num_var, "0"), terms + dont_cares)): # Convert to binary strings
        if form_terms.lower() == "min":
            count = term.count("1")
        elif form_terms.lower() == "max":
            count = term.count("0")
        merged_terms[count].append(term)

    merged_terms = list(filter(lambda b: b, merged_terms)) # Remove groups with no terms
    # print(merged_terms)

    # print("Current merged minterms:", merged_terms)


    while True:
        merged_terms_cache = [] # Cache to avoid adding duplicate unmatched terms, especially for largest group of terms
        new_merged_terms = [[] for _ in range(num_var + 1)]

        for j in range(len(merged_terms)-1): # Loop for every term group except last one
            for term1 in merged_terms[j]: # Loop for every term in current term group
                noMatches = True 
                for term2 in merged_terms[j+1]: # Check every term of next term group
                    
                    diff = -1 # index of only different digit
                    for d in range(len(term1)): # Check every digit of two terms
                        if term1[d] != term2[d] and diff == -1:
                            diff = d
                        elif term1[d] == term2[d]:
                            continue
                        else:
                            break # Stop if there's another difference
                    else: #
                        noMatches = False

                        # Save to cache for prime implicant saving
                        if term1 not in merged_terms_cache:
                            merged_terms_cache.append(term1)
                        if term2 not in merged_terms_cache:
                            merged_terms_cache.append(term2)

                        new_term = list(term1)
                        new_term[diff] = "-"
                        new_term = "".join(new_term)
                        if new_term not in new_merged_terms[j]: # Avoid repeating terms
                            new_merged_terms[j].append(new_term)

                if noMatches:
                    if term1 not in merged_terms_cache:
                        prime_implicants.append(term1)

        # Check last group of terms
        for mt in merged_terms[-1]:
            if mt not in merged_terms_cache:
                    prime_implicants.append(mt)

        if new_merged_terms == [[] for _ in range(num_var + 1)]: # If no new terms were merged
            # Add all remaining terms if not in current prime implicant list and finish loop
            for group in merged_terms:
                for mt in group:
                    if mt not in prime_implicants:
                        prime_implicants.append(mt)
            break 

        else: # If there are new minterms, repeat loop
            merged_terms = new_merged_terms
            merged_terms = list(filter(lambda b: b, merged_terms)) # Remove groups with no terms

    # print(prime_implicants)
    return prime_implicants



def minimizePrimeImplicants(num_var: int, 
                                terms: list, 
                                prime_implicants: list[str],
                                form_terms: str = "min"
                                ) -> list[list[set[str]]]:
    """
    Returns a list of all possible minimal expressions given a list of terms and prime implicants.
    The form of the minimal expression is dependent on the form of the given terms, i.e. minterms 
    produce a minimal SOP expression while maxterms produce a minimal POS expression.

    :param num_var: Number of variables in boolean expression
    :type num_var: int
    :param terms: List of given min/maxterms as integers
    :type terms: list[int]
    :param prime_implicants: List of prime implicants as strings of binary and '-' as don't cares.
    :type prime_implicants: list[str]
    :param form_terms: `"min"` or `"max"`, determines if the given terms are minterms or maxterms. Defaults to `"min"`.
    :type form_terms: str, optional

    :rtype: list[ list[ set[ str ] ] ]
    :returns: List of all possible minimal expressions. Each expression is a list of terms, 
    which are represented as a set of strings.
    """

    prime_implicant_chart: dict = {}
    terms = list(map(lambda mt: bin(mt).lstrip("0b").rjust(num_var, "0"), terms)) # Convert to strings of binary
    for pi in prime_implicants: # Add keys with empty string values in chart for every prime implicant
        prime_implicant_chart[pi] = ""

    # Fill up prime implicant chart
    for pi in prime_implicant_chart.keys(): # For every prime implicant...
        for term in terms: # ... check if they cover any term in list of terms
            for answer in range(len(pi)):
                if pi[answer] == term[answer] or pi[answer] == "-":
                    continue
                else:
                    prime_implicant_chart[pi] += "0"
                    break # Stop if prime implicant does not cover term
            else:
                prime_implicant_chart[pi] += "1"


    # Start of chart simplification (at this point, currently SOP of prime implicant literals?)
    curr_min_exp = [[] for _ in range(len(terms))]
    
    # Write initial expression
    for i in range(len(terms)):
        for pi in prime_implicant_chart.keys():
            if prime_implicant_chart[pi][i] == "1":
                curr_min_exp[i].append(prime_implicants.index(pi))


    # Minimize absorbing literals, e.g. (A)(A+B) = (A), (A+B)(A+B+C) = (A+B), ...
    temp_min_exp = copy.deepcopy(curr_min_exp)
    for curr_answer in curr_min_exp:
        for other_group in curr_min_exp:
            if curr_answer == other_group:
                continue
            elif all(literal in other_group for literal in curr_answer) and other_group in temp_min_exp:
                temp_min_exp.remove(other_group)
    curr_min_exp = temp_min_exp
                    
    # Minimize distributive groups with the same number of literals
    # Example: (A+B) (B+C) = (B + AC), (A+B+C)(A+B+D) = (A + B + CD),...
    # For now, this code block only processes groups with only 1 different literalm check if need to check for more
    while True:
        temp_min_exp = copy.deepcopy(curr_min_exp)
        for curr_answer in curr_min_exp:
            if len(curr_answer) < 2:
                continue
            for other_group in curr_min_exp:
                if curr_answer == other_group:
                    continue
                else:
                    curr_in_other = [literal in other_group for literal in curr_answer] # list of boolean if elements in curr_group are missing in other
                    other_in_curr = [literal in curr_answer for literal in other_group] # list of boolean if elements in other_group are missing in curr
                    if curr_in_other.count(False) == 1 and other_in_curr.count(False) == 1:
                        if curr_answer in temp_min_exp and other_group in temp_min_exp:
                            temp_min_exp.remove(curr_answer)
                            temp_min_exp.remove(other_group)
                            # Get all literals existing in both groups
                            new_literal = list(filter(lambda literal: curr_in_other[curr_answer.index(literal)], curr_answer))
                            # Get all literals that are different in both groups
                            curr_missing = list(filter(lambda literal: not curr_in_other[curr_answer.index(literal)], curr_answer))
                            other_missing = list(filter(lambda literal: not other_in_curr[other_group.index(literal)], other_group))
                            new_literal.append(tuple(curr_missing + other_missing))
                            temp_min_exp.append(new_literal)

        if curr_min_exp == temp_min_exp: # If no simplification was done
            break
        else:
            curr_min_exp = temp_min_exp


    # Multiply all POS to form SOPs
    new_min_exp = []
    while len(curr_min_exp) > 0:
        curr_group = []
        for group in curr_min_exp.pop(0):
            if type(group) is tuple:
                curr_group.append(''.join(str(val) for val in group))
            else:
                curr_group.append(group)

        if len(new_min_exp) == 0:
            if len(curr_min_exp) == 0:
                new_min_exp.append(curr_group)
            else:
                new_min_exp = curr_group
            continue 
        else:
            temp_minbool = []
            for el1 in new_min_exp:
                for el2 in curr_group:
                    temp_minbool.append(str(el1) + str(el2))
            new_min_exp = temp_minbool

    # Convert to sets to remove repeating literals, e.g. AAB = AB
    for i in range(len(new_min_exp)):
        new_min_exp[i] = sorted(list(set(list(new_min_exp[i]))))
    new_min_exp.sort(key=lambda x: len(x))

    # Remove all absorbing literals but in SOP form
    while True:
        temp_min_exp = copy.deepcopy(new_min_exp)
        for i in range(len(new_min_exp)):
            for j in range(i, len(new_min_exp)):
                curr_answer = new_min_exp[i]
                other_group = new_min_exp[j]
                if curr_answer == other_group:
                    continue
                elif len(other_group) > len(curr_answer) and [literal in other_group for literal in curr_answer].count(False) >= 1 and other_group in temp_min_exp:
                    temp_min_exp.remove(other_group)

        if new_min_exp == temp_min_exp:
            break
        else:
            new_min_exp = temp_min_exp

    # Get the smallest length groups
    min_length = min(len(x) for x in new_min_exp)
    minimal_expressions = list(filter(lambda x: len(x) == min_length, new_min_exp))
    # print(f"Minimal expression: {minimal_expressions}")

    # Get final expression from literals
    final_expressions = []
    terms = [chr(65+x) for x in range(num_var)]

    # brute force switching T_T sorry AHAHHA
    if num_var == 2:
        terms[0], terms[1] = terms[1], terms[0]
    elif num_var == 3:
        terms[0], terms[1], terms[2] = terms[2], terms[0], terms[1]
    elif num_var == 4:
        terms[0:2], terms[2:4] = terms[2:4], terms[0:2]
    elif num_var == 5:
        terms[1:3], terms[3:5] = terms[3:5], terms[1:3]
    elif num_var == 6:
        terms[0], terms[1], terms[2:4], terms[4:6] = terms[1], terms[0], terms[4:6], terms[2:4]
    # print(f"Terms: {terms}")
    for answer in minimal_expressions:
        curr_answer = []
        for group in answer:
            curr_group = set()
            for f in range(len(prime_implicants[int(group)])):
                if prime_implicants[int(group)][f] == "-":
                    continue
                elif prime_implicants[int(group)][f] == "1":
                    curr_group.add(str(terms[f]) if form_terms == "min" else str(terms[f]) + "'")
                elif prime_implicants[int(group)][f] == "0":
                    curr_group.add(str(terms[f]) + "'" if form_terms == "min" else str(terms[f]))
            curr_answer.append(curr_group)
        final_expressions.append(curr_answer)

    return final_expressions



def checkAnswer(minimal_expressions: list[list[set[str]]], input_answer: str, form_answer: str = "min") -> int:
    """
    Checks a given answer against the minimal expression given by `minimizePrimeImplicants()`.

    :param minimal_expressions: List of all possible minimal expressions. Each expression is a list of terms, 
    which are represented as a set of strings.
    :type minimal_expressions: list[list[set[str]]]
    :param input_answer: Given answer in string. Must only contain the following characters: ABCD\'()+ and space.
    :type input_answer: str
    :param form_terms: `"min"` or `"max"`, determines if the given terms are minterms or maxterms. Defaults to `"min"`.
    :type form_terms: str, optional

    :rtype result: int
    :returns:  Results in the following integer values:

            - `1` = input answer is correct
            - `0` = input answer is incorrect
            - `-1` = Answer contains other characters
            - `-2`= Answer is given in the wrong form (SOP/POS, does not guarantee correctness)
            - `-3`= Any other error caught by the checker (ideally should not be returned)
    
    """
    # Input parser
    try:
        if all(char in ['A', 'B', 'C', 'D', 'E', 'F', '\'', ' ', '(', ')', '+', '', '\u2018', '\u0027', '\u2019'] for char in input_answer) == False: 
            raise ValueError('Answer contains other characters besides ABCD\'()+.')
        else:
            input_answer = input_answer.replace(' ', '')
            input_answer = input_answer.replace('\u2018', '\'')
            input_answer = input_answer.replace('\u0027', '\'')
            input_answer = input_answer.replace('\u2019', '\'')
            if form_answer == "min":
                # Group minterms
                input_answer = input_answer.replace("(", '').replace(")", '').split('+')

                # Answer check
                if len(input_answer) == 0:
                    raise IndexError('Answer is given as POS, not SOP form.')

                # Group literals
                for i in range(len(input_answer)): # Loop through minterms
                    temp_term = []
                    for j in range(len(input_answer[i])): # Loop through literals
                        char = input_answer[i][j]
                        if char == '\'':
                            temp_term[-1] = temp_term[-1] + '\''
                        else:
                            temp_term.append(char)
                    input_answer[i] = set(temp_term)

            elif form_answer == "max":
                # Group maxterms
                input_answer = re.split('\)\(|\(|\)', input_answer)
                input_answer = list(filter(lambda x: x != "", input_answer))
                # Answer check
                if len(input_answer) == 0:
                    raise IndexError('Answer is given as SOP, not POS form.')

                # Clean max terms of parentheses and group literals
                for i in range(len(input_answer)):
                    input_answer[i] = set(input_answer[i].strip('()').split('+'))

            # print("Input answer:", input_answer)


    except ValueError: # Answer contains other characters besides ABCD\'()+.
        return -1
    except IndexError: # Answer is given in wrong form (SOP/POS).
        return -2
    except: # Catch all, answer is given in wrong format.
        return -3
    
    # Checker proper
    for answer in minimal_expressions:
        # print(answer)
        for term in answer:
            # print(term)
            if len(input_answer) == 1:
                if len(term) == len(input_answer[0]) and list(term)[0] in list(input_answer[0])[0]:
                    continue
                else:
                    print("oh no")
                    break
            else:
                if term in input_answer:
                    continue
                else:
                    break
        else:
            # print("Answer is right!")
            return 1
    else:
        # print("Answer is wrong!")
        return 0



def stringifyExpression(expression: list[set[str]], form_answer: str = "min") -> str:
    """
    Changes a boolean expression in minimal SOP/POS form into a string.

    :param minimal_expression: A minimal expression given as a list of terms, which are represented as a set of strings.
    :type minimal_expression: list[set[str]]
    :param form_terms: `"min"` or `"max"`, determines if the given terms are minterms or maxterms. Defaults to `"min"`.
    :type form_terms: str, optional

    :rtype: str
    :returns:  String equivalent of the given minimal expression.
    """
    stringified_expression = ""
    if form_answer == "min":
        expression.sort(key = lambda answer: len(answer))
        for i in range(len(expression)): # loop through every term
            if i != 0:
                stringified_expression += " + "
            term = sorted(expression[i])
            for literal in term:
                stringified_expression += literal
    if form_answer == "max":
        expression.sort(key = lambda answer: len(answer))
        for i in range(len(expression)): # loop through every term
            if i != 0:
                stringified_expression += " "
            stringified_expression += "("    
            term = sorted(expression[i])
            for j in range(len(term)):
                if j != 0:
                   stringified_expression += "+" 
                literal = term[j]
                stringified_expression += literal
            stringified_expression += ")"

    return stringified_expression

def minimizeAndCheck(   
        num_var: int, 
        terms: list[int], 
        dont_cares: list[int] = [],  
        form_terms: str = "min",
        input_answer: str = ""
        ):
    prime_implicants = getPrimeImplicants(num_var=num_var, terms=terms, dont_cares=dont_cares, form_terms=form_terms)
    final_expressions = minimizePrimeImplicants(num_var=num_var, terms=terms, prime_implicants=prime_implicants, form_terms=form_terms)
    result = checkAnswer(minimal_expressions=final_expressions, input_answer=input_answer, form_answer=form_terms)
    stringified_expressions = []
    for i in range(len(final_expressions)):
        stringified_expressions.append(stringifyExpression(expression=final_expressions[i], form_answer=form_terms))
    return result, stringified_expressions

def answerUserQuestion():
    import requests, group_generator as gg

    # Running server needed!
    # users = requests.get("http://localhost:8000/user").json()
    # username = "francois"
    # user = next(user for user in users if user['username'] == username)
    
    num_var = 2
    terms = [2]
    dont_cares = []
    form_terms = "max"
    # num_var, form_terms, terms, dont_cares = randomizeQuestion(4)
    print("Number of variables:", num_var, "Form:", form_terms)
    print("Terms:", terms)
    print("Don't cares", dont_cares)
    input_answer = "A+B‘"

    prime_implicants = getPrimeImplicants(num_var=num_var, terms=terms, dont_cares=dont_cares, form_terms=form_terms)
    # print("Prime implicants:", prime_implicants)
    final_expressions = minimizePrimeImplicants(num_var=num_var, terms=terms, prime_implicants=prime_implicants, form_terms=form_terms)
    # print("Minimal expressions:", final_expressions)
    if len(final_expressions) == 1:
        stringified_expression = stringifyExpression(expression=final_expressions[0], form_answer=form_terms)
        print("Correct answer:", stringified_expression)
    else:
        for i in range(len(final_expressions)):
            stringified_expression = stringifyExpression(expression=final_expressions[i], form_answer=form_terms)
            print(f"Correct answer {i}:", stringified_expression)
    print("Given answer", input_answer)

    result = checkAnswer(minimal_expressions=final_expressions, input_answer=input_answer, form_answer=form_terms)
    if result == 1:
        print("Correct!")
    elif result == 0:
        print("Wrong.")
    elif result == -1:
        print("Invalid characters present.")
    elif result == -2:
        print("Wrong form (SOP/POS).")
    elif result == -3:
        print("Error: please contact dev.")

if __name__ == "__main__":
    import group_generator as gg
    # print('\u2018')
    answerUserQuestion()
    # num_var, form, terms, dont_cares, groupings = randomizeQuestion(3)
    # print("Number of variables:", num_var, "Form:", form)
    # print("Terms:", terms)
    # print("Don't cares", dont_cares)
