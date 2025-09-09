import os
import json
import time
import nltk

from collections import Counter
from nltk.stem.snowball import SnowballStemmer


#Función que dado un listado de tokens y el nombre del fichero del que provienen, crea un fichero .json y los
#   almacena en su interior en la carpeta indicada
def load(tokens, nombre_fichero_origen):

    nombre_fichero_destino = os.path.splitext(nombre_fichero_origen)[0] + '.json'
    with open(os.path.join('stemmer', nombre_fichero_destino), 'w') as file:
        json.dump(tokens, file)


#Función que dadas unas estadisticas de ejecucion, crea un fichero .txt en el directorio base y las almacena
def guardar_Estadisticas(modulo_algoritmo, tiempo_total, palabras_totales_antes, palabras_totales_despues, media_palabras_antes, media_palabras_despues, minimo_palabras_antes, minimo_palabras_despues, maximo_palabras_antes, maximo_palabras_despues, comunes_antes, comunes_despues, palabras_unicas_totales_antes, palabras_unicas_totales_despues, media_palabras_unicas_antes, media_palabras_unicas_despues, minimo_palabras_unicas_antes, minimo_palabras_unicas_despues, maximo_palabras_unicas_antes, maximo_palabras_unicas_despues):
    stats = modulo_algoritmo + '\nTiempo de ejecución total: ' + str(tiempo_total) + ' segundos.\n' + '\t->Palabras totales ANTES: ' + str(palabras_totales_antes) + ' | Palabras totales DESPUÉS: ' + str(palabras_totales_despues) + '\n\t->Media palabras ANTES: ' + str(media_palabras_antes) + ' | Media palabras DESPUÉS: ' +  str(media_palabras_despues) + '\n\t->Mínimo de palabras ANTES: ' + str(minimo_palabras_antes) + ' | Mínimo de palabras DESPUÉS: ' + str(minimo_palabras_despues) + '\n\t->Máximo de palabras ANTES: ' + str(maximo_palabras_antes) + ' | Máximo de palabras DESPUÉS: ' + str(maximo_palabras_despues)     
    stats += '\n\nLas (10) palabras más comunes antes: \n\t' + str(comunes_antes) + '\nLas (10) palabras más comunes después: \n\t' + str(comunes_despues)
    stats += '\n\n\t->Palabras únicas totales ANTES: ' + str(palabras_unicas_totales_antes) + ' | Palabras únicas totales DESPUÉS: ' + str(palabras_unicas_totales_despues) + '\n\t->Media palabras únicas ANTES: ' + str(media_palabras_unicas_antes) + ' | Media palabras únicas DESPUÉS: ' +  str(media_palabras_unicas_despues) + '\n\t->Mínimo de palabras únicas ANTES: ' + str(minimo_palabras_unicas_antes) + ' | Mínimo de palabras únicas DESPUÉS: ' + str(minimo_palabras_unicas_despues) + '\n\t->Máximo de palabras únicas ANTES: ' + str(maximo_palabras_unicas_antes) + ' | Máximo de palabras únicas DESPUÉS: ' + str(maximo_palabras_unicas_despues)     
    with open(os.path.join('.', 'stats' + modulo_algoritmo + '.txt'), 'w') as file:
        file.write(stats)


#Función Stemmer, para cada fichero del directorio indicado, lo abre y de cada palabra, realiza la extracción de raices (además de contar las palabras totales y las palabras únicas totales)
def stemmer(nombre_fichero, palabras_totales, palabras_totales_unicas, contador_antes, contador_despues):

    with open(nombre_fichero, 'r', encoding='utf-8') as file:
        datos = json.load(file)

    stemmer = SnowballStemmer(language='spanish')

    datos_filtrados = []
    conjunto_palabras_diferentes_antes = set(datos)
    conjunto_palabras_diferentes_despues = set()

    for palabra in datos:
        palabras_totales[0] += 1
        palabra = stemmer.stem(palabra)
        datos_filtrados.append(palabra)
        palabras_totales[1] += 1

        conjunto_palabras_diferentes_despues.add(palabra)

    contador_antes.update(datos)
    contador_despues.update(datos_filtrados)

    palabras_totales_unicas[0] = len(conjunto_palabras_diferentes_antes)
    palabras_totales_unicas[1] = len(conjunto_palabras_diferentes_despues)

    return datos_filtrados


