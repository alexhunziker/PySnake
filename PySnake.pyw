""" An slim implementation of the game snake with tkinter """

import tkinter as tk
from tkinter import messagebox
import random

__author__ = "Alex Hunziker"
__licence__ = "GPL v3"
__email__ = "alexhunziker@sunrise.ch"


class SnakeGUI(object):
    """ This class implements the GUI for the game """
    
    def __init__(self, snake_obj):
        """ Creates all the necessary objects for the snake GUI """
        self.master = tk.Tk()
        self.master.title("PySnake")
        self.master.minsize(420, 450)
        self.master.maxsize(1220, 1250)
        self.canvas = tk.Canvas(self.master, width=420, height=450,
                                background="#ffffff")
        self.master.bind("<Key>", self.key_pressed)
        self.canvas.pack()
        self.snake_obj = snake_obj
        self.snake_obj.snake_gui = self
        # This keeps track of the window size
        self.canvas.bind("<Configure>", self.resize) 

    def help(self):
        self.snake_obj.pause = True
        """ Displays the help and keyboard controls """
        messagebox.showinfo("PySnake HELP", """Welcome to PySnake.
The aim of the game is: Eat the stars, avoid the red crosses and the border \
of the field. Stay alive as long as possible and collect some points. \n

Controls:
w - change the direction of the snake to "up"
a - change the direction of the snake to "left"
s - change the direction of the snake to "down"
d - change the direction of the snake to "right"

n - New Game
p - Start/Continue or Pause the game

If you have changed the size of the window the field will be adjusted\
 automatically. (Step size 80 pixels, field ratio 4:3 fixed)

Every piece of food you eat gives you 10 points. The speed increases by \
0.5% every time the snake moves""")

    def key_pressed(self, event):
        """ Fetches which key was pressed and takes the required action """
        if event.char == "p":
            self.snake_obj.un_pause()
        elif event.char == "n":
            self.snake_obj.reset(self.snake_obj.fieldsize_x)
        elif event.char == "h":
            self.help()
        else:
            self.snake_obj.get_key_event(event.char)

    def update(self):
        """ Updates the snake field after each turn """
        self.canvas.delete("all")
        self.canvas.create_rectangle(8, 8, self.snake_obj.fieldsize_x*20+12,
                                     self.snake_obj.fieldsize_y*20+12,
                                     fill="#698264", outline="black", width=3)
        for i in range(self.snake_obj.fieldsize_y):
            for j in range(self.snake_obj.fieldsize_x):
                if self.snake_obj.field[i][j] > 0:
                    self.canvas.create_rectangle(j*20+10, i*20+10, j*20+30,
                                                 i*20+30, fill="white")
                if self.snake_obj.field[i][j] == -1:
                    p, o = i*20, j*20
                    points = [o+28, p+20, o+22, p+22, o+20, p+28, o+18, p+22,
                              o+12, p+20, o+18, p+18, o+20, p+12, o+22, p+18]
                    self.canvas.create_polygon(points, outline="black", 
                                               fill='yellow', width=1)
                if self.snake_obj.field[i][j] < -1:
                    p, o = i*20, j*20
                    points = [o+28, p+28, o+20, p+20, o+12, p+28, o+20, p+20,
                              o+12, p+12, o+20, p+20, o+28, p+12, o+20, p+20]
                    self.canvas.create_polygon(points, outline="red", 
                                               width=3)
        self.canvas.create_text(100, self.snake_obj.fieldsize_y * 20 + 30,
                                text="Current Score: {}"
                                .format(self.snake_obj.points))
        self.canvas.create_text(100, self.snake_obj.fieldsize_y * 20 + 42,
                                text="Current Speed: {0:.2f}"
                                .format(500 / self.snake_obj.wait_time))
        self.canvas.create_text(100, self.snake_obj.fieldsize_y * 20 + 100,
                                text="""Controls:
w, a, s, d - Change snake direction
n - New Game
p - Play / Pause
h - Show more help""")

    def resize(self, event=None):
        """ Resizes the field for the snake """
        new_x = (self.master.winfo_width()-20) // 80 * 4
        new_y = int(new_x / 4 * 3)
        self.canvas.config(width=new_x*20+20, height=new_y*20+150)
        self.master.config(width=new_x*20+20, height=new_y*20+150)
        self.snake_obj.reset(new_x)
                   
        
