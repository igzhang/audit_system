# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.


import socket
import sys
from paramiko.py3compat import u
from backend import models

# windows does not have termios...
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan,session_history_obj,user_obj):
    if has_termios:
        posix_shell(chan,session_history_obj,user_obj)
    else:
        windows_shell(chan,session_history_obj,user_obj)


def posix_shell(chan,session_history_obj,user_obj):
    import select
    
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)
        cmd_list = []
        complete_flag = False
        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    if len(x) == 0:
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    sys.stdout.write(x)
                    if complete_flag:
                        cmd_list.append(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                if x == "\r" or x == "\n":
                    models.SessionDetail.objects.create(
                        link=session_history_obj,user=user_obj,cmd="".join(cmd_list)
                    )
                    cmd_list.clear()
                elif x == "\t":         #补全会粘包   #vim支持性不好
                    complete_flag = True
                else:
                    cmd_list.append(x)
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

    
# thanks to Mike Looijmans for this code
def windows_shell(chan,session_history_obj,user_obj):
    import threading

    sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")
    cmd_list = []
    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data.decode("utf8"))
            sys.stdout.flush()
        
    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()
        
    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            if d == "\n":
                cmd = "".join(cmd_list)
                models.SessionDetail.objects.create(
                    link=session_history_obj, user=user_obj, cmd=cmd
                )
                cmd_list.clear()
            else:
                cmd_list.append(d)
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass
