import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import base64
from fpdf import FPDF
from funciones_pdf import PDF1,PDF2
import math
import PyPDF2
import io
from datetime import  datetime
import dateutil.parser
import pdfplumber

def CYC():
    """ Dispone una sección en streamlit para cargar archivos pdf con
    certificado de cámara y comercio, lo lee y extare los datos de interés
    Returns:
    list: Lista con los siguientes elementos:
     Fecha de emisión del certificado(str),
     Razón Social(str),
     Número de identificación tributaria(str),
     Fecha de mátricula del certificado(str),
     Fecha de renovación del certificado(str),
     Capital pagado por la empresa(str),
     Objeto social de la empresa(str),
     Representante legal de la empresa(str),
     Facultades del representante legal(str),
     Cantidad de embargos de la empresa(int),
     Cantidad de porcesos legales de la empresa(int),
     Si el usuario registró alguna observación del cerificado(bool),
     La observación que se resgistró(str)]

    """
    #diccionario con los nombres de los meses como llaves y números como values
    meses = {'enero':1,'febrero':2, 'marzo':3,
    'abril':4,'mayo': 5, 'junio':6,'julio':7, 'agosto':8,
    'septiembre':9,'octubre':10,  'noviembre':11, 'diciembre':12}
    #Se lee el archivo local con los códigos CIIU y su respectiva descripción
    #los codigos CIIU se usan para saber el objeto social de la empresa a partir de su código
    codigos = pd.read_csv('Data/Diccionario códigos ciiu.csv', dtype = {'Código':str})
    codigos = codigos.set_index('Código')
    #Se crea un cargador de archivos de tipo pdf en la interfaz
    pdfFileObj = st.file_uploader('Cargar Cámara y Comercio', type='pdf')
    #Se verifica si se ha cargado un archivo
    #Si ya se cargó un archivo
    if pdfFileObj is not None:
        #string vacio donde se va a guardar todo el texto del pdf
        text=''
        #se abre el archivo
        with pdfplumber.open(pdfFileObj) as pdf:
            #se recorre cada página del archivo
            for page in pdf.pages:
                # se agregar e texto de la página al string text
                text += page.extract_text()

        def encontar_fecha(inicio, texto):
            """Si encuentra una fecha en el argumento texto depués del caracter
            de inicio la retonra en fomato AAAA-MM-DD de lo contrario retorna un
            texto avisando que el formato no es el deseado
            El formato deseado es como el siguiente: 18 de marzo de 2021
            Parameters:
            inicio (int): locaclización del principio de la fecha en el string texto
            texto (str): texto donde se va a buscar la fecha

            Returns:
            str:La fecha que se encontró o la excepción de lo contrario

            """
            #caracter donde debería acabar la fecha
            fin = texto[inicio:].find('2021') + 4 + inicio# Actualizar solo sirve si está en el año 2022
            #se usa un try por que puede que el formato de la fecha no sea el que se está considerando en este caso
            try:
                #se extrae el pedazo de string del texto que contiene la fecha
                fecha = texto[inicio: fin]
                #se divide la fecha en sus diferentes partes
                fecha = fecha.split('de')
                #se extra el día y se pasa a formato int
                dia = int(fecha[0])
                #se extra el mes y se pasa a formato int con ayuda del diccionario meses
                mes = meses[fecha[1]]
                #se extra el año y se pasa a formato int
                anio = int(fecha[2])
                #se crea el objeto fecha ene el formato deseao
                then = datetime(anio, mes, dia)
                return then
            except:
                #si falla es por que el formato no es el esperado.
                return 'Por favor revisar el formato de la fecha de expedición.'



        def leer_fecha_emision():
            '''Extrae la fecha de emisión del certificado '''
            #abre el pdf
            with pdfplumber.open(pdfFileObj) as pdf:
                #toma la primera página donde se encuentra típicamente la fecha de emisión
                page = pdf.pages[0]
                # extrae el texto de la pagina 1
                pagina_1 =  page.extract_text()
            #se pone todo el texto en minúsculas sin expacios y sin saltos de línea para evitar casos exóticos
            pagina_1 = pagina_1.lower().replace(' ', '').replace('\n', '')
            #caso A buscamos el string fechaexpedición
            inicio_A = pagina_1.find('fechaexpedición:')
            #caso A buscamos el string fechadeexpedición
            inicio_B = pagina_1.find('fechadeexpedición:')
            #Caso C buscamos el string fechadeexpedición:bucaramanga,
            inicio_C = pagina_1.find('fechadeexpedición:bucaramanga,')

            # si encontró el string del caso A
            if inicio_A != -1:
                #se define la localización del inicio de  la fecha
                inicio_A += len('fechaexpedición:')
                try:
                    # se intenta leer la fecha con un formato únicamente en números
                    respuesta = dateutil.parser.parse(pagina_1[inicio_A: inicio_A+10])
                except:
                    # sino  se logra se lee la fecha con formato en texto en español
                    respuesta = encontar_fecha(inicio_A, pagina_1)
            # si encontró el string del caso C
            elif inicio_C != -1:
                #se define la localización del inicio de  la fecha
                inicio_C += len('fechadeexpedición:bucaramanga,')
                try:
                    # se intenta leer la fecha con un formato únicamente en números
                    respuesta = dateutil.parser.parse(pagina_1[inicio_C: inicio_C+10])
                except:
                    # sino  se logra se lee la fecha con formato en texto en español
                    respuesta = encontar_fecha(inicio_A, pagina_1)
            # si encontró el string del caso B
            elif inicio_B != -1:
                #se define la localización del inicio de  la fecha
                inicio_B += len('fechadeexpedición:')
                try:
                    # se intenta leer la fecha con un formato únicamente en números
                    respuesta = dateutil.parser.parse(pagina_1[inicio_B: inicio_B+10])
                except:
                    # sino  se logra se lee la fecha con formato en texto en español
                    respuesta = encontar_fecha(inicio_B, pagina_1)
            # si no encontró ninguno de los casos A,B o C
            else:
                # se avisa al usuario
                st.warning('No se encontró la fecha de expedición.')
                # se da la opción de que la digite
                respuesta = st.text_input('Digite fecha de emisión')
            #Si se encontró la fecha pero no se pudo decifrar el formato
            if respuesta == 'Por favor revisar el formato de la fecha de expedición.':
                # se avisa al usuario
                st.warning(f'**{respuesta}**')
                # se da la opción de que la digite
                respuesta = st.text_input('Digite fecha de emisión')
            else:

                hoy = datetime.now()
                #se cacula hace cuantos días se emitió el certificado
                diferencia = (hoy - respuesta).days
                #se convierte la respuesta a formato string
                respuesta = respuesta.strftime("%d-%m-%Y")
                # si el cerificao se emitió hace más de 60 días se avisa al usuario
                if diferencia > 60:
                    st.error( f'**Fecha de expedición**: {respuesta} (Mayor a 60 días)')
                else:
                    # se muestra la fecha de expedición
                    st.write( f'**Fecha de expedición**: {respuesta}')
            return respuesta

        def leer_razon_social():
            '''Extrae la razón social del certificado '''
            #Se pasa todo el texto a minúsculas
            minus = text.lower()
            #Se buscan los tres formatos en los que podría estar presentada la razón social
            inicio_A = minus.find("razón social:")
            inicio_B = minus.find("razón social :")
            inicio_C = minus.find('nombre:')
            #De acuerdo al caso se guarda donde empieza el nombre de la empresa
            if inicio_A != -1:
                inicio = inicio_A + len("razón social:")
            elif inicio_B != -1:
                inicio = inicio_B + len("razón social :")
            elif inicio_C != -1:
                inicio = inicio_C + len('nombre:')
            else :
                # sino se encontró formato el inicio se sfija en -1
                inicio = -1
            #revisamos si se encontró o no razón social
            if inicio == -1:
                #si no se encontró  se le avisa al usuario
                st.warning('Revisar formato razón social')
                substring = st.text_input('Digite fecha de emisión')

            else:
                #si sí se encontró se busca hasta donde va  el nombre
                sigla = minus[inicio:].find('sigla') + inicio
                nit = minus[inicio:].find("nit") + inicio
                # por lo general el nombre de la empresa va hasta que empiece el nit
                if (sigla != inicio -1 ) & (sigla<nit):
                    end = sigla
                else:
                    end=nit
                substring = text[inicio:end]
                st.write(f'**Razón social**:{substring}')
            return substring

        def leer_nit():
            '''Extrae el nit del certifiado'''
            #se pone todo el texto en minúsculas sin expacios y sin saltos de línea para evitar casos raros
            minus = text.lower().replace(' ', '').replace('.', '').replace('\n', '')
            #busca el caracter dodnde comienza el nit
            start = minus.find("nit:") + len("nit:")
            #extrae el nit
            substring = minus[start:start+11]
            #lo escribe en la interfaz
            st.write(f'**NIT**: {substring}' )
            return substring

        def leer_fecha_matricula():
            '''Extrae la fecha de matrícula del certifiado'''
            #se pone todo el texto en minúsculas sin expacios y sin saltos de línea para evitar casos raros
            minus = text.lower().replace(':', '').replace('\n', '').replace(' ', '')
            #Se buscan los tres posibles casos
            caso_A = minus.find("fechadematrículaenestacámara")
            caso_B =  minus.find("fechadematrícula")
            caso_C = minus.find('certificamatricula')
            #Se identifica cual de los tres es
            if caso_A != -1:
                start = caso_A + len("fechadematrículaenestacámara")
            elif caso_B != -1:
                start = caso_B + len("fechadematrícula")
            elif caso_C != -1:
                start = minus.find('del', caso_C)  + 3
            else:
                start = -1
            # si encontró algún caso
            if start != - 1:
                #extrae el pedazo de string donde estaría la fecha
                substring = minus[start:start+25]
                fecha = substring.split('de')
                #trata de leer la fecha como texto 10 de enero de 2022
                try:
                    dia =  int(fecha[0])
                    mes = meses[fecha[1]]
                    anio = int(fecha[2][:4])
                    dt = datetime(anio, mes, dia)
                    dt = dt.strftime("%d-%m-%Y")
                    # se escribe en la interfaz
                    st.write(f'**Fecha de matrícula** :{dt}')
                # si la fecha no tenía ese formato el código manda excepción
                except:
                    # se tarta de leer la fecha en formato de marzo 13 de 2022
                    try:
                        dia = int(fecha[0][-2:])
                        mes = meses[fecha[0][:-2]]
                        anio = int(fecha[1][:4])
                        dt = datetime(anio, mes, dia)
                        dt = dt.strftime("%d-%m-%Y")
                        #se escribe en la interfaz
                        st.write(f'**Fecha de matrícula** :{dt}')
                    #si la fecha no tenía ese formato el código manda excepción
                    except:
                        # se tarta de leer la fecha en formato de marzo 3 de 2022
                        try:
                            dia = int(fecha[0][-1:])
                            mes = meses[fecha[0][:-1]]
                            anio = int(fecha[1][:4])
                            dt = datetime(anio, mes, dia)
                            dt = dt.strftime("%d-%m-%Y")
                            #se escribe en la interfaz
                            st.write(f'**Fecha de matrícula** :{dt}')
                        #si la fecha no tenía ese formato el código manda excepción
                        except:
                            # se tarta de leer la fecha en formato de números
                            try:
                                dt = dateutil.parser.parse(substring.strip()[:10])
                                dt = dt.strftime("%d-%m-%Y")
                                st.write(f'**Fecha de matrícula** :{dt}')
                            #si la fecha no tenía ese formato el código manda excepción
                            except:
                                #avisa al usuario que no logró extraer la fecha
                                st.warning('**Revisar el formato de la fecha de matrícula.**')
                                #da la opción de que el usuario la digite
                                dt = st.text_input('Digite fecha de matrícula')
            #si no encontró ningún caso
            else:
                #avisa al usuario que no encontró feha de matricula
                st.warning('**Revisar el formato de la fecha de matrícula. (descripción)**')
                #da la opción de que el usuario la digite
                dt = st.text_input('Digite fecha de matrícula')
            return dt

        def leer_fecha_renovacion():
            '''Extrae la fecha de matrícula del certifiado'''
            #se pone todo el texto en minúsculas sin dos punto y sin saltos de línea para evitar casos raros
            #se quitan las tíldes para uniformar todos los formatos
            minus = text.lower().replace('ó', 'o').replace('í', 'i').replace(':', '').replace('\n', '')
            #busca los posibles casos
            caso_A = minus.find("fecha de renovacion de la matricula")
            caso_B = minus.find("fecha de renovacion")
            #identifica en qué caso estamos
            if caso_A !=-1:
                start = caso_A+ len("fecha de renovacion de la matricula")
            elif caso_B !=-1:
                start = caso_B+ len("fecha de renovacion")
            else:
                # sino encuentra ningun caso
                start =-1
            # si encuentra algún caso
            if start !=-1:
                #extrae el string donde estaría la fecha de renovación
                substring = minus[start:start+70].replace(' ', '')
                fecha = substring.split('de')
                #trata de leer la fecha como texto 10 de enero de 2022
                try:
                    dia =  int(fecha[0])
                    mes = meses[fecha[1]]
                    anio = int(fecha[2][:4])
                    dt = datetime(anio, mes, dia)
                    dt = dt.strftime("%d-%m-%Y")
                    #se escribe en la interfaz
                    st.write(f'**Fecha de renovación**: {dt}')
                except:
                    # se tarta de leer la fecha en formato de marzo 3 de 2022
                    try:
                        anio = int(fecha[1].strip()[:4])
                        dia = int(fecha[0][-2:])
                        mes = meses[fecha[0][:-2]]
                        dt = datetime(anio, mes, dia)
                        dt = dt.strftime("%d-%m-%Y")
                        #se escribe en la interfaz
                        st.write(f'**Fecha de renovación**: {dt}')
                    except:
                        # se tarta de leer la fecha en formato de números
                        try:
                            dt = dateutil.parser.parse(substring.strip()[: 10])
                            dt = dt.strftime("%d-%m-%Y")
                            #se escribe en la interfaz
                            st.write(f'**Fecha de renovación**: {dt}')
                        #si la fecha no tenía ninguno de los formatos manda excepción
                        except:
                            #se avisa al usuario que la fecha no tiene formato conocido
                            st.warning('**Revisar el formato de la fecha de renovación. (fecha)**')
                            # se da la opción de digitar la fecha al usuario
                            dt = st.text_input('Digite fecha de renovación')
            # si no encontró ningún caso
            else:
                #avisa al usuario que no encontró fechaa
                st.info('No se encontró fecha de renovación.')
                # se da la opción de digitar la fecha al usuario
                dt = st.text_input('Digite fecha de renovación')
            return dt

        def leer_capital_pagado():
            '''Extrae el capiltal pagado por la empresa'''
            #se pone todo el texto en minúsculas sin dos puntos o asteríscos
            #sin saltos de línea o espacios para evitar casos raros
            pegado = text.replace(' ', '').replace('*', '').replace(':', '').replace('\n','').lower()
            # se busca el primer caso
            inicio_1 = pegado.find('capitalpagadovalor')
            # se vuelve al texto original se quitan los dos puntos
            texto = text.replace(':', '')
            # se busca el segundo caso
            inicio_2 = texto.find('CAPITAL PAGADO')
            #se identifica que caso es
            if inicio_1 != -1 :
                #si es el primer caso se busca hasta donde va el capital
                # que es dodne aparece por primera vez la letra n
                fin = pegado.find('n', inicio_1)
                #se guarda el pedazo de string que tiene el capital en el objeto k
                k = pegado[inicio_1+len('capitalpagadovalor'):fin]
                # se escribe en la interfaz
                st.write(f'**Capital Pagado**: {k}')
            elif inicio_2 != -1:
                #si es el segundo caso se busca hasta donde va el capital
                # que es dodne a parece por primera vez el primer espacio
                k = texto[inicio_2+len('CAPITAL PAGADO'):inicio_2+len('CAPITAL PAGADO')+40].strip().split()[0]
                # se escribe en la interfaz
                st.write(f'**Capital Pagado**: {k}')
            else:
                #sino enontró ninguno de los dos casos
                #avisa al usuario
                st.warning('Revisar formato de capital pagado.')
                # se da la opción de digitar el capital pagado
                k = st.text_input('Digite capital pagado')
            return k

        def leer_objeto_social():
            '''Extrae el objeto social del certificado'''
            # se pone el texto en minúsculas sin espacios ni saltos de línea
            pegado_minus = text.lower().replace(' ', '').replace('\n', '')
            #se buscan los tres posibles casos
            caso1 = pegado_minus.find('actividadprincipalcódigociiu:')
            caso2 = pegado_minus.find('actividadprincipal:')
            caso3 = pegado_minus.find('actividadeconómicaporlaquepercibiómayoresingresosenelperiodo-ciiu:')
            #se identifica en qué caso estamos
            if caso1!=-1:
                start = caso1+len('actividadprincipalcódigociiu:')
            elif caso2 !=-1:
                start = caso2+len('actividadprincipal:')
            elif caso3 !=-1:
                start = caso3+len('actividadeconómicaporlaquepercibiómayoresingresosenelperiodo-ciiu:')
            else:
                #si no se encuentra ningún caso
                start = -1
            # si se encontró algun caso
            if start!=-1:
                # tarata de leer el código como los primeros 4 caracteres despues del start
                try:
                    #busca la actividad en el diccionario de códigos que se leyó antes
                    act = codigos.loc[pegado_minus[start:start+4]]['Actividad']
                    st.write(f"** Actividad principal**: {act}")
                except:
                    # tarata de leer el código como los primeros 4 caracteres despues del start +1
                    try:
                        #busca la actividad en el diccionario de códigos que se leyó antes
                        act =codigos.loc[pegado_minus[start+1:start+5]]['Actividad']
                        st.write(f"** Actividad principal**: {act}")
                    except:
                        # si no encontró la actividad con el código se avisa al usuario
                        st.error('**Revisar código CIIU.**')
                        # se da la opción al usuario de digitar la actividad
                        act = st.text_input('Digite actividad principal')
            #si no encontró ningún caso
            else:
                #se avisa al usuario
                st.error('**No se encontró actividad principal.**')
                # se da la opción al usuario de digitar la actividad
                act = st.text_input('Digite actividad principal')
            return act

        def leer_rep_legal():
            '''Extrae el representante legal de la empresa'''
            #se quitan backslash, salto de línea y tíldes en las O
            texto = text.replace('/', ' ').upper().replace('\n', '').replace('Ó', 'O')
            #se busca la paabra CARGO
            inicio = texto.find('CARGO')
            # si no se encontró la palabra
            if inicio == -1:
                # se avisa al usuario
                st.error('**No se encontró representante legal**')
                # se da la opción de que anote el nombre
                rep_legal = st.text_input('Ingrese el nombre del representante legal')
            else:
                #se toma solo el texto que venga después de la palabra cargo
                # y se guarda en el objeto texto_2
                texto_2 = texto[inicio+5:].strip()
                # mientras que no se haya encontrado la palabra nombre
                while texto_2[:6]!='NOMBRE':
                    #se busca el siguiente CARGO
                    inicio_nuevo = texto_2.find('CARGO')+5
                    #se toma solo el texto que venga después de la sigiente aparición de la palabra cargo
                    # y se guarda en el objeto texto_2
                    texto_2 = texto_2[inicio_nuevo:].strip()
                    # si deja de haber cargos en el texto que queda y no se encontró el sring NOMBRE
                    if inicio_nuevo == -1:
                        # se avisa al usuario que no se encontró representante legal
                        st.error('**No se encontró representante legal**')
                        #se da la opción al usuario de digitar el nombre
                        rep_legal = st.text_input('Ingrese el nombre del representante legal')
                        break
                #si encontró el NOMBRE del representante legal
                #quita todas las palabra asociadas a su cargo para dejar únicamente el nombre desnudo
                desnudo = texto_2.replace('IDENTIFICACION', '').replace('REPRESENTANTE', '').replace('LEGAL', '').replace('GERENTE', '').replace('PRINCIPAL', '').replace('GENERAL', '').strip()
                # como no se sabe hasta donde va el nombre se toma arbitrariamentw 112 caracteres
                desnudo = desnudo[6:].strip()[:112]
                #se buscan los casos posibles en donde puede terminar el nombre
                fin1 = desnudo.find('C.')
                fin2 = desnudo.find('CC')
                fin3 = desnudo.find(' C ')
                fin4 = desnudo.find('DOC.')
                #se identifica cual de los casos es
                if fin1 ==-1:
                    fin1 = 112
                if fin2 ==-1:
                    fin2 = 112
                if fin3 ==-1:
                    fin3 = 112
                if fin4 ==-1:
                    fin4 = 112
                # en el peor de los casos el fin es 112
                fin = min(fin1, fin2, fin3, fin4)
                #se extrae el string hasta el mejor final
                rep_legal = desnudo[:fin]
                # se escribe en la interfaz
                st.write(f"** Representante legal ** : {rep_legal}")
                return rep_legal

        def buscar_embargos():
            '''Extrae el número de embargos que aparecen en el certifiado'''
            #se cuenta el número de apariciones de la palabra 'embargo'
            n_embargos = text.lower().count('embargo')
            #si hay embargos
            if n_embargos !=0:
                # se avisa al usuario
                st.error(f'**Se encontraron {n_embargos} embargos**.')
            else:
                # si no hay también se avisa
                st.write('No aparecen embargos.')
            return n_embargos

        def buscar_procesos():
            '''Extrae el número de procesos que aparecen en el certifiado'''
            #se cuenta el número de apariciones del string 'PROCESO EJECUTIVO'
            n_procesos = text.upper().count('PROCESO EJECUTIVO')
            #si hay prosecos
            if n_procesos !=0:
                #se avisa a l usuario
                st.error(f'**Se encontraron {n_procesos} procesos ejecutivos**.')
            else:
                #si no hay tambien se avisa al usuario
                st.write('No aparecen procesos ejecutivos.')
            return n_procesos

        def leer_facultades_rlegal():
            '''Extrae las facultades del representante legal '''
            # se pone el texto en minúsculas sin espacios ni saltos de línea
            minus = text.lower().replace('\n', ' ').replace('  ', ' ')
            #se buscan todos los posibles casos
            A = minus.find('celebrar actos y contratos que no excedan')
            fin_A = minus[A:].find('.') + A
            B = minus.find('celebrar o ejecutar')
            fin_B = minus[B:].find('.') + B
            C =  minus.find('representante legal para la celebración')
            fin_C = minus[C:].find('"') + C
            E = minus.find('ejercer libremente todos los actos')
            fin_E = minus[E:].find(';')+E
            #G = minus.find('los representantes legales tendrán las más amplias y suficientes facultades')
            #H = minus.find('SUSCRIBIR LOS CONTRATOS QUE SEAN NECESARIOS PARA CUMPLIR CON EL OBJETO DE LA SOCIEDAD'.lower())
            #I = minus.find('cuando el cargo de representante legal o su suplencia recaiga en un tercero, este tendrá restricciones o limitaciones para la contratación tanto por naturaleza del negocio como de cuantía.')
            #J = minus.find('cuando la representación legal principal o supletoria recaiga en uno de los accionistas de la sociedad por acciones simplificada,')
            L = minus.find('celebrar todo')
            fin_L = minus[L:].find('.') + L if minus[L:].find('.') != -1 else  minus[L:].find(';') + L
            M = minus.find('en desarrollo de su objeto')
            fin_M = minus[M:].find('.')+M
            N = minus.find('autorizar al gerente general')
            fin_N = minus[N:].find('.')+N
            #Se guarda un diccionario de llaves la letre de cada opción
            #valores una lista con el principio y fin de esa opción
            opciones= { 'A': [A, fin_A],
                        'B': [B,fin_B],
                        'C': [C,fin_C],
                        'E': [E,fin_E],
                        #'G': [G,-1],
                        #'H': [H,-1],
                        #'I': [I,-1],
                        #'J': [J,-1],
                        'L': [L,fin_L],
                        'M': [M,fin_M],
                        'N': [N,fin_N ]
                        }
            #se crea un strin ació donde se van a guardar las facultades
            facultades = ''
            #se itera sobre las opciones
            for l in opciones.keys():
                #si el inicio de la opcion es distinto de nulo
                #signifinca que ese es el formato en el qu están escritas las facultades
                if opciones[l][0] != -1:
                    #se escriben las facultades
                    st.write('**Facultades del representante legal **')
                    st.write(minus[opciones[l][0]:opciones[l][1]])
                    # se guardan en el string  de facultades
                    facultades += minus[opciones[l][0]:opciones[l][1]] + ';'
            # si el string sigue vacio despues de iterar significa que no se encontró ninguno de los casos
            if facultades == '':
                #se avisa al usuario que no se encontraron facultades
                st.warning('No se encontraron facultades del representante legal.')
                #se da la opción al usuario para digitarlas
                fac_rl = st.text_input('Facultades del representante legal')
            #si si se encontraron
            else:
                #se pregunta al usuario si quiere editarlas en dado caso que haya un error
                editar = st.checkbox('Editar facultades')
                if editar:
                    # si las quiere editar se abre un campo de edicón de texto con las facultades escritas
                    fac_rl = st.text_input('Facultades del representante legal', facultades)
                else:
                    #sino se dejan las que se encontraroon
                    fac_rl = facultades
            return fac_rl

        fecha_em = leer_fecha_emision()# se lee y se guarda  la fecha de emisión
        rs = leer_razon_social()# se lee y se guarda  la razón Social
        nitl = leer_nit()# se lee y se guarda el nit
        fecham = leer_fecha_matricula()# se lee y se guarda la fecha de matricula
        fechar = leer_fecha_renovacion()# se lee y se guarda la fecha de renovación
        k = leer_capital_pagado()# se lee y se guarda el capital pagado
        os = leer_objeto_social()# se lee y se guarda el objeto social de la empresa
        rep_legal = leer_rep_legal()# se lee y se guarda el nombre del representante
        fac_rl = leer_facultades_rlegal()# se lee y se guarda las facultades del representante
        n_embargos = buscar_embargos()# se lee y se guarda los embargos
        n_procesos = buscar_procesos()# se lee y se guarda los procesos
        # se da la opción de agregar observaciones
        obs_c = st.checkbox('Agregar observación')
        # se crea un string vacio con las observaciones
        obs_c_text = ''
        # si se quieren agregar obse
        if obs_c:
            #se pone una casilla de texto para las observaciones en la interfaz
            obs_c_text = st.text_area('Observaciones')
        #se cierra el archivo
        pdfFileObj.close()
        # se cre una lista con todos los datos extraídos del certificado y se retorna
        camycom = [fecha_em, rs, nitl, fecham, fechar, k, os, rep_legal, fac_rl, n_embargos, n_procesos, obs_c, obs_c_text]
        return camycom
    #si no se cargado ningún archivo
    else:
        #se retorna una lista vacía
        return []

