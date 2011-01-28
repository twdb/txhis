from Tkinter import * 
from tkMessageBox import askyesno

class ScrolledList(Frame):
    def __init__(self, options = [], parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)                  # make me expandable
        self.makeWidgets(options)
    def handleList(self, event):
        index = self.listbox.curselection()               # on list double-click
        #label = self.listbox.get(index)                   # fetch selection text
        if askyesno('Verify','Do you want to cancel this adaptor?'):
            self.runCommand(index)                        # and call action here
        else:
            pass
    def makeWidgets(self, options):                       # or get(ACTIVE)
        sbar = Scrollbar(self)
        list = Listbox(self, relief=SUNKEN)
        sbar.config(command=list.yview)                   # xlink sbar and list
        list.config(yscrollcommand=sbar.set)              # move one moves other
        sbar.pack(side=RIGHT, fill=Y)                     # pack first=clip last
        list.pack(side=LEFT, expand=YES, fill=BOTH)       # list clipped first
        pos = 0
        for label in options:                             # add to list-box
            list.insert(pos, label)                       # or insert(END,label)
            pos = pos + 1
       #list.config(selectmode=SINGLE, setgrid=1)         # select,resize modes
        list.bind('<Double-1>', self.handleList)          # set event handler
        self.listbox = list
    def runCommand(self,selection):              # redefine me lower
        print 'You selected:', self.listbox.get(index)
    
if __name__ == '__main__':
    options = map((lambda x: 'Lumberjack-' + str(x)), range(20))
    ScrolledList(options).mainloop()

