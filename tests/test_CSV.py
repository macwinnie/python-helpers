#!/usr/bin/env python3
import copy
import io
import os
from datetime import datetime
from unittest import TestCase
from unittest.mock import mock_open
from unittest.mock import patch

import pandas as pd
import pytest

from macwinnie_pyhelpers.CSV import CSV
from macwinnie_pyhelpers.CSV import int2xlsCol
from macwinnie_pyhelpers.CSV import xlsCol2Int


def prepareExampleCSV(cols=10, rows=150, vals=[], lb="\n"):
    """Helper to prepare CSV for testing

    This method creates dynamic example CSV data – by a fixed schema:
    The column headers / keys are named `Col[0-9]+` while the column
    values of each row are `Row[0-9]+Col[0-9]+`.

    Counting starts by `0`!

    Args:
        cols (number): number of columns to be created (default: `20`)
        rows (number): number of rows to be created (default: `200`)
        vals ([str]): only fetch specific values? By default all values are returned.
                      possible values and default order are: colNames, dataRows,
                      semicolonCSV, commaCSV, csvData, csvRows, pandasData (default: `[]`)
        lb (str): line break (default: `\\n`)

    Returns:
        mixed: prepared helper variables
    """
    if vals == []:
        vals = [
            "colNames",
            "dataRows",
            "semicolonCSV",
            "commaCSV",
            "csvData",
            "csvRows",
            "pandasData",
        ]

    data = {}
    data["colNames"] = ["Col" + str(j) for j in range(0, cols)]
    data["dataRows"] = []

    if "csvData" in vals:
        data["csvData"] = dict(
            zip(data["colNames"], [[] for _ in range(len(data["colNames"]))])
        )

    for i in range(0, rows):
        r = ["Row" + str(i) + "Col" + str(j) for j in range(0, cols)]
        data["dataRows"].append(r)
        if "csvData" in vals:
            for j, v in enumerate(r):
                data["csvData"][data["colNames"][j]].append(v)

    if "csvRows" in vals:
        data["csvRows"] = []
        for r in data["dataRows"]:
            data["csvRows"].append(dict(zip(data["colNames"], r)))

    if "semicolonCSV" in vals:
        data["semicolonCSV"] = csvDataToCsvString(
            data["colNames"], data["dataRows"], ";", "\n"
        )

    if "commaCSV" in vals:
        data["commaCSV"] = csvDataToCsvString(
            data["colNames"], data["dataRows"], ",", "\n"
        )

    if "pandasData" in vals:
        if "commaCSV" in data:
            csv = data["commaCSV"]
        else:
            csv = csvDataToCsvString(data["colNames"], data["csvRows"], ",", "\n")
        data["pandasData"] = pd.read_csv(
            io.StringIO(csv),
            delimiter=",",
            low_memory=False,
        )

    values = tuple()
    for k in vals:
        values += (data[k],)

    return values


def csvDataToCsvString(columns, dataRows, delimiter=";", lb="\n"):
    '''helper to generate CSV string from rows

    Args:
        columns ([str]): list of columns for the csv string
        dataRows ([dict]): csv row contents – they won't be adjusted, so encoding
                           and transformation (`"` => `"""`) needs to be done before;
                           BUT all the values will be quoted into `"`.
        delimiter (str): delimiter to be used in test csv (default: `";"`)
        lb (str): line break to be used (default: `\\n`)

    Returns:
        str: csv string
    '''
    delimiter = '"' + delimiter + '"'
    data = '"' + delimiter.join(columns) + '"' + lb
    for r in dataRows:
        data += '"' + delimiter.join(r) + '"' + lb
    return data


def test_transform_range_xls_int():
    """general test

    Test method for transforming XLS Column names to Integers and vice versa
    """
    chars = []
    ints = []
    r = range(0, 100000)
    # translate all numbers in range
    for i in r:
        chars.append(int2xlsCol(i))
    # remove duplicates
    chars = list(dict.fromkeys(chars))
    assert len(chars) == len(list(r))
    # translate alphabeticals back to ints
    for a in chars:
        ints.append(xlsCol2Int(a))
    ints = list(dict.fromkeys(ints))
    assert len(ints) == len(list(r))
    assert ints == list(r)


