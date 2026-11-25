"""App web en Solara: ¿quién aprovecha las becas en el exterior en Colombia?"""
import os

import solara

from logica import (
    anos,
    becarios_por_estrato,
    becarios_por_genero,
    becarios_por_nivel,
    becarios_por_pais,
    cargar_becas,
    total_becarios,
)

# Configuración: viene del entorno, no del código.
NOMBRE = os.environ.get("NOMBRE_APP", "Becas en el exterior")
CLAVE_ADMIN = os.environ.get("CLAVE_ADMIN", "")  # secreto: nunca escriba su valor aquí

# Lo que la app le dice a quien la abre.
NECESIDAD = (
    "De las becas en el exterior que ICETEX otorga a colombianos, "
    "¿qué estratos, niveles académicos y países concentran el aprovechamiento, "
    "y qué grupos quedan por fuera?"
)
FUENTE = (
    "Datos abiertos: [Becas en el exterior para colombianos]"
    "(https://www.datos.gov.co/d/g85v-p2ik), ICETEX, convocatorias 2018–2025. "
    "Licencia CC BY-SA 4.0."
)

becas = cargar_becas()
lista_anos = anos(becas)

# Opciones del selector: "Todos los años" + cada año como string.
# El valor reactivo también es string, y se convierte a int o None cuando hace falta.
opciones_ano = ["Todos los años"] + [str(a) for a in lista_anos]
ano = solara.reactive("Todos los años")
clave = solara.reactive("")


def _ano_a_int(valor):
    """Convierte la opción del selector en un int (año) o None (todos)."""
    if valor == "Todos los años":
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


@solara.component
def Page():
    solara.Title(NOMBRE)
    solara.Markdown(f"# {NOMBRE}\n\n{NECESIDAD}")

    # Selector de año: opciones como strings, sin parámetro 'labels'.
    solara.Select(label="Año de selección", value=ano, values=opciones_ano)

    ano_int = _ano_a_int(ano.value)
    solara.Markdown(f"**Total de becarios:** {total_becarios(becas, ano_int):,}")

    solara.Markdown("## Distribución por estrato socioeconómico")
    solara.DataFrame(becarios_por_estrato(becas, ano_int))

    solara.Markdown("## Distribución por género")
    solara.DataFrame(becarios_por_genero(becas, ano_int))

    solara.Markdown("## Distribución por nivel académico")
    solara.DataFrame(becarios_por_nivel(becas, ano_int))

    solara.Markdown("## Distribución por país de destino")
    solara.DataFrame(becarios_por_pais(becas, ano_int))

    # Vista privada: solo aparece si la clave coincide con la del servidor.
    solara.InputText("Clave de administración", value=clave, password=True)
    if CLAVE_ADMIN and clave.value == CLAVE_ADMIN:
        solara.Markdown("## Vista privada — tabla completa")
        d = becas if ano_int is None else becas[becas["ano_seleccion"] == ano_int]
        solara.DataFrame(d)

    solara.Markdown(FUENTE)