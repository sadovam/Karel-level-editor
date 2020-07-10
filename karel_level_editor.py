#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import filedialog
import json

BITMAP = """
#define im_width 32
#define im_height 32
static char im_bits[] = {
"""
for i in range(128):
    BITMAP += '0x00,'
BITMAP += '};'

root = Tk()
bitmap = BitmapImage(data=BITMAP)

class Board(Frame):
    def __init__(self, parent, image, width=3, length=5, world=[]):
        super().__init__(parent)
        self.width = width
        self.length = length
        self.world = world
        self.image = image
        
    def get_symbol_by_coords(self, x, y):
        if not self.world or y >= len(self.world) or x >= len(self.world[0]):
            return ' '
        else:
            return self.world[y][x]
    
    def clear(self):
        for w in self.grid_slaves():
            w.grid_remove()
   
    def redraw(self, width=0, length=0, world=None):
        if self.grid_slaves() and not world:
            self.save_world()
        if world:
            self.world = world
        self.clear()
        if width:
            self.width = width
        if length:
            self.length = length
        for y in range(self.length):
            for x in range(self.width):
                l = Label(self, image=self.image, 
                  text=self.get_symbol_by_coords(x, y), 
                  compound=CENTER, 
                  relief=SUNKEN, bd=3)
                l.grid(row=y, column=x)
                l.bind("<Shift-Button-1>", self.set_wall)
                l.bind("<Button-1>", self.add_beeper)
                l.bind("<Button-3>", self.remove_beeper)
                l.bind("<Control-Button-1>", self.put_karel)
                l.bind("<Double-1>", self.clear_cell)
            
    def save_world(self):
        labels = self.grid_slaves()
        self.world = []
        for y in range(self.length):
            s = ''
            for x in range(self.width):
                s = labels[y * self.width + x]['text'] + s
            self.world.insert(0, s)
        return self.world
            
    def set_wall(self, event):
        event.widget['text'] = "x"
    
    def clear_cell(self, event):
        event.widget['text'] = " "

    def put_karel(self, event):
        t = event.widget['text']
        if t == '>':
            t = '^'
        elif t == '^':
            t = '<'
        elif t == '<':
            t = 'v'
        else:
            t = '>'
        event.widget['text'] = t

    @staticmethod
    def test_cell(text):
        if text.isdigit():
            return int(text)
        return 0

    def add_beeper(self, event):
        num = self.test_cell(event.widget['text'])
        if num < 9:
            num += 1
        event.widget['text'] = str(num)

    def remove_beeper(self, event):
        num = test_cell(event.widget['text'])
        if num > 1:
            num -= 1
        event.widget['text'] = str(num)


class Controls(Frame):
    def __init__(self, parent, board=None, width=3, length=5, actions=1000, beepers=1000):
        super().__init__(parent)
        self.board = board
        
        Label(self, text="Width: ").grid(row=0, column=0)
        Label(self, text="Length: ").grid(row=1, column=0)
        
        self.widthSbx = Spinbox(self, from_=1, to=1000, 
                                width=5, 
                                command=self.change_world_size)
        self.widthSbx.grid(row=0, column=1)
        self.lengthSbx = Spinbox(self, from_=1, to=1000, 
                                 width=5, 
                                 command=self.change_world_size)
        self.lengthSbx.grid(row=1, column=1)
        self.change_readonly_widget_value(self.widthSbx, width)
        self.change_readonly_widget_value(self.lengthSbx, length)
        
        Label(self, text="Actions: ").grid(row=0, column=2)
        Label(self, text="Beepers: ").grid(row=1, column=2)
        
        self.actionsEntry, self.beepersEntry = Entry(self, width=6), Entry(self, width=6)
        self.actionsEntry.grid(row=0, column=3)
        self.beepersEntry.grid(row=1, column=3)
        self.actionsEntry.insert(0, actions)
        self.beepersEntry.insert(0, beepers)
               
        Button(self, text="Load", command=self.load).grid(row=0, column=4)
        Button(self, text="Save", command=self.save).grid(row=1, column=4)
        
        self.board.redraw(width, length)

    def change_readonly_widget_value(self, widget, value):
        widget['state'] = 'normal'
        self.change_widget_value(widget, value)
        widget['state'] = 'readonly'
    
    def change_widget_value(self, widget, value):
        widget.delete(0,END)
        widget.insert(0, value)
    
    def change_world_size(self):
        self.board.redraw(int(self.widthSbx.get()), int(self.lengthSbx.get()))
    
    def load(self):
        new_file = filedialog.askopenfilename(defaultextension='.json')
        if not new_file:
            return
        with open(new_file, "r") as level_file:
            j = json.load(level_file)
        
        w = len(j['scene'][0])
        l = len(j['scene'])
        
        self.change_readonly_widget_value(self.widthSbx, w)
        self.change_readonly_widget_value(self.lengthSbx, l)
        
        self.board.redraw(w, l, j['scene'])
        
        beepers = j["configurations"]["default"]["initial_beepers_count"]
        actions = j["configurations"]["default"]["actions_limit"]
        self.change_widget_value(self.actionsEntry, actions)
        self.change_widget_value(self.beepersEntry, beepers)    
        
    def save(self):
        world = self.board.save_world()
        beepers = self.beepersEntry.get()
        actions = self.actionsEntry.get()
        
        j = {
            'scene': world,
            "configurations" : {
            "default" : {
                "initial_beepers_count" : beepers,
                "actions_limit": actions
            }
            }
        }
        
        new_file = filedialog.asksaveasfilename(defaultextension='.json')
        if not new_file:
            return
        with open(new_file, "w") as level_file:
            json.dump(j, level_file)
    

class App(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        mes = '''Contrl+LeftMouseButton - Add/Rotate Karel
        LeftMouseButton - Add beeper
        RightMouseButton - Remove beeper
        Shift+LeftMouseButton - Add wall
        DoubleClickLeftMouseButton - Clear cell'''
        Label(self, text=mes).pack(side='bottom')
        
        board = Board(self, bitmap)
        board.pack(side='bottom')
        controls = Controls(self, board)
        controls.pack(side='top')

        
app = App(root)
app.pack()        

root.mainloop()
