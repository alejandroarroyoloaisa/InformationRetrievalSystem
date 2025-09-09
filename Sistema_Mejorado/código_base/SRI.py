import re
import os
import json
import time
import math

from nltk.stem.snowball import SnowballStemmer
from collections import Counter
from rank_bm25 import BM25Okapi

coleccion = {}
indice = {}

# Función que dado el nombre del fichero, extrae de él el contenido requerido de toda la información contenida.
#   devuelve un diccionario con el nombre del fichero como clave y los tokens como valor. Además, realiza la normalización de los tokens
def extract_Transform(nombre_fichero):

    with open(nombre_fichero, 'r', encoding='utf-8') as file:
        for linea in file:
            informacion = linea.split("\t")
            nombre = informacion[0]
            contenido = informacion[1]
            contenido = contenido.lower()
            contenido = re.sub(r'[^a-záéíóúñ_\n0-9 -]', '', contenido)
            coleccion[nombre] = contenido.split()
    return coleccion


# Función que carga el listado de stopwords y lo devuelve
def cargar_stopwords(nombre_fichero):
    with open(nombre_fichero, 'r', encoding='iso-8859-1') as file:
        stopwords = file.readlines()

    stopwords_aux = list()
    for stopword in stopwords:
        stopwords_aux.append(stopword.rstrip())
    return stopwords_aux

# Función Stopper, borra del fichero indicado las palabras que se encuentren en la lista de stopwords
def stopper_coleccion(stopwords, nombre_fichero, coleccion):

    datos = coleccion[nombre_fichero]
    datos_filtrados = list()
    for palabra in datos:
        if palabra not in stopwords:
            datos_filtrados.append(palabra)

    return datos_filtrados

# Función Stemmer, para cada palabra de cada documento, realiza la extracción de raices
def stemmer_coleccion(stemmer, nombre_fichero, coleccion):

    datos = coleccion[nombre_fichero]
    datos_filtrados = []
    for palabra in datos:
        palabra = stemmer.stem(palabra)
        datos_filtrados.append(palabra)

    return datos_filtrados

# Función para crear/actualizar el indice invertido. Para el fichero indicado:
#       -mira si cada palabra está o no ya en el indice
#       -si está, añade (si no está) el documento en el que apareció
#       -actualiza para el documento en el que apareció el número de repeticiones
# ESTÁ INDEXADO COMO EN UNA TABLA HASH, POR CLAVES
def crear_indice_invertido(nombre_fichero, indice, coleccion):

    datos = coleccion[nombre_fichero]

    for palabra in datos:
        if palabra not in indice:
            indice[palabra]={}
        if nombre_fichero not in indice[palabra]:
            indice[palabra][nombre_fichero] = {
                "reps":0
            }

        indice[palabra][nombre_fichero]["reps"] += 1

    return indice


# Función que en el INDICE INVERTIDO, calcula el TF IDF de cada palabra en cada documento y almacena el IDF de cada palabra y sus respectivos TF.IDF
def calcular_pesos(indice, num_ficheros_coleccion):
    
    frec_max = {}

    for palabra in indice:
        for nombre_fichero in indice[palabra]:

            if nombre_fichero not in frec_max:
                frec_max[nombre_fichero] = indice[palabra][nombre_fichero]["reps"]
            
            else:
                if frec_max[nombre_fichero] < indice[palabra][nombre_fichero]["reps"]:
                    frec_max[nombre_fichero] = indice[palabra][nombre_fichero]["reps"]
    
    
        num_ficheros_aparicion = len(indice[palabra])
        idf = math.log2(num_ficheros_coleccion / num_ficheros_aparicion)

        for nombre_fichero in indice[palabra]:
                
                indice[palabra][nombre_fichero]["reps"] = (indice[palabra][nombre_fichero]["reps"] / frec_max[nombre_fichero] )* idf
    
        indice[palabra] = { "idf": idf, "ficheros": indice[palabra]}
    
        vector = [indice[palabra]["ficheros"][nombre_fichero]["reps"] for nombre_fichero in indice[palabra]["ficheros"]]
        modulo = math.sqrt(sum(value**2 for value in vector))

        for nombre_fichero in indice[palabra]["ficheros"]:
            indice[palabra]["ficheros"][nombre_fichero]["reps"] = indice[palabra]["ficheros"][nombre_fichero]["reps"] / modulo

    return indice

