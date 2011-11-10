from Tkinter import * 
from ScrolledText import ScrolledText

class GuiOutput:
    def __init__(self, name,parent=None):
        self.text = None
        self.titleName = name
        if parent: self.popupnow(name,parent)         # popup now or on first write
    def popupnow(self,name,parent=None):             # in parent now, Toplevel later
        if self.text: return
        newTopLevel = Toplevel()
        self.text = ScrolledText(parent or newTopLevel)
        newTopLevel.title(name)
        self.text.config(font=('courier', 9, 'normal'))
        #if it is a toplevel textbox, set its title.
        self.text.pack()
    def write(self, text):
        self.popupnow(self.titleName)
        #if len(self.text.get("1.0")) > 1024:
        #    self.text.delete("1.0",END)
        self.text.insert(END, str(text))
        self.text.see(END)
        self.text.update()
    def writelines(self, lines):                 # lines already have '\n'
        for line in lines: self.write(line)      # or map(self.write, lines)
    def flush(self):
        pass

    
if __name__ == '__main__':
    import logging
    #sample logging
    def test_sampleLog():
        # create logger
        logger = logging.getLogger("simple_example")
        logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler(GuiOutput("something"))
        ch.setLevel(logging.DEBUG)   
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")   
        # add formatter to ch
        ch.setFormatter(formatter)    
        # add ch to logger
        logger.addHandler(ch)    
        # "application" code
        logger.debug("debug message")
        logger.info("info message")
        logger.warn("warn message")
        logger.error("error message")
        logger.critical("critical message")
    root = Tk()
    Button(root, text = "test logging to GuiStreams",
                   command = lambda: test_sampleLog()).pack(fill=X)
    root.mainloop()

