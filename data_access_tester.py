#!/usr/bin/python
# encoding: utf-8

#import unittest
from data_access import Experiment

class test:
    ## TODO: an unittest anpassen
    Experiment.debug = 1
    debug = 1
    badtestcount = 0
    goodtestcount = 0
    baderrorcount = 0
    gooderrorcount = 0
    errbuffer = ""
    dbpath = '/tmp/'
    dbname = 'example'
    dbdestination = dbpath + dbname    
    dbdestination = ':memory:'
       
    def __init__(self):
        self.goodtest()
        self.badtest()
        
    def goodtest(self):
        """This Test should NOT raise Errors"""
        testcount = 0
        errorcount = 0

        # Here come some tests    
        for n in [2,12]:
            testcount += 1
            try: 
                e = Experiment(self.dbdestination,n)

                values = []
                for i in range(2):
                    values += [[i] + [0] * n]
                e.store_values(values)

                result = e.load_values()
                if result != [(0.0,) + n * (0.0,),
                              (1.0,) + n * (0.0,)]:
                    raise Exception("library malfunction")

            except Exception, e: 
                errorcount += 1
                if self.debug: self.errbuffer += str(e) + "\n"
            
        self.goodtestcount = testcount
        self.gooderrorcount = errorcount
        
    def badtest(self):
            """This Test should raise Errors"""
            testcount = 0
            errorcount = 0  
            # Here come some tests     
            testcount += 1
            try: 
                e = Experiment(self.dbdestination,"blubber")
            except Exception, e:
                errorcount += 1
                self.errbuffer += str(e) + "\n"
            for n in [-1,99,109,"blub"]:
                testcount += 1
                try: 
                    e = Experiment(self.dbdestination,n)
                except Exception, e: 
                    errorcount += 1
                    self.errbuffer += str(e) + "\n"
                
            self.badtestcount = testcount
            self.baderrorcount = errorcount
    
test1 = test()

if test1.baderrorcount == test1.badtestcount:
    print "baderror(): OK"
else:
    print "baderror(): Panic!"
    if self.debug: print "errbuffer: \n" + test1.errbuffer
    print "bad errorcount == " + str(test1.baderrorcount)
if test1.gooderrorcount == 0:
    print "gooderror(): OK"
else:
    print "gooderror(): Not OK"
    if test1.debug: print "errbuffer: \n" + test1.errbuffer