# Función que carga el diccionario de sinonimos y lo devuelve
def cargar_diccionario_sinonimos(dir_dic_sinonimos):

    with open(dir_dic_sinonimos, 'r', encoding='utf-8') as file:
        dic_sin = json.load(file)
    return dic_sin

# Función que dado un texto:
#   -lo pone en minúsculas
#   -sustituye los caracteres que no estén en el conjunto [^a-záéíóú_\n0-9 -] por '' (espacio en blanco)
#   -corta el texto ya transformado en tokens individuales
def transform_consulta(texto):

    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñ_\n0-9 -]', '', texto)
    tokens = texto.split()

    return tokens

# Función Stopper de consultas, borra de la consulta indicada las palabras que se encuentren en la lista de stopwords
def stopper_consulta(stopwords, consulta):
    datos_filtrados = list()

    for palabra in consulta:
        if palabra not in stopwords:
            datos_filtrados.append(palabra)
    
    return datos_filtrados

# Función Stemmer de consultas, para cada palabra de la consulta, realiza la extracción de raices
def stemmer_consulta(consulta):

    stemmer = SnowballStemmer(language='spanish')

    datos_filtrados = []

    for palabra in consulta:
        palabra = stemmer.stem(palabra)
        datos_filtrados.append(palabra)

    return datos_filtrados


# Función que dada una consulta, y un diccionario de sinónimos, añade los sinónimos de las palabras de la consulta a esta (5 como máximo por palabra)
def agregar_sinonimos(consulta, dic_sinonimos):

    # MEJORA 2: EXPANSIÓN CONSULTA (SINÓNIMOS)
    sinonimos = []
    for palabra in consulta:
        if palabra in dic_sinonimos:
            sinonimos.extend(dic_sinonimos[palabra][:5])
    consulta.extend(sinonimos)
    return consulta
    # FIN MEJORA 2


# Función que dada una consulta, un índice invertido y un número de documentos relevantes, devuelve los documentos más relevantes para la consulta
def encontrar_similitud(consulta, indice, num_doc_relevantes):
        # CALCULO LA FRECUENCIA DE LAS PALABRAS DE LA CONSULTA EN LA CONSULTA
        consulta_frecuencia = {}
        frec_max = -99999
        for palabra in consulta:
            if palabra in indice:
                if palabra in consulta_frecuencia:
                    consulta_frecuencia[palabra] += 1
                else:
                    consulta_frecuencia[palabra] = 1

                if consulta_frecuencia[palabra] > frec_max:
                    frec_max = consulta_frecuencia[palabra]
        
        # DIVIDO CADA FRECUENCIA ENTRE LA MÁXIMA Y MULTIPLICO POR EL IDF (TF*IDF)
        for frecuencia in consulta_frecuencia:
            consulta_frecuencia[frecuencia] = consulta_frecuencia[frecuencia] / frec_max
            consulta_frecuencia[frecuencia] = consulta_frecuencia[frecuencia] * indice[frecuencia]['idf']

        # CALCULO EL MÓDULO DE LA CONSULTA
        modulo = math.sqrt(sum(f**2 for f in consulta_frecuencia.values()))

        # DIVIDO CADA PALABRA ENTRE EL MÓDULO DE LA CONSULTA
        for palabra in consulta_frecuencia:
            consulta_frecuencia[palabra] /= modulo

        # CALCULO LA SIMILITUD DE CADA DOCUMENTO CON LA CONSULTA
        doc_similitud = {}
        for palabra, frecuencia in consulta_frecuencia.items():
            if palabra in indice:
                for doc, doc_info in indice[palabra]['ficheros'].items():
                    doc_frecuencia = doc_info['reps']
                    if doc in doc_similitud:
                        doc_similitud[doc] += frecuencia * doc_frecuencia
                    else:
                        doc_similitud[doc] = frecuencia * doc_frecuencia
        
        return sorted(doc_similitud.items(), key=lambda x: x[1], reverse=True)[:num_doc_relevantes]

