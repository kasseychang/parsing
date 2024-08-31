"""
cc4876 Kassey Chang 
"""
"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum
import math

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        for lhs, rules in self.lhs_to_rules.items():
            total_prob = 0.0

            for rule in rules:
                lhs, rhs, prob = rule

                # Return False if it is not A -> B C (nonterminals)
                if len(rhs) == 2 and (rhs[0] not in self.lhs_to_rules or rhs[1] not in self.lhs_to_rules):
                    return False
                # Return False if it is not A -> b (nonterminal->terminal)
                if len(rhs) == 1 and rhs[0] in self.lhs_to_rules:
                    return False

                total_prob += prob

            # Check if the sum of probabilities for LHS is close to 1
            if not math.isclose(total_prob, 1.0, rel_tol=1e-9):
                return False

        return True



if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)

        # Return statements
        if grammar.verify_grammar():
            print('The grammar is a valid PCFG in CNF.')
        else:
            print('Error: The grammar is not a valid PCFG in CNF.')
        
