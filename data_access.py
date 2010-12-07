#!/usr/bin/python
# encoding: utf-8

import sys
import sqlite3

class Experiment:
    """
    access module (Data model) for an experiment
    
    the latest version of this code can be found on github:
        https://github.com/P2000/penview
    (EpyDoc generated) documentation is available on wuala:
        http://content.wuala.com/contents/patrick2000/Shared/school/11_Projekt/Pendulum/Dokumentation/DB%20V3.pdf?dl=1
        
    initial version by Tobias Thüring
    modified by Patrick Pfeifer
    
    Copyleft in December 2010 under the terms of the GNU GPL version 3 or any later version:
        http://www.gnu.org/licenses/gpl.html

    """
    debug = 0
    
    def create_experiment_table(self, p):
        """helper function for constructor (__init__)"""

        append = ""
        minv = 1
        maxv = 30
        if self.debug == True: print "vn " + str(vn)

        if self.nvalues < minv or self.nvalues > maxv:
            err = "Input Error: Second parameter must be between 1 and "
            err += str(maxv) + " (v1 to v" + str(maxv) + ")"
            raise Exception(err)

        append = "".join(", v%d FLOAT" % n for n in range(2, self.nvalues+1))

        sql = "CREATE TABLE 'values' (n INT, t FLOAT, v1 FLOAT%s)" % append
        if Experiment.debug == True: print "sql: " + str(sql)
        self.c.execute(sql)
       
    def __init__(self, p=':memory:', vn=1):
        """
        initiate a new experiment
        
        :Parameters:
            p      is the filesystem path where the experiment will be stored
            vn     is the number of parameters (y-values) in the data-set

        (p defaults to ":memory:" if not specified: 
         the database is lost when python quits - good for testing)
        """
        # number of x values
        self.nvalues = vn;

        self.conn = sqlite3.connect(p)
        self.c = self.conn.cursor()

        ##TODO Abfangen, wenn die Tabelle bereits im Filesystem besteht
        
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [n[0] for n in self.c.fetchall()]
        
        # Test if 1st parameter has the right vartype
        if type(p) != str:
            raise Exception("Input Error: First parameter must be a string")
        # Test if 2nd parameter has the right vartype
        if type(vn) != int:
            raise Exception("Input Error: Second parameter must be an integer")

        # TODO: dokumentieren
        if 'values' not in tables and 'metadata' not in tables:
            self.create_experiment_table(p)
            sql = "CREATE TABLE 'metadata' (name TEXT UNIQUE, value TEXT)"
            if Experiment.debug == True: print "sql: " + str(sql)
            self.c.execute(sql)
        elif not ('values' in tables and 'metadata' in tables):
            raise Exception("inconsistent database in %s - try another file" % p)
 #       else:
 #           pass # opening of an existing experiment

    def store_values(self, nr, a):
        """
        store values a in 'values' table
        
        :Parameters:
            nr    data-set number
            a     values - ex. array of [[t, v1, v2, ...]]
            
        the data format is documented in "DB V3.pdf":
            http://content.wuala.com/contents/patrick2000/Shared/school/11_Projekt/Pendulum/Dokumentation/DB%20V3.pdf?dl=1
        """
 
        if type(nr) != int:
            raise Exception("Experiment number must be given as an int")
 
        if len(a[0])-1 != self.nvalues:
            raise Exception("wrong number of values")
  
        sql = "INSERT INTO 'values' VALUES (%d, ?%s)" % (nr, (len(a[0])-1) * ", ?")
        if Experiment.debug == True: print "sql: " + str(sql)
 
        self.c.executemany(sql, a)

        self.conn.commit()

    def load_values(self, nr=None):
        """
        load the experiments values
        
        :Parameters:
            n    data series number (default: all)
        
        if you specify n, the data is returned in an array like this: [[t,v1,v2,...]]
        if you DON'T specify n, the data is returned in an array like this: [[n,t,v1,v2,...]]
        """

        if nr == None: 
            sql = "SELECT * from 'values'"
            if Experiment.debug == True: print "sql: " + str(sql)
            self.c.execute(sql)
            return self.c.fetchall()

        if type(nr) != int:
            raise Exception("Experiment number must be given as an int")

        # construct a string like ", v2, v3, v4"
        # vN are numbered from 2 to self.nvalues
        append = "".join(", v%d" % n for n in range(2, self.nvalues+1))
        
        sql = "SELECT t, v1%s from 'values' WHERE n = %d" % (append, nr)
        if Experiment.debug == True: print "sql: " + str(sql)
        self.c.execute(sql)
        
        return self.c.fetchall()
        
    def store_metadata(self, a):
        """
        store metadata dictionary a in 'metadata' table, updating existing entries
        
        :Parameters:
            a    metadata dictionary - ex {"name":"value",...}

        the metadata format is documented in "DB V3.pdf":
            http://content.wuala.com/contents/patrick2000/Shared/school/11_Projekt/Pendulum/Dokumentation/DB%20V3.pdf?dl=1
        """
         
        if type(a) != dict:
            raise Exception("wrong type of argument")
 
        self.c.execute("SELECT * FROM 'metadata'")
        old = set(dict(self.c.fetchall()))
        new = set(a)
  
        # detail: for update, value and key are PURPOSELY in
        # the "wrong" order to fit into the sql update statement 
        update = [(a[key], key) for key in new & old]
        insert = [(key, a[key]) for key in new - old]
 
        if update:
            sql = "UPDATE 'metadata' SET value = ? WHERE name = ?"
            if Experiment.debug == True: print "sql: " + str(sql) + " (" + str(update) + ")"
            self.c.executemany(sql, update)
 
        if insert:
            sql = "INSERT INTO 'metadata' VALUES (?, ?)"
            if Experiment.debug == True: print "sql: " + str(sql) + " (" + str(insert) + ")"
            self.c.executemany(sql, insert)

        self.conn.commit()

    def load_metadata(self):
        """
        load metadata dictionary

        returns a new dictionary object of the experiments metadata values
        """

        sql = "SELECT * FROM 'metadata'"
        if Experiment.debug == True: print "sql: " + str(sql)
        self.c.execute(sql)

        return dict(self.c.fetchall())

    def close(self):
        """
        close the experiment
        
        write all data to the disk and close the connection to the database file
        
        after calling Experiment.close() the object must no longer be used
        """
        
        self.conn.close()
