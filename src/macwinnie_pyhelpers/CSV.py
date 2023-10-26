#!/usr/bin/env python3

import pandas as pd
import math
import io
import logging


class CSV:
    """Helper class for CSV files, where named columns will be retrievable

    The class needs the data being given as list of lists. Each row (outer list) contains multiple cells (inner list).
    If the data is given JSON like – as a list of dictionaries where each row (dictionary) contains the column names as keys and the cell content as value – the second constructor-parameter has to be set `True`.

    Attributes:
        specs: specifications for CSV, `delimiter` is defaulting to `;` and `linebreak` is defaulting to `\\n`.
    """

    specs = {
        "delimiter": ";",
        "linebreak": "\n",
    }

    def __init__(self, data={}, jsonLike=False):
        self.data = {}
        self.rows = []
        self.rowCheck = False
        self.loadData(data, jsonLike)

    def __getitem__(self, index):
        self.csvRows()
        self.rowCheck = True
        return self.rows[index]

    def getCSV(self):
        """get CSV data

        Return CSV data

        Returns:
            dict: keys are column titles, assigned lists are column values per row
        """
        self.refreshFromRows()
        return self.data

    def loadData(self, data, jsonLike=False, skipRows=False):
        """load data

        Method to load the data of the CSV.
        If data is a list of dicts, the dicts should have the keys in
        common and `jsonLike` shall be `True`.
        If the data is a dict of column-keys with a list of column-values
        where the index is the number of the row, `jsonLike` shall be `False`.

        Args:
            data (mixed): CSV data
            jsonLike (bool): is the data JSON like? (default: `False`)
            skipRows (bool): should the data be transferred into rows? DON'T USE UNLESS YOU KNOW WHAT YOU'RE DOING! (default: `False`)
        """
        if jsonLike:
            self.data = {}
            for row in data:
                try:
                    existingRowCount = len(next(iter(self.data.values())))
                except:
                    existingRowCount = 0
                keys = row.keys()
                for k in keys:
                    if k not in self.data:
                        if existingRowCount > 0:
                            self.data[k] = [None] * existingRowCount
                        else:
                            self.data[k] = []
                for k in self.data.keys():
                    if k in row:
                        self.data[k].append(row[k])
                    else:
                        self.data[k].append(None)
        else:
            self.data = data

        if not skipRows:
            self.csvRows(force=True)

    def setSpec(self, spec, val):
        """set specifications

        Method to set specifications for this CSV instance
        like the `delimiter` (default `;`) and the
        `linebreak` (default `\\n`)

        Args:
            spec(str): name of specification
            val(str): value for spec
        """
        self.specs[spec] = val

    def readFile(self, filepath, delimiter=None):
        """read CSV file

        Method to load especially a CSV file stored in the filesystem.

        Args:
            filepath (str): path to CSV file
            delimiter (str): delimiter to resolve the CSV data (default: `None`)
        """
        self.readCSV(filepath, delimiter=delimiter, file=True)

    def readCSV(self, path_or_csvstring, delimiter=None, file=False):
        """read CSV from string or file

        [description]

        Args:
            path_or_csvstring (string): either the path to the file to resolve or CSV data itself
            delimiter (str): delimiter to resolve the CSV data (default: `None`)
            file (bool): is it a file to read? (default: `False`)
        """
        if delimiter == None:
            delimiter = self.specs["delimiter"]
        if file:
            data = pd.read_csv(path_or_csvstring, delimiter=delimiter, low_memory=False)
        else:
            data = pd.read_csv(
                io.StringIO(path_or_csvstring),
                delimiter=delimiter,
                low_memory=False,
            )
        rows = {}
        for h in data.columns:
            rows[h] = data.get(h).to_list()
        self.data = rows

        self.csvRows(force=True)

    def csvRows(self, force=False):
        """prepare rows variable

        Method to get row representation of CSV and prepare an additional variable
        `rows` that allows us to use `CSV` object as iterable.

        Args:
            force (bool): Shall the row representation be renewed by force? (default: `False`)

        Returns:
            list: list of rows in CSV
        """
        if self.rows == []:
            force = True

        if force:
            self.rows = self.likeJSON()

        return self.rows

    def refreshFromRows(self):
        """reload the CSV from rows

        When one iterates over the rows of a CSV class and changes values, e.g.
        adding new columns or manipulate values, the CSV object needs to be
        rebuilt from the rows ... that's what this method is doing.
        """
        if self.rowCheck:
            self.loadData(data=self.rows, jsonLike=True, skipRows=True)
            self.rowCheck = False

    def likeJSON(self, keepEmpty=False, emptyValue=None):
        """data to list of rows

        Method to get row representation of CSV.

        Args:
            keepEmpty (bool): if set to True, empty values are kept in row representation (default: `False`)
            emptyValue (mixed): value that should be used for kept empty values (default: `None`)

        Returns:
            list: list of rows in CSV
        """
        self.refreshFromRows()

        jsonO = []
        keys = list(self.data.keys())
        if len(keys) > 0:
            count = len(self.data[keys[0]])
            i = 0
            while i < count:
                row = {}
                for key in keys:
                    value = self.data[key][i]
                    if value == "":
                        if keepEmpty:
                            row[key] = emptyValue
                    else:
                        row[key] = value
                jsonO.append(row)
                i += 1
        return jsonO

    def writeFile(self, filepath, delimiter=None, linebreak=None):
        """write CSV file

        Method to write out data of current object to a CSV file.

        Args:
            filepath (str): path to destination file
            delimiter (str): delimiter to be used for column separation in CSV representation (default: `None`)
            linebreak (str): linebreak to be used in CSV representation (default: `None`)
        """
        self.refreshFromRows()

        if delimiter == None:
            delimiter = self.specs["delimiter"]

        if linebreak == None:
            linebreak = self.specs["linebreak"]

        combined = [[k] + v for k, v in self.data.items()]
        cols = pd.DataFrame(combined).T.values.tolist()
        rows = []

        for r in cols:
            i = 0

            for c in r:
                if c == None:
                    r[i] = ""
                i += 1
            rows.append(
                '"{values}"'.format(
                    values='"{delim}"'.format(delim=delimiter).join(
                        [
                            str(c).replace('"', '"""')
                            if isinstance(c, str) or not math.isnan(c)
                            else ""
                            for c in r
                        ]
                    )
                )
            )

        with open(filepath, "w") as csv_file:
            csv_file.write(linebreak.join(rows))


class ColumnHelper:
    """Helper class for columns

    Attributes:
        ord0: integer representing the Unicode character `A`
    """

    ord0 = ord("A")

    def xlsCol2Int(self, colName):
        """XLS col to int

        According to `A` is `0`, `Z` is `26`, `AA` is `27` and so on, this
        method is meant to translate the alphabetic “number” to an integer.

        Args:
            colName (str): XLS column representation, e.g. `A` or `AA`, ...

        Returns:
            int: index representation as integer
        """
        val = 0
        for ch in colName:  # base-26 decoding "+1"
            val = val * 26 + ord(ch) - self.ord0 + 1
        return val - 1

    def int2xlsCol(self, colInt):
        """int index to XLS index

        According to `A` is `0`, `Z` is `26`, `AA` is `27` and so on, this
        function is meant to translate an integer to its alphabetic “number”
        representation.

        Args:
            colInt (int): index to be transferred to XLS column representation

        Returns:
            str: XLS column representation
        """
        chars = []
        while True:
            if len(chars) > 0:
                colInt = colInt - 1
            ch = colInt % 26
            chars.append(chr(ch + self.ord0))
            colInt = colInt // 26
            if not colInt:
                break
        return "".join(reversed(chars))
