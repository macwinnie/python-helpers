#!/usr/bin/env python3

import pandas as pd
import math
import io


class CSV:
    """
    Helper class for CSV files, where named columns will be retrievable

    The class needs the data being given as list of lists. Each row (outer list) contains multiple cells (inner list).
    If the data is given JSON like – as a list of dictionaries where each row (dictionary) contains the column names as keys and the cell content as value – the second constructor-parameter has to be set `True`.
    """

    data = {}
    specs = {
        "delimiter": ";",
        "linebreak": "\n",
    }

    def __init__(self, data={}, jsonLike=False):
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

    def setSpec(self, spec, val):
        """function to set specifications for this CSV instance"""
        self.specs[spec] = val

    def readFile(self, filepath, delimiter=None):
        """read a CSV file"""
        self.readCSV(filepath, delimiter=delimiter, file=True)

    def readCSV(self, path_or_csvstring, delimiter=None, encoding="utf-8", file=False):
        """load CSV"""
        if delimiter == None:
            delimiter = self.specs["delimiter"]
        if file:
            data = pd.read_csv(path_or_csvstring, delimiter=delimiter, low_memory=False)
        else:
            data = pd.read_csv(
                io.StringIO(path_or_csvstring.decode(encoding)),
                delimiter=delimiter,
                low_memory=False,
            )
        rows = {}
        for h in data.columns:
            rows[h] = data.get(h).to_list()
        self.data = rows

    def likeJSON(self, keepEmpty=False, emptyValue=None):
        """function to turn CSV to JSON like list of dictionaries"""
        keys = self.data.keys()
        count = len(self.data[keys[0]])
        i = 0
        jsonO = []
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
        return jsonO

    def writeFile(self, filepath, delimiter=None, linebreak=None):
        """function to write out data of current object to a CSV file"""
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
    """Helper class for columns"""

    ord0 = ord("A")

    def xlsCol2Int(self, colName):
        """
        According to `A` is `0`, `Z` is `26`, `AA` is `27` and so on, this
        function is meant to translate the alphabetic “number” to an integer
        """
        val = 0
        for ch in colName:  # base-26 decoding "+1"
            val = val * 26 + ord(ch) - self.ord0 + 1
        return val - 1

    def int2xlsCol(self, colInt):
        """
        According to `A` is `0`, `Z` is `26`, `AA` is `27` and so on, this
        function is meant to translate an integer to its alphabetic “number”
        representation.
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
