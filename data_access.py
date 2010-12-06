#!/usr/bin/python
# encoding: utf-8

import sys
import sqlite3

class Experiment:
    """access module (Data model) for an experiment"""
    debug = 0
    
    def create_experiment_table(self, p, append):
        """helper function for constructor __init__"""
        self.conn = sqlite3.connect(p)
        self.c = self.conn.cursor()
        sql="""CREATE TABLE 'values' (t FLOAT, v1 FLOAT""" + append + """)"""
        if Experiment.debug == True: print "sql: " + str(sql)
        self.c.execute(sql)     
       
    def __init__(self, p=':memory:', vn=2):
        """initiate a new experiment
        
        example usage:
        e = experiment("storage path","count of measurement (v1, v2, etc.)")
        "storage path" is :memory: if nothing is defined, 
        Database is lost when python quits! (ideal for testing)
        """
        self.nvalues = vn;
        
        ##TODO Abfangen, wenn die Tabelle bereits im Filesystem besteht
        
        # Test if 1st parameter has the right vartype
        if type(p) == str:
            append = ""
            minvn = 1
            maxvn = 30
            if self.debug == True: print "vn " + str(vn)
            # Test if 2nd parameter has the right vartype
            if type(vn) == int:
                if vn == minvn:
                    pass
                elif vn >= minvn + 1 and vn <= maxvn:
                    for n in range(vn-1):
                        nr = n+2
                        append += ", v" + str(nr) + " FLOAT"
                else:
                    err = "Input Error: Second parameter must be between 1 and "
                    err += str(maxvn) + " (v1 to v" + str(maxvn) + ")"
                    raise Exception(err)
                self.create_experiment_table(p, append) 
            else:
                raise Exception("Input Error: Second parameter must be an integer")
        else:
            raise Exception("Input Error: First parameter must be a string")

    def store_values(self, a):
        """store values in table values"""
#        a = [[t],[v1],[v2]]
 
        if len(a[0])-1 != self.nvalues:
            raise Exception("wrong number of values")
 
        append = ""
        for n in range(len(a[0])-1):
            append += ", ?"
 
        sql="INSERT INTO 'values' VALUES (?" + append + ")"
        if Experiment.debug == True: print "sql: " + str(sql)
 
        self.c.executemany(sql, a)
        
    def load_values(self):
        """load the experiments values"""
        
        sql="SELECT * from 'values'"
        if Experiment.debug == True: print "sql: " + str(sql)
        self.c.execute(sql)
        
        return self.c.fetchall()
        
    def store_metadata(a):
        """store metadata in table metadata"""
        """ Mögliche metadatenparameter:
        name:value
        ----------
        date:YYYYMMDDmmss               Datum an dem das Experiment durchgeführt wurde
        name:Experiment1                Name des Experiments
        actor_names:Alice,Dave,Petra    Experimentatoren
        v1_unit:Unit                    Einheit des Messungsvariable v1
        v1_desc:Description             Beschreibung oder Name der Messungsvariable v1 (wird im Plot angezeigt)
        v1_fault:FaultTolerance         Fehlertoleranz
        vn_unit:Unit
        vn_desc:Desc                    vn = v1, v2, v3, etc...
        vn_fault:FaultTolerance         Fehlertoleranz
        id:1                            Messreihen Nummer

        ----------     """
        """"a = {"name":"value",
             }"""
        
        if type(a) != dict:
            raise Exception("wrong type of argument")
 
        sql="INSERT INTO 'metadata' VALUES (?, ?)"
        if Experiment.debug == True: print "sql: " + str(sql)
 
        self.c.executemany(sql, a)
        
# Save (commit) the changes
#conn.commit()

# We can also close the cursor if we are done with it
#c.close()