import os
import json
import time

from collections import Counter


#Función que dado un listado de tokens y el nombre del fichero del que provienen, crea un fichero .json y los
#   almacena en su interior en la carpeta indicada
def load(tokens, nombre_fichero_origen):

    nombre_fichero_destino = os.path.splitext(nombre_fichero_origen)[0] + '.json'
    with open(os.path.join('stopper', nombre_fichero_destino), 'w') as file:
        json.dump(tokens, file)


#Función que dadas unas estadisticas de ejecucion, crea un fichero .txt en el directorio base y las almacena
def guardar_Estadisticas(modulo_algoritmo, tiempo_total, palabras_totales_antes, palabras_totales_despues, media_palabras_antes, media_palabras_despues, minimo_palabras_antes, minimo_palabras_despues, maximo_palabras_antes, maximo_palabras_despues, comunes_antes, comunes_despues):
    stats = modulo_algoritmo + '\nTiempo de ejecución total: ' + str(tiempo_total) + ' segundos.\n' + '\t->Palabras totales ANTES: ' + str(palabras_totales_antes) + ' | Palabras totales DESPUÉS: ' + str(palabras_totales_despues) + '\n\t->Media palabras ANTES: ' + str(media_palabras_antes) + ' | Media palabras DESPUÉS: ' +  str(media_palabras_despues) + '\n\t->Mínimo de palabras ANTES: ' + str(minimo_palabras_antes) + ' | Mínimo de palabras DESPUÉS: ' + str(minimo_palabras_despues) + '\n\t->Máximo de palabras ANTES: ' + str(maximo_palabras_antes) + ' | Máximo de palabras DESPUÉS: ' + str(maximo_palabras_despues)     
    stats += '\nLas (10) palabras más comunes antes: \n\t' + str(comunes_antes) + '\nLas (10) palabras más comunes después: \n\t' + str(comunes_despues)
    with open(os.path.join('.', 'stats' + modulo_algoritmo + '.txt'), 'w') as file:
        file.write(stats)

#Función que carga el listado de stopwords y lo devuelve (además elimina el salto de línea de cada palabra)
def cargar_stopwords(nombre_fichero):
    with open(nombre_fichero, 'r', encoding='iso-8859-1') as file:
        stopwords = file.readlines()

    stopwords_aux = list()
    for stopword in stopwords:
        stopwords_aux.append(stopword.rstrip())
    return stopwords_aux


#Función Stopper, borra del fichero indicado las palabras que se encuentren en la lista de stopwords (y actualiza el conteo de palabras para estadísticas)
def stopper(stopwords, nombre_fichero, palabras_totales, contador_antes, contador_despues):
    with open(nombre_fichero, 'r', encoding='utf-8') as file:
        datos = json.load(file)

    datos_filtrados = list()

    for palabra in datos:
        palabras_totales[0] += 1
        if palabra not in stopwords:
            datos_filtrados.append(palabra)
            palabras_totales[1] += 1

    contador_antes.update(datos)
    contador_despues.update(datos_filtrados)
    
    return datos_filtrados

#Función principal.
#   -Calcula el tiempo de ejecución
#   -Abre el directorio indicado y para cada fichero en él, le aplica el proceso de stoppers
#   -Muestra el tiempo de ejecución en pantalla, más estadísticas adicionales
def main():

    ###Algoritmo Stoppper

    palabras_totales_antes = 0
    maximo_palabras_antes = 0
    minimo_palabras_antes = 9999

    palabras_totales_despues = 0
    maximo_palabras_despues = 0
    minimo_palabras_despues = 9999

    contador_antes = Counter()
    contador_despues = Counter()

    hora_inicio = time.time()
    stopwords = cargar_stopwords(os.path.join('.', 'stopwords.txt'))

    for nombre_fichero in os.listdir('./tokens'):
        if nombre_fichero.endswith('.json'):

            palabras_totales = [0, 0]
            datos_filtrados = stopper(stopwords, os.path.join('tokens', nombre_fichero), palabras_totales, contador_antes, contador_despues)
            load(datos_filtrados, nombre_fichero)

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

    hora_fin = time.time()

    #Estadisticas Stopper
    tiempo_total = hora_fin - hora_inicio
    media_palabras_antes = palabras_totales_antes / len(os.listdir('./tokens'))
    media_palabras_despues = palabras_totales_despues / len(os.listdir('./tokens'))
    print(f'\nSTOPPER:')
    print(f'Tiempo de ejecución total: {tiempo_total} segundos')
    print(f'\t->Palabras totales ANTES: {palabras_totales_antes} | Palabras totales DESPUÉS: {palabras_totales_despues}')
    print(f'\t->Media palabras ANTES: {media_palabras_antes} | Media palabras DESPUÉS: {media_palabras_despues}')
    print(f'\t->Mínimo de palabras ANTES: {minimo_palabras_antes} | Mínimo de palabras DESPUÉS: {minimo_palabras_despues}')
    print(f'\t->Máximo de palabras ANTES: {maximo_palabras_antes} | Máximo de palabras DESPUÉS: {maximo_palabras_despues}')
    print(f'Las (10) palabras más comunes antes: ')
    print(contador_antes.most_common(10))
    print(f'Las (10) palabras más comunes después: ')
    print(contador_despues.most_common(10))

    guardar_Estadisticas('STOPPER', tiempo_total, palabras_totales_antes, palabras_totales_despues, media_palabras_antes, media_palabras_despues, minimo_palabras_antes, minimo_palabras_despues, maximo_palabras_antes, maximo_palabras_despues, contador_antes.most_common(10), contador_despues.most_common(10))
    ###FIN STOPPER


if __name__ == "__main__":

    main()
