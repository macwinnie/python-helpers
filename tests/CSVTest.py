#!/usr/bin/env python3

import os, sys
# CAUTION: `path[0]` is reserved for script path (or '' in REPL)
sys.path.insert( 1, os.getcwd() + '/src/' )

import unittest

from macwinnie_pyhelpers.CSV import ColumnHelper

class CSVTest( unittest.TestCase ):

    def test_numberTransform( self ):
        ch = ColumnHelper()
        chars = []
        ints  = []
        r     = range( 0, 100000 )
        # translate all numbers in range
        for i in r:
            chars.append( ch.int2xlsCol( i ) )
        # remove duplicates
        chars = list( dict.fromkeys( chars ) )
        self.assertEqual( len( chars ), len( list( r ) ) )
        # translate alphabeticals back to ints
        for a in chars:
            ints.append( ch.xlsCol2Int( a ) )
        ints = list( dict.fromkeys( ints ) )
        self.assertEqual( len( ints ), len( list( r ) ) )
        self.assertEqual( ints, list( r ) )

if __name__ == "__main__":
    unittest.main()
