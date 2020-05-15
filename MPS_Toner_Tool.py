import tkinter as tk
import random as rd
from urllib import request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
from html.entities import name2codepoint
import threading
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
import webbrowser as web

# HTML Parser for old
class OldParser(HTMLParser):
    
    stateMap = {}

    def __init__(self):
        super().__init__()
        # self.__flag = ''
        self.stateMap['CyanToner'] = '100%'
        self.stateMap['MagentaToner'] = '100%'
        self.stateMap['YellowToner'] = '100%'
        self.stateMap['BlackToner'] = '100%'

    def handle_starttag(self, tag, attrs):
        # for 950&725
        if tag == 'td' and len(attrs) == 3:  
            if ('#00ffff') in attrs[1]:
                self.stateMap['CyanToner'] = attrs[2][1]
            if ('#ff00ff') in attrs[1]:
                self.stateMap['MagentaToner'] = attrs[2][1]
            if ('#ffff00') in attrs[1]:
                self.stateMap['YellowToner'] = attrs[2][1]
            if ('#000000') in attrs[1]:
                self.stateMap['BlackToner'] = attrs[2][1]
        # for 811
        if tag == 'td' and len(attrs) == 2 and ('#ffffff') in attrs[1]:
            self.stateMap['BlackToner'] = attrs[0][1]

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

# HTML Parser for new
class NewParser(HTMLParser):

    stateMap = {}

    def __init__(self):
        super().__init__()
        self.__flag = ''
        self.stateMap = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'li' and ('id', 'TonerSupplies') in attrs:
            self.__flag = 'Toner'      
        if self.__flag == 'Toner' and tag =='div' and ('class', 'progress-inner BlackGauge') in attrs:
            print(attrs)
            self.stateMap['BlackToner'] = attrs[2][1]
        if self.__flag == 'Toner' and tag =='div' and ('class', 'progress-inner CyanGauge') in attrs:
            self.stateMap['CyanToner'] = attrs[2][1]
        if self.__flag == 'Toner' and tag =='div' and ('class', 'progress-inner MagentaGauge') in attrs:
            self.stateMap['MagentaToner'] = attrs[2][1]
        if self.__flag == 'Toner' and tag =='div' and ('class', 'progress-inner YellowGauge') in attrs:
            self.stateMap['YellowToner'] = attrs[2][1]

        if tag == 'td' and len(attrs) == 3:  
            if ('#00ffff') in attrs[1]:
                self.stateMap['CyanToner'] = attrs[2][1]
            if ('#ff00ff') in attrs[1]:
                self.stateMap['MagentaToner'] = attrs[2][1]
            if ('#ffff00') in attrs[1]:
                self.stateMap['YellowToner'] = attrs[2][1]
            if ('#000000') in attrs[1]:
                self.stateMap['BlackToner'] = attrs[2][1]
        if tag == 'td' and len(attrs) == 2 and ('#ffffff') in attrs[1]:
            self.stateMap['BlackToner'] = attrs[0][1]

    def handle_endtag(self, tag):
        if tag == 'li':
            self.__flag = ''

    def handle_data(self, data):
        pass

