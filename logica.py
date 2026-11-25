"""Reglas de la app, sin pantalla. Se prueban con pytest (tests/test_logica.py)."""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).parent / "datos" / "becas_exterior_icetex.csv"


def limpiar_becas(df):
    """Normaliza el dataset de ICETEX.

    - Quita duplicados completos.
    - Unifica mayúsculas/minúsculas y tildes en todas las columnas de texto.
    - Unifica sinónimos (género, nivel académico, modalidad, rango de edad).
    - Unifica los 'no aplica' (NaN, 'N/A', 'NA') en 'Sin información'.
    - Convierte estrato a categoría string y año a entero.
    - Estandariza los nombres de columnas a minúsculas sin espacios.
    """
    d = df.drop_duplicates().copy()

    # Renombrar columnas a minúsculas con guiones bajos.
    d.columns = [c.strip().lower().replace(" ", "_") for c in d.columns]

    # ---- Genero ----
    def _norm_genero(x):
        if pd.isna(x):
            return "Sin información"
        s = str(x).strip().lower()
        if s in {"f", "femenino"}:
            return "Femenino"
        if s in {"m", "masculino", "maculino"}:
            return "Masculino"
        if s == "no binario":
            return "No binario"
        return "Sin información"
    d["genero"] = d["genero"].map(_norm_genero)

    # ---- Estrato socioeconómico ----
        # ---- Estrato socioeconómico ----
    def _norm_estrato(x):
        if pd.isna(x):
            return "Sin información"
        # El CSV de SODA2 trae el estrato como float (5.0, 3.0 ...).
        # Convertir a entero primero, luego a string.
        try:
            n = int(float(x))
            if n in {1, 2, 3, 4, 5, 6}:
                return str(n)
        except (ValueError, TypeError):
            pass
        s = str(x).strip()
        if s.upper() in {"N/A", "NA", "NAN", ""}:
            return "Sin información"
        if s in {"1", "2", "3", "4", "5", "6"}:
            return s
        return "Sin información"
    d["estrato_socioeconomico"] = d["estrato_socioeconomico"].map(_norm_estrato)

    # ---- Rango de edad ----
    def _norm_edad(x):
        if pd.isna(x):
            return "Sin información"
        s = str(x).strip()
        if s.upper() in {"N/A", "NA", "0", ""}:
            return "Sin información"
        # Unificar variantes de escritura del mismo rango.
        if s == "21- 25 AÑOS":
            return "21 - 25 AÑOS"
        if s == "36 - MÁS AÑOS":
            return "MÁS DE 36"
        return s
    d["rango_de_edad"] = d["rango_de_edad"].map(_norm_edad)

    # ---- Pertenece a minoría ----
    def _norm_minoria(x):
        if pd.isna(x):
            return "Sin información"
        s = str(x).strip().lower()
        if s in {"si", "sí"}:
            return "Sí"
        if s == "no":
            return "No"
        return "Sin información"
    d["pertenece_a_minoria"] = d["pertenece_a_minoria"].map(_norm_minoria)

    # ---- Tiene discapacidad ----
    def _norm_discapacidad(x):
        if pd.isna(x):
            return "Sin información"
        s = str(x).strip().lower()
        if s in {"si", "sí"}:
            return "Sí"
        if s == "no":
            return "No"
        return "Sin información"
    d["tiene_discapacidad"] = d["tiene_discapacidad"].map(_norm_discapacidad)

    # ---- País de destino ----
    def _norm_pais(x):
        if pd.isna(x):
            return "Sin información"
        s = str(x).strip()
        if s.upper() in {"N/A", "NA", ""}:
            return "Sin información"
        # Unificar tildes y grafías comunes.
        if s.lower() == "japon":
            return "Japón"
        if s.lower() == "mexico":
            return "México"
        if s.lower() == "perú" or s.lower() == "peru":
            return "Perú"
        return s
    d["pais_de_destino"] = d["pais_de_destino"].map(_norm_pais)

    # ---- Nivel académico ----
    def _norm_nivel(x):
        if pd.isna(x):
            return "Sin información"
        s = str(x).strip().lower()
        if s in {"maestría", "maestria"}:
            return "Maestría"
        if s in {"doctorado"}:
            return "Doctorado"
        if s in {"pregrado"}:
            return "Pregrado"
        if s in {"especialización"}:
            return "Especialización"
        if s in {"especialización y maestría"}:
            return "Especialización y Maestría"
        if s in {"posgrado", "postgrado"}:
            return "Posgrado"
        if s in {"curso corto", "curso corto", "cursos cortos"}:
            return "Curso corto"
        if s in {"investigación", "investigacion"}:
            return "Investigación"
        if s in {"otro"}:
            return "Otro"
        return s.capitalize()
    d["nivel_academico"] = d["nivel_academico"].map(_norm_nivel)

    # ---- Modalidad ----
    def _norm_modalidad(x):
        if pd.isna(x):
            return "Sin información"
        s = str(x).strip().lower()
        if s == "presencial" or s in {"presencial - virtual", "presencial o virtual", "presencial - virtual"}:
            return "Presencial"
        if s in {"virtual", "online"}:
            return "Virtual"
        if s in {"virtual - asincrónico", "virtual - asincronico"}:
            return "Virtual asincrónica"
        if s == "semipresencial":
            return "Semipresencial"
        # Variantes que listan varias modalidades a la vez.
        if "presencial" in s and "virtual" in s and "semi" in s:
            return "Mixta"
        if "presencial" in s and "virtual" in s:
            return "Mixta"
        if s == "intercambio":
            return "Intercambio"
        if s == "alojamiento":
            return "Alojamiento"
        return s.capitalize()
    d["modalidad"] = d["modalidad"].map(_norm_modalidad)

    # ---- Año: a entero ----
    d["ano_seleccion"] = pd.to_numeric(d["ano_seleccion"], errors="coerce").astype("Int64")

    # Segundo drop_duplicates: al normalizar, filas que antes eran distintas
    # (p. ej. 'Maestria' vs 'Maestría') pueden volverse idénticas. Hay que
    # quitarlas también, además del drop_duplicates que se hizo al inicio.
    d = d.drop_duplicates()

    return d.reset_index(drop=True)


