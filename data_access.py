#!/usr/bin/python
# encoding: utf-8

import sys
import sqlite3

class experiment:

    debug = 0
    
    def create_experiment_table(self, p, append):
        """helper function for constructor __init__"""
        self.conn = sqlite3.connect(p)
        self.c = self.conn.cursor()
        sql="""CREATE TABLE 'values' (t FLOAT, v1 FLOAT""" + append + """)"""
        if self.debug == True: print "sql: " + str(sql)
        self.c.execute(sql)
        
       
    def __init__(self, p=':memory:', vn=2):
        """initiate a new experiment
        
        example usage:
        e = experiment("storage path","count of measurement (v1, v2, etc.)")
        "storage path" is :memory: if nothing is defined, 
        Database is lost when python quits! (ideal for testing)
        """
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
                    return None
                self.create_experiment_table(p, append) 
            else:
                raise Exception("Input Error: Second parameter must be an integer")
                return None  
        else:
            raise Exception("Input Error: First parameter must be a string")
            return None  

    def store_values(a):
        """store values in table values"""
        a = [[t],[v1],[v2]]
        
    def load_experiment(p):
        """load an experiment"""
        
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
        
# Save (commit) the changes
#conn.commit()

# We can also close the cursor if we are done with it
#c.close()