def encontrar_ef():
    """Crea en la interfaz los inputs necesarions para encontrar los estados
    fnancieros de la empresa y encuentra los estados financieros de la empresa
    """
    #el salario mimnimo mensual vigente
    salario_minimo = 908526# Se debe actualizar cada año

    def dividir(a,b):
        """"Retorna la division de a por b a menos que
          a sea 0 --> retorna 0
          b sea cero pero a no --> retorna un string que avisa
          """
        if a == 0:
            return 0
        elif b == 0:
            return 'Error división por 0'
        else:
            return round(a/b, 1)
    # se usa el siguiente comando para no tener que crear las columnas 1 y 2
    #cada vez que se ponga el título de una parte
    with st.form(key='columns_in_form'):
        #título primera parte
        st.write("## Balance general")
        # se crean dos columnas
        col1, col2 = st.columns(2)
        #la primera columna contiene los datos del hace dos años (por default 2020)
        anio1 = col1.number_input('Periodo 1',value = 2020,step =1 )
        #la segunda columna contiene los datos del año anterior( por default 2019)
        anio2 = col2.number_input('Periodo 2',value = 2019,step =1 )
        #puede que sean datos anuales, semestrales, etc
        # se escoge cuantos meses se tienen en cuenta en los estados financieros
        meses = st.slider('Mes de corte de los periodos.', min_value=1, max_value=12, value=12,  step=1)
        # se escoge la unidad en la que se van a digitar los datos
        unidad = st.radio('Unidad COP', ('Unidades', 'Miles', 'Millones'))
        st.write("### Activos")
        # se crean nuevamente las dos columnas
        col1, col2 = st.columns(2)
        # se agrega input para los dos periodos de tiempo
        activo_corriente = col1.number_input('Activo corriente',value =0)
        activo_corriente2 = col2.number_input('Activo corriente ',value =0)
        # se agrega input para los dos periodos de tiempo
        deudores_clientes = col1.number_input('Deudores',value = 0)
        deudores_clientes2 = col2.number_input('Deudores ', value =0)
        # se agrega input para los dos periodos de tiempo
        inventarios = col1.number_input('Inventarios', value =0)
        inventarios2 = col2.number_input('Inventarios ', value =0)
        # se agrega input para los dos periodos de tiempo
        tot_activo = col1.number_input('Total activo',value = 0)
        tot_activo2 = col2.number_input('Total activo ', value =0)
        #título segunda parte
        st.write("### Pasivos y patrimonio")
        # se crean nuevamente las dos columnas
        col1, col2 = st.columns(2)
        # se agrega input para los dos periodos de tiempo
        pasivo_corriente = col1.number_input('Pasivo corriente',  value =0)
        pasivo_corriente2 = col2.number_input('Pasivo corriente ', value =0)
        # se agrega input para los dos periodos de tiempo
        proveerdores = col1.number_input('Proveedores', value =0)
        proveerdores2 = col2.number_input('Proveedores ', value =0)
        # se agrega input para los dos periodos de tiempo
        pasivo_total = col1.number_input('Pasivo total' , value =0)
        pasivo_total2 = col2.number_input('Pasivo total ',value =0)
        # se agrega input para los dos periodos de tiempo
        patrimonio = col1.number_input('Patrimonio total',value =0)
        patrimonio2 = col2.number_input('Patrimonio total ',value =0)
        #título tercera parte
        st.write("## Estado de resultados")
        # se crean nuevamente las dos columnas
        col1, col2 = st.columns(2)
        # se agrega input para los dos periodos de tiempo
        ingresos_op_netos= col1.number_input('Ingresos operacionales netos', value =0)
        ingresos_op_netos2 = col2.number_input('Ingresos operacionales netos ', value =0)
        # se agrega input para los dos periodos de tiempo
        costo_ventas = col1.number_input('Costo de ventas', value =0)
        costo_ventas2 = col2.number_input('Costo de ventas ', value =0)
        # se agrega input para los dos periodos de tiempo
        utilidad_opercional = col1.number_input('Utilidad neta operacional',value = 0)
        utilidad_opercional2 = col2.number_input('Utilidad neta operacional ',value = 0)
        # se agrega input para los dos periodos de tiempo
        gastos_financieros = col1.number_input('Gastos financieros',value = 0)
        gastos_financieros2 = col2.number_input('Gastos financieros ',value =0)
        # se agrega input para los dos periodos de tiempo
        antes_impuestos = col1.number_input('Utilidad antes de impuestos',value = 0)
        antes_impuestos2 = col2.number_input('Utilidad antes de impuestos ',value = 0)
        # se agrega input para los dos periodos de tiempo
        utilidad_neta = col1.number_input('Utilidad neta', value = 0)
        utilidad_neta2 = col2.number_input('Utilidad neta ',value = 0)
        # se agrega input del plazo para pagar el crédito  en días
        plazo = st.number_input('Plazo en días del crédito.', 1 ,step = 1)
        # Botón para saber que ya se digitaron todos los estados financieros
        submitted = st.form_submit_button('Encontrar índices financieros')
    #si se dio click al botón
    if submitted:
        #se calculan los índices
        utilidad_bruta = ingresos_op_netos-costo_ventas
        provision_impuestos= antes_impuestos - utilidad_neta
        compras_mat_prima = costo_ventas + inventarios -inventarios2
        utilidad_bruta2 = ingresos_op_netos2 - costo_ventas2
        provision_impuestos2 = antes_impuestos2 - utilidad_neta2
        compras_mat_prima2 = costo_ventas2 + inventarios2
        razon_corriente1 =dividir(activo_corriente, pasivo_corriente)
        razon_acida1 = dividir((activo_corriente-inventarios),pasivo_corriente)
        rotacion_act_cts1 = dividir(activo_corriente*360, ingresos_op_netos)
        rotacion_cxc1 = dividir(deudores_clientes*360, ingresos_op_netos)
        rotacion_inv1 = dividir(inventarios*360, costo_ventas)
        rotacion_cxp1 = dividir(proveerdores*360, compras_mat_prima)
        rentabilidad_op1 = dividir(utilidad_opercional*100, activo_corriente)
        kd1 = dividir(gastos_financieros*100, pasivo_total)
        rentabilidad_neta1 = dividir(utilidad_neta*100, patrimonio)
        endeudamiento1 =dividir(pasivo_total*100,tot_activo)
        i_patrimonial1 =dividir(patrimonio*100,tot_activo)
        cobertura_i1 =dividir(utilidad_opercional*100, gastos_financieros)
        mg_op1 = dividir(utilidad_opercional*100, ingresos_op_netos)
        mg_impos1 = dividir(antes_impuestos*100, ingresos_op_netos)
        mg_neto1 = dividir(utilidad_neta*100, ingresos_op_netos)
        mg_bruto1 = dividir(utilidad_bruta*100, ingresos_op_netos)
        retorno_patri1 = dividir(utilidad_neta*2*100, (patrimonio+patrimonio2))
        retorno_activo1 =dividir((utilidad_opercional- provision_impuestos)*2*100, (tot_activo+tot_activo2))
        net = "${:,.0f}".format(deudores_clientes + inventarios - proveerdores)
        tot = "${:,.0f}".format(activo_corriente - pasivo_corriente)
        razon_corriente2 = dividir(activo_corriente2, pasivo_corriente2)
        razon_acida2 = dividir((activo_corriente2-inventarios2), pasivo_corriente2)
        rotacion_act_cts2 =dividir(activo_corriente2*360,ingresos_op_netos2)
        rotacion_cxc2=dividir(deudores_clientes2*360,ingresos_op_netos2)
        rotacion_inv2 = dividir(inventarios2*360, costo_ventas2)
        rotacion_cxp2 = dividir(proveerdores2*360, compras_mat_prima2)
        rentabilidad_op2 = dividir(utilidad_opercional2*100,activo_corriente2)
        kd2 = dividir(gastos_financieros2*100,pasivo_total2)
        rentabilidad_neta2 = dividir(utilidad_neta2*100,patrimonio2 )
        endeudamineto2 = dividir(pasivo_total2*100, tot_activo2)
        i_patrimonial2 = dividir(patrimonio2*100, tot_activo2)
        cobertura_i2 = dividir(utilidad_opercional2*100,gastos_financieros2)
        mg_op2 = dividir(utilidad_opercional2*100,ingresos_op_netos2)
        mg_impos2 = dividir(antes_impuestos2*100,ingresos_op_netos2)
        mg_neto2 = dividir(utilidad_neta2*100,ingresos_op_netos2)
        mg_bruto2 = dividir(utilidad_bruta2*100,ingresos_op_netos2)
        retorno_patri2 = dividir((utilidad_neta2)*100,patrimonio2)
        retorno_activo2 = dividir((utilidad_opercional2- provision_impuestos2)*2*100,(tot_activo2+tot_activo2))
        net2 = "${:,.0f}".format(deudores_clientes2 + inventarios2 - proveerdores2)
        tot2 = "${:,.0f}".format(activo_corriente2 - pasivo_corriente2)
        #se guarda una lista con los indices financieros del peiriodo 1 en el session state
        # más como último objeto de la lista en qué unidades está expresados los EEFF
        st.session_state.indices_2019 = [anio2, razon_corriente2, razon_acida2, rotacion_act_cts2, rotacion_cxc2,
                        rotacion_inv2, rotacion_cxp2, rentabilidad_op2, kd2,
                        rentabilidad_neta2, endeudamineto2, i_patrimonial2, cobertura_i2,
                        mg_op2, mg_impos2, mg_neto2, mg_bruto2, retorno_patri2,
                        retorno_activo2, net2,  tot2 , unidad]
        # en esta seccion se escriben todos los indices en la interfaz que se encontraron previamente
        st.write('## Indices de Liquidez')
        # se crean tres columnas
        col1, col2, col3 = st.columns(3)
        #la primera columna tiene el nombre de los índices
        col1.write('Indices')
        col1.write('**Razón Corriente**')
        col1.write('**Razón ácida**')
        col1.write('**Rotación Act. Ctes.**')
        col1.write('**Rotación de CXC**')
        col1.write('**Rotación Inventarios**')
        col1.write('**Rotación CXP**')
        #la segunda columna tiene los índices del periodo 1
        col2.write(f'**{anio1}**')
        col2.write(f'{razon_corriente1}')
        col2.write(f'{razon_acida1}')
        col2.write(f'{rotacion_act_cts1} días')
        col2.write(f'{rotacion_cxc1} días')
        col2.write(f'{rotacion_inv1} días')
        col2.write(f'{rotacion_cxp1} días')
        #la tercera columna tiene los índices del periodo 2
        col3.write(f'**{anio2}**')
        col3.write(f'{razon_corriente2}')
        col3.write(f'{razon_acida2}')
        col3.write(f'{rotacion_act_cts2} días')
        col3.write(f'{rotacion_cxc2} días')
        col3.write(f'{rotacion_inv2} días')
        col3.write(f'{rotacion_cxp2} días')
        st.write('## Indices de Rentabilidad')
        # se crean nuevamente las tres columnas
        col1, col2, col3 = st.columns(3)
        #la primera columna tiene el nombre de los índices
        col1.write('**Rentabilidad Op./Activo Cte.**')
        col1.write('**Costo de la Deuda (KD)**')
        col1.write('**Rentabilidad Neta/ Patrimonio**')
        #la segunda columna tiene los índices del periodo 1
        col2.write(f'{rentabilidad_op1}%')
        col2.write(f'{kd1} %')
        col2.write(f'{rentabilidad_neta1}%')
        #la tercera columna tiene los índices del periodo 2
        col3.write(f'{rentabilidad_op2}%')
        col3.write(f'{kd2} %')
        col3.write(f'{rentabilidad_neta2}%')
        st.write(""" ## Análisis de endeudamiento """)
        # se crean nuevamente las tres columnas
        col1, col2, col3 = st.columns(3)
        #la primera columna tiene el nombre de los índices
        col1.write('**Indice de Endeudamiento**')
        col1.write('**Indice Patrimonial**')
        col1.write('**Cobertura de Intereses**')
        col1.write(' ')
        #la segunda columna tiene los índices del periodo 1
        col2.write(f'{endeudamiento1}%')
        col2.write(f'{i_patrimonial1}%')
        col2.write(f'{cobertura_i1}%')
        col2.write(' ')
        #la tercera columna tiene los índices del periodo 2
        col3.write(f'{endeudamineto2}%')
        col3.write(f'{i_patrimonial2}%')
        col3.write(f'{cobertura_i2}%')
        col3.write(' ')
        #la primera columna tiene el nombre de los índices
        col1.write('**Margen Operacional**')
        col1.write('**Margen Antes de Impto.**')
        col1.write('**Margen Neto**')
        col1.write('**Margen Bruto**')
        col1.write(' ')
        #la segunda columna tiene los índices del periodo 1
        col2.write(f'{mg_op1}%')
        col2.write(f'{mg_impos1}%')
        col2.write(f'{mg_neto1}%')
        col2.write(f'{mg_bruto1}%')
        col2.write(' ')
        #la tercera columna tiene los índices del periodo 2
        col3.write(f'{mg_op2}%')
        col3.write(f'{mg_impos2}%')
        col3.write(f'{mg_neto2}%')
        col3.write(f'{mg_bruto2}%')
        col3.write(' ')
        #la primera columna tiene el nombre de los índices
        col1.write('**Retorno S/Patrimonio**')
        col1.write('**Retorno S/Activo**')
        #la segunda columna tiene los índices del periodo 1
        col2.write(f'{retorno_patri1}%')
        col2.write(f'{retorno_activo1}%')
        #la tercera columna tiene los índices del periodo 2
        col3.write(f'{retorno_patri2}%')
        col3.write(f'{retorno_activo2}%')
        #la primera columna tiene el nombre de los índices
        col1.write(' ')
        col1.write('**Capital de Trab. Neto Op.**')
        col1.write('**Capital de Trab. Neto**')
        #la segunda columna tiene los índices del periodo 1
        col2.write(' ')
        col2.write(f'{net}')
        col2.write(f'{tot}')
        #la tercera columna tiene los índices del periodo 2
        col3.write(' ')
        col3.write(f'{net2}')
        col3.write(f'{tot2}')

        # En esta seccion se utilizan los índices para calcular el cupo suguerido
        #se tienen en cuenta 6 variables
        # var1 que depende del tamaño de la empresa
        # var2 que depende del liquidacion parcial del margen operativo y neto
        # var4 que depende del endeudamiento
        # var5 que depende de la rentabilidad neta
        # var6 que depende de la rotación de activos
        # var7 que depende de la razón ácida

        #Se usa un try para calcular el cupo para que en dado caso de que haya
        #algún monto de los estados fianncienros (EEFF) mal digitado que genere
        # error el código sea capaz de atraparlo
        try:
            # se encuentra el tamaño de la empresa como activo/salario mínimo
            tamanio_empresa = tot_activo/salario_minimo
            # se calcula el puntaje de la variable 1 var_1 a partir del
            # tamaño de la empresa
            var_1 = 0
            if tamanio_empresa<500:
                var_1 = 80
            elif tamanio_empresa<5000:
                var_1 = 90
            elif tamanio_empresa<30000:
                var_1 = 100
            else:
                var_1 = 110
            # se calcula la liquidación parcial de margen neto a partir dl margen operativo
            liquidacion_parcial_mg_op = 0
            if mg_op1>=15:
                liquidacion_parcial_mg_op = 120
            elif mg_op1>=12:
                liquidacion_parcial_mg_op = 100
            elif mg_op1>= 9:
                liquidacion_parcial_mg_op = 80
            elif mg_op1>=6:
                liquidacion_parcial_mg_op = 60
            elif mg_op1>=3:
                liquidacion_parcial_mg_op = 40
            elif mg_op1>=1:
                liquidacion_parcial_mg_op = 20
            else:
                liquidacion_parcial_mg_op = 0
            # se calcula la liquidación parcial de margen neto a partir dl margen neto
            liquidacion_parcial_mg_neto = 0
            if mg_neto1 >=10:
                liquidacion_parcial_mg_neto = 120
            elif mg_neto1 >=8:
                liquidacion_parcial_mg_neto = 100
            elif mg_neto1 >=6:
                liquidacion_parcial_mg_neto = 80
            elif mg_neto1 >=4:
                liquidacion_parcial_mg_neto = 60
            elif mg_neto1 >=2:
                liquidacion_parcial_mg_neto = 40
            elif mg_neto1 >=1:
                liquidacion_parcial_mg_neto = 20
            else:
                liquidacion_parcial_mg_neto = 0
            # se calcula el puntaje de la variable 2 var_2 a partir de
            # la liquidación parcial de margen operativo y la liquidacion
            #parcial de margen neto
            var_2 = 0.7*liquidacion_parcial_mg_op + 0.3*liquidacion_parcial_mg_neto
            # se calcula el puntaje de la variable 4  a partir del endeudamiento1
            var_4 = 0
            if endeudamiento1 >=90:
                var_4 = 0
            elif endeudamiento1 >=80:
                var_4= 15
            elif endeudamiento1 >=70:
                var_4= 30
            elif endeudamiento1 >=60:
                var_4= 45
            elif endeudamiento1 >=50:
                var_4= 60
            elif endeudamiento1 >=40:
                var_4= 75
            elif endeudamiento1 >=30:
                var_4= 90
            elif endeudamiento1 >=20:
                var_4= 105
            else:
                var_4= 120
            # se calcula el puntaje de la variable 5 var_5 a partir de la
            # rentabilidad neta
            var_5 = 0
            if rentabilidad_neta1>20:
                var_5 = 125
            elif rentabilidad_neta1>15:
                var_5 = 100
            elif rentabilidad_neta1>10:
                var_5 = 75
            elif rentabilidad_neta1>5:
                var_5 = 50
            elif rentabilidad_neta1>1:
                var_5 = 25
            else:
                var_5 = 0
            # Se calcula el número de veces de rotación tomando el cociente de
            # los 360 días del año sobre la rotación de activos
            veces_rot = int(360/rotacion_act_cts1)
            # se fija un tope límite de rotación en 4
            if veces_rot>4:
                veces_rot = 4
            # diccionario que en las llaves tiene  el número de vece que rotó
            # la empresa y en valores el puntaje correspondiente le la var_6
            dict_var_6 ={0: 50 , 1:75, 2:100, 3:125, 4:150 }
            # se le asigna un puntaje a la variable 6
            var_6 = dict_var_6[veces_rot]
            # se calcula el puntaje de la variable 7 var_7 a partir de la
            # razón acida de la empresa
            var_7 = 0
            if razon_acida1 >2:
                var_7 = 100
            elif razon_acida1>1:
                var_7 = 75
            elif razon_acida1>0:
                var_7 = 50
            else:
                var_7 = 0
            # se calcula el puntaje total como un promedio ponderado de las
            # variables var1,  var2,  var4,  var5,  var6,   var7
            ptje_tot = 0.13*var_1 + 0.23*var_2 + 0.25*var_4 +0.13*var_5 + 0.08*var_6 + 0.18*var_7
            #Se crea el porcentaje de costo de ventas y se inicia en 0
            porcentaje_costo_ventas = 0
            # Basado en el nivel del puntaje total(ptje_tot) se asigna un
            # porcentaje_costo_ventas
            if ptje_tot>120:
                porcentaje_costo_ventas = 0.3
            elif ptje_tot>100:
                porcentaje_costo_ventas = 0.25
            elif ptje_tot>80:
                porcentaje_costo_ventas = 0.2
            elif ptje_tot>60:
                porcentaje_costo_ventas = 0.15
            elif ptje_tot>40:
                porcentaje_costo_ventas = 0.1
            elif ptje_tot>20:
                porcentaje_costo_ventas = 0.05
            else:
                porcentaje_costo_ventas = 0
            # el plazo en días inputado por el usuario se transforma a meses
            if plazo < 32:
                #se toma como un mes si el dígito tiene menos de 31 días de plazo
                plazo = 1
            else:
                #de lo contrario se redondea al número de meses que corresponda
                plazo = round(plazo/30)

            # se dividen los ingresos de los EEFF por el número de meses que se
            #incluyen en los EEFF
            ingresos_mensuales = ingresos_op_netos/meses
            # se inicializa el cupo en 0
            cupo_sugerido = 0
            # si el porcentaje de endeudamiento es superior a 90%
            if endeudamiento1>=90:
                # se sugiere no dar crédito/ el cupo es 0
                cupo_sugerido = 0
            # si el porcentaje de endeudamiento es superior a 70%
            elif endeudamiento1>=70:
                # se suegiere un cupo que siga la siguiente fórmula
                # el cupo se mitiga por el porcentaje de endeudamiento
                cupo_sugerido = ingresos_mensuales*porcentaje_costo_ventas*plazo*(100-endeudamiento1)
            # si el porcentaje de endeudamiento es inferior a 70%
            else:
                # se suegiere un cupo que siga la siguiente fórmula
                cupo_sugerido = ingresos_mensuales*porcentaje_costo_ventas*plazo
            # se pone el cupo en formato de dinero
            cupo_sugerido = "${:,.0f}".format(cupo_sugerido)
            #se guarda una lista con los indices financieros del peiriodo 1 en el session state
            # más como último objeto de la lista el cupo sugerido
            st.session_state.indices_2020 = [anio1, razon_corriente1, razon_acida1, rotacion_act_cts1, rotacion_cxc1,
                            rotacion_inv1, rotacion_cxp1, rentabilidad_op1, kd1,
                            rentabilidad_neta1, endeudamiento1, i_patrimonial1, cobertura_i1,
                            mg_op1, mg_impos1, mg_neto1, mg_bruto1, retorno_patri1,
                            retorno_activo1, net,  tot, cupo_sugerido ]
            # Se escribe el cupo sugerido en la interfaz
            st.write(f'**Cupo sugerirdo** : {cupo_sugerido}')
        # si alguno de los cálculos falla se crea un excepción
        except :
            # se notifica al usuario que no se pudo sacar el valor
            # la excepción más común es ue haya aguna división por 0 producto
            # de uno o varios montos mal digitados
            st.error('Por favor revisar valores para calcular el cupo.')
            # se fija el cupo sugerido en 0
            cupo_sugerido = 0
            #se guarda una lista con los indices financieros del peiriodo 1 en el session state
            # más como último objeto de la lista el cupo sugerido
            st.session_state.indices_2020 = [anio1, razon_corriente1, razon_acida1, rotacion_act_cts1, rotacion_cxc1,
                            rotacion_inv1, rotacion_cxp1, rentabilidad_op1, kd1,
                            rentabilidad_neta1, endeudamiento1, i_patrimonial1, cobertura_i1,
                            mg_op1, mg_impos1, mg_neto1, mg_bruto1, retorno_patri1,
                            retorno_activo1, net,  tot, cupo_sugerido ]

