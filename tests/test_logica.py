"""Pruebas de las reglas en logica.py."""
import csv
from collections import Counter

from logica import (
    anos,
    becarios_por_estrato,
    becarios_por_genero,
    becarios_por_nivel,
    cargar_becas,
    estratos,
    niveles_academicos,
    paises_destino,
    total_becarios,
    DATOS,
    filtrar_por_nivel,
)


def test_carga_datos():
    df = cargar_becas()
    assert len(df) > 0, "El dataset no debe estar vacío"
    assert len(df) > 1000, "El dataset debe tener miles de filas (ICETEX)"


def test_anos_ordenados():
    df = cargar_becas()
    a = anos(df)
    assert a == sorted(a), "Los años deben estar ordenados"
    assert 2018 in a or 2019 in a, "Debe haber años recientes"
    assert 2025 in a, "Debe incluir el año 2025"


def test_estratos_solo_1_a_6():
    df = cargar_becas()
    e = estratos(df)
    assert e == ["1", "2", "3", "4", "5", "6"], f"Estratos inesperados: {e}"


def test_niveles_academicos_normalizados():
    df = cargar_becas()
    n = niveles_academicos(df)
    # No deben quedar duplicados por tilde ni por mayúscula.
    assert "Maestría" in n
    assert "Maestria" not in n
    assert "Otro" in n
    assert "otro" not in n


def test_genero_normalizado():
    df = cargar_becas()
    g = sorted(df["genero"].unique())
    # Solo deben quedar: Femenino, Masculino, No binario, Sin información.
    assert set(g) <= {"Femenino", "Masculino", "No binario", "Sin información"}, f"Géneros inesperados: {g}"
    assert "F" not in g and "femenino" not in g, "El género no quedó normalizado"


def test_pais_japon_unificado():
    df = cargar_becas()
    paises = paises_destino(df)
    assert "Japón" in paises
    assert "Japon" not in paises, "Japón debe estar unificado con tilde"


def test_becarios_por_estrato_suman_total():
    df = cargar_becas()
    por_estrato = becarios_por_estrato(df)
    assert por_estrato["becarios"].sum() == total_becarios(df), (
        "La suma de becarios por estrato debe igualar el total"
    )


def test_becarios_por_genero_suman_total():
    df = cargar_becas()
    por_genero = becarios_por_genero(df)
    assert por_genero["becarios"].sum() == total_becarios(df), (
        "La suma de becarios por género debe igualar el total"
    )

def _contar_con_csv():
    """Cuenta las filas del CSV sin pandas: otro camino para la cifra de control."""
    with open(DATOS, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    por_ano = Counter(int(fila["ano_seleccion"]) for fila in filas)
    return len(filas), por_ano


def test_cifra_de_control_total():
    """El total de la app coincide con el conteo directo del CSV."""
    total_csv, _ = _contar_con_csv()
    assert total_csv == 8725, "El CSV de datos.gov.co debe tener 8.725 filas"
    assert total_becarios(cargar_becas()) == total_csv


def test_cifra_de_control_por_ano():
    df = cargar_becas()
    _, por_ano = _contar_con_csv()
    for ano, esperado in por_ano.items():
        assert total_becarios(df, ano) == esperado, f"Año {ano} no coincide"


def test_filtrar_por_nivel():
    df = cargar_becas()
    assert len(filtrar_por_nivel(df, "Todos los niveles")) == len(df)
    maestria = filtrar_por_nivel(df, "Maestría")
    assert 0 < len(maestria) < len(df)
    assert set(maestria["nivel_academico"]) == {"Maestría"}