import tkinter as tk
from tkinter import ttk
import tkinter.font
from tkinter.messagebox import showerror, showinfo
from datetime import datetime
import os, json, urllib.request
import valute
from operator import indexOf

link = "https://open.er-api.com/v6/latest/EUR"

lista25_most_traded = ('EUR', 'USD', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY',
                            'SEK', 'MXN', 'NZD', 'SGD', 'HKD', 'NOK', 'KRW', 'TRY',
                            'INR', 'RUB', 'BRL', 'ZAR', 'DKK', 'PLN', 'TWD', 'THB', 'MYR')
teme = (('gray93', 'black', ('Svijetlo','Light')), ('gray20', 'white', ('Tamno', 'Dark')),
        ('SpringGreen4', 'black', ('Zeleno', 'Green')), ('firebrick4', 'white', ('Crveno', 'Red')), ('navy', 'white', ('Plavo', 'Blue')))
tema = 4
trenutna_tema = 0 #zbog mijenjanja jezika
s_index = 0 #za pokretnu traku
petlja = None


def Provjera_Internetske_veze(link):
    try:
        urllib.request.urlopen(link)
        return True
    except:
        print("Pogreska! Nema internetske veze.")
        return False


def Dohvacanje_tecajne_liste_sa_interneta(link):
    with urllib.request.urlopen(link) as url:
        tecajna_lista = json.loads(url.read().decode())
    return tecajna_lista


def Inicijalizacija_i_azuriranje_datoteke(link):
    #provjera postoji li datoteka na racunalu
    if (os.path.isfile("./ExchangeRates.json")):
        #citam postojecu datoteku na racunalu
        with open("ExchangeRates.json", "r") as dat:
            postojeca_datoteka = json.load(dat)

        #provjera sljedeceg azuriranja
        vrijeme_sljedeceg_azuriranja_unix = postojeca_datoteka["time_next_update_unix"]
        vrijeme_sljedeceg_azuriranja_utc = datetime.utcfromtimestamp(vrijeme_sljedeceg_azuriranja_unix)

        #ako je vrijeme za dohvacanje nove tecajne liste sa interneta
        if (datetime.utcnow() >= vrijeme_sljedeceg_azuriranja_utc):
            #stvaranje datoteke top25 24hr change
            mapa = postojeca_datoteka['rates']
            #poredaj mapu prema listi
            mapa2 = {}
            for valuta in lista25_most_traded:
                mapa2[valuta] = mapa[valuta]
            #spremam mapu top25 valuta kao json
            with open('Top25_24hrChange.json', 'w') as top25:
                json.dump(mapa2, top25, indent=4)

            #ucitavanje web json datoteke u varijablu
            if (Provjera_Internetske_veze(link)):
                nova_datoteka = Dohvacanje_tecajne_liste_sa_interneta(link)
            else:
                showinfo('Information', 'Exchange rate list is outdated. Connect to Internet to fetch updated exchange rates')
                return postojeca_datoteka

            #prebrisavanje stare datoteke sa novom na racunalu
            with open("ExchangeRates.json", "w") as d:
                json.dump(nova_datoteka, d, indent=4)

            return nova_datoteka
        else:
            return postojeca_datoteka
    else:
        #ako neko obrise tecajnu listu json a ostavi 24hr json
        if (os.path.isfile("./Top25_24hrChange.json")):
            os.remove("./Top25_24hrChange.json")
        if (Provjera_Internetske_veze(link)):
            nova_tecajna_lista = Dohvacanje_tecajne_liste_sa_interneta(link)
            with open("ExchangeRates.json", "w") as dat:
                json.dump(nova_tecajna_lista, dat, indent=4)
            return nova_tecajna_lista
        else:
            showerror('Error: No internet connection', 'Program requires Internet connection for first time fetching of the exchange rates.')
            raise SystemExit(0)


