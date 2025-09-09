import json
import os 

from nltk.stem.snowball import SnowballStemmer

# Función que carga el listado de stopwords y lo devuelve
def cargar_stopwords(nombre_fichero):
    with open(nombre_fichero, 'r', encoding='iso-8859-1') as file:
        stopwords = file.readlines()

    stopwords_aux = list()
    for stopword in stopwords:
        stopwords_aux.append(stopword.rstrip())
    return stopwords_aux


# Función que elimina los acentos de una cadena de texto
def remove_accents(input_str):
    s = input_str
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b)
    return s


# Función principal:
#   - Carga el archivo 'sinonimos.json', es una lista de listas de palabras (cada lista de palabras son sinónimas entre ellas)
def main():

    # Cargar los sinónimos
    with open('./sinonimos.json', 'r') as f:
        data = json.load(f)

    # Cargar los stopwords
    stopwords = cargar_stopwords(os.path.join('.', 'stopwords.txt'))

    # Eliminar las stopwords de las listas de sinónimos
    for lista in data:
        for palabra in lista[:]:  #<-  Hacemos una copia de la lista para iterar sobre ella
            if palabra in stopwords:
                lista.remove(palabra)

    # Aplicar stemming a las palabras de las listas de sinónimos
    stemmer = SnowballStemmer(language='spanish')
    for lista in data:
        for palabra in lista[:]:  #<-  Hacemos una copia de la lista para iterar sobre ella
            lista.remove(palabra)
            lista.append(stemmer.stem(remove_accents(palabra)))

    # Crear un diccionario vacío
    diccionario = {}
    
    # Iterar sobre cada lista en el archivo JSON
    for lista in data:
        # Para cada lista, iterar sobre cada palabra
        for palabra in lista:
            # Crear una copia de la lista y eliminar la palabra clave
            sinonimos = lista.copy()
            sinonimos.remove(palabra)
            # Agregar la palabra como clave en el diccionario y los sinonimos como valor
            diccionario[palabra] = sinonimos

    # Abrir el archivo 'diccionario_sinonimos.json' en modo escritura y guardar el diccionario
    with open('diccionario_sinonimos.json', 'w') as f:
        json.dump(diccionario, f)

if __name__ == "__main__":

    main()