def concepto_segun_dias(dias):
    '''Retorna el concepto de acuerdo a los días promedio de pago'''
    # si el cliente paga en promedio antes de la fecha de corte
    if dias<=0:
        concepto1 = 'Excelente'
    # si el cliente paga en promedio antes de 15 días después de la fecha de corte
    elif dias <= 15:
        concepto1 = 'Muy bueno'
    # si el cliente paga en promedio antes de 30 días después de la fecha de corte
    elif dias<= 30:
        concepto1 = 'Bueno'
    # si el cliente paga en promedio antes de 60 días después de la fecha de corte
    elif dias <= 60:
        concepto1 = 'A revisar'
    # si el cliente paga en promedio después 60 días de la fecha de corte
    else:
        concepto1 = 'Bloquear'
    return concepto1

def imprimir_edades(cod,semestre,abonos):
    """
    Encuentra el porcentaje de la deuda pagada por un cliente
    para cada una de las edades de vencimiento.
    Inputs:
    cod(str): código del cliente
    semetre (bool): si es true es para calcular el pago por edades de los últimos 6
                    si es False es para calcular el pago por edades histórico
    abonos(DataFrame): el DataFrame de  de los clientes
    Returns:
    total_abonado(float): Total de lo que el cliente ha abonado
    dias_promedio(float): Días promedio de pago después del plazo
    fig(figure): Tabla que muestra el porcentaje de pagos por edades
    """
    #filtro el dataframe de abonos para tener sólo los abonos del cliente
    temporal = abonos[abonos['Nit tercero']==cod]
    #Si se quiere los pagos de los últimos 6 meses
    if semestre:
        #se filtra el dataframe de abonos del cliente para obtener
        # los últimos 6 meses
        temporal = temporal[temporal['Fecha']>np.datetime64('2021-02-28')]#AACTUALIZAR
        #título del plot
        titulo =  'Último semestre'
        #la columna dias de pago tiene la diferencia en días entre el día
        #en que vencía elplazo y y el día que el cliente abonó
        dias_promedio = temporal['Días de pago'].mean()# se toma el promedio
    # si se quiere los pagos del cliente históricos
    else:
        #título del plot
        titulo =  'Histórico'
        #la columna Días de pago tiene la diferencia en días entre el día
        #en que vencía el plazo y y el día que el cliente abonó
        dias_promedio = temporal['Días de pago'].mean()# se toma el promedio
    # en la columna créditos está el valor abonado por el tipo_cliente
    total_abonado = temporal['Créditos'].sum()#se toma la suma
    # la columna Edad es categórica y tiene la categoría de edad
    # a la que corresponden los días promedio de pago
    #se agrupan los abonos por edad de pago se suma cuanto se abonó en cada edad
    # y se divide por el total abonado para obtener un porcentaje
    resultado = temporal.groupby('Edad').sum()['Créditos']/total_abonado
    # se crea un diccionario con las edades como llaves y cero en valores
    tabla = {'Corriente':0, '1 a 30 días':0, '31 a 60 días' :0, '61 a 90 días':0, 'Mayor a 90 días':0 }
    #se itera sobre las edades en las que el cliente abonó
    for key in resultado.keys():
        #para cada edad se guarda el porcentaje abonado por el cliente
        #en el diccionario
        tabla[key]=resultado[key]
    #Se crea un data frame con la info del diccionario
    tabla = pd.DataFrame.from_dict(tabla, orient='index', columns=[' '])
    # se crea una figura
    fig = plt.figure()
    # se usa la función de mapa de calor para plotear la tabla con colores jiji
    sns.heatmap(tabla, annot = True, cmap = 'summer', fmt=".1%" ,  annot_kws={"size":18 } , cbar= False )
    #se agrga el título
    plt.title(label = titulo, fontsize=20, color = 'w',  fontweight ='bold')
    # se cambia el formato de las etiquetas
    plt.yticks(fontsize = 18 )
    plt.tight_layout()
    # se guarda la imagen en la caroeta imagenes
    plt.savefig('Imagenes/'+titulo)
    return total_abonado, dias_promedio, fig

