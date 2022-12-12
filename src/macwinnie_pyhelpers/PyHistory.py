#!/usr/bin/env python3

import readline


class PyHistory:
    """
    Helper while development: python cli history to summarize the executed commands on CLI
    """

    showLineNumbers = False

    def __init__(self, lineNumbers=False):
        """initialize the History object"""
        self.showLineNumbers = lineNumbers

    def print(self, showLineNumbers=None):
        """Print out history"""
        if showLineNumbers == None:
            showLineNumbers = self.showLineNumbers
        if showLineNumbers:
            formatstring = "{0:4d}  {1!s}"
        else:
            formatstring = "{1!s}"
        for i in range(1, readline.get_current_history_length() + 1):
            print(formatstring.format(i, readline.get_history_item(i)))
