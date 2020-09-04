import socket
import sys
import select
import getpass
import getopt
import time

#Klient TCP

try:
    opts, ar = getopt.getopt(sys.argv[1:], 'p:s:l:i')
except getopt.GetoptError as ge:
    print(repr(ge))
    sys.exit()

value = ''
port = int(55500)
serwer = 'localhost'
pseudonim = getpass.getuser()
wyl_wys = 1


if len(opts) > 0:
    for opt, arg in opts:
        if opt in ('-p'):
            value = int(arg)
            port = value
        elif opt in ('-s'):
            value = str(arg)
            serwer = value
        elif opt in ('-l'):
            value = str(arg.strip())
            pseudonim = value
        elif opt in ('-i'):
            wyl_wys = 2
        else:
            print('brak wybranych opcji')
            sys.exit(1)


g = socket.socket()
g.connect((serwer, port))

pseudo = 'LLOGIN' + ' ' + str(pseudonim) + '\r\n'
g.sendall(pseudo.encode('utf-8'))


while True:
    r, w, x = select.select([g, sys.stdin], [], [])
    if g in r:
        odp = g.recv(1024)
        od = odp.decode('utf-8')
        od = od.split()

        if len(odp) > 0:
            if od[0] == 'PUB_MSG':
                if wyl_wys != 2:
                    print('>>>', odp.decode('utf-8'))
            else:
                print('>>>', odp.decode('utf-8'))

        if not odp:
            print('Koniec pracy serwera')
            sys.exit(3)

    if sys.stdin in r:
        wprow  = input()
        wpro = wprow.split()

        if len(wpro) > 0:
            n = wpro[0]

            if n == '/rename':
                if len(wpro) > 1:
                    n1 = wpro[1]
                    wys = ''
                    wys = 'LLOGIN' + ' ' + str(n1)
                    wys = str(wys)
                    wys = wys.encode('utf-8')
                    g.sendall(wys)

            elif n == '/list':
                wys = ''
                wys = 'LLIST'
                wys = str(wys)
                wys = wys.encode('utf-8')
                g.sendall(wys)

            elif n == '/priv':
                if len(wpro) > 2:
                    n1 = wpro[1]
                    wys = ''
                    for w in wpro[2:]:
                        wys = wys + ' ' +  str(w)
                    wy = 'PPRIV ' + str(n1) + ' ' + wys
                    wy = str(wy)
                    wy = wy.encode('utf-8')
                    g.sendall(wy)

            else:
                wprow = wprow.encode('utf-8')
                g.sendall(wprow)