@pytest.mark.parametrize(
    ("strRep", "intRep"),
    (
        ("A", 0),
        ("AB", 27),
        ("ZZAB", 474579),
    ),
)
def test_specific_xls_int_values(strRep: str, intRep: int):
    """Test transformation of values

    Test specific XLS column names and their corresponding numbers.

    Args:
        strRep (str): expected / given XLS column identity
        intRep (int): expected / given integer column identity
    """
    assert xlsCol2Int(strRep) == intRep
    assert int2xlsCol(intRep) == strRep


@pytest.mark.parametrize(
    "csvCreation",
    (
        "commaSeparatedFile",
        "semicolonSeparatedText",
        "byRows",
        "byColumns",
    ),
)
def test_loading_csv(csvCreation):
    """test loading CSV

    This method tests creation of CSV objects and their general integrity.

    Args:
        csvCreation ([string]): which loading type should be used? Types are defined above and named speaking.
    """
    (
        colNames,
        dataRows,
        semicolonCSV,
        commaCSV,
        csvData,
        csvRows,
        pandasData,
    ) = prepareExampleCSV()
    delimiter = ";"

    # prepare CSV object for tests
    match csvCreation:
        case "commaSeparatedFile":
            delimiter = ","
            # load file
            with patch("pandas.read_csv") as patched_pandas_read_csv:
                patched_pandas_read_csv.return_value = pandasData
                csvObject = CSV()
                csvObject.setSpec("delimiter", delimiter)
                csvObject.readFile("/random/path/to/file.csv")

        case "semicolonSeparatedText":
            # load from CSV text variable
            csvObject = CSV()
            csvObject.readCSV(semicolonCSV)
        case "byRows":
            # load from list of dicts, the rows
            csvObject = CSV(csvRows, kvDict=True)
        case "byColumns":
            # load from dict of lists, the columns (like structure of `csv.data`)
            csvObject = CSV(csvData, kvDict=False)

    assert csvObject.specs["delimiter"] == delimiter
    assert len(csvObject) == len(dataRows)
    assert csvRows == csvObject.getRows()
    assert csvData == csvObject.getCSV()


def test_get_row_100():
    """test integrity of row 100 in testing CSV"""
    cols = 10
    (csvRows,) = prepareExampleCSV(cols=cols, vals=["csvRows"])
    csvObject = CSV(csvRows)
    row100 = csvObject[100]

    expected = dict(
        zip(
            ["Col" + str(j) for j in range(0, cols)],
            ["Row100Col" + str(j) for j in range(0, cols)],
        )
    )
    assert row100 == expected


@pytest.mark.parametrize(
    ("rows", "cols"),
    ((10, 10),),
)
@pytest.mark.parametrize(
    "addKeyInRow",
    set(range(0, 10)),
)
def test_new_key_in_row(rows, cols, addKeyInRow):
    # prepare CSV Rows list
    (csvRows,) = prepareExampleCSV(rows=rows, cols=cols, vals=["csvRows"])
    csvRows[addKeyInRow][f"Col{cols}"] = f"Row{addKeyInRow}Col{cols}"

    # create CSV object
    csvObject = CSV(csvRows)

    # adjust the whole rows csvRows to match expectation
    for r in range(0, rows):
        if f"Col{cols}" not in csvRows[r]:
            csvRows[r][f"Col{cols}"] = None

    assert csvObject.getRows() == csvRows


@pytest.mark.parametrize(
    ("rows", "cols"),
    ((10, 10),),
)
@pytest.mark.parametrize(
    "removeRow",
    set(range(0, 10)),
)
def test_row_removal(rows, cols, removeRow):
    (csvRows,) = prepareExampleCSV(rows=rows, cols=cols, vals=["csvRows"])
    csvObject = CSV(csvRows)

    assert len(csvObject) == rows

    csvObject.remove(csvRows[removeRow])

    assert len(csvObject) == rows - 1
    assert csvRows[removeRow] not in csvObject.getRows()


@pytest.mark.parametrize(
    ("rows", "cols"),
    ((10, 10),),
)
@pytest.mark.parametrize(
    "popRow",
    set(range(0, 10)),
)
def test_popping_row(rows, cols, popRow):
    (
        csvData,
        csvRows,
    ) = prepareExampleCSV(rows=rows, cols=cols, vals=["csvData", "csvRows"])
    csvObject = CSV(csvRows)

    assert len(csvObject) == rows

    popped = csvObject.pop(popRow)

    for col in csvData:
        csvData[col].pop(popRow)

    assert len(csvObject) == rows - 1
    assert csvRows[popRow] not in csvObject.getRows()
    assert csvRows[popRow] == popped
    assert csvData == csvObject.getCSV()


@pytest.mark.parametrize(
    ("rows", "cols"),
    ((10, 10),),
)
@pytest.mark.parametrize(
    "emptyCols",
    set(range(0, 9)),
)
@pytest.mark.parametrize(
    "fromRows",
    (
        True,
        False,
    ),
)
def test_removing_totaly_empty_cols(rows, cols, emptyCols, fromRows):
    (
        colNames,
        csvData,
        csvRows,
    ) = prepareExampleCSV(rows=rows, cols=cols, vals=["colNames", "csvData", "csvRows"])

    expectedRows = copy.deepcopy(csvRows)
    expectedData = copy.deepcopy(csvData)

    for i in range(0, emptyCols):
        c = colNames[i]

        csvData[c] = [""] * rows
        del expectedData[c]

        for j in range(0, rows):
            csvRows[j][c] = ""
            del expectedRows[j][c]

    if fromRows:
        csvObject = CSV(csvRows)
        csvObject.dropEmptyColumns()
    else:
        csvObject = CSV(csvData, kvDict=False)
        csvObject.dropEmptyColumns()

    assert csvObject.getRows() == expectedRows
    assert csvObject.getCSV() == expectedData


@pytest.mark.parametrize(
    ("rows", "cols"),
    ((10, 10),),
)
@pytest.mark.parametrize(
    "emptyCols",
    (8,),
)
@pytest.mark.parametrize(
    "keepRows",
    set(range(0, 9)),
)
@pytest.mark.parametrize(
    "keyEquality",
    (
        True,
        False,
    ),
)
def test_removing_partially_empty_cols(rows, cols, emptyCols, keepRows, keyEquality):
    (
        colNames,
        csvData,
        csvRows,
    ) = prepareExampleCSV(rows=rows, cols=cols, vals=["colNames", "csvData", "csvRows"])

    expectedRows = copy.deepcopy(csvRows)
    expectedData = copy.deepcopy(csvData)

    for i in range(0, emptyCols):
        c = colNames[i]

        delRowRange = range(0, rows - keepRows)
        for j in delRowRange:
            csvData[c][j] = ""
            expectedData[c][j] = None
            csvRows[j][c] = ""
            if keepRows == 0 or not keyEquality:
                del expectedRows[j][c]
            else:
                expectedRows[j][c] = None

        if keepRows == 0:
            del expectedData[c]

    csvObject = CSV(csvRows)
    csvObject.dropEmptyColumns(ensureKeyEquality=keyEquality)

    assert csvObject.getRows() == expectedRows
    assert csvObject.getCSV() == expectedData


@pytest.mark.parametrize(
    ("rows", "cols"),
    ((10, 10),),
)
@pytest.mark.parametrize(
    "delimiter",
    (
        ",",
        ";",
        "\t",
    ),
)
@pytest.mark.parametrize(
    "linebreak",
    (
        "\n",
        "\r\n",
    ),
)
@pytest.mark.parametrize(
    "backupExisting",
    (
        True,
        False,
    ),
)
@pytest.mark.parametrize(
    "fileExists",
    (
        True,
        False,
    ),
)
@pytest.mark.parametrize(
    ("filename", "format_backup"),
    (
        ("file.csv", "file{}.csv"),
        ("csv", "csv{}"),
        (".hidden_csv", ".hidden_csv{}"),
    ),
)
@patch("builtins.open", new_callable=mock_open())
def test_write_csv_file(
    mock_open_file,
    mocker,
    rows,
    cols,
    delimiter,
    linebreak,
    backupExisting,
    fileExists,
    filename,
    format_backup,
):
    (
        colNames,
        dataRows,
        csvRows,
    ) = prepareExampleCSV(
        rows=rows,
        cols=cols,
        vals=[
            "colNames",
            "dataRows",
            "csvRows",
        ],
    )

    dummy_timestamp_string = "_20111111-111111"
    dummy_timestamp = datetime.timestamp(
        datetime(
            year=int(dummy_timestamp_string[1:5]),
            month=int(dummy_timestamp_string[5:7]),
            day=int(dummy_timestamp_string[7:9]),
            hour=int(dummy_timestamp_string[10:12]),
            minute=int(dummy_timestamp_string[12:14]),
            second=int(dummy_timestamp_string[14:16]),
        )
    )
    pathToFile = "/dummy/path/to/"
    filepath = "{}{}".format(pathToFile, filename)
    buFilepath = f"{pathToFile}{format_backup}".format(dummy_timestamp_string)

    csvString = csvDataToCsvString(colNames, dataRows, delimiter, linebreak)

    if backupExisting:
        file_insert = datetime.fromtimestamp(dummy_timestamp).strftime("_%Y%m%d-%H%M%S")

        assert file_insert == dummy_timestamp_string

        mocker.patch("os.path.isfile").return_value = fileExists
        mocker.patch("os.path.getmtime").return_value = dummy_timestamp
        mocker.patch("os.rename")

    csvObject = CSV(csvRows)
    csvObject.writeFile(filepath, delimiter, linebreak, backupExisting)

    if backupExisting:
        os.path.isfile.assert_called_once_with(filepath)
        if fileExists:
            os.path.getmtime.assert_called_once_with(filepath)
            os.rename.assert_called_once_with(filepath, buFilepath)
    mock_open_file.assert_called_once_with(filepath, "w")
    mock_open_file.return_value.__enter__().write.assert_called_once_with(csvString)
    mock_open_file.reset_mock()


