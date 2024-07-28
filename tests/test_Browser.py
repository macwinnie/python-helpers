#!/usr/bin/env python3
import gc
import logging
import os
import pickle
from unittest.mock import MagicMock

import pytest
import requests
from selenium.webdriver.remote.webdriver import WebDriver
from testfixtures import log_capture
from testfixtures import LogCapture

from macwinnie_pyhelpers.Browser import Browser
from macwinnie_pyhelpers.Browser import helper_set_value_at_key
from macwinnie_pyhelpers.Browser import session_file


def test_helper_set_value_at_key():
    """test helper function for setting value on dotted key"""
    dotkey = "lorem.ipsum.foo"
    value = "bar"
    expected = {"lorem": {"ipsum": {"foo": value}}}
    dictionary = {}
    helper_set_value_at_key(dictionary, dotkey, value)
    assert expected == dictionary


@pytest.fixture(autouse=True)
def test_browser_creation():
    """test browser object creation
    no session file
    """
    try:
        os.remove(session_file)
    except:
        pass
    selenium_browser = MagicMock(spec=WebDriver)
    base_url = "http://127.0.0.1"
    user_agent = "custom useragent"
    b = Browser(
        base_url=base_url,
        dump_session=True,
        selenium=selenium_browser,
        session_user_agent=user_agent,
        ssl_ignore_error=True,
    )
    assert b.base_url == base_url
    assert b.dump_session
    assert b.session.headers["user-agent"] == user_agent
    try:
        os.remove(session_file)
    except:
        pass
    del b
    gc.collect()


@pytest.mark.parametrize(
    "loglevel",
    (logging.DEBUG, logging.INFO),
)
def test_fail_loading_browser_wrong_sessionfile(loglevel):
    try:
        os.remove(session_file)
    except:
        pass
    content = "this is a string object"
    with open(session_file, "wb") as file:
        pickle.dump(content, file)
    base_url = "http://127.0.0.1"
    user_agent = "custom useragent"
    with LogCapture(level=loglevel) as l:
        b = Browser(base_url=base_url, dump_session=True)
    string_type = type(content)
    if loglevel == logging.DEBUG:
        l.check_present(
            (
                "macwinnie_pyhelpers.Browser",
                "ERROR",
                f"No Session object stored in {session_file} but an object of type {string_type}",
            ),
            order_matters=False,
        )
    else:
        l.check_present(
            (
                "macwinnie_pyhelpers.Browser",
                "ERROR",
                f"No Session object stored in {session_file} but an object of type {string_type}",
            ),
            order_matters=False,
        )


@log_capture()
def test_load_saved_session(capture):
    try:
        os.remove(session_file)
    except:
        pass
    session = requests.Session()
    with open(session_file, "wb") as file:
        pickle.dump(session, file)
    base_url = "http://127.0.0.1"
    user_agent = "custom useragent"
    b = Browser(base_url=base_url, dump_session=True)
    capture.check_present(
        ("macwinnie_pyhelpers.Browser", "INFO", f"Session loaded from {session_file}"),
        order_matters=False,
    )


@log_capture()
def test_no_session_file(capture):
    try:
        os.remove(session_file)
    except:
        pass
    base_url = "http://127.0.0.1"
    user_agent = "custom useragent"
    b = Browser(base_url=base_url, dump_session=False)
    capture.check_present(
        (
            "macwinnie_pyhelpers.Browser",
            "INFO",
            f"Session file disabled by `dump_session` attribute.",
        ),
        order_matters=False,
    )


def test_invalid_browser_attributes():
    try:
        os.remove(session_file)
    except:
        pass
    base_url = False
    user_agent = "custom useragent"
    try:
        b = Browser(base_url=base_url, user_agent=user_agent)
    except TypeError as e:
        assert (
            str(e)
            == f"Type <class 'bool'> not in allowed types [<class 'str'>] for attribute `base_url` ..."
        )
    except:
        assert False

    base_url = "http://127.0.0.1"
    user_agent = "custom useragent"
    try:
        b = Browser(base_url=base_url, lorem=user_agent)
    except KeyError as e:
        assert str(e) == "'Invalid basic attribute `lorem` given ...'"
    except:
        assert False
