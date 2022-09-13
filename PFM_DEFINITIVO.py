####DESARROLLADO POR: JESÚS RUIZ####


import os
import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression

dirname = os.path.dirname(__file__)
fullpath = os.path.join(dirname, r'BA_Application.xlsx')

transaccional = pd.read_excel(fullpath, sheet_name="Transaccional") #READING OF TRANSACTIONAL DATAFRAME
abono = pd.read_excel(fullpath, sheet_name="Dicc_Abono") #READING OF TRANSACTIONAL DATAFRAME
debito = pd.read_excel(fullpath, sheet_name="Dicc_Debito") #READING OF TRANSACTIONAL DATAFRAME
secundario = pd.read_excel(fullpath, sheet_name="Dicc_Secundario") #READING OF TRANSACTIONAL DATAFRAME


np.set_printoptions(suppress=True) #NOT CIENTIFIC NOTATION

diccionario = {
    '1':'enero',
    '2':'febrero',
    '3':'marzo',
    '4':'abril',
    '5':'mayo',
    '6':'junio',
}

#CREATION OF THE GUI
app = tk.Tk()

app.geometry("850x800")
app.minsize(width=850,height=800)
app.maxsize(width=850,height=800)

app.configure(background="#9CF9FF")
tk.Wm.wm_title(app, "PFM")



#IF WE WANT TO CHANGE THE USER, WE SHOULD CLEAN THE GUI
def limpiar(x, nombremes):
    for widget in app.winfo_children():
        widget.destroy()
    my_canvas = tk.Canvas(app)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    my_scrollbar = ttk.Scrollbar(app, orient='vertical', command=my_canvas.yview)
    my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))
    my_canvas.configure(background='#9CF9FF')

    second_frame = tk.Frame(my_canvas)      
    second_frame.configure(background="#9CF9FF")

    my_canvas.create_window((0,0), window=second_frame, anchor="nw")
    mainView(x, nombremes, second_frame)

#ALTERNATIVE WAY FOR CLEANING THE GUI
def limpiarsecondframe(secondframe, x, nombremes):
    for widget in secondframe.winfo_children():
        widget.destroy()
    mainView(x, nombremes, secondframe)




#OPEN SCREEN OF THE GUI. HERE WE CHOOSE WHICH USER WE WANT TO LOG AS        
def inicio():
    
    for widget in app.winfo_children():
        widget.destroy()
    tk.Button(
        app,
        text="Usuario 1 (305443)",
        font=("Courier", 14),
        bg="#00FFFB",
        fg="black",
        relief="flat",
        command= lambda: limpiar(1, "Junio")
    ).pack(
        fill=tk.BOTH,
        expand=True
    )
    tk.Button(
        app,
        text="Usuario 2 (305436)",
        font=("Courier", 14),
        bg="#00C5FF",
        fg="black",
        relief="flat",
        command= lambda: limpiar(2, "Junio")
    ).pack(
        fill=tk.BOTH,
        expand=True
    )
    tk.Button(
        app,
        text="Usuario 3 (305434)",
        font=("Courier", 14),
        bg="#0070FF",
        fg="black",
        relief="flat",
        command= lambda: limpiar(3, "Junio")
    ).pack(
        fill=tk.BOTH,
        expand=True
    )
    
#WE CAN SEE HOW USER'S MONEY VARIES OVER THE MONTH
def movimientosMes(mes, second_frame):
        
    figure1 = plt.Figure(figsize=(8,4), dpi=100)
    figure1.patch.set_facecolor('#9CF9FF')
    ax1 = figure1.add_subplot(111)
    line1 = FigureCanvasTkAgg(figure1, second_frame)
    line1.get_tk_widget().pack(
        side=tk.TOP
    )
    movimientos = mes[['DIA','SALDO_CUENTAS']] #WE ONLY TAKE INTO ACCOUNT THE MONEY FOR EACH DAY
    movimientos = movimientos.rename(columns={'SALDO_CUENTAS':'DINERO EN LA CUENTA'})
    movimientos = movimientos.drop_duplicates(subset=['DIA'], keep='first').groupby('DIA').sum() #WE ONLY NEED THE FIRST ROW, WHICH IS THE LAST OPERATION FOR THAT DAY. THEN WE USE ACCUMULATED SUM
    movimientos.plot(kind='line', legend=True, ax=ax1, color='r',marker='o', fontsize=10)
    ax1.set_title('Movimientos') 


