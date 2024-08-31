"""
cc4876 Kassey Chang 
"""
"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        n = len(tokens)
        # Initialize the parse table
        table = [[set() for j in range(n)] for i in range(n)]

        # Diagonal of the table: Insert lhs (nonterminals) based on rhs in rules
        for i, token in enumerate(tokens):
            for lhs, rhs, _ in self.grammar.rhs_to_rules[(token,)]:
                table[i][i].add(lhs)

        # Loop through the rest of the table
        for span in range(2, n+1):  # span is length of the substring
            for begin in range(n+1-span):  # begin is left index of the substring
                end = begin + span - 1  # end is right index of the substring
                for split in range(begin, end):
                    for rules in self.grammar.rhs_to_rules.values():
                        for lhs, rhs, _ in rules:
                            if len(rhs) == 2 and rhs[0] in table[begin][split] and rhs[1] in table[split+1][end]:
                                table[begin][end].add(lhs)

        # Return True if the start symbol can generate the whole sentence
        return self.grammar.startsymbol in table[0][n-1]

       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        n = len(tokens)
        # Initialize the parse table with backpointers and the log probabilities table
        table = defaultdict(dict)
        probs = defaultdict(dict)

        # Diagonals of the tables
        for begin, token in enumerate(tokens):
            end = begin + 1
            span = (begin, end)
            table[span]
            probs[span]
            if (token,) in self.grammar.rhs_to_rules:
                for rule in self.grammar.rhs_to_rules[(token,)]:
                    lhs, _, prob = rule
                    table[span][lhs] = token
                    probs[span][lhs] = math.log2(prob)

        # Fill the rest of the tables
        for length in range(2, n + 1):
            for begin in range(0, n - length + 1):
                end = begin + length
                span = (begin, end)
                table[span]
                probs[span]
                for split in range(begin + 1, end):
                    combinations = list(itertools.product(list(table[(begin, split)].keys()), list(table[(split, end)].keys())))
                    for combination in combinations:
                        if combination in self.grammar.rhs_to_rules:
                            rules = self.grammar.rhs_to_rules[combination]
                            for rule in rules:
                                lhs, _, rule_prob = rule
                                log_prob = math.log2(rule_prob) + probs[(begin, split)][combination[0]] + probs[(split, end)][combination[1]]
                                if lhs not in probs[span] or log_prob > probs[span][lhs]:
                                    table[span][lhs] = ((combination[0], begin, split), (combination[1], split, end))
                                    probs[span][lhs] = log_prob

        return table, probs

def get_tree(chart,i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
    if j - i == 1:
        # Return a tuple with nt and the string (terminal)
        return (nt, chart[i, j][nt])
    else:
        # Backpointers (child nodes) from the chart
        backpointer1, backpointer2 = chart[(i, j)][nt]
        # Recursively call get_tree() to get the two subtrees
        tree1 = get_tree(chart, backpointer1[1], backpointer1[2], backpointer1[0])
        tree2 = get_tree(chart, backpointer2[1], backpointer2[2], backpointer2[0])
        # Return a tuple with nt and the two child trees
        return (nt, tree1, tree2)
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        #toks=['show','me','the','flights','from','baltimore','to','seattle','.']
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        # assert check_table_format(chart)
        # assert check_table_format(table)
        # assert check_probs_format(probs)
        get_tree(table, 0, len(toks), grammar.startsymbol)
        