class Snake(object):
    """ This class implements the logic of the snake game """
    
    def __init__(self, snake_gui=None):
        """ Initialization; connects the gui to this object, if specified """
        self.reset(20)
        self.snake_gui = snake_gui
        if self.snake_gui is not None:
            self.snake_gui.snake_obj = self

    def reset(self, size_x):
        """ This funciton initializes / resets the game """
        self.turn = 5
        self.direction = "d"
        self.delete = 1
        self.fieldsize_x = size_x
        self.fieldsize_y = int(self.fieldsize_x / 4 * 3)
        self.field = []
        for filler in range(self.fieldsize_y):
            self.field.append([0]*self.fieldsize_x)
        self.field[5][1] = 2
        self.field[5][2] = 3
        self.field[5][3] = 4
        self.head = [5, 3]
        self.wait_time = 500
        self.points = 0
        self.place_food()
        self.pause = True

    def start(self):
        """ This is the main loop and controlls if the game is paused """
        if not self.pause:
            self.move_snake()
        self.snake_gui.update()
        self.curr_dir_changed = False
        self.snake_gui.master.after(self.wait_time, self.start)

    def place_food(self):
        """ Creates a new food (star) if required """
        while True:
            ran_f = random.choice(range(self.fieldsize_x * self.fieldsize_y))
            pos_x = ran_f // self.fieldsize_x
            pos_y = ran_f % self.fieldsize_x
            if self.field[pos_x][pos_y] == 0\
               and self.mindist(2, ran_f):
                self.field[pos_x][pos_y] = -1
                break

    def place_obstacle(self):
        if random.uniform(0, 1) > 0.8:
            while True:
                ran_f = random.choice(range(self.fieldsize_x*self.fieldsize_y))
                pos_x = ran_f // self.fieldsize_x
                pos_y = ran_f % self.fieldsize_x
                if self.field[pos_x][pos_y] == 0\
                   and self.mindist(3, ran_f):
                    self.field[pos_x][pos_y]\
                                = -self.delete - random.choice(range(3, 20))
                    break

    def mindist(self, dist, ran_f):
        """ Makes sure objects do not appear to close to the snake """
        x = ran_f // self.fieldsize_x
        y = ran_f % self.fieldsize_x
        if self.head[0] in range(x-dist, x+dist+1) and \
           self.head[1] in range(y-dist, y+dist+1):
            return False
        return True

    def un_pause(self):
        """ Pause or unpause the game, by setting the required flag """
        if self.pause:
            self.pause = False
        else:
            self.pause = True

    def move_snake(self):
        """ This funciton implements the movement of the snake
        and collision detection """
        
        if self.direction == "d" and self.fieldsize_x > self.head[1]+1:
            self.head[1] += 1
        elif self.direction == "a" and 0 < self.head[1]:
            self.head[1] -= 1
        elif self.direction == "w" and 0 < self.head[0]:
            self.head[0] -= 1
        elif self.direction == "s" and self.fieldsize_y > self.head[0]+1:
            self.head[0] += 1
        else:
            messagebox.showinfo("Oh no...", "You just collided with the \
wall... Game over")
            self.reset(self.fieldsize_x)
            return
        self.delete += 1
        for i in range(self.fieldsize_y):
            for j in range(self.fieldsize_x):
                if abs(self.field[i][j]) == self.delete:
                    self.field[i][j] = 0
        # Food eaten
        if self.field[self.head[0]][self.head[1]] == -1:
            # Limit snake size to maximum of 10
            if self.turn - self.delete < 10:
                self.turn += 1
            self.update_points(10)
            self.place_food()
        if self.field[self.head[0]][self.head[1]] > 0:
            messagebox.showinfo("Oh no...", "You just collided with yourself\
... Game over")
            self.reset(self.fieldsize_x)
        elif self.field[self.head[0]][self.head[1]] < -1:
            messagebox.showinfo("Oh no...", "You just collided with an \
obstacle... Game over")
            self.reset(self.fieldsize_x)
        else:
            self.field[self.head[0]][self.head[1]] = self.turn
            self.place_obstacle()
            self.increase_speed()
            self.turn += 1

    def increase_speed(self):
        """ Increases the speed after each move """
        if self.wait_time > 50:
            self.wait_time = int(self.wait_time * 0.995)       

    def update_points(self, points):
        """ Adds some points if food was eaten """
        self.points += points

    def get_key_event(self, char):
        """ Updates the direction of the snake """
        if self.curr_dir_changed:    # Avoid double movements in one turn
            return
        if char == "a" and self.direction != "d":
            self.direction = "a"
        elif char == "d" and self.direction != "a":
            self.direction = "d"
        elif char == "w" and self.direction != "s":
            self.direction = "w"
        elif char == "s" and self.direction != "w":
            self.direction = "s"
        else:
            return
        self.curr_dir_changed = True


if __name__ == "__main__":
    # Here we launch the game, by initializing 2 objects and
    # calling the start funciton
    so = Snake()
    sg = SnakeGUI(so)
    so.start()
    sg.master.mainloop()
