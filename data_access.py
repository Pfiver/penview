# encoding: utf-8
#
# access module (Data model) for an experiment
# 
# the latest version of this code can be found on github:
#     https://github.com/P2000/penview
# (EpyDoc generated) documentation is available on wuala:
#     http://content.wuala.com/contents/patrick2000/Shared/school/11_Projekt/Pendulum/Dokumentation/DB%20V3.pdf?dl=1
#     
# initial version by Tobias Thüring
# modified by Patrick Pfeifer
# 
# Copyleft in December 2010 under the terms of the GNU GPL version 3 or any later version:
#     http://www.gnu.org/licenses/gpl.html

import sys, sqlite3

debug_flag = 0
def debug(*args):
    if not debug_flag:
        return
    import sys
    f = sys._getframe(1)
    if len(args) < 1: args = [""]
    print "%s: %s(): %s" % (f.f_locals.values()[0].__class__, f.f_code.co_name, args[0] % args[1:])

class ExperimentFile:
    
    def create_experiment_table(self):
        """helper function for constructor (__init__)"""

        append = ""
        minv = 1
        maxv = 30

        if self.nvalues < minv or self.nvalues > maxv:
            err = "Input Error: Second parameter must be between 1 and "
            err += str(maxv) + " (v1 to v" + str(maxv) + ")"
            raise Exception(err)

        append = "".join(", v%d FLOAT" % n for n in range(2, self.nvalues+1))

        sql = "CREATE TABLE 'values' (n INT, t FLOAT, v1 FLOAT%s)" % append
        debug("sql: %s" % sql)
        self.c.execute(sql)
       
    def __init__(self, p=':memory:', nv=1):
        """
        initiate a new experiment
        
        :Parameters:
            p      is the filesystem path where the experiment will be stored
            nv     is the number of parameters (y-values) in the data-set

        (p defaults to ":memory:" if not specified: 
         the database is lost when python quits - good for testing)
        """
        # number of x values
        self.nvalues = nv;

        self.conn = sqlite3.connect(p)
        self.c = self.conn.cursor()

        ##TODO Abfangen, wenn die Tabelle bereits im Filesystem besteht
        
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [n[0] for n in self.c.fetchall()]
        
        # Test if 1st parameter has the right vartype
        if type(p) != str:
            raise Exception("Input Error: First parameter must be a string")
        # Test if 2nd parameter has the right vartype
        if type(nv) != int:
            raise Exception("Input Error: Second parameter must be an integer")

        # TODO: dokumentieren
        if 'values' not in tables and 'metadata' not in tables:
            self.create_experiment_table()
            sql = "CREATE TABLE 'metadata' (name TEXT UNIQUE, value TEXT)"
            debug("sql: %s" % sql)
            self.c.execute(sql)
        elif not ('values' in tables and 'metadata' in tables):
            raise Exception("inconsistent database in %s - try another file" % p)
        else:
            # opening of an existing experiment
            sql = "SELECT * from 'values' LIMIT 1"
            debug("sql: %s" % sql)
            self.c.execute(sql)
#            self.nvalues = len(self.c.fetchone())-2
            self.nvalues = len(self.c.description)-2
            debug("nvalues: %d", self.nvalues)

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
            raise Exception("ExperimentFile number must be given as an int")

        debug("a[0]: %s" % str(a[0]) )
        if len(a[0])-1 != self.nvalues:
            raise Exception("wrong number of values")
  
        sql = "INSERT INTO 'values' VALUES (%d, ?%s)" % (nr, (len(a[0])-1) * ", ?")
        debug("sql: %s" % sql)
 
        self.c.executemany(sql, a)

        self.conn.commit()

    def load_values(self, nr=1):
        """
        load the experiments values
        
        :Parameters:
            nr    data series number (default: 1)
        
        if you specify nr, the data is returned in an array like this: [[t,v1,v2,...]]
        """
        if nr == None: 
            sql = "SELECT * from 'values'"
            debug("sql: %s" % sql)
            self.c.execute(sql)
            return self.c.fetchall()

        if type(nr) != int:
            raise Exception("ExperimentFile number must be given as an int")
        
        # test if there are any data series with n
        sql_n = "SELECT DISTINCT n from 'values' "
        debug("sql_n: %s" % sql_n )
        self.c.execute(sql_n)
        nlist = map(lambda x: x[0], self.c.fetchall())
        debug("nr: %s\nnlist: %s" % ( nr, nlist ))
        if nr not in nlist:
            raise Exception("No such data series in values table (%d). Specify another nr" % nr)

        # construct a string like ", v2, v3, v4"
        # vN are numbered from 2 to self.nvalues
        append = "".join(", v%d" % n for n in range(2, self.nvalues+1))
        
        sql = "SELECT t, v1%s from 'values' WHERE n = %d" % (append, nr)
        debug("sql: %s" % sql)
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
            debug("sql, update: %s ( %s )" % ( sql, update ))
            self.c.executemany(sql, update)
 
        if insert:
            sql = "INSERT INTO 'metadata' VALUES (?, ?)"
            debug("sql, insert: %s ( %s )" % ( sql, insert ))
            self.c.executemany(sql, insert)

        self.conn.commit()

    def load_metadata(self):
        """
        load metadata dictionary

        returns a new dictionary object of the experiments metadata values
        """

        sql = "SELECT * FROM 'metadata'"
        debug("sql: %s" % sql )
        self.c.execute(sql)

        return dict(self.c.fetchall())

    def close(self):
        """
        close the experiment
        
        write all data to the disk and close the connection to the database file
        
        after calling ExperimentFile.close() the object must no longer be used
        """
        
        self.conn.close()
