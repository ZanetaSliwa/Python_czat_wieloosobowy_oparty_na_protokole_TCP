import select
import socket
import getopt
import sys

#Serwer TCP select

try:
    opts, ar = getopt.getopt(sys.argv[1:], 'p:t:vq')
except getopt.GetoptError as ge:
    print(repr(ge))
    sys.exit()

value = ''
port = int(55500)
tekst_powitalny = 'Witaj na czacie wieloosobowym!'
info_dzialan = 1
info_fatal = 1
info = 1

if len(opts) > 0:
    for opt, arg in opts:
        if opt in ('-p'):
            value = int(arg)
            port = int(value)
        elif opt in ('-t'):
            value = str(arg)
            tekst_powitalny = value
        elif opt in ('-v'):
            info_dzialan = 2
        elif opt in ('-q'):
            info_fatal = 2
        else:
            print('ERROR brak wybranych opcji')
            sys.exit(1)

if (info_dzialan == 2 and info_fatal == 2) or (info_dzialan == 1 and info_fatal == 1):
    info = 2

if (info_fatal == 1 and info_dzialan == 2):
    info = 3

if (info_fatal == 2 and info_dzialan == 1):
    info = 4

g_nas = socket.socket()
g_nas.bind(('', port))
g_nas.listen()

l_do_czyt = [g_nas]
l_do_pis = []
l_do_wyj = []
czas = 0.1


users = {}

pseudonimy = {}


while True:
    l_g_do_czyt, l_g_do_pis, l_z_wyj = select.select(l_do_czyt, l_do_pis, l_do_wyj, czas)
    do_usuniecia = []
    for g in l_g_do_czyt:
        if g == g_nas:
            nowe_g, adres = g_nas.accept()
            if info == 3:
                print('INFO USER ACTIONS: nowe połączenie:', adres, '\r\n')
            l_do_czyt.append(nowe_g)
        else:
            if info == 3:
                print('INFO USER ACTIONS: komunikat z gniazda:', g, '\r\n')
            adres_gniazda_docelowego = g.getpeername()
            adr_g_docel = adres_gniazda_docelowego[1]

            dane = g.recv(1024)
            dane = dane.decode('utf-8').split()

            if len(dane) > 0:
                if dane[0] == 'LLOGIN':
                    if len(dane) > 1:
                        log = dane[1]

                        if adr_g_docel in users:
                            if not log in pseudonimy:
                                l = users[adr_g_docel]
                                del users[adr_g_docel]
                                users[adr_g_docel] = log
                                del pseudonimy[l]
                                pseudonimy[log] = g
                                g.sendall(b'OK\r\n')
                                if info == 3:
                                    print('INFO USER ACTIONS: użytkownik (' + l + ') zmienił pseudonim na ' + log + '\r\n')
                            else:
                                g.sendall(b'ERROR uzytkownik zajerestrowany\r\n')
                                u = users[adr_g_docel]
                                if (info == 2 or info == 4):
                                    print('INFO ERROR: nieudana próba zmiany pseudonimu użytkownika ' + u + '\r\n')
                                elif info == 3:
                                    print('INFO USER ACTIONS: nieudana próba zmiany pseudonimu użytkownika ' + u + '\r\n')

                        else:
                            if log in pseudonimy:
                                g.sendall(b'ERROR uzytkownik zarejestrowany\r\n')
                                if (info == 2 or info == 4):
                                    print('INFO ERROR: nieudana próba rejestracji nowego użytkownika\r\n')
                                elif info == 3:
                                    print('INFO USER ACTIONS: nieudana próba rejestracji nowego użytkownika\r\n')
                            else:
                                users[adr_g_docel] = log
                                pseudonimy[log] = g
                                g.sendall(b'OK\r\n')
                                powit = str(tekst_powitalny) + '\r\n'
                                powit = powit.encode('utf-8')
                                g.sendall(powit)
                                if info == 3:
                                    print('INFO USER ACTIONS: zarejestrowano pseudonim ' + log + '\r\n')
                                    print('INFO USER ACTIONS: wysłano powitalny tekst (' + tekst_powitalny + ') do użytkownik o pseudonimie ' + log + '\r\n')

                elif dane[0] == 'LLIST':
                    if adr_g_docel in users:
                        tre = 'USERS '
                        tr = ''
                        for u, pseudon in users.items():
                            tr = tr + str(pseudon) + ' '
                        tresc = tre + tr + '\r\n'
                        tresc = str(tresc)
                        t = tresc.encode('utf-8')
                        g.sendall(t)
                        if info == 3:
                            uzyt = users[adr_g_docel]
                            print('INFO USER ACTIONS: użytkownik (' + uzyt + ') przesłał rozkaz przesłania listy zarejestrowanych użytkowników czatu\r\n')
                            print('INFO USER ACTIONS: wysłano listę zarejestrowanych użytkowników do użytkownika ' + uzyt + '\r\n')

                elif dane[0] == 'PPRIV':
                    if adr_g_docel in users:
                        if len(dane) > 1:
                            adresat = dane[1]
                            uu = users[adr_g_docel]
                            if info == 3:
                                print('INFO USER ACTIONS: użytkownik (' + str(uu) + ') przesłał rozkaz wysłania wiadomości prywatnej do użytkownika ' + str(adresat) + '\r\n')
                            tresc = ''
                            for d in dane[2:]:
                                tresc = tresc + ' ' + d
                            if adresat in pseudonimy:
                                g_adresata = pseudonimy[adresat]
                                u = users[adr_g_docel]
                                wiad = 'PRIV_FROM ' + str(u)  + tresc + '\r\n'
                                wiad = wiad.encode('utf-8')
                                g_adresata.sendall(wiad)
                                g.sendall(b'OK\r\n')
                                if info == 3:
                                    print('INFO USER ACTIONS: wysłano wiadomość prywatną do użytkownika ' + str(adresat) + '\r\n')
                            else:
                                g.sendall(b'ERROR nie mozna wyslac wiadomosci\r\n')
                                if (info == 2 or info == 4):
                                    print('INFO ERROR: błąd wysyłania wiadomości prywatnej do użytkownika ' + str(adresat) + '\r\n')


                else:
                    if adr_g_docel in users:
                        wiad = ''
                        for w in dane[0:]:
                            wiad = wiad + ' ' + w
                        wiad_pub = 'PUB_MSG' + str(wiad) + '\r\n'
                        wiad_pub = str(wiad_pub)
                        wp = wiad_pub.encode('utf-8')
                        nad = users[adr_g_docel]
                        for k, odbiorca in pseudonimy.items():
                            if k != nad:
                                odbiorca.sendall(wp)
                        g.sendall(b'OK\r\n')
                        if info == 3:
                            print('INFO USER ACTIONS: wiadomość publiczna (' + nad + ')\r\n')

            elif len(dane) == 0:
                if adr_g_docel in users:
                    pp = users[adr_g_docel]
                    del users[adr_g_docel]
                    del pseudonimy[pp]
                u = g.getpeername()
                g.close()
                do_usuniecia.append(g)
                if info == 3:
                    print('INFO USER ACTIONS: zamykamy połączenie ' + str(u) + '\r\n')
    for g in do_usuniecia:
        l_do_czyt.remove(g)