#Función principal.
#   -Calcula el tiempo de ejecución
#   -Abre el directorio indicado y para cada fichero en él, le aplica el proceso de stemming
#   -Muestra el tiempo de ejecución en pantalla, más estadísticas adicionales
def main():

    ###Algoritmo STEMMER

    #Palabras diferentes
    palabras_totales_antes = 0
    maximo_palabras_antes = 0
    minimo_palabras_antes = 9999

    palabras_totales_despues = 0
    maximo_palabras_despues = 0
    minimo_palabras_despues = 9999

    #Palabras únicas
    palabras_unicas_totales_antes = 0
    maximo_palabras_unicas_antes = 0
    minimo_palabras_unicas_antes = 9999

    palabras_unicas_totales_despues = 0
    maximo_palabras_unicas_despues = 0
    minimo_palabras_unicas_despues = 9999

    contador_antes = Counter()
    contador_despues = Counter()

    hora_inicio = time.time()

    for nombre_fichero in os.listdir('./stopper'):
        if nombre_fichero.endswith('.json'):

            palabras_totales = [0, 0]
            palabras_totales_unicas = [0, 0]
            datos_filtrados = stemmer(os.path.join('stopper', nombre_fichero), palabras_totales, palabras_totales_unicas, contador_antes, contador_despues)
            load(datos_filtrados, nombre_fichero)

            #Actualización de estadísticas de palabras
            palabras_totales_antes += palabras_totales[0]
            palabras_totales_despues += palabras_totales[1]
            if maximo_palabras_antes < palabras_totales[0]:
                maximo_palabras_antes = palabras_totales[0]
            if maximo_palabras_despues < palabras_totales[1]:
                maximo_palabras_despues = palabras_totales[1]
            if minimo_palabras_antes > palabras_totales[0]:
                minimo_palabras_antes = palabras_totales[0]
            if minimo_palabras_despues > palabras_totales[1]:
                minimo_palabras_despues = palabras_totales[1]   

            #Actualización de estadísticas de palabras únicas
            palabras_unicas_totales_antes += palabras_totales_unicas[0]
            palabras_unicas_totales_despues += palabras_totales_unicas[1]
            if maximo_palabras_unicas_antes < palabras_totales_unicas[0]:
                maximo_palabras_unicas_antes = palabras_totales_unicas[0]
            if maximo_palabras_unicas_despues < palabras_totales_unicas[1]:
                maximo_palabras_unicas_despues = palabras_totales_unicas[1]
            if minimo_palabras_unicas_antes > palabras_totales_unicas[0]:
                minimo_palabras_unicas_antes = palabras_totales_unicas[0]
            if minimo_palabras_unicas_despues > palabras_totales_unicas[1]:
                minimo_palabras_unicas_despues = palabras_totales_unicas[1]      

    hora_fin = time.time()

    #Estadisticas STEMMER
    tiempo_total = hora_fin - hora_inicio
    media_palabras_antes = palabras_totales_antes / len(os.listdir('./stopper'))
    media_palabras_despues = palabras_totales_despues / len(os.listdir('./stopper'))
    print(f'\nSTEMMER:')
    print(f'Tiempo de ejecución total: {tiempo_total} segundos')
    print(f'\t->Palabras totales ANTES: {palabras_totales_antes} | Palabras totales DESPUÉS: {palabras_totales_despues}')
    print(f'\t->Media palabras ANTES: {media_palabras_antes} | Media palabras DESPUÉS: {media_palabras_despues}')
    print(f'\t->Mínimo de palabras ANTES: {minimo_palabras_antes} | Mínimo de palabras DESPUÉS: {minimo_palabras_despues}')
    print(f'\t->Máximo de palabras ANTES: {maximo_palabras_antes} | Máximo de palabras DESPUÉS: {maximo_palabras_despues}')
    print(f'\nLas (10) palabras más comunes antes: ')
    print(contador_antes.most_common(10))
    print(f'Las (10) palabras más comunes después: ')
    print(contador_despues.most_common(10))
    media_palabras_unicas_antes = palabras_unicas_totales_antes / len(os.listdir('./stopper'))
    media_palabras_unicas_despues = palabras_unicas_totales_despues / len(os.listdir('./stopper'))
    print(f'\n\t->Palabras únicas totales ANTES: {palabras_unicas_totales_antes} | Palabras únicas totales DESPUÉS: {palabras_unicas_totales_despues}')
    print(f'\t->Media palabras únicas ANTES: {media_palabras_unicas_antes} | Media palabras únicas DESPUÉS: {media_palabras_unicas_despues}')
    print(f'\t->Mínimo de palabras únicas ANTES: {minimo_palabras_unicas_antes} | Mínimo de palabras únicas DESPUÉS: {minimo_palabras_unicas_despues}')
    print(f'\t->Máximo de palabras únicas ANTES: {maximo_palabras_unicas_antes} | Máximo de palabras únicas DESPUÉS: {maximo_palabras_unicas_despues}')

    guardar_Estadisticas('STEMMER', tiempo_total, palabras_totales_antes, palabras_totales_despues, media_palabras_antes, media_palabras_despues, minimo_palabras_antes, minimo_palabras_despues, maximo_palabras_antes, maximo_palabras_despues, contador_antes.most_common(10), contador_despues.most_common(10), palabras_unicas_totales_antes, palabras_unicas_totales_despues, media_palabras_unicas_antes, media_palabras_unicas_despues, minimo_palabras_unicas_antes, minimo_palabras_unicas_despues, maximo_palabras_unicas_antes, maximo_palabras_unicas_despues)
    ###FIN STEMMER


if __name__ == "__main__":

    main()
