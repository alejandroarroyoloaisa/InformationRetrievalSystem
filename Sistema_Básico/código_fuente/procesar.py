import re
import os
import json
import time

from bs4 import BeautifulSoup

#Función que dado el nombre del fichero, extrae de él el contenido requerido de toda la información contenida.
#   Se apoya de la biblioteca BeautifulSoup que facilita bastante el trabajo de búsqueda de la información indicada.
def extract(nombre_fichero):

    with open(nombre_fichero, 'r', encoding='utf-8') as file:
        datos = file.read()

    soup = BeautifulSoup(datos, "lxml-xml")

    titulo = soup.find('title').text if soup.find('title') else ''
    fecha = soup.find('date').text if soup.find('date') else ''
    autores = soup.find('creator').text if soup.find('creator') else ''
    tema = soup.find('subject').text if soup.find('subject') else ''
    descripcion = soup.find('description').text if soup.find('description') else ''

    return titulo + ' ' + fecha + ' ' + autores + ' ' + tema + ' ' + descripcion


#Función que dado un texto:
#   -lo pone en minúsculas
#   -sustituye los caracteres que no estén en el conjunto [^a-záéíóú_\n0-9 -] por '' (espacio en blanco)
#   -corta el texto ya transformado en tokens individuales
def transform(texto):

    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñ_\n0-9 -]', '', texto)
    tokens = texto.split()

    return tokens


#Función que dado un listado de tokens y el nombre del fichero del que provienen, crea un fichero .json y los
#   almacena en su interior en la carpeta indicada
def load(tokens, nombre_fichero_origen):

    nombre_fichero_destino = os.path.splitext(nombre_fichero_origen)[0] + '.json'
    with open(os.path.join('tokens', nombre_fichero_destino), 'w') as file:
        json.dump(tokens, file)


#Función que dadas unas estadisticas de ejecucion, crea un fichero .txt en el directorio base y las almacena
def guardar_Estadisticas(modulo_algoritmo, tiempo_total, ficheros_procesados, tokens_totales_coleccion, numero_medio_tokens):
    stats = modulo_algoritmo + '\nTiempo de ejecución total: ' + str(tiempo_total) + ' segundos.\n' + '->Se han procesado: ' + str(ficheros_procesados) + ' ficheros.\n' + '->Tokens totales: ' + str(tokens_totales_coleccion) + '\n->Número medio de tokens: ' + str(numero_medio_tokens)        
    with open(os.path.join('.', 'stats' + modulo_algoritmo + '.txt'), 'w') as file:
        file.write(stats)

#Función para mostrar estadísticas del algoritmo
def mostrar_Estadisticas(modulo_algoritmo, tiempo_total, ficheros_procesados, tokens_totales_coleccion, numero_medio_tokens):
    print(modulo_algoritmo)
    print(f'Tiempo de ejecución total: {tiempo_total} segundos')
    print(f'\t->Se han procesado: {ficheros_procesados} ficheros')
    print(f'\t->Tokens totales: {tokens_totales_coleccion}')
    print(f'\t->Número medio de tokens: {numero_medio_tokens}')

#Función principal.
#   -Calcula el tiempo de ejecución
#   -Abre el directorio indicado y para cada fichero en él, le aplica la Extracción, Normalización y Tokenización, y la Carga de resultados
#   -Muestra el tiempo de ejecución en pantalla, más estadísticas adicionales
def main():

    ###Algoritmo PreProcesado
    ficheros_procesados = 0
    tokens_totales_coleccion = 0

    
    hora_inicio = time.time()
    for nombre_fichero in os.listdir('./data'):
        if nombre_fichero.endswith('.xml'):
            texto = extract(os.path.join('data', nombre_fichero))
            tokens = transform(texto)
            load(tokens, nombre_fichero)

            ficheros_procesados += 1
            tokens_totales_coleccion += len(tokens)
    hora_fin = time.time()

    #Estadisticas PreProcesado
    tiempo_total = hora_fin - hora_inicio
    numero_medio_tokens = tokens_totales_coleccion / ficheros_procesados
    mostrar_Estadisticas('PREPROCESADO', tiempo_total, ficheros_procesados, tokens_totales_coleccion, numero_medio_tokens)
    guardar_Estadisticas('PREPROCESADO', tiempo_total, ficheros_procesados, tokens_totales_coleccion, numero_medio_tokens)
    ###FIN PREPROCESADO

if __name__ == "__main__":

    main()
