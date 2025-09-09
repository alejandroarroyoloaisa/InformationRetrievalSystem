import os
import json
import time
import sys
import math
import re

from nltk.stem.snowball import SnowballStemmer

#Función que dadas unas estadisticas de ejecucion, crea un fichero .txt en el directorio base y las almacena
def guardar_Estadisticas(modulo_algoritmo, tiempo_total, doc_similitud):
    stats = modulo_algoritmo + '\nTiempo de ejecución total: ' + str(tiempo_total) + ' segundos.\nPalabras totales indexadas: ' + str(numero_palabras) + ' palabras.\nTamaño en memoria del índice: ' + str(size) + ' bytes.'
    with open(os.path.join('.', 'stats' + modulo_algoritmo + '.txt'), 'w') as file:
        file.write(stats)

#Función que dado un texto:
#   -lo pone en minúsculas
#   -sustituye los caracteres que no estén en el conjunto [^a-záéíóú_\n0-9 -] por '' (espacio en blanco)
#   -corta el texto ya transformado en tokens individuales
def transform(texto):

    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñ_\n0-9 -]', '', texto)
    tokens = texto.split()

    return tokens

#Función que carga el listado de stopwords y lo devuelve (además elimina el salto de línea de cada palabra)
def cargar_stopwords(nombre_fichero):
    with open(nombre_fichero, 'r', encoding='iso-8859-1') as file:
        stopwords = file.readlines()

    stopwords_aux = list()
    for stopword in stopwords:
        stopwords_aux.append(stopword.rstrip())
    return stopwords_aux

#Función Stopper, borra del fichero indicado las palabras que se encuentren en la lista de stopwords (y actualiza el conteo de palabras para estadísticas)
def stopper(stopwords, consulta):
    datos_filtrados = list()

    for palabra in consulta:
        if palabra not in stopwords:
            datos_filtrados.append(palabra)
    
    return datos_filtrados

#Función Stemmer, para cada fichero del directorio indicado, lo abre y de cada palabra, realiza la extracción de raices (además de contar las palabras totales y las palabras únicas totales)
def stemmer(consulta):

    stemmer = SnowballStemmer(language='spanish')

    datos_filtrados = []

    for palabra in consulta:
        palabra = stemmer.stem(palabra)
        datos_filtrados.append(palabra)

    return datos_filtrados

#Función que carga el índice invertido y lo devuelve
def cargar_indice_invertido(dir_indice):

    with open(dir_indice, 'r', encoding='utf-8') as file:
        indice = json.load(file)
    
    return indice


#Función principal.
#   -Calcula el tiempo de ejecución
#   -Calcula los documentos relevantes en función de la consulta, tras procesar esta, y obtener las similitudes
#   -Guarda el tiempo de ejecución, más estadísticas adicionales
def main():

    ###Algoritmo PROCESAR CONSULTA

    hora_inicio = time.time()


    # CONFIGURAMOS NUESTRO ENTORNO y CARGAMOS LOS DATOS NECESARIOS
    with open('config.txt', 'r', encoding='utf-8') as file:
        config = file.readlines()

    dir_indice = config[0].strip()
    dir_consultas = config[1].strip()
    num_doc_relevantes = int(config[2].strip())
    dir_stopwords = config[3].strip()

    with open(dir_consultas, 'r', encoding='utf-8') as file:
        consultas = file.readlines()
    
    stopwords = cargar_stopwords(os.path.join('.', dir_stopwords))
    indice = cargar_indice_invertido(dir_indice)

    # PROCESAMOS LAS CONSULTAS, IGUAL QUE LOS DOCUMENTOS
    consultas_procesadas = []
    for consulta in consultas:
        consulta = transform(consulta)
        consulta = stopper(stopwords, consulta)
        consulta = stemmer(consulta)
        consultas_procesadas.append(consulta)


    # PARA CADA CONSULTA
    i=1
    for consulta in consultas_procesadas:    
        

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
        
        doc_similitud = sorted(doc_similitud.items(), key=lambda x: x[1], reverse=True)[:num_doc_relevantes]

        for doc in doc_similitud:
            print(str(i) + "  " + doc[0] + "   " + str(doc[1]))
        i+=1

    hora_fin = time.time()

    #Estadisticas PROCESAR CONSULTA
    tiempo_total = hora_fin - hora_inicio
    print("Tiempo total de ejecución:  " + str(tiempo_total) + " segundos.\n")
    ###FIN PROCESAR CONSULTA


if __name__ == "__main__":

    main()
