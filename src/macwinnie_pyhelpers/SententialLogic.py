#!/usr/bin/env python3

import re


class Truth:
    """
    Basic truth check class.
    """

    def verify(self, proposition):
        """
        * boolean propositions will be returned as they are
        * numbers (float, integers) will return true if > 0, 0 and negatives will return false
        * `nein`, `no`, `n`, `falsch`, `false`, `f` will return `False`
        * `ja`, `j`, `yes`, `y`, `wahr`, `w`, `true`, `t` will return `True`
        """
        trueMatch = r"^((t(rue)?)|(y(es)?)|(w(ahr)?)|(j(a)?))$"
        falseMatch = r"^((f((alse)|(alsch))?)|(n((o)|(ein))?))$"
        if type(proposition) is bool:
            return proposition
        elif isinstance(proposition, (int, float)):
            return proposition > 0
        elif type(proposition) is str:
            if re.match(trueMatch, proposition.strip(), re.IGNORECASE):
                return True
            elif re.match(falseMatch, proposition.strip(), re.IGNORECASE):
                return False
        raise Exception('No interpretion found for given proposition "{}"!'.format(proposition))


class Sentence:
    """
    String to be checked for truth.

    Binding can be done using regular brackets `(` and `)` – and
    the operators binding order.

    Operators supported are (top is more binding than bottom):
    * `¬` as `not`
    * `∧` as `and`
    * `∨` as `or` (not the letter `v`!)
    """

    sentence = None
    verificator = None

    def __init__(self, sentence, verificator=None):
        """
        given a `sentence` and a `verificator` object which has a method
        `verify` implemented to check the truth value of a single proposition,
        this `sentence` class will verify your given propositional sentence.
        """
        self.sentence = sentence
        if verificator == None:
            self.verificator = Truth()
        else:
            self.verificator = verificator
        self.verifyAllPropositions()

    def verifyAllPropositions(self):
        deviders = r"([^(¬∧∨\(\)]+)"
        verified = []
        for p in re.findall(deviders, self.sentence):
            x = p.strip()
            if x not in verified:
                if self.verificator.verify(x):
                    self.sentence = self.sentence.replace(p, " T ")
                else:
                    self.sentence = self.sentence.replace(p, " F ")