@pytest.mark.parametrize(
    ("rows", "cols"),
    ((10, 10),),
)
@pytest.mark.parametrize(
    ("rowWithQuotes", "colWithQuotes"),
    (
        (
            5,
            5,
        ),
    ),
)
def test_string_escape_quotes(rows, cols, rowWithQuotes, colWithQuotes):
    (
        colNames,
        dataRows,
        csvRows,
    ) = prepareExampleCSV(
        rows=rows,
        cols=cols,
        vals=[
            "colNames",
            "dataRows",
            "csvRows",
        ],
    )

    quotedPlainString = 'That\'s a "quote" test!'
    escapedQuoteString = quotedPlainString.replace('"', '"""')
    csvRows[rowWithQuotes][colNames[colWithQuotes]] = quotedPlainString
    dataRows[rowWithQuotes][colWithQuotes] = escapedQuoteString

    expected = csvDataToCsvString(colNames, dataRows)
    csvObject = CSV(csvRows)

    assert str(csvObject) == expected


def test_string_escape_quotes_reverse():
    cell_1_1 = 'This is a """TEST"""'
    cell_2_1 = 'Unclosed """ quote'
    cell_3_1 = 'Single quote"""'
    load_csv = f""""three";"test";"columns"
"{cell_1_1}";"with escaped";"quotes"
"{cell_2_1}";"in first cell";"of row"
"""

    # # this test is more complex to fix while `pandas` Bug ...
    #     load_csv = f'''{load_csv}"{cell_3_1}";"at the end of";"first cell"
    # '''

    csvObject = CSV()
    csvObject.readCSV(load_csv)

    assert cell_1_1.replace('"""', '"') == csvObject.rows[0]["three"]
    assert cell_2_1.replace('"""', '"') == csvObject.rows[1]["three"]
    # assert cell_3_1.replace('"""', '"') == csvObject.rows[2]["three"]
    assert str(csvObject) == load_csv


def test_load_multiline_cell_csv():
    first_cell = """This is a
multiline cell"""
    load_csv = f""""test";"columns"
"{first_cell}";"And this is another
multiline cell"
"""

    csvObject = CSV()
    csvObject.readCSV(load_csv)

    assert csvObject.rows[0]["test"] == first_cell
    assert str(csvObject) == load_csv


@pytest.mark.parametrize(
    ("rows", "cols"),
    ((10, 10),),
)
@pytest.mark.parametrize(
    ("rowWithEmpty", "emptyCol"),
    (
        (
            5,
            5,
        ),
    ),
)
def test_string_emtpy_cell(rows, cols, rowWithEmpty, emptyCol):
    (
        colNames,
        dataRows,
        csvRows,
    ) = prepareExampleCSV(
        rows=rows,
        cols=cols,
        vals=[
            "colNames",
            "dataRows",
            "csvRows",
        ],
    )

    csvRows[rowWithEmpty][colNames[emptyCol]] = None
    dataRows[rowWithEmpty][emptyCol] = ""

    expected = csvDataToCsvString(colNames, dataRows)
    csvObject = CSV(csvRows)

    assert str(csvObject) == expected