def cargar_becas(ruta=DATOS):
    """Lee los datos, los limpia y los devuelve listos para la app."""
    crudo = pd.read_csv(ruta)
    return limpiar_becas(crudo)


def anos(df):
    """Lista ordenada de años de selección disponibles."""
    return sorted(df["ano_seleccion"].dropna().astype(int).unique().tolist())


def estratos(df):
    """Lista ordenada de estratos socioeconómicos (excluye 'Sin información')."""
    e = df.loc[df["estrato_socioeconomico"] != "Sin información", "estrato_socioeconomico"]
    return sorted(e.unique().tolist(), key=lambda x: int(x))


def niveles_academicos(df):
    """Lista ordenada de niveles académicos."""
    return sorted(df["nivel_academico"].unique().tolist())


def paises_destino(df):
    """Lista ordenada de países de destino (excluye 'Sin información')."""
    p = df.loc[df["pais_de_destino"] != "Sin información", "pais_de_destino"]
    return sorted(p.unique().tolist())


def becarios_por(df, columna):
    """Cuenta becarios agrupando por una columna. Devuelve un DataFrame con la columna y 'becarios'."""
    return (
        df.groupby(columna, dropna=False)
        .size()
        .reset_index(name="becarios")
        .sort_values("becarios", ascending=False)
    )


def becarios_por_estrato(df, ano=None):
    """Becarios por estrato, opcionalmente filtrado por año."""
    d = df if ano is None else df[df["ano_seleccion"] == ano]
    return becarios_por(d, "estrato_socioeconomico")


def becarios_por_nivel(df, ano=None):
    """Becarios por nivel académico, opcionalmente filtrado por año."""
    d = df if ano is None else df[df["ano_seleccion"] == ano]
    return becarios_por(d, "nivel_academico")


def becarios_por_pais(df, ano=None):
    """Becarios por país de destino, opcionalmente filtrado por año."""
    d = df if ano is None else df[df["ano_seleccion"] == ano]
    return becarios_por(d, "pais_de_destino")


def becarios_por_genero(df, ano=None):
    """Becarios por género, opcionalmente filtrado por año."""
    d = df if ano is None else df[df["ano_seleccion"] == ano]
    return becarios_por(d, "genero")


def total_becarios(df, ano=None):
    """Total de becarios, opcionalmente filtrado por año."""
    d = df if ano is None else df[df["ano_seleccion"] == ano]
    return int(len(d))