def main():
    root = tk.Tk()

    #centriranje prozora
    win_width = 320
    win_height = 240

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    center_x = int(screen_width/2 - win_width/2)
    center_y = int(screen_height/2 - win_height/2)

    root.geometry(f'{win_width}x{win_height}+{center_x}+{center_y}')
    root.resizable(False, False)
    root.title('Currency Converter')
    root.iconbitmap('zastave/icon.ico')

    # POSTAVLJANJE #################################################################################################################

    glavna_boja = teme[0][0]
    sekundarna_boja = teme[0][1]
    root.configure(background=glavna_boja)

    #font config
    glavni_font = tkinter.font.nametofont('TkDefaultFont')
    glavni_font.config(size=10)
    root.option_add('*Font', glavni_font)

    #jezik
    jezik = tk.IntVar()
    jezik.set(1) #hrvatkski 0, engleski 1
    Jezici = {
        'checkbox_tekst': ('Tečajevi', 'Show rates'),
        'ime_labela': ('Konverter Valuta v1.0', 'Currency Converter v1.0'),
        'status_labela': ('Tečajevi ažurirani: ', 'Rates updated: '),
        'status_labela2': ('Sljedeće ažuriranje: ', 'Next update: '),
        'checkbox_info': ('Prikaži tečajeve 25 najtrgovanijih valuta na deviznom tržištu ',
                          'Show exchange rates for 25 most traded currencies on forex '),
        'programer': ('Programer: ', 'Programmer: '),
        'pružatelj': ('Pružatelj: ', 'Provider: '),
        'vrijeme': ('GMT', 'UTC'),
        'jezik': ('Promjeni jezik (engleski, hrvatski)', 'Change language (english, croatian)'),
        'br_skracenice': (('', ' tis.', ' mil.', ' mlrd.', ' bil.'), ('', 'K', 'M', 'B', 'T'))
    }

    #dohvacanje json datoteke #######################################################
    trenutni_tecajevi = Inicijalizacija_i_azuriranje_datoteke(link)

    #vrijeme tecaja
    vrijeme_unix = trenutni_tecajevi["time_last_update_unix"]
    vrijeme2_unix = trenutni_tecajevi['time_next_update_unix']
    vrijeme_utc = datetime.utcfromtimestamp(vrijeme_unix).strftime("%d.%m.%Y, %H:%M:%S ")
    vrijeme2_utc = datetime.utcfromtimestamp(vrijeme2_unix).strftime("%d.%m.%Y, %H:%M:%S ")

    #rjecnik valute (kljuc: kod valute, vrijednost: tecaj po eur-u)
    mapa_valuta = trenutni_tecajevi["rates"]

    mapa_valutaSVE = valute.mapa_valutaSVE

    lista_valuta = [] #lista za comboboxove
    indeks = 0
    for valuta in mapa_valuta.keys():
        lista_valuta.append(valuta)
        if (valuta in mapa_valutaSVE):
                lista_valuta[indeks] = f'{valuta} {mapa_valutaSVE[valuta][0][jezik.get()]}'
        indeks += 1

    string25 = '' #string tecajeva za pokretnu status traku
    if (os.path.isfile("./Top25_24hrChange.json")):
        with open("Top25_24hrChange.json", "r") as dat:
            jsonTop25 = json.load(dat)
        mapaTop25 = jsonTop25
        
        for valuta, vrijednost in mapaTop25.items():
            if (valuta == 'EUR'):
                string25 += '>>'+valuta+' '+str(mapa_valuta[valuta])+'<<   '
            else:
                string25 += valuta+' '+str(mapa_valuta[valuta])+('🞀' if mapa_valuta[valuta] == vrijednost
                                                                     else ('🞁' if mapa_valuta[valuta] > vrijednost else '🞃'))+'   '
    else:
        for i in range(len(lista25_most_traded)):
            for valuta in mapa_valuta.keys():
                if (valuta == lista25_most_traded[i]):
                    if (valuta == 'EUR'):
                        string25 += '>>'+valuta+'<< '+str(mapa_valuta[valuta])+'   '
                    else:
                        string25 += valuta+' '+str(mapa_valuta[valuta])+'   '

    # FUNKCIJE ######################################################################################################################

    def pretvori(arg):
        try:
            val1 = vrijednost1.get() #iznos
            var1 = varijabla1.get()[0:3] #ime valute
            val2 = vrijednost2.get()
            var2 = varijabla2.get()[0:3]
            tecaj1 = mapa_valuta.get(var1)
            tecaj2 = mapa_valuta.get(var2)
            print('tracer '+arg)
            if (arg == '1'):
                iznos = float(val1.replace(',',''))/tecaj1
                iznos = iznos*tecaj2
                vrijednost2.set('{:,.2f}'.format(iznos))
            if (arg == '2'):
                iznos = float(val2.replace(',',''))/tecaj2
                iznos = iznos*tecaj1
                vrijednost1.set('{:,.2f}'.format(iznos))
        except:
            pass

    def promjeniTemu():
        global tema
        global trenutna_tema
    
        root.configure(background=teme[tema][0])
        okvir_ime.configure(background=teme[tema][0])
        ime_labela.configure(background=teme[tema][0], foreground=teme[tema][1])

        okvir_simbol1.configure(background=teme[tema][0])
        simbol_labela1.configure(background=teme[tema][0], foreground=teme[tema][1])
        okvir_zastava1.configure(background=teme[tema][0])
        zastava_labela1.configure(background=teme[tema][0])

        okvir_simbol2.configure(background=teme[tema][0])
        simbol_labela2.configure(background=teme[tema][0], foreground=teme[tema][1])
        okvir_zastava2.configure(background=teme[tema][0])
        zastava_labela2.configure(background=teme[tema][0])

        gumb.configure(background=teme[tema][0], foreground=teme[tema][1], text=teme[tema][2][jezik.get()])
        status_labela.configure(background=teme[tema][0], foreground=teme[tema][1])
        cek_gumb.configure(background=teme[tema][0], activebackground=teme[tema][0],
                           selectcolor=teme[tema][0], foreground=teme[tema][1], activeforeground='magenta')
        pj_gumb.configure(background=teme[tema][0])
    
        trenutna_tema = tema  
        print(tema)
        if(tema == 0):
            tema = 4
        else:
            tema -= 1
    
    def pokretnaLabela(prvi_put):
        s = string25
        global s_index
        global petlja
    
        dupli = s + '' + s                  # dupliraj string
        prikaz = dupli[s_index:s_index+62] # dohvati prikaz porciju
        status_labela.config(text=prikaz)

        s_index += 1                        # prebaci sljedeci prikaz ljevo
        if s_index >= len(dupli) // 2:     # resetiraj indeks 
            s_index = 0

        # vrti prikaz
        if (prvi_put):
            petlja = root.after(500, lambda: pokretnaLabela(False))
        else:
            petlja = root.after(100, lambda: pokretnaLabela(False))

    def pokaziTecajeve():
        global petlja
        if(pokaziTecaj.get()):
            pokretnaLabela(True)
        else:
            root.after_cancel(petlja)

    def promjeniJezik():
        if (jezik.get() == 0):
            jezik.set(1)
            zastavica_jezik = tk.PhotoImage(file='zastave/en16.png')
            pj_gumb.configure(image=zastavica_jezik)
            pj_gumb.image = zastavica_jezik
        else:
            jezik.set(0)
            zastavica_jezik = tk.PhotoImage(file='zastave/cro16.png')
            pj_gumb.configure(image=zastavica_jezik)
            pj_gumb.image = zastavica_jezik

        #indeksi valuta koje su bile odabrane prije promjene jezika
        valuta1_idx = indexOf(lista_valuta, varijabla1.get())
        valuta2_idx = indexOf(lista_valuta, varijabla2.get())

        #izmjeni listu valuta i postavi je na comboboxe
        lista_valuta.clear()
        for valuta in mapa_valutaSVE.keys():
            lista_valuta.append(f'{valuta} {mapa_valutaSVE[valuta][0][jezik.get()]}')
        combo1.configure(values=lista_valuta)
        combo2.configure(values=lista_valuta)
        varijabla1.set(lista_valuta[valuta1_idx])
        varijabla2.set(lista_valuta[valuta2_idx])

        #izmjeni widgete
        gumb.configure(text=teme[trenutna_tema][2][jezik.get()])
        cek_gumb.configure(text=Jezici['checkbox_tekst'][jezik.get()])
        ime_labela.configure(text=Jezici['ime_labela'][jezik.get()])

        misNeLebdi('') #da se apdejta status traka
        izgubiFokus('')

    # EVENTI ###############################################################################################################################

    def dodajTracer1(event):
        #stopiraj drugu
        while (vrijednost2.trace_info()):
            idx = 0
            vrijednost2.trace_remove(*vrijednost2.trace_info()[idx])
        #dodaj prvu
        vrijednost1.trace_add('write', lambda a, b, c: pretvori('1'))

    def dodajTracer2(event):
        #stopiraj prvu
        while(vrijednost1.trace_info()):
            idx = 0
            vrijednost1.trace_remove(*vrijednost1.trace_info()[idx])
        # dodaj drugu
        vrijednost2.trace_add('write', lambda a, b, c: pretvori('2'))

    def unos1_izgubiFokus(event):
        if(vrijednost1.get() == ''):
            vrijednost1.set('0.00')
        else:
            vrijednost1.set('{:,.2f}'.format(float(vrijednost1.get().replace(',',''))))

    def unos2_izgubiFokus(event):
        if(vrijednost2.get() == ''):
            vrijednost2.set('0.00')
        else:
            vrijednost2.set('{:,.2f}'.format(float(vrijednost2.get().replace(',',''))))

    def promjeniZastavicuSimbol1(event):
        trenutna_valuta1 = str.lower(varijabla1.get()[0:3])
        if (trenutna_valuta1.upper() in mapa_valuta.keys()): #npr unos: bzvz i stisne enter
            zastava1 = tk.PhotoImage(file=f'zastave/{trenutna_valuta1}32.png')
            zastava_labela1.configure(image=zastava1)
            zastava_labela1.image = zastava1

            trenutni_simbol1 = mapa_valutaSVE[trenutna_valuta1.upper()][1]
            simbol_labela1.configure(text=trenutni_simbol1)
        else:
            simbol_labela1.configure(text='?')
            zastava1 = tk.PhotoImage(file=f'zastave/32.png')
            zastava_labela1.configure(image=zastava1)
            zastava_labela1.image = zastava1
            
    def promjeniZastavicuSimbol2(event):
        trenutna_valuta2 = str.lower(varijabla2.get()[0:3])
        if (trenutna_valuta2.upper() in mapa_valuta.keys()):
            zastava2 = tk.PhotoImage(file=f'zastave/{trenutna_valuta2}32.png')
            zastava_labela2.configure(image=zastava2)
            zastava_labela2.image = zastava2

            trenutni_simbol2 = mapa_valutaSVE[trenutna_valuta2.upper()][1]
            simbol_labela2.configure(text=trenutni_simbol2)
        else:
            simbol_labela2.configure(text='?')
            zastava2 = tk.PhotoImage(file=f'zastave/32.png')
            zastava_labela2.configure(image=zastava2)
            zastava_labela2.image = zastava2
            

    def comboPretrazivanje(event, arg):
        unos = event.widget.get()
        if arg == '1':
            if unos == '':
                combo1['values'] = lista_valuta
            else:
                nova_lista = []
                for valuta in lista_valuta:
                    if unos.lower() in valuta.lower():
                        nova_lista.append(valuta)
                combo1['values'] = nova_lista
                if (len(nova_lista) == 1):
                    varijabla1.set(nova_lista[0])
                    root.after(200, izgubiFokus(''))
        else:           
            if unos == '':
                combo2['values'] = lista_valuta
            else:
                nova_lista = []
                for valuta in lista_valuta:
                    if unos.lower() in valuta.lower():
                        nova_lista.append(valuta)
                combo2['values'] = nova_lista
                if (len(nova_lista) == 1):
                    varijabla2.set(nova_lista[0])
                    root.after(200,izgubiFokus(''))

    def SelektirajNaKlik(event):
        event.widget.select_range(0,'end') #selektiraj sve na klik
        event.widget.icursor('end') #postavi kursor na kraj
        return 'break'

    def human_format(num):
        num = float(num.replace(',',''))
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), Jezici['br_skracenice'][jezik.get()][magnitude])

    def misLebdi(event, arg):
        if (not pokaziTecaj.get()):
            if (arg == '1'):
                status_labela.configure(text=vrijednost1.get()+' ('+human_format(vrijednost1.get())+') '+varijabla1.get()[0:3]+' ')
                return
            else:
                status_labela.configure(text=vrijednost2.get()+' ('+human_format(vrijednost2.get())+') '+varijabla2.get()[0:3]+' ')

    def misNeLebdi(event):
        if (not pokaziTecaj.get()):
            status_labela.configure(text=Jezici['status_labela'][jezik.get()]+vrijeme_utc+Jezici['vrijeme'][jezik.get()]+' ')

    def pokaziInfo(event):
        if (not pokaziTecaj.get()):
            status_labela.configure(text=Jezici['programer'][jezik.get()]+'Marko Zec; '+Jezici['pružatelj'][jezik.get()]+'exchangerate-api.com'+' ')

    def izgubiFokus(event):
        root.focus_set()

    def sljedeciUpdate(event):
        if (not pokaziTecaj.get()):
            status_labela.configure(text=Jezici['status_labela2'][jezik.get()]+vrijeme2_utc+Jezici['vrijeme'][jezik.get()]+' ')

    def cekGumbInfo(event):
        if (not pokaziTecaj.get()):
            status_labela.configure(text=Jezici['checkbox_info'][jezik.get()])

    def pjInfo(event):
        if (not pokaziTecaj.get()):
            status_labela.configure(text=Jezici['jezik'][jezik.get()]+' ')

    # WIDGETI ###########################################################################################################################################

    #unos 1
    vrijednost1 = tk.StringVar()
    vrijednost1.set('0.00')
    unos1 = ttk.Entry(root, textvariable=vrijednost1, justify='center', font=(glavni_font, 12))
    unos1.place(x=40, y=40)

    #unos 2
    vrijednost2 = tk.StringVar()
    vrijednost2.set('0.00')
    unos2 = ttk.Entry(root, textvariable=vrijednost2, justify='center', font=(glavni_font, 12))
    unos2.place(x=40, y=135)

    #promjeni temu gumb
    gumb = tk.Button(root, text=teme[0][2][jezik.get()], relief='raised', command=promjeniTemu)
    gumb.configure(font=(glavni_font, 7), background=glavna_boja, foreground=sekundarna_boja)
    gumb.place(x=5, y=5)

    #promjeni jezik gumb
    zastavica_jezik = tk.PhotoImage(file='zastave/en16.png')
    pj_gumb = tk.Button(root, image=zastavica_jezik, command=promjeniJezik)
    gumb.configure(background=glavna_boja)
    pj_gumb.place(y=200, x=5)

    #cek gumb
    pokaziTecaj = tk.BooleanVar()
    pokaziTecaj.set(False)
    cek_gumb = tk.Checkbutton(root, text=Jezici['checkbox_tekst'][jezik.get()], variable=pokaziTecaj, command=pokaziTecajeve)
    cek_gumb.configure(font=(glavni_font, 8), background=glavna_boja, activebackground=glavna_boja,
                             selectcolor=glavna_boja, foreground=sekundarna_boja, activeforeground='magenta')
    cek_gumb.place(x=50, y=4)

    #ime programa
    okvir_ime = tk.Frame(root, height=15, width=150, background=glavna_boja)
    okvir_ime.place(x=160, y=7)
    okvir_ime.pack_propagate(0)
    ime_labela = ttk.Label(okvir_ime, text=Jezici['ime_labela'][jezik.get()], foreground=sekundarna_boja)
    ime_labela.configure(font=(glavni_font, 8), background=glavna_boja)
    ime_labela.pack(anchor='e')

    #combo box1
    varijabla1 = tk.StringVar()
    varijabla1.set(lista_valuta[0]) #euro
    varijabla1.trace_add('write', lambda a, b, c: pretvori('2'))
    combo1 = ttk.Combobox(root, textvariable=varijabla1, values=lista_valuta, width=23)
    combo1.place(x=40, y=80)

    #combo2
    varijabla2 = tk.StringVar()
    varijabla2.set(lista_valuta[145]) #americki dolar 145
    varijabla2.trace_add('write', lambda a, b, c: pretvori('1'))
    combo2 = ttk.Combobox(root, textvariable=varijabla2, values=lista_valuta, width=23)
    combo2.place(x=40, y=175)

    #zastava1
    okvir_zastava1 = tk.Frame(root, height=34, width=80, background=glavna_boja)
    okvir_zastava1.place(x=230, y=74)
    okvir_zastava1.pack_propagate(0)
    trenutna_valuta1 = str.lower(varijabla1.get()[0:3])
    zastava1 = tk.PhotoImage(file=f'zastave/{trenutna_valuta1}32.png')
    zastava_labela1 = ttk.Label(okvir_zastava1, image=zastava1, background=glavna_boja)
    zastava_labela1.pack(anchor='center')

    #zastava2
    okvir_zastava2 = tk.Frame(root, height=34, width=80, background=glavna_boja)
    okvir_zastava2.place(x=230, y=169)
    okvir_zastava2.pack_propagate(0)
    trenutna_valuta2 = str.lower(varijabla2.get()[0:3])
    zastava2 = tk.PhotoImage(file=f'zastave/{trenutna_valuta2}32.png')
    zastava_labela2 = ttk.Label(okvir_zastava2, image=zastava2, background=glavna_boja)
    zastava_labela2.pack(anchor='center')

    #simbol1
    okvir_simbol1 = tk.Frame(root, height=27, width=80, background=glavna_boja)
    okvir_simbol1.place(x=230, y=40)
    okvir_simbol1.pack_propagate(0)
    trenutni_simbol1 = mapa_valutaSVE[trenutna_valuta1.upper()][1]
    simbol_labela1 = ttk.Label(okvir_simbol1, text=trenutni_simbol1, background=glavna_boja, foreground=sekundarna_boja)
    simbol_labela1.configure(font=(glavni_font, 12, 'bold'))
    simbol_labela1.pack(anchor='center')

    #simbol2
    okvir_simbol2 = tk.Frame(root, height=27, width=80, background=glavna_boja)
    okvir_simbol2.place(x=230, y=135)
    okvir_simbol2.pack_propagate(0)
    trenutni_simbol2 = mapa_valutaSVE[trenutna_valuta2.upper()][1]
    simbol_labela2 = ttk.Label(okvir_simbol2, text=trenutni_simbol2, background=glavna_boja, foreground=sekundarna_boja)
    simbol_labela2.configure(font=(glavni_font, 12, 'bold'))
    simbol_labela2.pack(anchor='center')

    #status_labela
    status_labela = tk.Label(root, text=Jezici['status_labela'][jezik.get()]+vrijeme_utc+Jezici['vrijeme'][jezik.get()]+' ', relief='sunken')
    status_labela.configure(background=glavna_boja, foreground=sekundarna_boja, font=(glavni_font, 8), anchor='e')
    status_labela.pack(fill='x', side='bottom', ipady=1)

    unos1.bind('<FocusIn>', dodajTracer1)
    unos2.bind('<FocusIn>', dodajTracer2)
    unos1.bind('<FocusOut>', unos1_izgubiFokus)
    unos2.bind('<FocusOut>', unos2_izgubiFokus)
    combo1.bind('<<ComboboxSelected>>', promjeniZastavicuSimbol1)
    combo2.bind('<<ComboboxSelected>>', promjeniZastavicuSimbol2)
    combo1.bind('<FocusOut>', promjeniZastavicuSimbol1) #kad se nista ne odabere da postavi upitnik
    combo2.bind('<FocusOut>', promjeniZastavicuSimbol2)
    combo1.bind('<KeyRelease>', lambda event, arg='1': comboPretrazivanje(event, arg))
    combo2.bind('<KeyRelease>', lambda event, arg='2': comboPretrazivanje(event, arg))
    combo1.bind('<ButtonRelease-1>', SelektirajNaKlik)
    combo2.bind('<ButtonRelease-1>', SelektirajNaKlik)
    unos1.bind('<Enter>', lambda event, arg='1': misLebdi(event, arg))
    unos2.bind('<Enter>', lambda event, arg='2': misLebdi(event, arg))
    unos1.bind('<Leave>', misNeLebdi)
    unos2.bind('<Leave>', misNeLebdi)
    ime_labela.bind('<Enter>', pokaziInfo)
    ime_labela.bind('<Leave>', misNeLebdi)
    root.bind('<Return>', izgubiFokus)
    status_labela.bind('<Enter>', sljedeciUpdate)
    status_labela.bind('<Leave>', misNeLebdi)
    cek_gumb.bind('<Enter>', cekGumbInfo)
    cek_gumb.bind('<Leave>', misNeLebdi)
    pj_gumb.bind('<Enter>', pjInfo)
    pj_gumb.bind('<Leave>', misNeLebdi)

    root.mainloop()


if __name__=='__main__':
    main()