def crear_reporte(x,df,abonos):
    """
    Extrae la información de interés de un cliente la proyecta en la interfaz
    y retorna una lista con los datos del cliente

    Inputs:
    x (str): el índice del cliente en Dataframe de clientes
    df (DataFrame): El DataFrame de los clientes
    abonos (DataFrame): El DataFrame de los abonos

    Returns:
    resumen (list): Lista con todos los datos relevantes del cliente
    """
    # La primera parte es extraer los datos del cliente del DataFrame de clientes

    # usando el índice del cliente se saca de Dataframe de clientes el nombre
    nombre = df.at[x, 'Razón social']
    # usando el índice del cliente se saca de Dataframe de clientes el código
    codigo = df.at[x, 'Código']
    # usando el índice del cliente se saca de Dataframe de clientes la facturación
    #se pone en formato de dinero
    facturacion_total = "${:,.0f}".format(df.at[x, 'Facturación total'])
    # usando el índice del cliente se saca de Dataframe de clientes la facturación promedio
    #se pone en formato de dinero
    facturacion_promedio =  "${:,.0f}".format( df.at[x, 'Facturación promedio mensual'])
    # usando el índice del cliente se saca de Dataframe de clientes la facturación del los últimos 6 meses
    #se pone en formato de dinero
    facturacion_ultimo_semestre = "${:,.0f}".format( df.at[x, 'Facturación promedio último semestre'])
    # usando el índice del cliente se saca de Dataframe de clientes la prob. de pago
    probabilidad = df.at[x, 'Probabilidad de pago oportuno']
    # usando el índice del cliente se saca de Dataframe de clientes el cupo
    # se pone en formato de dinero
    cupo =  "${:,.0f}".format(df.at[x, 'Cupo de crédito'])
    # usando el índice del cliente se saca de Dataframe de clientes si es aliado o no
    aliado = df.at[x, 'Aliado']
    # usando el índice del cliente se saca de Dataframe de clientes la antigüedad
    antiguedad =  df.at[x,'Antiguedad']
    # usando el índice del cliente se saca de Dataframe de clientes los fletes acumulados
    tot_fletes = df.at[x, 'Total acumulado fletes']
    # usando el índice del cliente se saca de Dataframe de clientes promedio en fletes mensual
    prom_fletes = df.at[x, 'Promedio hitórico fletes']
    # usando el índice del cliente se saca de Dataframe de clientes el acumulado de fletes de los últimos 6 meses
    fletes_ultimo_sem = df.at[x, 'Promedio último semestre fletes']

    # La segunda parte es ecribir esos dato en la interfaz
    # en cuatro  partes : info básica, facturación, fletes y cartera
    # el subtítulo para la interfaz
    st.markdown('## Datos básicos')
    #los datos
    st.markdown(f'** Razón social **: {nombre}')
    st.markdown(f'** Código **: {codigo}')
    st.markdown(f'** Antiguedad **: {antiguedad}')
    st.markdown(f'** Cupo de crédito **: {cupo}')
    if aliado:
        st.markdown('**Aliado**: Sí')
    else:
        st.markdown('**Aliado**: No')
    # el subtítulo para la interfaz
    st.markdown('## Facturación')
    # se verifica si el cliente ha facturado nunca
    if  facturacion_total == 0:
        # Si no ha facturado sel e avisa al usuario
        st.write(f'{nombre} no factura desde Enero de 2019')
    else:
        #de lo contrario
        # se ponen los datos de facturación en la interfaz
        st.write(f"**Facturación total **: {facturacion_total} . ")
        st.write(f"**Facturación promedio mensual **: {facturacion_promedio}. ")
        st.write(f"**Facturación promedio último semestre **: {facturacion_ultimo_semestre}. ")
    # si el cliente tiene fletes su promedio es distinto de cero
    if prom_fletes!=0:
        #se pone la info de fletes en la interfaz
        prom_fletes ="${:,.0f}".format(prom_fletes) # se pone en formato de dinero
        tot_fletes ="${:,.0f}".format(tot_fletes)# se pone en formato de dinero
        fletes_ultimo_sem="${:,.0f}".format( fletes_ultimo_sem)# se pone en formato de dinero
        st.markdown('## Fletes')
        st.markdown(f'**Total acumulado**: {tot_fletes}')
        st.markdown(f'**Promedio histórico**: {prom_fletes}')
        st.markdown(f'**Promedio último semestre**: {fletes_ultimo_sem}')

    # el subtítulo para la interfaz
    st.markdown('## Cartera')
    #se cre un boolean que verifica en el DataFame de abonos si el cliente he hecho abonos
    tiene_abonos = str(codigo) in set(abonos['Nit tercero'])
    # se crean los strings del concepto del cliente y se inician en no registra (nr)
    concepto1 = 'nr'# el primer concepto sale de los días promedio de pago
    concepto11 = 'nr'# el segundo concepto sale de la probabilidad de pago
    # si el cliente tiene abonos
    if tiene_abonos:
        #se crean dos columnas
        col1, col2 = st.columns(2)
        #se llama a la función de imprimir edades que calcula las edades históricas de pago del cliente
        # y se  guarda el total abonado, los días promedio de pago y la tabla con las edades
        tot, dias, fig1 = imprimir_edades(codigo, False, abonos)
        col1.pyplot(fig1)# se plotea la tabla en la interfaz
        #se llama a la función de imprimir edades que calcula las edades de los últimos 6 meses de pago del cliente
        # y se  guarda el total abonado, los días promedio de pago y la tabla con las edades
        a, dias2, fig2 = imprimir_edades(codigo,  True, abonos)
        # se verifivca que haya abonos en los últimos 6 meses
        if not pd.isna(dias2):
            # se plotea la tabla de edades en la interfaz
            col2.pyplot(fig2)
        else:
            # si no hay abonos en los últimos 6 meses
            #se informa al usuario
            st.info(f'El cliente no tiene abonos en los últimos seis meses')
        #Se escribe los datos de cartera obtendos enla interfaz
        st.write(f'**Días promedio de pago**:')
        # se crean dos columnas
        col1, col2 = st.columns(2)
        # se llama a la función concepto_segun_dias para obtener el concepto del cliente segun su promedio de días de pago
        concepto1 = concepto_segun_dias(dias)
        # se escribe en la interfaz el promedio y su respectivo concepto
        col1.write(f'Acumulado: {round(dias)}')
        col2.write(f'**Concepto**:{concepto1}')
        # se vuelve a verficar si hay abonos en los últimos 6 meses
        if not pd.isna(dias2):
            # si lo hay se llama a la función concepto_segun_dias
            concepto11 = concepto_segun_dias(dias2)
            # se escribe en la interfaz el promedio y su respectivo concepto
            col1.write(f'Último semestre: {round(dias2)}')
            col2.write(f'**Concepto**:{concepto11}')
        # se cambia el formato del total abonado a dinero y se escribe en la interfaz
        tot = "${:,.0f}".format(tot)
        st.write(f'**Total abonado**: {tot}.')
    # en el caso que no haya abonos
    else:
        # se notifica al usuario
        st.write('El cliente no registra abonos.')
        tot ='nr'# el total facturado se fija en no registra
        dias = 0 # los días promedio de pago se deja en 0
        dias2 = 0# los días promedio de pago  de los últimos 6 mesesse deja en 0
    # se crean dos columnas
    col1, col2 = st.columns(2)
    # se redondea la probabilidad de pago y se pone en formato de porcentaje
    p = round(probabilidad*100,1)
    concepto2 = 'nr'# se fija el concepto a no registra
    col1.markdown(f'**Probabilidad de pago oportuno**: {p}%')# se escribe la prob de pago en la interfaz
    # si la probabilidad de pago es menor a 80
    if p < 80:
        #se asigna un concepto y se escribe en la interfaz
        col2.write('**Concepto**: Revisar')
        concepto2 = 'Revisar'
    # si la probabilidad de pago es menor a 90
    elif p < 90:
        #se asigna un concepto y se escribe en la interfaz
        col2.write('**Concepto**: Bueno')
        concepto2 = 'Bueno'
    # si la probabilidad de pago es menor a 100
    elif p < 100:
        #se asigna un concepto y se escribe en la interfaz
        col2.write('**Concepto**: Muy bueno')
        concepto2 = 'Muy bueno'
    # si la probabilidad de pago es 100
    else:
        #se asigna un concepto y se escribe en la interfaz
        col2.write('**Concepto**: Excelente')
        concepto2 = 'Excelente'
    # se crea un objeto resumen con todos los datos que se extrayeron
    resumen = [ nombre, codigo, facturacion_total, facturacion_promedio, facturacion_ultimo_semestre,
                p, cupo, aliado, dias, antiguedad, tot_fletes, prom_fletes, fletes_ultimo_sem,
                tiene_abonos, tot, dias, concepto1, concepto2 , dias2, concepto11]
    # se retorna el resumen
    return resumen

