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
import itertools
import select
import struct
import socket
import time

import numpy as np

O = -1  # O piece
E = 0   # Empty tile
X = 1   # X piece

BUFFER = 4096
STATE = struct.Struct('!bbb9b')
PLACE = struct.Struct('!2b')
PSIZE = struct.Struct('!B')


class Server(object):
    def __init__(self, host, port):
        self.players = {}
        self.connections = []
        self.game = Game()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5)

        self.connections.append(self.sock)

    def main_loop(self):
        while True:
            read, write, errors = select.select(self.connections, [], [])
            for sock in read:
                if sock == self.sock:
                    self.on_connect()
                    continue
                else:
                    print("reading data")
                    try:
                        data = sock.recv(BUFFER)
                    except ConnectionResetError:
                        # fucking shitdows
                        self.on_disconnect(sock)
                        sock.close()
                        continue

                    if data:
                        print("recieved data")
                        self.on_recieve(sock, data)
                    else:
                        self.on_disconnect(sock)
                        continue

    def on_connect(self):
        if len(self.players) >= 2:
            return
        sock, addr = self.sock.accept()
        self.connections.append(sock)
        if X not in self.players.values():
            self.players[sock] = X
        else:
            self.players[sock] = O
        sock.send(self.game.state(self.players[sock]))
        print("Connection recieved: {addr}".format(addr=addr))

    def on_disconnect(self, sock):
        if sock in self.connections:
            self.connections.remove(sock)
        self.players.pop(sock, None)
        print("Client disconnected: {sock}".format(sock=sock))

    def on_recieve(self, sock, data):
        try:
            data = PLACE.unpack(data)
        except struct.error:
            return
        print("Recieved move data: {data}".format(data=data))

        if self.players[sock] == self.game.turn:
            self.game.place_tile(data[0], data[1])

        for player in self.players.keys():
            player.send(self.game.state(self.players[player]))

        if self.game.win is not None:
            time.sleep(1)
            self.game.reset()

        for player in self.players.keys():
            player.send(self.game.state(self.players[player]))


class Game(object):
    def __init__(self):
        self.board = np.ndarray(shape=(3, 3))
        self.reset()

    def check_win(self):
        for row in self.board:
            if sum(row) == X * 3:
                return X
            elif sum(row) == O * 3:
                return O
        for col in self.board.T:
            if sum(col) == X * 3:
                return X
            elif sum(col) == O * 3:
                return O
        if sum(np.diagonal(self.board)) == X * 3:
            return X
        if sum(np.diagonal(self.board)) == O * 3:
            return O
        if sum(np.diagonal(self.board[:, ::-1])) == X * 3:
            return X
        if sum(np.diagonal(self.board[:, ::-1])) == O * 3:
            return O
        if E not in self.board:
            return E

    def state(self, player):
        win = 2 if self.win is None else self.win
        return STATE.pack(self.turn, player, win, *itertools.chain(*self.board.astype(int)))
        # if self.win:
        #     return "{winner} wins!".format(winner=pieces[self.win])
        # elif self.win == 0:
        #     return "It's a draw!"
        # else:
        #     return "It's {piece}'s turn".format(piece=pieces[self.turn])

    def place_tile(self, x, y):
        print("Placing tile at X: {x}, Y: {y}".format(x=x, y=y))
        if self.board[x, y] != E:
            return
        if self.win is not None:
            return
        self.board[x, y] = self.turn
        self.turn = -self.turn
        self.win = self.check_win()
        # if self.win is not None:
        #     pyglet.clock.schedule_once(self.reset, 1)

    def reset(self, dt=0):
        self.board.fill(E)
        self.turn = X
        self.win = None


if __name__ == "__main__":
    server = Server('', 420)
    server.main_loop()
