import os
import json
import time
import sys


#Función que dado un listado de tokens y el nombre del fichero del que provienen, crea un fichero .json y los
#   almacena en su interior en la carpeta indicada
def load(tokens, nombre_fichero_origen):

    nombre_fichero_destino = os.path.splitext(nombre_fichero_origen)[0] + '.json'
    with open(os.path.join('indice_invertido', nombre_fichero_destino), 'w') as file:
        json.dump(tokens, file, indent=4)


#Función que dadas unas estadisticas de ejecucion, crea un fichero .txt en el directorio base y las almacena
def guardar_Estadisticas(modulo_algoritmo, tiempo_total, size, numero_palabras):
    stats = modulo_algoritmo + '\nTiempo de ejecución total: ' + str(tiempo_total) + ' segundos.\nPalabras totales indexadas: ' + str(numero_palabras) + ' palabras.\nTamaño en memoria del índice: ' + str(size) + ' bytes.'
    print(stats)
    with open(os.path.join('.', 'stats' + modulo_algoritmo + '.txt'), 'w') as file:
        file.write(stats)

#Función para crear/actualizar el indice invertido. Para el fichero indicado:
#       -mira si cada palabra está o no ya en el indice
#       -si está, añade (si no está) el documento en el que apareció
#       -actualiza para el documento en el que apareció el número de repeticiones
#ESTÁ INDEXADO COMO EN UNA TABLA HASH, POR CLAVES
def crear_indice_invertido(nombre_fichero, indice):

    with open(os.path.join('stemmer', nombre_fichero), 'r', encoding='utf-8') as file:
        datos = json.load(file)

    for palabra in datos:
        if palabra not in indice:
            indice[palabra]={}
        if nombre_fichero not in indice[palabra]:
            indice[palabra][nombre_fichero] = {
                "reps":0
            }

        indice[palabra][nombre_fichero]["reps"] += 1

    return indice

#Función principal.
#   -Calcula el tiempo de ejecución
#   -Abre el directorio indicado y para cada fichero en él, actualiza el índice invertido
#   -Muestra el tiempo de ejecución en pantalla, más estadísticas adicionales
def main():

    ###Algoritmo INDICE INVERTIDO

    hora_inicio = time.time()

    indice = {}
    for nombre_fichero in os.listdir('./stemmer'):
        if nombre_fichero.endswith('.json'):

            indice = crear_indice_invertido(nombre_fichero, indice)
            
    hora_fin = time.time()

    #Guardar y ordenar el índice (para cada palabra, orden descendente de documentos en los que aparece, ordenados por número de apariciones)
    for palabra in indice:
        indice[palabra] = dict(sorted(indice[palabra].items(), key=lambda item: item[1]['reps'], reverse=True))
    load(indice, "indice_invertido")

    #Estadisticas STEMMER
    tiempo_total = hora_fin - hora_inicio
    size = sys.getsizeof(indice)
    guardar_Estadisticas("INDICE_INVERTIDO", tiempo_total, size, len(indice))
    ###FIN STEMMER


if __name__ == "__main__":

    main()
