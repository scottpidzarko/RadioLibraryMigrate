import unittest
import main

#Example
"""class IntegerArithmenticTestCase(unittest.TestCase):
    def testAdd(self):  ## test method names begin 'test*'
        self.assertEquals((1 + 2), 3)
        self.assertEquals(0 + 1, 1)
    def testMultiply(self):
        self.assertEquals((0 * 10), 0)
        self.assertEquals((5 * 8), 40)"""

class FuzzyMatchTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.femconMisspell = ("emcon","fmcon","fecon","femon","femcn","femco","ffemcon","feemcon","femmcon","femccon","femcoon","femconn","demcon","remcon","temcon","gemcon","vemcon","cemcon","fwmcon","f3mcon","f4mcon","frmcon","ffmcon","fdmcon","fsmcon","fencon","fejcon","fekcon","femxon","femdon","femfon","femvon","femcin","femc9n","femc0n","femcpn","femcln","femckn","femcob","femcoh","femcoj","femcom","dfemcon","fdemcon","rfemcon","fremcon","tfemcon","ftemcon","gfemcon","fgemcon","vfemcon","fvemcon","cfemcon","fcemcon","fwemcon","fewmcon","f3emcon","fe3mcon","f4emcon","fe4mcon","fremcon","fermcon","ffemcon","fefmcon","fdemcon","fedmcon","fsemcon","fesmcon","fenmcon","femncon","fejmcon","femjcon","fekmcon","femkcon","femxcon","femcxon","femdcon","femcdon","femfcon","femcfon","femvcon","femcvon","femcion","femcoin","femc9on","femco9n","femc0on","femco0n","femcpon","femcopn","femclon","femcoln","femckon","femcokn","femcobn","femconb","femcohn","femconh","femcojn","femconj","femcomn","femconm")
        self.canconMisspell = ("ancon",  "cncon", "cacon", "canon","cancn","canco","ccancon","caancon","canncon","canccon","cancoon","canconn","xancon","dancon","fancon","vancon","cqncon","cwncon","csncon","cxncon","czncon","cabcon","cahcon","cajcon","camcon","canxon","candon","canfon","canvon","cancin","canc9n","canc0n","cancpn","cancln","canckn","cancob","cancoh","cancoj","cancom","xcancon","cxancon","dcancon","cdancon","fcancon","cfancon","vcancon","cvancon","cqancon","caqncon","cwancon","cawncon","csancon","casncon","cxancon","caxncon","czancon","cazncon","cabncon","canbcon","cahncon","canhcon","cajncon","canjcon","camncon","canmcon","canxcon","cancxon","candcon","cancdon","canfcon","cancfon","canvcon","cancvon","cancion","cancoin","canc9on","canco9n","canc0on","canco0n","cancpon","cancopn","canclon","cancoln","canckon","cancokn","cancobn","canconb","cancohn","canconh","cancojn","canconj","cancomn","canconm")
        self.localMisspell = ("ocal","lcal","loal","locl","loca","llocal","loocal","loccal","locaal","locall","kocal","oocal","pocal","lical","l9cal","l0cal","lpcal","llcal","lkcal","loxal","lodal","lofal","loval","locql","locwl","locsl","locxl","loczl","locak","locao","locap","klocal","lkocal","olocal","loocal","plocal","lpocal","liocal","loical","l9ocal","lo9cal","l0ocal","lo0cal","lpocal","lopcal","llocal","lolcal","lkocal","lokcal","loxcal","locxal","lodcal","locdal","lofcal","locfal","lovcal","locval","locqal","locaql","locwal","locawl","locsal","locasl","locxal","locaxl","loczal","locazl","locakl","localk","locaol","localo","locapl","localp")

    def testCancon(self):
        for misspelling in self.femconMisspell:
            #print( misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "cancon", 15), False)
        for misspelling in self.canconMisspell:
            #print(misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "cancon", 15), True)
        for misspelling in self.localMisspell:
            #print(misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "cancon", 15), False)
    def testFemcon(self):
        for misspelling in self.femconMisspell:
            #print( misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "femcon", 15), True)
        for misspelling in self.canconMisspell:
            #print(misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "femcon", 15), False)
        for misspelling in self.localMisspell:
            #print(misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "femcon", 15), False)
    def testLocal(self):
        for misspelling in self.femconMisspell:
            #print( misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "local", 15), False)
        for misspelling in self.canconMisspell:
            #print(misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "local", 15), False)
        for misspelling in self.localMisspell:
            #print(misspelling)
            self.assertEqual(main.fuzzyContains(misspelling, "local", 15), True)

if __name__ == '__main__':
        unittest.main()
