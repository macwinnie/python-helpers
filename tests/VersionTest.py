#!/usr/bin/env python3

import os, sys

# CAUTION: `path[0]` is reserved for script path (or '' in REPL)
sys.path.insert(1, os.getcwd() + "/src/")

import unittest

from macwinnie_pyhelpers.Version import Version
import macwinnie_pyhelpers.SententialLogic as SL


class VersionTest(unittest.TestCase):
    """
    Tests for the `Version` collection.
    """

    p1 = "v"
    p2 = ["v", "V.", "version "]
    v1 = "1.2.1"
    v2 = "2.3.2"
    v3 = "1.2.2"
    v4 = "1.3.0"
    v5 = "2.0.0"

    def test_definitions(self):
        """Test if string representation of a version stays exact"""
        vObj = Version(self.v1)
        self.assertEqual(vObj, self.v1)
        vObj = Version(self.p1 + self.v2, self.p1)
        self.assertEqual(vObj, self.v2)

    def test_increase(self):
        """Test increasing versions"""
        vObj = Version(self.v1)
        self.assertEqual(str(vObj.increase()), self.v3)
        self.assertEqual(str(vObj.increaseMinor()), self.v4)
        self.assertEqual(str(vObj.increaseMajor()), self.v5)

    def test_compare(self):
        """Test version comparison"""
        self.assertEqual(Version(self.v1), Version(self.v1))
        self.assertIsNot(Version(self.v1), Version(self.v3))
        #
        self.assertLess(Version(self.v1), Version(self.v3))
        self.assertLessEqual(Version(self.v1), Version(self.v1))
        self.assertLessEqual(Version(self.v1), Version(self.v3))
        #
        self.assertGreater(Version(self.v2), Version(self.v1))
        self.assertGreaterEqual(Version(self.v1), Version(self.v1))
        self.assertGreaterEqual(Version(self.v2), Version(self.v1))

    def test_prefixed_equals(self):
        """Test prefixed versions"""
        for p in self.p2:
            vs = p + self.v1
            vo = Version(vs, self.p2)
            self.assertEqual(vo, self.v1)

    def test_version_propositional_logic(self):
        """Testing propositional / sentential logic expressions with versions"""
        given = [
            # list of testing lists with #1 logic expression #2 expected result
            ["1.2.3 <= 2.3.4", True],
            ["1.2.3 == 1.2.3", True],
            ["2.3.4 <= 2.3.4", True],
            ["1.2.3 < 1.2.4", True],
            ["1.3.1 > 1.2.3", True],
            ["1.2.3 != 3.2.1", True],
            ["1.2.9 >= 1.2.4 <= 1.2.5", True],
            ["1.2.3 == 2.3.1", False],
            ["2.3.4 <= 1.2.3", False],
            ["1.2.3 >= 2.3.4", False],
            ["1.2.3 > 1.2.4", False],
            ["1.3.1 < 1.2.3", False],
            ["1.2.3 != 1.2.3", False],
            ["1.2.9 >= 1.2.4 >= 1.2.5", False],
        ]
        for [s, r] in given:
            i = SL.Sentence(s, interpretingExample=Version("1.2.3"))
            self.assertEqual(i.truth(), r)


if __name__ == "__main__":
    unittest.main()
