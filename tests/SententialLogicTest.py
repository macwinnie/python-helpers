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
            raise Exception("Only single characters are allowed here!")
        return ord(proposition) % 2 == 0


class SententialLogicTest(unittest.TestCase):
    """
    Tests for the collection `SententialLogic`.
    """

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
            Exception, lambda: tester.verify("This is a nonsense check for truth ...")
        )


if __name__ == "__main__":
    unittest.main()
