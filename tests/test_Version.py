#!/usr/bin/env python3
import pytest

import macwinnie_pyhelpers.SententialLogic as SL
from macwinnie_pyhelpers.Version import Version

p1 = "v"
p2 = ["v", "V.", "version "]
v1 = "1.2.1"
v2 = "2.3.2"
v3 = "1.2.2"
v4 = "1.3.0"
v5 = "2.0.0"


def test_definitions():
    """Test if string representation of a version stays exact"""
    vObj = Version(v1)
    assert vObj == v1

    vObj = Version(p1 + v2, p1)
    assert vObj == v2


def test_increase():
    """Test increasing versions"""
    vObj = Version(v1)
    assert str(vObj.increase()) == v3
    assert str(vObj.increaseMinor()) == v4
    assert str(vObj.increaseMajor()) == v5


def test_compare():
    """Test version comparison"""
    assert Version(v1) == Version(v1)
    assert Version(v1) != Version(v3)
    #
    assert Version(v1) < Version(v3)
    assert Version(v1) <= Version(v1)
    assert Version(v1) <= Version(v3)
    #
    assert Version(v2) > Version(v1)
    assert Version(v1) >= Version(v1)
    assert Version(v2) >= Version(v1)


def test_prefixed_equals():
    """Test prefixed versions"""
    for p in p2:
        vs = p + v1
        vo = Version(vs, p2)
        assert vo == v1


@pytest.mark.parametrize(
    ("sentence", "expected"),
    (
        ("1.2.3 <= 2.3.4", True),
        ("1.2.3 == 1.2.3", True),
        ("2.3.4 <= 2.3.4", True),
        ("1.2.3 < 1.2.4", True),
        ("1.3.1 > 1.2.3", True),
        ("1.2.3 != 3.2.1", True),
        ("1.2.9 >= 1.2.4 <= 1.2.5", True),
        ("1.2.3 == 2.3.1", False),
        ("2.3.4 <= 1.2.3", False),
        ("1.2.3 >= 2.3.4", False),
        ("1.2.3 > 1.2.4", False),
        ("1.3.1 < 1.2.3", False),
        ("1.2.3 != 1.2.3", False),
        ("1.2.9 >= 1.2.4 >= 1.2.5", False),
    ),
)
def test_version_propositional_logic(sentence: str, expected: bool):
    """version logic

    Testing propositional / sentential logic expressions with versions
    """
    i = SL.Sentence(sentence, interpretingExample=Version("1.2.3"))
    assert i.truth() == expected


@pytest.mark.parametrize(
    "givenPrefixes",
    (
        p1,
        p2,
        {},
    ),
)
def test_version_instantiation_with_different_prefixes(givenPrefixes):
    if givenPrefixes == {}:
        with pytest.raises(Exception) as excinfo:
            versionObj = Version(v1, givenPrefixes)
        expected = "Prefixes need to be either string or list of strings!"
        assert expected == str(excinfo.value)
    else:
        assert str(Version(f"v{v1}", givenPrefixes)) == f"v{v1}"


@pytest.mark.parametrize(
    ("version", "compareValue", "typeError", "valueError"),
    (
        (v1, None, True, False),
        (v1, "lorem", False, True),
        (v1, 123, True, False),
    ),
)
def test_version_comparison_typerrror(version, compareValue, typeError, valueError):
    t = type(compareValue)
    v = Version(version)
    if typeError:
        expected = f'Only able to compare Versions, "{t}" given.'
        with pytest.raises(TypeError) as excinfo:
            compared = v == compareValue
    elif valueError:
        expected = f'Value "{compareValue}" (type "{t}") is not a Version string!'
        with pytest.raises(ValueError) as excinfo:
            compared = v == compareValue

    assert expected == str(excinfo.value)
