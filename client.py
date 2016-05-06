# A tic-tac-toe game written in Python with Pyglet.
# Copyright (C) 10se1ucgo 2016
#
# This file is part of TicTacToe.
#
# TicTacToe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TicTacToe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TicTacToe. If not, see <http://www.gnu.org/licenses/>.
import math
import select
import struct
import socket

import pyglet
from pyglet.gl import *

LINE_THICKNESS = 24

O = -1  # O piece
E = 0   # Empty tile
X = 1   # X piece

pieces = {
    O: "O",
    X: "X"
}

BUFFER = 4096
STATE = struct.Struct('!bbb9b')
PLACE = struct.Struct('!2b')
PSIZE = struct.Struct('!B')


class Game(object):
    def __init__(self):
        self.win = None
        self.turn = X
        self.board = [[E, E, E], [E, E, E], [E, E, E]]
        self.piece = E

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 420))
        self.update()

    def state(self):
        if self.win:
            return "{winner} wins!".format(winner=pieces[self.win])
        elif self.win == 0:
            return "It's a draw!"
        elif self.turn == self.piece:
            return "It's your turn"
        else:
            return "It's {piece}'s turn".format(piece=pieces[self.turn])

    def update(self, dt=0):
        read, write, errors = select.select([self.sock], [], [], 0)
        for sock in read:
            if sock == self.sock:
                data = self.sock.recv(12)
                state = STATE.unpack(data)
                self.turn = state[0]
                self.piece = state[1]
                self.win = None if state[2] == 2 else state[2]
                self.board = [state[3:][x:x + 3] for x in range(0, len(state[3:]), 3)]
                print("I am {piece}".format(piece=pieces[self.piece]))

    def place_tile(self, x, y):
        if self.board[x][y] != E:
            return
        if self.win is not None:
            return
        if self.turn != self.piece:
            return
        self.sock.send(PLACE.pack(x, y))
        # if self.board[x, y] != E:
        #     return
        # if self.win is not None:
        #     return
        # self.board[x, y] = self.turn
        # self.turn = -self.turn
        # self.win = self.check_win()
        # if self.win is not None:
        #     pyglet.clock.schedule_once(self.reset, 1)

    # def reset(self, dt=0):
    #     self.board.fill(E)
    #     self.turn = X
    #     self.win = None


class MainWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(600, 600, *args, **kwargs)
        self.set_caption("Tic-Tac-Toe")

    def on_mouse_press(self, x, y, button, modifiers):
        for i in range(1, 4):
            if x < (self.width / 3) * i:
                col = i - 1
                break

        for i in range(1, 4):
            if y < (self.height / 3) * i:
                row = 3 - i
                break

        game.place_tile(row, col)

    def on_draw(self):
        self.clear()
        glLineWidth(LINE_THICKNESS)
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.draw_board()

        board = list(zip(*game.board[::-1]))
        for x in range(3):
            for y in range(3):
                glPushMatrix()
                glTranslatef(((self.width / 3) * (x - 1)), ((self.height / 3) * (y - 1)), 0.0)
                if board[x][y] == X:
                    self.draw_x()
                elif board[x][y] == O:
                    self.draw_o()
                glPopMatrix()

        state_label = pyglet.text.Label(game.state(),
                                        font_name='Arial',
                                        font_size=self.width // 10,
                                        x=self.width // 2, y=self.width // 10,
                                        anchor_x='center', anchor_y='center',
                                        color=(255, 0, 0, 255))
        state_label.draw()

    def draw_board(self):
        for x in range(1, 3):
            glBegin(GL_LINES)
            glVertex2f(0, ((self.height / 3) * x))
            glVertex2f(self.width, ((self.height / 3) * x))
            glEnd()

        for x in range(1, 3):
            glBegin(GL_LINES)
            glVertex2f(((self.width / 3) * x), 0)
            glVertex2f(((self.width / 3) * x), self.height)
            glEnd()

    def draw_o(self):
        glPushMatrix()
        glTranslatef(self.width / 2, self.height / 2, 0.0)
        glBegin(GL_LINE_LOOP)
        for x in range(360):
            rad = math.radians(x)
            glVertex2f(math.cos(rad) * self.width / 10, math.sin(rad) * self.height / 10)
        glEnd()
        glPopMatrix()

    def draw_x(self):
        glPushMatrix()
        glTranslatef(self.width / 2, self.height / 2, 0.0)
        glBegin(GL_LINES)
        glVertex2f(self.width / 10, -self.height / 10)
        glVertex2f(-self.width / 10, self.height / 10)
        glEnd()
        glBegin(GL_LINES)
        glVertex2f(self.width / 10, self.height / 10)
        glVertex2f(-self.width / 10, -self.height / 10)
        glEnd()
        glPopMatrix()

if __name__ == "__main__":
    game = Game()
    config = pyglet.gl.Config(samples=4)
    window = MainWindow(config=config, resizable=True)
    pyglet.clock.schedule_interval(game.update, 1 / 30)
    pyglet.app.run()
