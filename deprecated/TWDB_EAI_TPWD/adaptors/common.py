'''
Created on Jul 30, 2010

@author: CTtan
'''
import StringIO,threading,thread


class Operation(threading._Timer):
    def __init__(self, name, *args, **kwargs):
        #first time flag. the first run of function will have no pause/interval
        self.firstTime = True
        #add a name for selective terminate:
        self.name = name
        #other initialization chore
        threading._Timer.__init__(self, *args, **kwargs)
        self.setDaemon(True)

    def run(self):
        if self.firstTime :
            self.function(*self.args, **self.kwargs)
            self.firstTime = False
        while True:
            self.finished.clear()
            self.finished.wait(self.interval)
            if not self.finished.isSet():
                self.function(*self.args, **self.kwargs)
            else:
                return
            self.finished.set()


#build a complete adapter (including source,pipe(s) and sink (s))
#note: an adapter can have multiple log(s), pipe(s) and sink(s)
config = ["testAdaptor_config\logParam.xml","testAdaptor_config\srcParam.xml", \
          "testAdaptor_config\pipeParam.xml","testAdaptor_config\sinkParam.xml"]

#make this a singleton, Borg style: for possible extension
class Singleton(object):
    _state = {}
    def __new__(cls,*args,**kw):
        ob = super(Singleton,cls).__new__(cls,*args,**kw)
        ob.__dict__ = cls._state
        return ob


class adaptor_pool(Singleton):
    existingAdaptor = ["TPWD","TCEQ"]
    adaptors = {}
    ops = []
    def add_operation(self,name,operation, interval, args=[], kwargs={}):
        op = Operation(name,interval, operation, args, kwargs)
        self.ops.append(op)
        thread.start_new_thread(op.run, ())

    def stop_all(self):
        for op in self.ops:
            op.cancel()
        #self._event.set()
    def stop(self,name):
        for op in self.ops:
            if op.name == name:
                op.cancel()
            else:
                continue
