from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox as msgbox
class PassEntry(Entry):
    def __init__(self,master,**kwargs):
        Entry.__init__(self,master,show="*",**kwargs)
        self.cb_var = StringVar()
        self.cb = Checkbutton(master,text="显示密码",variable=self.cb_var,\
                              onvalue="",offvalue="*",command=self.change_cb)
        self.cb_var.set("*")
    def get_cb(self):
        return self.cb
    def change_cb(self):
        self.configure(show=self.cb_var.get())