def agregar_observaciones():
    """Dispone una sección en streamlit para agregar observaciones por tipo que
    luego van a ser agregadas al pdf
    Returns:
    obs (list): una lista que contiene 4 booleanos y 4 string
    Cada string corresponde a la observación de algún tipo:
    de EEFF, de multiburó, de data crédito o  general
    Si el i-ésimo booleano es False significa que el i-ésimo string está vacío"""
    # se crean las variables de strings vacíos que van a contener las observaciones
    text_obs_1 = ''
    text_obs_2 = ''
    text_obs_3 = ''
    text_obs_4 = ''
    # se crean los boleanos que dicen si hay o no un tipo de observación
    obs_1 = False
    obs_2 = False
    obs_3 = False
    obs_4 = False
    # Se crea un casilla en la interfaz para saber si el usuario
    #va a querer agregar observaciones a los estados financieros
    obs_1 = st.checkbox('EEFF')
    #Si el usuario da check en la casilla
    if obs_1:
        #Se crea un área de texto en la interfazpara que el usuario agregue observaciones
        text_obs_1 = st.text_area('Escriba aquí sus observaciones')
    # Se crea un casilla en la interfaz para saber si el usuario
    #va a querer agregar observaciones de Multiburó
    obs_2 = st.checkbox('Multiburó')
    #Si el usuario da check en la casilla
    if obs_2:
        #Se crea un área de texto en la interfaz para que el usuario agregue observaciones
        text_obs_2 = st.text_area('Escriba aquí sus observaciones ')
    # Se crea un casilla en la interfaz para saber si el usuario
    #va a querer agregar observaciones de datacrédito
    obs_3 = st.checkbox('Datacrédito')
    #Si el usuario da check en la casilla
    if obs_3:
        #Se crea un área de texto en la interfazpara que el usuario agregue observaciones
        text_obs_3 = st.text_area('Escriba aquí sus observaciones  ')
    # Se crea un casilla en la interfaz para saber si el usuario
    #va a querer agregar observaciones generales
    obs_4 = st.checkbox('Generales')
    #Si el usuario da check en la casilla
    if obs_4:
        #Se crea un área de texto en la interfazpara que el usuario agregue observaciones
        text_obs_4 = st.text_area('Escriba aquí sus observaciones   ')
    # se guarda todo en una lista para retornar
    obs = [obs_1, obs_2, obs_3,obs_4, text_obs_1, text_obs_2, text_obs_3, text_obs_4]
    return obs