#WE CAN SEE HOW MUCH MONEY THE USER HAS SPENT OVER THE MONTH
def gastosMes(gastosmesxdia, mes, numeromes, second_frame):

    figure3 = plt.Figure(figsize=(8,4), dpi=100)
    figure3.patch.set_facecolor('#9CF9FF')
    ax3 = figure3.add_subplot(111)
    line3 = FigureCanvasTkAgg(figure3, second_frame)
    line3.get_tk_widget().pack(
        side=tk.TOP
    )


    if numeromes != 0:
        gastosmesxdia[numeromes-1] = gastosmesxdia[numeromes-1].rename(columns={'CANTIDAD':'GASTOS DEL MES ANTERIOR'})
        gastosmesxdia[numeromes-1].plot(kind='line', legend=True, ax=ax3, color='black',marker='o', fontsize=10) #WE PLOT THE EXPENSES FOR THE LAST MONTH
        
    gastosactuales=mes.loc[mes['CANTIDAD']<0]
    gastosactuales = gastosactuales[['DIA','CANTIDAD']]
    gastosactuales['CANTIDAD'] = gastosactuales ['CANTIDAD'] * (-1)
    gastosactuales = gastosactuales.rename(columns={'CANTIDAD':'GASTOS DEL MES ACTUAL'})
    gastosactuales = gastosactuales.groupby('DIA').sum().cumsum() #WE GROUP THE EXPENSES BY DAY AND USE ACCUMULATED SUM
    gastosactuales.plot(kind='line', legend=True, ax=ax3, color='r',marker='o', fontsize=10)
    ax3.set_title('Gastos')

    return gastosactuales


#WE CAN PREDICT HOW MUCH MONEY THE USER IS SUPPOSED TO HAVE SPENT ACCORDING TO THE CURRENT DAY
def estimarGastado(gastosmesxdia):

    todos=pd.concat([gastosmesxdia[0], gastosmesxdia[1], gastosmesxdia[2], gastosmesxdia[3], gastosmesxdia[4], gastosmesxdia[5]]) #WE NEED TO STORAGE ALL EXPENSES FOR THE AVAILABLE MONTHS
    y=todos.iloc[:,0].to_numpy()
    X=todos.index.to_numpy()

    clasificador = LinearRegression()
    clasificador.fit(X.reshape(-1,1), y) #WE TRAIN OUR CLASSIFIER WITH THE DAYS (X) AND THE MONEY (y)

    diaactual = np.array([16]) # NOTE: I USED 16 AS IT'S THE LAST DAY THAT FIGURES ON THE .XLSX FILE, SO I TOOK IT AS THE CURRENT DAY
    estimacion = clasificador.predict(diaactual.reshape(-1,1))

    return estimacion
    
