import os
import json
import time
import sys
import math


#Función que dado un listado de tokens y el nombre del fichero del que provienen, crea un fichero .json y los
#   almacena en su interior en la carpeta indicada
def load(tokens, nombre_fichero_origen):

    nombre_fichero_destino = os.path.splitext(nombre_fichero_origen)[0] + '.json'
    with open(os.path.join('calcular_pesos', nombre_fichero_destino), 'w') as file:
        json.dump(tokens, file, indent=4)


#Función que dadas unas estadisticas de ejecucion, crea un fichero .txt en el directorio base y las almacena
def guardar_Estadisticas(modulo_algoritmo, tiempo_total, size, numero_palabras):
    stats = modulo_algoritmo + '\nTiempo de ejecución total: ' + str(tiempo_total) + ' segundos.\nPalabras totales indexadas: ' + str(numero_palabras) + ' palabras.\nTamaño en memoria del índice: ' + str(size) + ' bytes.'
    print(stats)
    with open(os.path.join('.', 'stats' + modulo_algoritmo + '.txt'), 'w') as file:
        file.write(stats)

#Función que abre el INDICE INVERTIDO, calcula el TF IDF de cada palabra en cada documento y almacena el IDF de cada palabra y sus respectivos TF IDF
def calcular_pesos():

    with open(os.path.join('indice_invertido', 'indice_invertido.json'), 'r', encoding='utf-8') as file:
        indice = json.load(file)

    num_ficheros_coleccion = len([f for f in os.listdir('stemmer') if os.path.isfile(os.path.join('stemmer', f))])

    frec_max = {}

    for palabra in indice:
        for nombre_fichero in indice[palabra]:

            if nombre_fichero not in frec_max:
                frec_max[nombre_fichero] = indice[palabra][nombre_fichero]["reps"]
            
            else:
                if frec_max[nombre_fichero] < indice[palabra][nombre_fichero]["reps"]:
                    frec_max[nombre_fichero] = indice[palabra][nombre_fichero]["reps"]
    
    for palabra in indice:

        num_ficheros_aparicion = len(indice[palabra])
        idf = math.log2(num_ficheros_coleccion / num_ficheros_aparicion)

        for nombre_fichero in indice[palabra]:
                
                indice[palabra][nombre_fichero]["reps"] = (indice[palabra][nombre_fichero]["reps"] / frec_max[nombre_fichero] )* idf
    
        indice[palabra] = { "idf": idf, "ficheros": indice[palabra]}

    
    for palabra in indice:

            vector = [indice[palabra]["ficheros"][nombre_fichero]["reps"] for nombre_fichero in indice[palabra]["ficheros"]]
            modulo = math.sqrt(sum(value**2 for value in vector))

            for nombre_fichero in indice[palabra]["ficheros"]:
                indice[palabra]["ficheros"][nombre_fichero]["reps"] = indice[palabra]["ficheros"][nombre_fichero]["reps"] / modulo

    
    return indice

#Función principal.
#   -Calcula el tiempo de ejecución
#   -Calcula los pesos de las palabras en los documentos, basándose en el índice invertido
#   -Guarda el tiempo de ejecución, más estadísticas adicionales
def main():

    ###Algoritmo CALCULAR PESOS

    hora_inicio = time.time()

    indice = {}
    indice = calcular_pesos()

    hora_fin = time.time()

    #Guardar el indice de pesos
    load(indice, "calcular_pesos")

    #Estadisticas CALCULAR PESOS
    tiempo_total = hora_fin - hora_inicio
    size = sys.getsizeof(indice)
    guardar_Estadisticas("CALCULAR_PESOS", tiempo_total, size, len(indice))
    ###FIN CALCULAR PESOS


if __name__ == "__main__":

    main()