def create_download_link(val,filename):
    """
    Crea un enlace para poder descargar un Documentopdf
    Inputs:
    val(b64):el archivo
    filename(str): El nombre del archivo
    """
    b64 = base64.b64encode(val)  # Se codifica el archivo
    # se retorna el link
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Descargar reporte</a>'

def escribir_observaciones(pdf, obs):
    """
    Dado un archivo pdf abierto y una lista de observaciones
    agrega una página al pdf con las respectibas observaciones
    Inputs:
    pdf(FPDF): el archivo pdf que se va a modificar
    obs(list): lista de observaciones output de la función agregar_observaciones
    """
    # se extrae uno a uno los datos de la lista de observaciones
    # los primeros 4 son booleanos que avisan si el usuario
    # quiere o no una de esas observaciones
    obs_1 = obs[0]
    obs_2 = obs[1]
    obs_3 = obs[2]
    obs_4 = obs[3]
    # Si hay al menos una observación
    if obs_1|obs_2|obs_3|obs_4:
        # se agrega una página
        pdf.add_page()
        # se esxtare los últimos cuatro objetos de la lista obs que son strings con las observaciones
        text_obs_1 = obs[4]
        text_obs_2 = obs[5]
        text_obs_3 = obs[6]
        text_obs_4 = obs[7]
        # se agrega un espacio en blanco
        pdf.cell(0, 8, ' ', ln=1)
        #Se agrega el  tíltulo a la página
        pdf.chapter_title_2('Observaciones')
        # si hay una observaión de estados financieros
        if obs_1:
            # se pone el tipo de observación que es como subtítulo
            pdf.chapter_title('EEFF:')
            # se agrega una celda al pdf con la observación
            pdf.multi_cell(0, 10, text_obs_1)
            # saltan 5 líneas
            pdf.ln(5)
        # si hay una observaión de Multiburó
        if obs_2:
            # se pone el tipo de observación que es como subtítulo
            pdf.chapter_title('Multiburó:')
            # se agrega una celda al pdf con la observación
            pdf.multi_cell(0, 10, text_obs_2)
            # saltan 5 líneas
            pdf.ln(5)
        # si hay una observaión de Datacrédito
        if obs_3:
            # se pone el tipo de observación que es como subtítulo
            pdf.chapter_title('Datacrédito:')
            # se agrega una celda al pdf con la observación
            pdf.multi_cell(0, 10, text_obs_3)
            # saltan 5 líneas
            pdf.ln(5)
        # si hay observaciones generales
        if obs_4:
            # se pone el tipo de observación que es como subtítulo
            pdf.chapter_title('Generales:')
            # se agrega una celda al pdf con la observación
            pdf.multi_cell(0, 10, text_obs_4)
            # saltan 5 líneas
            pdf.ln(5)