def mainView(x, nombremes, second_frame):

    tk.Button(
        second_frame,
        text="<-",
        font=("Courier", 20),
        bg="red",
        fg="black",
        relief="flat",
        command=inicio
    ).pack(
        side=tk.TOP
    )
    
    combobox=ttk.Combobox(
        second_frame,
        state="readonly",
        values=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"],
        font=("Courier", 20),
    )
    combobox.set(nombremes)
    combobox.bind("<<ComboboxSelected>>", lambda event, a=x: limpiarsecondframe(second_frame, a, combobox.get()))
    combobox.pack(side=tk.TOP)

    #WE ADD THESE COLUMNS TO THE DATAFRAME
    transaccional['MES']= transaccional['FECHA'].dt.month
    transaccional['DIA']= transaccional['FECHA'].dt.day

    #WE CHANGE THE VIEW ACCORDING TO USER ID
    if x==1:
        userid=305443
    elif x==2:
        userid=305436
    else:
        userid=305434
        
    user = transaccional.loc[transaccional['ID_CLIENTE'] == userid] 
    mes = user.loc[transaccional["MES"] == combobox.current()+1]

    movimientosMes(mes, second_frame)

    gastos = user.loc[user['CANTIDAD']<0]
    gastos = gastos[['DIA','CANTIDAD']]
    gastos['CANTIDAD'] = gastos ['CANTIDAD'] * (-1)


    #IN THIS LIST WE STORAGE THE EXPENSES FOR EVERY MONTH
    gastosmes = [gastos.loc[transaccional["MES"] == 1], gastos.loc[transaccional["MES"] == 2],gastos.loc[transaccional["MES"] == 3], gastos.loc[transaccional["MES"] == 4], gastos.loc[transaccional["MES"] == 5], gastos.loc[transaccional["MES"] == 6]]

    #IN THIS OTHER LIST, WE STORAGE THE MONEY SPENT EACH DAY OF THE MONTH
    gastosmesxdia = []

    for x in range(len(gastosmes)):
        gastosmesxdia.append(gastosmes[x].groupby('DIA').sum().cumsum())

    #WE PREDICT THE MONEY THAT THE USER IS SUPOSED TO HAVE SPENT FOR THE CURRENT DAY
    estimacion = estimarGastado(gastosmesxdia)

    #WE CAN SEE THE EXPENSES FOR THE CURRENT MONTH
    gastosactuales = gastosMes(gastosmesxdia, mes, combobox.current(), second_frame)


    prescindible = 0
    imprescindible = 0

    gastos = mes.loc[user['CANTIDAD']<0]
    gastos = gastos[['DIA','CANTIDAD', 'TAG_DEBITO_ID', 'TAG_SECUNDARIO_ID']]

    

    #WE CAN CALCULATE HOW MUCH EXPENSES ARE INDISPENSABLE

    for row in gastos.itertuples():
        

        if row[3] == row[3]: #WE CHECK IF THE NUMBER IS REAL
            i = debito.loc[debito['id'] == int(row[3])] #WE SEARCH THE ID IN DEBITO'S DICTIONARY
            if str(i.iloc[-1,-1]) == 'PRESCINDIBLE': #WE ADD THE VALUE TO ONE VARIABLE OR THE OTHER
                prescindible += float(row[2])
            else:
                imprescindible += float(row[2])
        elif row[4] == row[4]: # IF WE DON'T FIND THE ID IN DEBITO'S DICTIONARY, WE LOOK FOR IT IN SECUNDARIO'S ONE
            i = secundario.loc[secundario['id'] == int(row[4])]
            if str(i.iloc[-1,-1]) == 'PRESCINDIBLE':
                prescindible += float(row[2])
            else:
                imprescindible += float(row[2])

    

    data = {'Nombre': [], 'Cantidad':[], 'CantidadAnterior':[]}
    
    #TOPICS WILL STORAGE THE USER'S TRENDS
    topics = pd.DataFrame(data)
    
    mesanterior = pd.DataFrame()
    
    if combobox.current() !=0:
        mesanterior = user.loc[transaccional["MES"] == combobox.current()]
        mesanterior = mesanterior.loc[mesanterior['CANTIDAD']<0]
        mesanterior = mesanterior[['DIA','CANTIDAD', 'TAG_SECUNDARIO_ID']]
        mesanterior['CANTIDAD'] = mesanterior ['CANTIDAD'] * (-1)

    #WE CAN SEE WHAT THE USER SPEND THE MONEY ON 
  
    for row in gastos.itertuples():
        cantidadanterior=0
        if row[4] == row[4]:
            i = secundario.loc[secundario['id'] == int(row[4])] #SAME METHOD AS BEFORE
            topic = str(i.iloc[-1,1]) #WE SAVE THE TOPIC
            if topics['Nombre'].eq(topic).any(): #IF THE TOPIC IS IN TOPICS DATAFRAME, WE ADD THE MONEY
                index = topics[topics['Nombre'] == i.iloc[-1,1]].index.values
                topics.at[index[0], 'Cantidad'] = row[2] + topics.at[index[0], 'Cantidad']  
            else: #IF IT'S NOT, WE CREATE A NEW TUPLE FOR THE DATAFRAME TRENDS

                #ALSO, WE CALCULATE HOW MUCH MONEY DID THE USER SPEND ON THIS LAST MONTH
                if combobox.current() !=0:
                    for rowanterior in mesanterior.itertuples():
                        if rowanterior[3] == rowanterior[3]:
                            j = secundario.loc[secundario['id'] == int(rowanterior[3])]
                            if i.iloc[-1,1] == j.iloc[-1,1]:
                                cantidadanterior += rowanterior[2]


                new_row = {'Nombre':i.iloc[-1,1], 'Cantidad': row[2], 'CantidadAnterior': cantidadanterior}
                topics = topics.append(new_row, ignore_index=True)
            
    
    #WE SHOW THE INFORMATION
    tk.Label(
        second_frame,
        text="Total gastado: "+ str(round(gastosactuales.iloc[-1,-1],2))+ "€",
        font=("Courier", 20),
        bg="#9CF9FF",
        fg="black",
        relief="flat",
    ).pack(
        side=tk.TOP,
        pady=10
    )

    tk.Label(
        second_frame,
        text="Prescindible: "+ str(round((prescindible/(prescindible+imprescindible)*100),2)) + "%",
        font=("Courier", 20),
        bg="#9CF9FF",
        fg="black",
        relief="flat",
    ).pack(
        side=tk.TOP,
        pady=10
    )


    tk.Label(
        second_frame,
        text="Estimación de gasto el día actual (16): "+ str(round(estimacion[0],2))+ "€",
        font=("Courier", 20),
        bg="#9CF9FF",
        fg="black",
        relief="flat",
    ).pack(
        side=tk.TOP,
        pady=10
    )
    tk.Label(
        second_frame,
        text="En qué has gastado tu dinero:",
        font=("Courier", 20),
        bg="#9CF9FF",
        fg="black",
        relief="flat",
    ).pack(
        side=tk.TOP,
        pady=50
    )

    for row in topics.itertuples():
        diferencia = -(row[2])-row[3]
        cadena=""

        if combobox.current() !=0:

            if (diferencia>0):
                cadena = row[1] +": "+ str(round(row[2]*-1,2))+ "€ ("+str(round(abs(diferencia),2))+" más que en "+ diccionario[str(combobox.current())] +")"
            elif (diferencia == 0):
                cadena = row[1] +": "+ str(round(row[2]*-1,2))+ "€ (igual que el mes pasado)"
            else:
                cadena = row[1] +": "+ str(round(row[2]*-1,2))+ "€ ("+str(round(abs(diferencia),2))+" menos que en "+ diccionario[str(combobox.current())] +")"

        else:
            cadena = row[1] +": "+ str(round(row[2]*-1,2))+ "€"

        tk.Label(
            second_frame,
            text=cadena,
            font=("Courier", 20),
            bg="#9CF9FF",
            fg="black",
            relief="flat",
        ).pack(
            side=tk.TOP
        )  


inicio()


app.mainloop()


