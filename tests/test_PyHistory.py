#!/usr/bin/env python3
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from macwinnie_pyhelpers.PyHistory import historyLength
from macwinnie_pyhelpers.PyHistory import printHistory
from macwinnie_pyhelpers.PyHistory import saveHistory


@pytest.mark.parametrize(
    "historyRowCount",
    (
        10,
        100,
        1000,
        # 10000,
    ),
)
@pytest.mark.parametrize(
    "maxPrintRows",
    (
        None,  # all possible
        10,
        100,
        # 1000,
    ),
)
@pytest.mark.parametrize(
    "lineBreak",
    (
        None,
        "\n",
        "\r\n",
    ),
)
@pytest.mark.parametrize("showLineNumbers", (True, False))
def test_history_output(
    historyRowCount: int, maxPrintRows, showLineNumbers: bool, capsys, lineBreak
):
    """test history output

    Method to test `macwinnie_pyhelpers.PyHistory.printHistory()` method.

    Args:
        historyRowCount (int): how many lines should be available in history?
        maxPrintRows (int): how many lines of history should maximal be printed?
        showLineNumbers (bool): should line numbers be printed?
    """
    historyItemPrefix = "History Item "

    if maxPrintRows == None:
        n = historyRowCount
    else:
        n = min(maxPrintRows, historyRowCount)

    with (
        patch("readline.get_current_history_length") as patched_history_length,
        patch("readline.get_history_item") as patched_history_item,
    ):
        patched_history_length.return_value = historyRowCount
        patched_history_item.side_effect = [
            historyItemPrefix + str(i)
            for i in range(historyRowCount - n, historyRowCount)
        ]

        assert historyLength() == historyRowCount

        attributes = {
            "lineNumbers": showLineNumbers,
            "n": maxPrintRows,
        }
        if lineBreak != None:
            attributes["newLine"] = lineBreak

        printHistory(**attributes)

    captured = capsys.readouterr()

    if lineBreak == None:
        lineBreak = "\n"

    formatString = f"{historyItemPrefix}{{1}}"
    if showLineNumbers:
        l = len(str(n))
        formatString = f"{{0:{l}d}}" + " " * 2 + formatString

    expected = (
        lineBreak.join(
            [formatString.format(i + 1, historyRowCount - n + i) for i in range(0, n)]
        )
        + "\n"
    )

    assert expected == captured.out


@pytest.mark.parametrize(
    "historyRowCount",
    (
        10,
        100,
        1000,
        # 10000,
    ),
)
@pytest.mark.parametrize(
    "maxPrintRows",
    (
        None,  # all possible
        10,
        100,
        # 1000,
    ),
)
@pytest.mark.parametrize(
    "lineBreak",
    (
        None,
        "\n",
        "\r\n",
    ),
)
@pytest.mark.parametrize("showLineNumbers", (True, False))
@patch("builtins.open", new_callable=mock_open())
def test_saving_history(
    mock_open_file,
    historyRowCount: int,
    maxPrintRows,
    showLineNumbers: bool,
    capsys,
    lineBreak,
):
    """test history output

    Method to test `macwinnie_pyhelpers.PyHistory.printHistory()` method.

    Args:
        historyRowCount (int): how many lines should be available in history?
        maxPrintRows (int): how many lines of history should maximal be printed?
        showLineNumbers (bool): should line numbers be printed?
    """
    historyItemPrefix = "History Item "

    storage_path = "/dummy/path/to/history.file"

    if maxPrintRows == None:
        n = historyRowCount
    else:
        n = min(maxPrintRows, historyRowCount)

    with (
        patch("readline.get_current_history_length") as patched_history_length,
        patch("readline.get_history_item") as patched_history_item,
    ):
        patched_history_length.return_value = historyRowCount
        patched_history_item.side_effect = [
            historyItemPrefix + str(i)
            for i in range(historyRowCount - n, historyRowCount)
        ]

        assert historyLength() == historyRowCount

        attributes = {
            "lineNumbers": showLineNumbers,
            "n": maxPrintRows,
        }
        if lineBreak != None:
            attributes["newLine"] = lineBreak

        saveHistory(storage_path, **attributes)

    if lineBreak == None:
        lineBreak = "\n"

    captured = capsys.readouterr()

    formatString = f"{historyItemPrefix}{{1}}"
    if showLineNumbers:
        l = len(str(n))
        formatString = f"{{0:{l}d}}" + " " * 2 + formatString

    expected = lineBreak.join(
        [formatString.format(i + 1, historyRowCount - n + i) for i in range(0, n)]
    )

    mock_open_file.assert_called_once_with(storage_path, "w")
    mock_open_file.return_value.__enter__().write.assert_called_once_with(expected)
    mock_open_file.reset_mock()
