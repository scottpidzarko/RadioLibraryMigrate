import unittest
import main
import string

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

#Since this deals with database tests we will use a modified version of the function to test it on an
class FuzzyListLMatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.data = ((1,"Good Tst"),(2,"Gibbrish Something Else"),(3,"A Good Test STrring"), (4,"A GoodTestStrign"),
        (5,"kjlkja;ldkjf"), (6,"A Bad Test String"),(7,"Firstname, Lastname"), (8,"Lastname, Firstname"),
        (9,"Firstname Lastname"), (10,"Lastname Firstname"), (11, "Firstname LAstnaem"),
        (12, "LAsTnaem Firstname"), (13, "Something Firstname"), (14, "lkj;lkj Lastname"),
        (15, "First Last"), (16,"Last First"))
    def testTypicalUse(self):
        self.assertEqual(main.fuzzyListMatch(self.data,"A Good Test String",10), [3])
    def testGibberish(self):
        self.assertEqual(main.fuzzyListMatch(self.data,"l;kj;lkj",10), [])
    def testTokenization(self):
        self.assertEqual(main.fuzzyListMatch(self.data, "Lastname, Firstname",50),[8,10,12])
    def testExactMatch(self):
        self.data = ((1,"abcde"), (2,"fghij"), (3,"klmno"), (4,"pqrst"), (5,"uvwxyz"))
        self.assertEqual(main.fuzzyListMatch(self.data, "abcde",75),[1])
        self.assertEqual(main.fuzzyListMatch(self.data, "fghij",75),[2])
        self.assertEqual(main.fuzzyListMatch(self.data, "klmno",75),[3])
        self.assertEqual(main.fuzzyListMatch(self.data, "pqrst",75),[4])
        self.assertEqual(main.fuzzyListMatch(self.data, "uvwxyz",75),[5])

class FilenameSanitizeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

    def testLegitimateString(self):
        self.assertEqual(main.formatFileName("A totally Legit string"), "A totally Legit string")
        self.assertEqual(main.formatFileName("-_()$!@#^&~`+=[]}{'., %s%s" % (string.digits,'%')), "-_()$!@#^&~`+=[]}{'., %s%s" % (string.digits,'%'))
        self.assertEqual(main.formatForDoubleFilePath("Totally Legit string"), "TO")
        self.assertEqual(main.formatForDoubleFilePath("-_()$!@#^&~`+=[]}{\'., %s%s" % (string.digits,'%')), ("-_"))
        self.assertEqual(main.formatFileName("TrailingSpaceTest "),"TrailingSpaceTest")
        self.assertEqual(main.formatForDoubleFilePath("A "),"A_")
        self.maxDiff = None
        self.assertEqual(main.formatFileName("PMUuKZYzT6bTUlwBQ9oZHDiTNq3ba9VyCMX70xIoMs02QOTgJ3z0kepsCSbSe2YawNrP4vvHugoqCwOGD4IhmFcyYTxWG6X26WiJ6uKT7JIcHhXNpmAqTwfPbGONmOV48yOfoQPQ409TETbrtLgfZcXgMCxavJtmYpP7HRVo58o9Z6RgbPwlgl6zazLJq9mSr0FPcHwsgFu9k4l7v2qyukBBkEwDI4Oug1W57q9jXEuo3jq" + \
        "7V5AAM3umAHIzSGM.mp3"),"PMUuKZYzT6bTUlwBQ9oZHDiTNq3ba9VyCMX70xIoMs02QOTgJ3z0kepsCSbSe2YawNrP4vvHugoqCwOGD4IhmFcyYTxWG6X26WiJ6uKT7JIcHhXNpmAqTwfPbGONmOV48yOfoQPQ409TETbrtLgfZcXgMCxavJtmYpP7HRVo58o9Z6RgbPwlgl6zazLJq9mSr0FPcHwsgFu9k4l7v2qy" + \
        "ukBBkEwDI4Oug1W57q9jXEuo3jq7V5AAM3u....mp3")
        self.assertEqual(main.formatFileName(None),"---")
        self.assertEqual(main.formatForDoubleFilePath(None),"--")
        self.assertEqual(main.formatFileDirectory(None),"---")

    def testIllegitimateString(self):
        string = "A totally <>:\"/\|?* Not Legit string"
        self.assertEqual(main.formatFileName(string), "A totally --------- Not Legit string")
        badlist = ("CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
    	 "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
    	 "LPT6", "LPT7", "LPT8", "LPT9", "nul")
        for s in badlist:
            self.assertEqual(main.formatFileName(s+".exe"), "(bad filename).exe")
        self.assertEqual(main.formatForDoubleFilePath("<>:\"/\|?* Not Legit string"), "--")
        self.assertEqual(main.formatFileName("One Girl / One Boy"),"One Girl - One Boy")

class ArtistTheTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

    def testGood(self):
        self.assertEqual(main.formatArtist("The Glitch Mob"), "Glitch Mob, The")
    def testBad(self):
        self.assertEqual(main.formatArtist("lkjaldkjfa;lkdsjf"), "lkjaldkjfa;lkdsjf")

if __name__ == '__main__':
        unittest.main()
