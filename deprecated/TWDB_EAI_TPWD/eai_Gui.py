# added file select dialogs, emptyness test; could use grids

import string
from glob import glob                                   # filename expansion
from Tkinter import *                                   # gui widget stuff
from tkFileDialog import *                              # file selector dialog
from tkMessageBox import showerror,showinfo
from tkSimpleDialog import askstring
from guiWidget.scrolledlist import ScrolledList
from adaptors import TPWDadaptor,TCEQadaptor
from adaptors.common import *



class customizeScrolledList(ScrolledList):
    def runCommand(self,index):
        adaptorPool = adaptor_pool()
        #this should not happen
        #if (not adaptorPool.adaptor.has_key(selection)):
            #print "Mysterious Error happen"
        selection = self.listbox.get(index)
        del adaptorPool.adaptors[selection]
        adaptorPool.stop(selection)
        #update listbox
        self.listbox.delete(index)
            
        

class AdaptorDialog(Frame):
    def __init__(self):
        Frame.__init__(self)                  # a new top-level window
        self.master.title('Adaptor testing....')      # 2 frames plus a button

        srcStrVal, pipeStrVal,sinkStrVal = StringVar(), StringVar(), StringVar()
        self.src, self.pipe, self.sink = srcStrVal, pipeStrVal,sinkStrVal 
        #src, pipe, and sink widgets
        srcFrame = Frame(self) 
        srcLabel = Label(srcFrame,  text='Src config file?', relief=RIDGE, width=15)
        srcEntry = Entry(srcFrame,  relief=SUNKEN) 
        srcBrowse = Button(srcFrame, text='browse...') 
        srcFrame.pack(fill=X)
        srcLabel.pack(side=LEFT)
        srcEntry.pack(side=LEFT, expand=YES, fill=X)
        srcBrowse.pack(side=RIGHT)
        srcBrowse.config(command = 
                         (lambda x=srcStrVal: x.set(askopenfilename())) )

        pipeFrame = Frame(self)
        pipeLabel = Label(pipeFrame,  text='Pipe config file?', relief=RIDGE, width=15)
        pipeEntry = Entry(pipeFrame,  relief=SUNKEN) 
        pipeBrowse = Button(pipeFrame, text='browse...') 
        pipeFrame.pack(fill=X)
        pipeLabel.pack(side=LEFT)
        pipeEntry.pack(side=LEFT, expand=YES, fill=X)
        pipeBrowse.pack(side=RIGHT)
        pipeBrowse.config(command =
                 (lambda x=pipeStrVal: x.set(askopenfilename())) )

        sinkFrame = Frame(self)
        sinkLabel = Label(sinkFrame,  text='Sink config file?', relief=RIDGE, width=15)
        sinkEntry = Entry(sinkFrame,  relief=SUNKEN) 
        sinkBrowse = Button(sinkFrame, text='browse...') 
        sinkFrame.pack(fill=X)
        sinkLabel.pack(side=LEFT)
        sinkEntry.pack(side=LEFT, expand=YES, fill=X)
        sinkBrowse.pack(side=RIGHT)
        sinkBrowse.config(command =
                 (lambda x = sinkStrVal: x.set(askopenfilename())) )

        toolFrame = Frame(self)
        Button(toolFrame, text='Quit', command=self.quit).pack(side=RIGHT)
        Button(toolFrame, text='Run', command=self.runAdaptorDialog).pack(side=RIGHT)
        srcEntry.config(textvariable=srcStrVal)
        pipeEntry.config(textvariable=pipeStrVal)
        sinkEntry.config(textvariable=sinkStrVal)
               
        toolFrame.pack(fill=X)
        
        adListFrame = Frame(self)
        self.adaptorList = customizeScrolledList(parent = adListFrame)
        adListFrame.pack(fill=X)
        self.adaptorList.pack(fill=X)



    def runAdaptorDialog(self):
        try:
           #to be complete
           adtName = askstring('name of the adaptor', 'Please name of the adaptor you are creating')
           #adaptor name verification: if None, just return; if empty string, illegal input
           while adtName == "":
               showinfo("adaptor name error", "sorry,adaptor name cannot be empty....")
               adtName = askstring('name of the adaptor', 'Please name of the adaptor you are creating')
           newAdaptor = None
           if adtName == None:
               return
           elif adtName.find("TPWD") != -1:
               newAdaptor = TPWDadaptor.adaptor(adtName,self.src.get(),self.pipe.get(),self.sink.get())
           elif adtName.find("TCEQ") != -1:
               newAdaptor = TCEQadaptor.adaptor(adtName,self.src.get(),self.pipe.get(),self.sink.get())
           adaptorPool = adaptor_pool()
           while (adaptorPool.adaptors.has_key(adtName)):
               adtName = askstring('name exists', 'Please enter another name for this adaptor')
           # add adaptor to adaptor pool               
           adaptorPool.adaptors[adtName]= newAdaptor
           # schedule the adaptor running 
           adaptorPool.add_operation(adtName,newAdaptor.adpator_run, newAdaptor.adaptorSource.interval)
           self.adaptorList.listbox.insert('end',adtName)
           #adaptor.test(srcConf=self.src.get(),pipeConf=self.pipe.get(),sinkConf=self.sink.get())
        except AssertionError,IOError:
           showerror("Error!",'sorry, an IO error occurred...')                        
           #print self.src.get(),self.pipe.get(),self.sink.get()
           
    def quit(self):
        adaptorPool = adaptor_pool()
        adaptorPool.stop_all()
        for key in adaptorPool.adaptors.keys():
            del adaptorPool.adaptors[key] 
        import sys
        sys.exit()
        #super(self,quit)


if __name__ == '__main__':
    root = Tk()
    AdaptorDialog().pack()
    root.mainloop()
