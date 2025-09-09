# InformationRetrievalSystem

Este repositorio contiene dos Sistemas de Recuperación de Información en español:

## Estructura del proyecto

```
Sistema_Básico/
    código_fuente/
        procesar.py
        stopper.py
        stemmer.py
        indice_invertido.py
        calcular_pesos.py
        procesar_consulta.py
        config.txt
        stopwords.txt
        consultas/
        data/
        tokens/
        stopper/
        stemmer/
        indice_invertido/
        calcular_pesos/
    Sistema Básico - Documentación.pdf

Sistema_Mejorado/
    código_base/
        SRI.py
        diccionario_sinonimos.json
        stopwords.txt
        consultas/
        data/
        creación_diccionario/
            crear_diccionario.py
            sinonimos.json
    Sistema Mejorado - Documentación.pdf

README.md
.gitattributes
```

## Descripción

- **Sistema_Básico**: Implementa un sistema de recuperación de información tradicional, con procesamiento de textos, eliminación de stopwords, stemming, creación de índice invertido y cálculo de pesos TF-IDF.
- **Sistema_Mejorado**: Añade funcionalidades avanzadas como el uso de sinónimos, mejora el procesamiento de consultas y utiliza el algoritmo BM25 para la recuperación de documentos relevantes.

## Requisitos

- Python 3.x
- Paquetes: `nltk`, `bs4`, `rank_bm25` (para el sistema mejorado)

Instala los requisitos con:

```sh
pip install nltk beautifulsoup4 rank_bm25
```

## Uso

### Sistema Básico

1. Coloca los documentos en `Sistema_Básico/código_fuente/data/` en formato XML.
2. Configura los parámetros en `config.txt`.
3. Ejecuta los scripts en el orden deseado para procesar, tokenizar, eliminar stopwords, aplicar stemming, crear el índice invertido y calcular los pesos.

### Sistema Mejorado

1. Coloca los documentos en `Sistema_Mejorado/código_base/data/`.
2. Ejecuta `crear_diccionario.py` para generar el diccionario de sinónimos.
3. Ejecuta `SRI.py` para procesar la colección y las consultas, obteniendo los resultados en `resultados.csv`.

## Documentación

Consulta los archivos PDF en cada sistema para una explicación detallada de la arquitectura y los algoritmos implementados.
