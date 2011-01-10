#!/usr/bin/python
# encoding: utf-8

#import unittest
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from data_access import ExperimentFile

class test:
    ## TODO: an unittest anpassen
    debug = 0
    badtestcount = 0
    goodtestcount = 0
    baderrorcount = 0
    gooderrorcount = 0
    errbuffer = ""
    dbpath = '/tmp/'
    dbname = 'example'
    dbdestination = dbpath + dbname    
    dbdestination = ':memory:'
       
    def run(self):
        self.goodtest()
        self.badtest()
        
    def goodtest(self):
        """This Test should NOT raise Errors"""
        testcount = 0
        errorcount = 0

        # Some value table tests    
        for n in [2,12]:
            testcount += 1
            try: 
                e = ExperimentFile(self.dbdestination,n)

                values = []
                for i in range(2):
                    values += [[i] + [0] * n]
                e.store_values(0, values)
                e.store_values(1, values)
                     
                result = e.load_values(0)
                if result != [(0.0,) + n * (0.0,),
                              (1.0,) + n * (0.0,)]:
                    if self.debug: 
                            print "res: %s" % result
                            print "res: %s" % [(0.0,) + n * (0.0,), (1.0,) + n * (0.0,)]
                    raise Exception("library malfunction 0")
                allresults = e.load_values(0)
                allresults += e.load_values(1)
                testresults = [(0.0,) + n * (0.0,),
                               (1.0,) + n * (0.0,),
                               (0.0,) + n * (0.0,),
                               (1.0,) + n * (0.0,)]
                if self.debug: print "testresults: %s" % testresults
                if allresults != testresults:
                    if self.debug: print "allresults:  %s" % allresults
                    raise Exception("library malfunction 1")
                e.close()

            except Exception, e: 
                errorcount += 1
                if self.debug: self.errbuffer += str(e) + "\n"

            if self.dbdestination != ":memory:": os.unlink(self.dbdestination)

        # Some metadata table tests
        testcount += 1
        e = ExperimentFile(self.dbdestination,1)

        if 1:
            for metadata in ({"x":u"y"}, {"x":u"z"}, {"name":u"x1", "v1unit":u"m/s^2"}):
                testcount += 1
                try:
                    e.store_metadata(metadata)
                    if not set(metadata.iteritems()) \
                        .issubset( set(e.load_metadata().iteritems()) ):
                        raise Exception("library malfunction 2")
                except Exception, ex:
                    errorcount += 1
                    if self.debug: self.errbuffer += str(ex) + "\n"

        if self.dbdestination != ":memory:": os.unlink(self.dbdestination)
        self.goodtestcount = testcount
        self.gooderrorcount = errorcount
        
    def badtest(self):
        """This Test should raise Errors"""
        testcount = 0
        errorcount = 0

        # Some constructor tests
        testcount += 1
        try: 
            e = ExperimentFile(self.dbdestination,"blubber")
        except Exception, e:
            errorcount += 1
#            if self.debug: self.errbuffer += str(e) + "\n"
        for n in [-1,99,109,"blub"]:
            testcount += 1
            try: 
                e = ExperimentFile(self.dbdestination,n)
            except Exception, e: 
                errorcount += 1
#                if self.debug: self.errbuffer += str(e) + "\n"

        if self.dbdestination != ":memory:": os.unlink(self.dbdestination)
        self.badtestcount = testcount
        self.baderrorcount = errorcount
    
test1 = test()

if test1.gooderrorcount == 0:
    print "goodtest(): OK"
else:
    print "goodtest(): Not OK"
    if test1.debug:
        print "errbuffer: \n" + test1.errbuffer

if test1.baderrorcount == test1.badtestcount:
    print "badtest(): OK"
else:
    print "badtest(): Not OK"
    if test1.debug:
        print "errbuffer: \n" + test1.errbuffer