def ecribir_info_basica(resumen):
    """
    Dada la información de un cliente escribe crea un archivo pdf y agrega
    esta información en el archivo

    Inputs:
    resumen(list): lista que devuelve la función crear_reporte
    con todos los datos de un cliente

    Returns:
    pdf(FPDF): Archivo pdf con la información de un cliente
    codigo(str): el código del cliente
    """
    # En primer lugar se extraen los datos uno a uno  de la lista de resumen
    nombre = resumen[0]
    codigo = resumen[1]
    facturacion_total = resumen[2]
    facturacion_promedio = resumen[3]
    facturacion_ultimo_semestre = resumen[4]
    probabilidad = resumen[5]
    cupo = resumen[6]
    aliado = resumen[7]
    dias = resumen[8]
    antiguedad = resumen[9]
    tot_fletes = resumen[10]
    prom_fletes = resumen[11]
    fletes_ultimo_sem = resumen[12]
    tiene_abonos = resumen[13]
    tot = resumen[14]
    dias = resumen[15]
    concepto_prob_pago = resumen[16]
    concepto_dias = resumen[17]
    dias_s = resumen[18]
    concepto_dias2 = resumen[19]
    #diccionario que convierte un booleano en lenguaje natural
    trad = { True: 'Sí', False: 'No'}
    # Se crea el pdf
    pdf = PDF1('P', 'mm', 'Letter')
    # se activa el salto de página automático
    pdf.set_auto_page_break(auto = True, margin = 11)
    # se fija las fuentes
    pdf.set_font('helvetica', '', 16)
    # ae agrega la primera págna al pdf
    pdf.add_page()
    #Se pone el título a la página
    pdf.chapter_title_2('Análisis de cumplimiento')
    # se pone el subtítulo
    pdf.chapter_title('Datos básicos')
    # se escribe a info del cliente
    pdf.cell(80, 10, f'Razón social:')
    pdf.multi_cell(100, 10, f'{nombre}')
    pdf.cell(80, 10, f'Código:')
    pdf.cell(100, 10, f'{codigo}', ln=1)
    pdf.cell(80, 10, f'Antigüedad:')
    pdf.cell(100, 10, f'{antiguedad}', ln=1)
    pdf.cell(80, 10, f'Cupo de crédito')
    pdf.cell(100, 10, f'{cupo}', ln=1)
    pdf.cell(80, 10, f'Aliado:')
    pdf.cell(100, 10, trad[aliado], ln=1)
    pdf.cell(0, 5, ' ', ln=1)
    # se agrega subtítulo para la facturación
    pdf.chapter_title('Facturación')
    # se verifica si el cliente ha facturado algo
    if  facturacion_total == 0:
        # Si no ha facturado se anota en el documento
        pdf.cell(0, 10, f'{nombre} no factura desde Enero de 2019', ln=1)
    # si sí ha facturado
    else:
        # se agregan los datos de facturación al pdf
        pdf.cell(80, 10, 'Facturación total:')
        pdf.cell(100, 10, f'{facturacion_total}', ln=1)
        pdf.cell(80, 10, "Facturación promedio mensual:")
        pdf.cell(100, 10, f'{facturacion_promedio}', ln=1)
        pdf.cell(80, 10, "Facturación promedio último semestre:")
        pdf.cell(100, 10, f'{facturacion_ultimo_semestre}', ln=1)
    # se verifica si el cliente tiene fletes
    if tot_fletes !=0:
        # si sí tiene fletes
        pdf.cell(0, 5, ' ', ln=1) # salto de línea
        pdf.chapter_title('Fletes') #subtitulo
        # se agregan los datos de fletes al pdf
        pdf.cell(80, 10, 'Total acumulado:')
        pdf.cell(100, 10, f'{tot_fletes}', ln=1)
        pdf.cell(80, 10, 'Promedio histórico:')
        pdf.cell(100, 10, f'{prom_fletes}', ln=1)
        pdf.cell(80, 10, 'Promedio último semestre:')
        pdf.cell(100, 10, f'{fletes_ultimo_sem}', ln=1)
    pdf.cell(0, 5, ' ', ln=1)#salto de linea
    # se agrega subtitulo para los datos de cartera
    pdf.chapter_title('Cartera')
    #Se escriben los datos de cartera
    pdf.cell(80, 10, f'Probabilidad de pago oportuno:')
    pdf.cell(20, 10, f'{probabilidad} %')
    pdf.cell(70, 10, f'{concepto_prob_pago} ', ln=1, align= 'R')
    # se verifica si el cliente tiene abonos
    if tiene_abonos:
        # si sí tiene e agregan los datos de abonos al documento
        pdf.cell(80, 10, f'Total abonado:')
        pdf.cell(100, 10, f'{tot}', ln=1)
        pdf.cell(80, 10, f"Días promedio pago")
        pdf.cell(20, 10, f"{round(dias)}" )
        pdf.cell(70, 10, f'{concepto_dias}', ln=1, align= 'R')
        pdf.cell(80, 10, f"Días promedio pago último semestre:")
        # se verifica si el cliente tiene pagos en el último semestre
        if concepto_dias2 != 'nr':
            # si sí tiene se agregan al documento
            pdf.cell(20, 10, f"{round(dias_s)}" )
            pdf.cell(70, 10, f'{concepto_dias2}', ln=1, align= 'R')
        else:
            # si no se anota en el documento que el cliento no tiene abonos en el último semestre
            pdf.cell(20, 10, 'No hay pagos en el último semestre.', ln = 1 )
        # se agrega un página
        pdf.add_page()
        # se agrega el título de la página
        pdf.chapter_title_2('Cumplimiento de pago por edades')
        pdf.cell(0, 110, ' ', ln=1)# salto de línea
        # se agrega la tabla de pagos por edades histórico
        pdf.image('Imagenes/Histórico.png',x= 17, y = 65,  w = (pdf.w /2)-20 )
        #se verifica si tiene pagos en el último semestre
        if concepto_dias2 != 'nr':
            # si sí tiene se agrega la tabla de pagos por edades de los últimos 6 meses
            pdf.image('Imagenes/Último semestre.png' ,x= 105, y = 65 ,  w = (pdf.w /2)-20)
    #Si no tiene abonos
    else:
        # se anota en el pdf que no hay abonos
        pdf.cell(0, 10, f'{nombre} no tiene abonos.', ln=1)
    #se retorna el pdf y el código del cliente
    return pdf, codigo

def escribir_eeff(pdf):
    """
    Agrega los índices financieros calculados a partir de estados financieros al
    pdf que le etra como parámetro

    Inputs:
    pdf(FPDF): Archivo pdf con la información de un cliente
    """
    # se agrega una página al pdf
    pdf.add_page()
    # se pone el título de la sección
    pdf.chapter_title_2(f'Indicadores financieros en {st.session_state.indices_2019[21]} ')
    # se fija la fuente a blod
    pdf.set_font('helvetica', 'B', 11)
    #salto de línea
    pdf.cell(80, 10, '')
    # se extrae el periodo 1 de EEFF de la lista st.session_state.indices_2020
    pdf.cell(40, 10, str(st.session_state.indices_2020[0]))
    # se extrae el periodo 1 de EEFF de la lista st.session_state.indices_2020
    pdf.cell(20, 10, str(st.session_state.indices_2019[0]), ln=1)
    #lista con los nombres de los índices financieros en el orden en que quedaron guardados
    indices = ['Razón Corriente', 'Razón ácida', 'Rotación Act. Ctes.',
    'Rotación de CXC','Rotación Inventarios', 'Rotación CXP',
    'Rentabilidad Op./Activo','Costo de la Deuda (KD)',
    'Rentabilidad Neta/ Patrimonio', 'Indice de Endeudamiento',
    'Indice Patrimonial', 'Cobertura de Intereses', 'Margen Operacional',
    'Margen Antes de Impto.','Margen Neto', 'Margen Bruto', 'Retorno S/Patrimonio',
    'Retorno S/Activo', 'Capital de Trab. Neto Op.', 'Capital de Trab. Neto']
    # se agrega un subtitulo para el primer tipo de índices
    pdf.chapter_title('Indices de liquidez')
    #se quita la fuente bold
    pdf.set_font('helvetica', '', 11)
    #se itera sobre un array de número del 1 al 21 para escribir los 21 índices
    for i in range(1, 21):
        # el idicador del nombre de los índices financieros inicia en 0 por eso se toma el i-1
        pdf.cell(65, 9, indices[i-1])
        # se extrae el índice financiero del periodo 1
        pdf.cell(50, 9, str(st.session_state.indices_2020[i]))
        # se extrae el índice financiero del periodo 2
        pdf.cell(20, 9, str(st.session_state.indices_2019[i]), ln =1)
        #a partir del índice financiero 5 empiezan otro tipo de índices
        if i  == 5 :
            # se agrega un subtitulo para el segundo tipo de índices
            pdf.chapter_title('Indices de Rentabilidad')
        #a partir del índice financiero 8 empiezan otro tipo de índices
        if i == 8 :
            # se agrega un subtitulo para el tercer tipo de índices
            pdf.chapter_title('Analisis de Enduedamiento')
    # se fija la fuente a blod
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(80, 9,'Cupo sugerido:')
    # se verifica si el cupo sugerido está en unidades
    if st.session_state.indices_2019[21] == 'Unidades':
        # se agrega el cupo sugerido al pdf
        pdf.cell(40, 9,str(st.session_state.indices_2020[21]) + 'COP')
    else :
        # se agrega el cupo sugerido al pdf con las respectivas unidades (miles o millones)
        pdf.cell(40, 9,str(st.session_state.indices_2020[21]) + ' '+ st.session_state.indices_2019[21] + ' de COP')

