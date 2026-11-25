"""Pruebas de las reglas en logica.py."""
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


def test_no_duplicados():
    df = cargar_becas()
    n_dup = int(df.duplicated().sum())
    assert n_dup == 0, f"Quedan {n_dup} filas duplicadas tras la limpieza"


def test_total_becarios_menor_que_crudo():
    """El CSV crudo tiene 8.725 filas; tras limpiar y desduplicar deben ser ~2.595."""
    df = cargar_becas()
    assert len(df) < 8725, f"Esperaba menos de 8725 filas tras limpieza, hay {len(df)}"
    assert 2000 < len(df) < 4000, f"Esperaba entre 2000 y 4000 becarios únicos, hay {len(df)}"


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