# Función que dada una consulta, el índice invertido, el número de documentos relevantes, la colección y la longitud media de los documentos,
#   devuelve los documentos más relevantes para la consulta.
def encontrar_similitud_bm25(consulta, indice, num_doc_relevantes, coleccion, avgdl):
    k = 2
    b = 0.75

    doc_similitud = {}
    N = len(coleccion)  # Número total de documentos
    for palabra in consulta:
        if palabra in indice:
            n_qi = len(indice[palabra]['ficheros'])  # Número de documentos que contienen la palabra
            idf = math.log((N - n_qi + 0.5) / (n_qi + 0.5))
            frecuencia = 0
            for doc in indice[palabra]['ficheros'].items():
                
                for word in coleccion[doc]:
                    if word == palabra:
                        frecuencia += 1
                
                tf = (frecuencia / len(coleccion[doc]))
                dl = len(coleccion[doc])

                # Fórmula BM25
                bm25 = idf * ((tf * (k + 1)) / (tf + k * (1 - b + b * (dl / avgdl))))

                if doc in doc_similitud:
                    doc_similitud[doc] += bm25
                else:
                    doc_similitud[doc] = bm25

    # Devuelvo un array con los num_doc_relevantes documentos más relevantes, ordenados de mejor a peor
    return sorted(doc_similitud.items(), key=lambda x: x[1], reverse=True)[:num_doc_relevantes]

# Función que dado el índice, el array de documentos similares, la consulta el número de documentos relevantes y la colección,
#   añade a la consulta las palabras más relevantes de los documentos similares.
#   -> se añaden las palabras con mejor TF.IDF que no estén ya en la consulta
def pseudoalimentacionPorRelevancia(indice, doc_similitud, consulta, num_doc_relevantes, coleccion):
    N = len(coleccion)

    for doc in doc_similitud:
        data = coleccion[doc[0]]
        counter = Counter(data)
        tf_idf = {}
        for palabra, count in counter.items():
            tf = count
            n_qi = len(indice[palabra]['ficheros'])
            idf = math.log((N - n_qi + 0.5) / (n_qi + 0.5))
            tf_idf[palabra] = tf * idf
        for palabra in sorted(tf_idf.items(), key=lambda x: x[1], reverse=True)[:num_doc_relevantes]:
            if palabra[0] not in consulta:
                consulta.append(palabra[0])
    return consulta

# Función que procesa la colección de documentos, aplicando las funciones de Extracción, Normalización y Tokenización,
#   STOPPER y STEMMER, creación del índice invertido del corpus de documentos y el cálculo de los pesos de la colección
def procesar_coleccion(indice, coleccion):

    print("###### |LEYENDO Y PROCESANDO COLECCIÓN| ######")
    hora_inicio = time.time()

    for nombre_fichero in os.listdir('./data'):
            if nombre_fichero.endswith('.tsv'):
                coleccion = extract_Transform(os.path.join('data', nombre_fichero))

    hora_fin = time.time()
    print(f'Tiempo requerido: {hora_fin-hora_inicio} segundos')

    ########################################################################

    print("###### |APLICANDO STOPPER| ######")
    hora_inicio = time.time()

    stopwords = cargar_stopwords('stopwords.txt')
    for nombre_fichero in coleccion:
        coleccion[nombre_fichero] = stopper_coleccion(stopwords, nombre_fichero, coleccion)

    hora_fin = time.time()
    print(f'Tiempo requerido: {hora_fin-hora_inicio} segundos')

    ########################################################################

    print("###### |APLICANDO STEMMER| ######")
    hora_inicio = time.time()

    stemmer_obj = SnowballStemmer(language='spanish')
    for nombre_fichero in coleccion:
        coleccion[nombre_fichero] = stemmer_coleccion(stemmer_obj, nombre_fichero, coleccion)

    hora_fin = time.time()
    print(f'Tiempo requerido: {hora_fin-hora_inicio} segundos')

    ########################################################################

    print("###### |CREANDO ÍNDICE INVERTIDO| ######")
    hora_inicio = time.time()

    for nombre_fichero in coleccion:
        indice = crear_indice_invertido(nombre_fichero, indice, coleccion)

    #Guardar y ordenar el índice (para cada palabra, orden descendente de documentos en los que aparece, ordenados por número de apariciones)
    for palabra in indice:
        indice[palabra] = dict(sorted(indice[palabra].items(), key=lambda item: item[1]['reps'], reverse=True))

    hora_fin = time.time()
    print(f'Tiempo requerido: {hora_fin-hora_inicio} segundos')
    
    ########################################################################

    print("###### |CALCULANDO PESOS DE LA COLECCIÓN| ######")
    hora_inicio = time.time()

    indice = calcular_pesos(indice, len(coleccion))

    hora_fin = time.time()
    print(f'Tiempo requerido: {hora_fin-hora_inicio} segundos')

    return indice, coleccion