def escribri_camycom(camycom, pdf):
    """
    Agrega los datos extraídos del certificado de cámara de comercio que le
    entran como parámetro al pdf que le entra como parámetro

    Inputs:
    camycom (list): Lista con todos los datos extraídos del camara de comercio
     con el formato del objeto que retorna la función CYC
    pdf(FPDF): Archivo pdf con la información de un cliente
    """
    # se agrega una página
    pdf.add_page()
    # se agrega el título de la sección
    pdf.chapter_title_2('Datos cámara y comercio')
    # lista con los nombres de los datos del certificado de cámara y comercio
    index_camycom = ['Fecha de emisión:','Razón Social:','NIT:',
    'Fecha de matrícula:','Fecha renovación:','Capital pagado:','Objeto Social:',
    'Representante legal', 'Facultades del representante legal:','Embargos:',
    'Procesos:' ]
    # se itera sobre un array del 0 al 11 para recorrer el objeto camycom
    for i in range(11):
        # se fija la fuente a bold
        pdf.set_font('helvetica', 'B', 12)
        # Se escribe el nombre del dato
        pdf.multi_cell(80, 9, index_camycom[i])
        # se quita el bold de la fuente
        pdf.set_font('helvetica','', 12)
        # se escribe el dato del certifiado
        pdf.multi_cell(0, 9, str(camycom[i]).strip())
    # se verifica si hay alguna observación
    if camycom[11]:
        #salto de línea
        pdf.cell(0, 8, ' ', ln=1)
        #se agrega el subtitulo de la parte de observaciones
        pdf.chapter_title_2('Observaciones')
        #se quita el bold de la fuente
        pdf.set_font('helvetica','', 12)
        # se escribe la observación en el pdf
        pdf.multi_cell(0, 10, camycom[12])

def escribir_info_basica_cliente_nuevo(nombre, nit, dpto, tipo_cliente, plazo, aliado, cupo, antiguedad):
    """
    Crea un archivo pdf con los datos del cliente nuevo que entran como parámetro.

    Inputs:
    nombre(str): el nombre del clienteo razón social
    nit(str): el Número de Identidad tributaria o documento del cliente
    dpto(str): El departamento donde se encuentra ubicado el cliente
    tipo_cliente(str): el tipo de producto que el cliente quiere pedir en crédito
    plazo(str): el plazo en días que solicitó el cliente para pagar el crédito
    aliado(boolean): True si es aliado de Gasco y False de lo contrario
    cupo(float): El cupo en COP del crédito
    antiguedad(int): Número de años en los que lleva siendo cliente de Gasco

    Returns:
    pdf(FPDF): El archivo con los datos escritos
    nit(str): El documento de identidad del cliente
    """
    # diccionario que extrae el
    fyv = {1:'Sí', 0: 'No'}
    #crear el pdf
    pdf = PDF2('P', 'mm', 'Letter')
    # se agrega una página
    pdf.add_page()
    # se fija la fuente
    pdf.set_font('Helvetica','',  16)
    # se agrega el título de la página
    pdf.chapter_title_2('Predicción de pago')
    # salto de línea
    pdf.ln(10)
    # se agrega subtitulo de la parte 1
    pdf.chapter_title('Datos del cliente')
    # se escribe la información
    pdf.multi_cell(0, 10, f'Nombre o Razón social: {nombre}')
    pdf.cell(0, 10, f'Documento o NIT: {nit}', ln=1 )
    pdf.cell(0, 10, f'Departamento: {dpto}', ln=1 )
    pdf.cell(0, 10, f'Tipo de cliente: {tipo_cliente}', ln=1 )
    pdf.cell(0, 10, f'Aliado: {fyv[aliado]}', ln=1 )
    pdf.cell(0, 10, f'Cupo de crédito solicitado: {cupo}', ln=1 )
    pdf.cell(0, 10, f'Antigüedad: {antiguedad}', ln=1 )
    # se llama al objeto st.session_state.prediccion para obtener la probabilidad
    pdf.cell(0, 10, f"Probabilidad de pago oportuno: {st.session_state.prediccion}", ln=1 )
    p = st.session_state.prediccion
    # si la propbabilidad de pago es menor a 80
    if p < 80:
        # se le asigna el concepto
        concepto2 = 'Revisar'
    # si la propbabilidad de pago es menor a 90
    elif p < 90:
        # se le asigna el concepto
        concepto2 = 'Bueno'
    # si la propbabilidad de pago es menor a 100
    elif p < 100:
        # se le asigna el concepto
        concepto2 = 'Muy bueno'
    # si la propbabilidad de pago es 100
    else:
        # se le asigna el concepto
        concepto2 = 'Excelente'

    # se ecribe el concepto
    pdf.cell(0, 10, f'Concepto de cliente: {concepto2 }', align ='C', ln = 1)
    # se pega la igaen donde dice endonde está ubicado e cliente frente a la
    #población de clientes oportunos e inoportunos
    pdf.image('Imagenes/modelo.png',  w = pdf.w - 60 )
    return pdf, nit

def crear_pdf_anal(resumen, obs):
    """
    Dado el resumen de la información de un cliente de Gasco y la lista
    de observaciones para ese cliente crea el pdf con esta info y un link para
    descargar el pdf.

    Inputs:
    resumen(list): lista que devuelve la función crear_reporte
    con todos los datos de un cliente
    obs(list): lista de observaciones output de la función agregar_observaciones
    """
    # se llama a la función que se encarga de escribir el pdf
    # se guardan el pdf y el codigo del cliente
    pdf, codigo = ecribir_info_basica(resumen)
    # se llama a la funcion que crea el link de descarga con el pdf
    # el primer argumento es el archivo  pdf codificado
    # el segundo argumento el nombre del archivo
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), f"Reporte cliente {codigo}")
    # se pone a disposición el link en la interfaz
    st.markdown(html, unsafe_allow_html=True)

def crear_pdf_reevaluacion(resumen,obs,camycom, incluir_ef):
    """
    Dado el resumen de la información de un cliente de Gasco, la lista
    de observaciones para ese cliente y los datos de camara y comercio,
    crea el pdf con esta info y los índices financieros si el usuario aceptó
    incluirlos y un link para descargar el pdf.

    Inputs:
    resumen(list): lista que devuelve la función crear_reportecon todos los
    datos de un cliente
    obs(list): lista de observaciones output de la función agregar_observaciones
    camycom(list): Lista con todos los datos extraídos del camara de comercio
    con el formato del objeto que retorna la función CYC
    incluir_ef(boolean): True si el usuario quiere inluir los índices
    financieros de cliente y False de lo contrario.
    """
    # se llama a la función que se encarga de escribir el pdf
    # se guardan el pdf y el codigo del cliente
    pdf, codigo = ecribir_info_basica(resumen)
    # si el usuario quiere incluir índices financieros
    if incluir_ef:
        # se llama a la función que se encarga de escribir los índices en el pdf
        escribir_eeff(pdf)
    # se llama a la función que se encarga de escribir las observaciones
    escribir_observaciones(pdf, obs)
    #Si la lista con los datos del certificado de camara y comercio no está vacía
    if camycom != []:
        # Se llama a la función que se encarga de escribir el caamra de comercio
        escribri_camycom(camycom, pdf)
    # se llama a la funcion que crea el link de descarga con el pdf
    # el primer argumento es el archivo  pdf codificado         # el segundo argumento el nombre del archivo
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), f"Reporte cliente {codigo}")
    # se pone a disposición el link en la interfaz
    st.markdown(html, unsafe_allow_html=True)

def crear_pdf_asignacion(nombre,nit, depto, tipo_cliente, plazo, aliado, cupo, antiguedad, obs, camycom, incluir_ef):
    """
    Dado los datos del cliente nuevo que entran como parámetro, la lista
    de observaciones para ese cliente y los datos de cámara y comercio,
    crea un pdf con esta info y los índices financieros si el usuario aceptó
    incluirlos y un link para descargar el pdf.

    Inputs:
    nombre(str): el nombre del clienteo razón social
    nit(str): el Número de Identidad tributaria o documento del cliente
    dpto(str): El departamento donde se encuentra ubicado el cliente
    tipo_cliente(str): el tipo de producto que el cliente quiere pedir en crédito
    plazo(str): el plazo en días que solicitó el cliente para pagar el crédito
    aliado(boolean): True si es aliado de Gasco y False de lo contrario
    cupo(float): El cupo en COP del crédito
    antiguedad(int): Número de años en los que lleva siendo cliente de Gasco
    obs(list): lista de observaciones output de la función agregar_observaciones
    camycom(list): Lista con todos los datos extraídos del camara de comercio
    con el formato del objeto que retorna la función CYC
    incluir_ef(boolean): True si el usuario quiere inluir los índices
    financieros de cliente y False de lo contrario.
    """
    # se llama a la función que se encarga de escribir el pdf de un cliente nuevo
    # se guardan el pdf y el codigo/documento del cliente
    pdf, codigo = escribir_info_basica_cliente_nuevo(nombre, nit, depto, tipo_cliente, plazo, aliado, cupo, antiguedad)
    # si el usuario quiere incluir índices financieros
    if incluir_ef:
        # se llama a la función que se encarga de escribir los índices en el pdf
        escribir_eeff(pdf)
    # se llama a la función que se encarga de escribir las observaciones
    escribir_observaciones(pdf, obs)
    #Si la lista con los datos del certificado de camara y comercio no está vacía
    if camycom != []:
        # Se llama a la función que se encarga de escribir el caamra de comercio
        escribri_camycom(camycom, pdf)
    # se llama a la funcion que crea el link de descarga con el pdf
    # el primer argumento es el archivo  pdf codificado         # el segundo argumento el nombre del archivo
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), f"Reporte cliente nuevo {codigo}")
    # se pone a disposición el link en la interfaz
    st.markdown(html, unsafe_allow_html=True)
