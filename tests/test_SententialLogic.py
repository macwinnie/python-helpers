#!/usr/bin/env python3
import math

import pytest

import macwinnie_pyhelpers.SententialLogic as SL


class AlphabetVerifyer:
    """
    Simple helper for below tests: if a character has an even order, the verify
    method will return true. For that, `a` and `A` are False while  `b` and `B`
    are True, ...
    """

    def verify(self, proposition):
        if len(proposition) != 1:
            raise Exception(
                'Only single characters are allowed here, "{}" given!'.format(
                    proposition
                )
            )
        elif proposition in ["⊤", "⊥", "∧", "∨", "¬"]:
            raise Exception(
                'Verum ⊤, Falsum ⊥ and the logical operators ∧∨¬ are not allowed here – don\'t use "{}"!'.format(
                    proposition
                )
            )
        return ord(proposition) % 2 == 0


mainVerifier = AlphabetVerifyer()
tests = (
    # This list contains lists with those elements:
    # #1 sentence to parse, #2 t-sentence, #3 final result expected
    # The sentence to parse uses the AlphabetVerifyer from above
    ("B", "⊤", True),
    ("B ∧ ¬A", "⊤∧¬⊥", True),
    ("¬(A ∨ C ∧ ¬B)", "¬(⊥∨⊥∧¬⊤)", True),
    ("(B∨A) ∧ ¬C", "(⊤∨⊥)∧¬⊥", True),
    ("B ∧ (G∨¬(A∧F))", "⊤∧(⊥∨¬(⊥∧⊤))", True),
    ("A", "⊥", False),
    ("¬B", "¬⊤", False),
    ("¬(A∨B∧D)", "¬(⊥∨⊤∧⊤)", False),
    ("A∧B∨¬(F∧H)", "⊥∧⊤∨¬(⊤∧⊤)", False),
    (
        "(A ∧ (B ∨ ¬C) ∧ (E ∨ ¬G)) ∨ ¬(D ∧ (F ∨ ¬H))",
        "(⊥∧(⊤∨¬⊥)∧(⊥∨¬⊥))∨¬(⊤∧(⊤∨¬⊤))",
        False,
    ),
)


def test_alphabetVerifyer():
    """Test the verifyer above to be able to run correct tests"""
    tester = mainVerifier
    assert not tester.verify("A")
    assert not tester.verify("a")
    assert tester.verify("B")
    assert tester.verify("b")


def test_basic_truth():
    """Test the real basics of the `Truth` class"""
    tester = SL.Truth()

    # first branch: boolean values
    for x in [True, False]:
        assert tester.verify(x) == x

    # second branch: numbers as values
    for x in [1, 2, 153, 0.3, math.pi]:
        assert tester.verify(x) == True

    for x in [0, -10, -0.5, -math.pi]:
        assert tester.verify(x) == False

    # the string branches – direct comparisons
    for x in ["ja", "j", "yes", "y", "wahr", "w", "true", "t"]:
        assert tester.verify(x) == True
        assert tester.verify(x.capitalize()) == True
        assert tester.verify(x.upper()) == True

    for x in ["nein", "no", "n", "falsch", "false", "f"]:
        assert tester.verify(x) == False
        assert tester.verify(x.capitalize()) == False
        assert tester.verify(x.upper()) == False

    # error throwing
    nonsense = "This is a nonsense check for truth ..."
    with pytest.raises(Exception) as excinfo:
        x = tester.verify(nonsense)

    expected = f'No interpretion found for given proposition "{nonsense}"!'
    assert expected == str(excinfo.value)


@pytest.mark.parametrize(
    ("s", "t", "r"),
    tests,
)
def test_proposition_verification(s, t, r):
    """
    After the run of `verifyAllPropositions`, the `tsentence` should no more be
    `None` and only contain `⊤` / `⊥` literals additional to the operators and
    brackets.
    """
    i = SL.Sentence(s, verifier=mainVerifier)
    assert i.tsentence == t


@pytest.mark.parametrize(
    ("s", "t", "r"),
    tests,
)
def test_proposition_truth(s, t, r):
    """
    The sentences have a final truth value – and that will be tested here
    """
    i = SL.Sentence(s, verifier=mainVerifier)
    assert i.truth() == r


@pytest.mark.parametrize(
    (
        "proposition",
        "expectedVerum",
    ),
    (
        # <=
        ("1 <= 2", True),
        ("1 <= 1", True),
        ("1 <= 0", False),
        # >=
        ("1 >= 2", False),
        ("1 >= 1", True),
        ("1 >= 0", True),
        # <
        ("1 < 2", True),
        ("1 < 1", False),
        ("1 < 0", False),
        # >
        ("1 > 2", False),
        ("1 > 1", False),
        ("1 > 0", True),
        # ==
        ("1 == 2", False),
        ("1 == 1", True),
        ("1 == 0", False),
        # !=
        ("1 != 2", True),
        ("1 != 1", False),
        ("1 != 0", True),
    ),
)
def test_integer_truth(proposition: str, expectedVerum: bool):
    t = SL.Truth(1)
    assert t.verify(proposition) == expectedVerum


@pytest.mark.parametrize(
    "proposition",
    (
        "a <= 2",
        "1 << 2",
        "1 !! 2",
    ),
)
def test_truth_exception(proposition):
    t = SL.Truth(1)
    with pytest.raises(Exception) as excinfo:
        x = t.verify(proposition)

    expected = f'No interpretion found for given proposition "{proposition}"!'
    assert expected == str(excinfo.value)


@pytest.mark.parametrize(
    (
        "sentence",
        "expectedSymbol",
        "expectedBool",
        "interpretingExample",
    ),
    (
        ("1 < 2", "⊤", True, 1),
        ("1 > 2", "⊥", False, 1),
        ("yes", "⊤", True, None),
        ("no", "⊥", False, None),
    ),
)
def test_basicSentenceWithoutVerifier(
    sentence, expectedSymbol, expectedBool, interpretingExample
):
    s = SL.Sentence(sentence, interpretingExample)
    assert str(s) == expectedSymbol
    assert bool(s) == expectedBool


@pytest.mark.parametrize(
    (
        "sentence",
        "openingBracketRX",
        "closingBracketRX",
        "expectedException",
    ),
    (
        ("((yes)", r"\(+", r"\)", "Opening only has to match single characters!"),
        ("(yes))", r"\(", r"\)+", "Closing only has to match single characters!"),
        ("yes(", r"\(", r"\)", "Last bracket has to be a closing one!"),
        (")yes", r"\(", r"\)", "First bracket has to be an opening one!"),
    ),
)
def test_breakingBrackets(
    sentence, openingBracketRX, closingBracketRX, expectedException
):
    with pytest.raises(Exception) as excinfo:
        s = SL.Sentence(
            sentence,
            openingBracketRX=openingBracketRX,
            closingBracketRX=closingBracketRX,
        )

    assert expectedException == str(excinfo.value)
