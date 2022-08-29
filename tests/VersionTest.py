#!/usr/bin/env python3

import os, sys
# CAUTION: `path[0]` is reserved for script path (or '' in REPL)
sys.path.insert( 1, os.getcwd() + '/src/' )

import unittest

from macwinnie_pyhelpers.Version import Version

class VersionTest( unittest.TestCase ):

    p1 = 'v'
    p2 = [ 'v', 'V.', 'version ' ]
    v1 = '1.2.1'
    v2 = '2.3.2'
    v3 = '1.2.2'
    v4 = '1.3.0'
    v5 = '2.0.0'

    def test_definitions( self ):
        """Test if string representation of a version stays exact"""
        vObj = Version( self.v1 )
        self.assertEqual( str( vObj ), self.v1 )
        vObj = Version( self.p1 + self.v2, self.p1 )
        self.assertEqual( str( vObj ), self.v2 )

    def test_increase( self ):
        """Test increasing versions"""
        vObj = Version( self.v1 )
        self.assertEqual( str( vObj.increase() ), self.v3 )
        self.assertEqual( str( vObj.increaseMinor() ), self.v4 )
        self.assertEqual( str( vObj.increaseMajor() ), self.v5 )

    def test_compare( self ):
        """Test version comparison"""
        self.assertEqual( Version( self.v1 ), Version( self.v1 ) )
        self.assertIsNot( Version( self.v1 ), Version( self.v3 ) )
        #
        self.assertLess( Version( self.v1 ), Version( self.v3 ) )
        self.assertLessEqual( Version( self.v1 ), Version( self.v1 ) )
        self.assertLessEqual( Version( self.v1 ), Version( self.v3 ) )
        #
        self.assertGreater( Version( self.v2 ), Version( self.v1 ) )
        self.assertGreaterEqual( Version( self.v1 ), Version( self.v1 ) )
        self.assertGreaterEqual( Version( self.v2 ), Version( self.v1 ) )

    def test_prefixed_equals( self ):
        """Test prefixed versions"""
        for p in self.p2:
            vs = p + self.v1
            vo = Version( vs, self.p2 )
            self.assertEqual( str( vo ), self.v1 )

if __name__ == "__main__":
    unittest.main()
