#!/usr/bin/env python3

import os, sys

# CAUTION: `path[0]` is reserved for script path (or '' in REPL)
sys.path.insert(1, os.getcwd() + "/src/")

import unittest

import macwinnie_pyhelpers.SententialLogic as SL
import math


class AlphabetVerifyer:
    """
    Simple helper for below tests: if a character has an even order, the verify
    method will return true. For that, `a` and `A` are False while  `b` and `B`
    are True, ...
    """

    def verify(self, proposition):
        if len(proposition) != 1:
            raise Exception(
                'Only single characters are allowed here, "{}" given!'.format(proposition)
            )
        elif proposition in ["⊤", "⊥", "∧", "∨", "¬"]:
            raise Exception(
                'Verum ⊤, Falsum ⊥ and the logical operators ∧∨¬ are not allowed here – don\'t use "{}"!'.format(
                    proposition
                )
            )
        return ord(proposition) % 2 == 0


class SententialLogicTest(unittest.TestCase):
    """
    Tests for the collection `SententialLogic`.
    """

    mainVerifier = AlphabetVerifyer()
    tests = [
        # This list contains lists with those elements:
        # #1 sentence to parse, #2 t-sentence, #3 final result expected
        # The sentence to parse uses the AlphabetVerifyer from above
        ["B", "⊤", True],
        ["B ∧ ¬A", "⊤∧¬⊥", True],
        ["¬(A ∨ C ∧ ¬B)", "¬(⊥∨⊥∧¬⊤)", True],
        ["(B∨A) ∧ ¬C", "(⊤∨⊥)∧¬⊥", True],
        ["B ∧ (G∨¬(A∧F))", "⊤∧(⊥∨¬(⊥∧⊤))", True],
        ["A", "⊥", False],
        ["¬B", "¬⊤", False],
        ["¬(A∨B∧D)", "¬(⊥∨⊤∧⊤)", False],
        ["A∧B∨¬(F∧H)", "⊥∧⊤∨¬(⊤∧⊤)", False],
        ["(A ∧ (B ∨ ¬C) ∧ (E ∨ ¬G)) ∨ ¬(D ∧ (F ∨ ¬H))", "(⊥∧(⊤∨¬⊥)∧(⊥∨¬⊥))∨¬(⊤∧(⊤∨¬⊤))", False],
    ]

    def test_alphabetVerifyer(self):
        """Test the verifyer above to be able to run correct tests"""
        tester = self.mainVerifier
        self.assertFalse(tester.verify("A"))
        self.assertFalse(tester.verify("a"))
        self.assertTrue(tester.verify("B"))
        self.assertTrue(tester.verify("b"))

    def test_basic_truth(self):
        """Test the real basics of the `Truth` class"""
        tester = SL.Truth()
        # first branch: boolean values
        for x in [True, False]:
            self.assertEqual(tester.verify(x), x)
        # second branch: numbers as values
        for x in [1, 2, 153, 0.3, math.pi]:
            self.assertEqual(tester.verify(x), True)
        for x in [0, -10, -0.5, -math.pi]:
            self.assertEqual(tester.verify(x), False)
        # the string branches – direct comparisons
        for x in ["ja", "j", "yes", "y", "wahr", "w", "true", "t"]:
            self.assertEqual(tester.verify(x), True)
            self.assertEqual(tester.verify(x.capitalize()), True)
            self.assertEqual(tester.verify(x.upper()), True)
        for x in ["nein", "no", "n", "falsch", "false", "f"]:
            self.assertEqual(tester.verify(x), False)
            self.assertEqual(tester.verify(x.capitalize()), False)
            self.assertEqual(tester.verify(x.upper()), False)
        # error throwing
        self.assertRaises(
            Exception, tester.verify("This is a nonsense check for truth ...")
        )

    def test_proposition_verification(self):
        """
        After the run of `verifyAllPropositions`, the `tsentence` should no more be
        `None` and only contain `⊤` / `⊥` literals additional to the operators and
        brackets.
        """
        for [s, t, r] in self.tests:
            i = SL.Sentence(s, verifier=self.mainVerifier)
            self.assertEqual(i.tsentence, t)

    def test_proposition_truth(self):
        """
        The sentences have a final truth value – and that will be tested here
        """
        for [s, t, r] in self.tests:
            i = SL.Sentence(s, verifier=self.mainVerifier)
            self.assertEqual(i.truth(), r)


if __name__ == "__main__":
    unittest.main()