# Función que procesa las consultas, aplicando las funciones de ETL, STOPPER y STEMMER, y devuelve las consultas procesadas.
#   Además, aplica las mejoras 1 (EXPANSIÓN DE CONSULTA CON SINÓNIMOS) y 2 (PSEUDO-REALIMENTACIÓN POR RELEVANCIA)
def procesar_consultas(indice, coleccion):

    print("###### |PROCESANDO CONSULTAS| ######")
    hora_inicio = time.time()

    dir_consultas = 'consultas/queries.txt'
    num_doc_relevantes = 10

    with open(dir_consultas, 'r', encoding='utf-8') as file:
        consultas = file.readlines()

    stopwords = cargar_stopwords('stopwords.txt')
    dic_sinonimos = cargar_diccionario_sinonimos('diccionario_sinonimos.json')

    avgdl = sum(len(coleccion[doc]) for doc in coleccion) / len(coleccion)
    consultas_procesadas = {}
    # PARA CADA CONSULTA
    for consulta in consultas:

        # PROCESAMOS LAS CONSULTAS, IGUAL QUE LOS DOCUMENTOS
        consulta = transform_consulta(consulta)
        consulta = stopper_consulta(stopwords, consulta)
        # MEJORA 2: EXPANSIÓN CONSULTA (SINÓNIMOS)
        consulta = agregar_sinonimos(consulta, dic_sinonimos) 
        #FIN MEJORA 2
        consulta = stemmer_consulta(consulta)
        doc_similitud = encontrar_similitud_bm25(consulta, indice, num_doc_relevantes, coleccion, avgdl)
        #MEJORA 1: PSEUDOALIMENTACIÓN POR RELEVANCIA
        consulta = pseudoalimentacionPorRelevancia(indice, doc_similitud, consulta, num_doc_relevantes, coleccion)
        #FIN MEJORA 1

        consulta_str = ' '.join(consulta)
        consultas_procesadas[consulta_str] = consulta

    hora_fin = time.time()
    tiempo_total = hora_fin - hora_inicio
    print(f'Tiempo de ejecución total: {tiempo_total} segundos')
    return consultas_procesadas


# Función principal.
#   -Calcula el tiempo de ejecución
#   -Procesa la colección y la devuelve
#   -Procesa las consultas y las devuelve
#   -Crea un modelo BM25Okapi con la colección
#   -Para cada consulta, calcula los scores de los documentos de la colección y los guarda en un fichero.
#       usando para ello el objeto bm25 creado anteriormente
def main():


    hora_inicio = time.time()
    
    coleccion = {}
    indice = {}
    indice, coleccion = procesar_coleccion(indice, coleccion)
    consultas = procesar_consultas(indice, coleccion)


    corpus = list(coleccion.values())
    consultas_procesadas = list(consultas.values())
    bm25 = BM25Okapi(corpus)

    doc_scores = {}
    texto=""
    nombre_documento = {str(v): k for k, v in coleccion.items()}   #<- Crear un diccionario inverso

    print("###### |BUSCANDO SIMILITUD CON LAS CONSULTAS| ######")    
    for i, consulta in enumerate(consultas_procesadas):
        consulta_str = ' '.join(consulta)
        doc_scores[consulta_str] = bm25.get_scores(consulta)
        mejores_documentos = bm25.get_top_n(consulta, corpus, n=10)
        
        # Obtener los nombres de los mejores documentos en el diccionario inverso (ya que solo tenemos el contenido de los documentos, no sus nombres)
        nombres_mejores_documentos = [nombre_documento[str(doc)] for doc in mejores_documentos]

        texto += str(i) + ","
        for doc in nombres_mejores_documentos:
            texto += doc + " "
        texto += "\n"
        i+=1

    print("###### |GUARDANDO RESULTADOS| ######")
    with open('resultados.csv', 'w', newline='') as file:
        file.write(texto)
        
    hora_fin = time.time()

    tiempo_total = hora_fin - hora_inicio
    print(f'\n\n->TIEMPO DE EJECUCIÓN TOTAL DEL SRI: {tiempo_total} segundos')

if __name__ == "__main__":

    main()