class App:

    def thread_it(self, func):
        t = threading.Thread(target=func)
        t.setDaemon(True)
        t.start()

    def __init__(self, parent):
        self.parent = parent
        self.setupUI()

    def setupUI(self):
        fm = tk.Frame(self.parent)
        fm.pack()

        userLb = tk.Label(fm, text='Directory')
        userLb.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)

        self.dirStr = tk.StringVar()
        userEt = tk.Entry(fm, width=30, textvariable=self.dirStr)
        userEt.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        dirBt = tk.Button(fm, text='Choose dir', command=self.selectPath)
        dirBt.grid(row=0, column=2, sticky=tk.W, padx=5)

        scroll = tk.Scrollbar(self.parent)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb = tk.Listbox(self.parent, yscrollcommand=scroll.set)
        scroll.config(command=self.lb.yview)
        self.lb.bind('<<ListboxSelect>>', self.onClick)

        self.lb.pack(side=tk.TOP, fill = tk.BOTH, expand = tk.YES)
        refreshBtn = tk.Button(self.parent, text='Refresh', command=lambda :self.thread_it(self.refresh), bg = 'CornflowerBlue', fg = 'GhostWhite')
        refreshBtn.pack(side = tk.BOTTOM)

    def onClick(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        web.open(self.lines[index])

    def selectPath(self):
        addrStr_ = askopenfilename()
        self.file = addrStr_
        self.dirStr.set(addrStr_)

    def refresh(self):
        self.lb.delete(0, tk.END)
        if self.file == "":
            showinfo(title='Open file error', message='OOPS, I cannot open your file.')
            return
        try:
            fo = open(r'{0}'.format(self.file), 'r')
            self.lines = fo.readlines()
            if len(self.lines) <= 0:
                showinfo(title='Empty file', message='OOPS, Your file is empty.')
                return
            for index, name in enumerate(self.lines):
                printerName = ''
                if name == '\n':
                    continue
                elif '\n' in name:
                    printerName = name[:-1]
                else:
                    printerName = name
                url = 'http://{}/webglue/content?c=%2FStatus&lang=en'.format(printerName)
                req = request.Request(url)
                try:
                    result = request.urlopen(req, timeout=3)
                    data = result.read().decode('utf-8')
                    parser = NewParser()
                    parser.feed(data)
                    tempStr = ''
                    flag = 4
                    for (k, v) in parser.stateMap.items():
                        tempStr += '{0} {1}'.format(k, v)
                        percent = int(v[:-1])
                        if percent < 30 and flag > 3:
                            flag = 3
                        if percent < 10 and flag > 2:
                            flag = 2
                        if percent < 5 and flag > 1:
                            flag = 1
                    tempStr = '' + name + ': ' + tempStr
                    print(name)
                    self.lb.insert(tk.END, tempStr)
                    if flag == 4:
                        self.lb.itemconfig(index, {'fg': 'green'})
                    elif flag == 1:
                        self.lb.itemconfig(index, {'fg': 'red'})
                    elif flag == 2:
                        self.lb.itemconfig(index, {'fg': 'orangered'})
                    elif flag == 3:
                        self.lb.itemconfig(index, {'fg': 'orange'})

                except URLError as e:
                    url = 'http://{}/cgi-bin/dynamic/printer/PrinterStatus.html'.format(printerName)
                    req = request.Request(url)
                    try:
                        result = request.urlopen(req, timeout=3)
                        data = result.read().decode('utf-8')
                        parser = OldParser()
                        parser.feed(data)
                        tempStr = ''
                        flag = 4
                        for (k, v) in parser.stateMap.items():
                            tempStr += '{0} {1}'.format(k, v)
                            percent = int(v[:-1])
                            if percent < 30 and flag > 3:
                                flag = 3
                            if percent < 10 and flag > 2:
                                flag = 2
                            if percent < 5 and flag > 1:
                                flag = 1
                        tempStr = '' + name + ': ' + tempStr
                        self.lb.insert(tk.END, tempStr)
                        if flag == 4:
                            self.lb.itemconfig(index, {'fg': 'green'})
                        elif flag == 1:
                            self.lb.itemconfig(index, {'fg': 'red'})
                        elif flag == 2:
                            self.lb.itemconfig(index, {'fg': 'orangered'})
                        elif flag == 3:
                            self.lb.itemconfig(index, {'fg': 'orange'})
                    except URLError as e:
                        self.lb.insert(tk.END, '{0}: Not new Lexmark printer or disconnected'.format(name))
                        self.lb.itemconfig(index, {'fg': 'gray'})
        except IOError  as e:
            showinfo(title='Open file error', message='OOPS, I cannot open your file.')
        else:
            fo.close()

root = tk.Tk()
root.title('MPS - Lexmark Printer Toner State Tool')
root.geometry('500x400')
display = App(root)
root.mainloop()

