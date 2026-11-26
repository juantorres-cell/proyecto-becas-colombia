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


def _barras_html(df_distrib, color="#1976D2", resaltar=None, top=15):
    """Construye HTML con barras horizontales. No usa matplotlib.

    df_distrib: DataFrame con columnas [categoria, becarios].
    resaltar: valor o lista de valores a mostrar en naranja.
    top: máximo número de barras a mostrar.
    """
    d = df_distrib.copy()
    # Quitar 'Sin información' del gráfico (queda en la tabla).
    d = d[d.iloc[:, 0] != "Sin información"]
    if len(d) == 0:
        return "<p style='color:#888;font-size:13px'>Sin datos para mostrar.</p>"
    d = d.sort_values("becarios", ascending=False).head(top)
    max_val = int(d["becarios"].max())
    resaltar_set = set([resaltar] if isinstance(resaltar, str) else (resaltar or []))

    filas = []
    for _, row in d.iterrows():
        cat = str(row.iloc[0])
        val = int(row["becarios"])
        pct = val / max_val * 100 if max_val else 0
        color_barra = "#F57C00" if cat in resaltar_set else color
        filas.append(
            f"<div style='display:flex;align-items:center;margin-bottom:6px;font-family:sans-serif'>"
            f"<div style='width:150px;text-align:right;padding-right:10px;font-size:13px;"
            f"color:#333;overflow:hidden;text-overflow:ellipsis;white-space:nowrap'>{cat}</div>"
            f"<div style='flex:1;background:#f0f0f0;height:22px;border-radius:3px'>"
            f"<div style='width:{pct:.1f}%;height:100%;background:{color_barra};border-radius:3px'></div>"
            f"</div>"
            f"<div style='width:70px;padding-left:8px;font-size:13px;font-weight:bold;"
            f"color:#444'>{val:,}</div>"
            f"</div>"
        )
    return "".join(filas)


@solara.component
def Page():
    solara.Title(NOMBRE)
    ano_int = _ano_a_int(ano.value)
    total = total_becarios(becas, ano_int)

    # --- Encabezado ---
    solara.Markdown(f"# {NOMBRE}\n\n{NECESIDAD}")

    # --- Selector de año ---
    solara.Select(label="Año de selección", value=ano, values=opciones_ano)

    # --- KPIs (tarjetas) ---
    df_gen = becarios_por_genero(becas, ano_int)
    fem = df_gen.loc[df_gen["genero"] == "Femenino", "becarios"].sum()
    pct_fem = int(round(fem / total * 100)) if total else 0

    df_est = becarios_por_estrato(becas, ano_int)
    baja = df_est.loc[df_est["estrato_socioeconomico"].isin(["1", "2"]), "becarios"].sum()
    pct_baja = int(round(baja / total * 100)) if total else 0

    df_pais = becarios_por_pais(becas, ano_int)
    df_pais_sin = df_pais[df_pais["pais_de_destino"] != "Sin información"]
    top_pais = df_pais_sin.iloc[0]["pais_de_destino"] if len(df_pais_sin) else "—"
    pct_top = int(round(df_pais_sin.iloc[0]["becarios"] / total * 100)) if len(df_pais_sin) and total else 0

    with solara.Row():
        with solara.Card(title="Becarios", style="min-width: 160px"):
            solara.Markdown(f"### {total:,}")
        with solara.Card(title="% Femenino", style="min-width: 160px"):
            solara.Markdown(f"### {pct_fem}%")
        with solara.Card(title="% Estratos 1–2 (bajos)", style="min-width: 160px"):
            solara.Markdown(f"### {pct_baja}%")
        with solara.Card(title="País top", style="min-width: 160px"):
            solara.Markdown(f"### {top_pais}")
            solara.Markdown(f"{pct_top}% de las becas")

    solara.Markdown("---")

    # --- Distribución por estrato ---
    solara.Markdown(
        "## Distribución por estrato socioeconómico\n\n"
        "Los estratos 1 y 2 (los más bajos) están resaltados en naranja "
        "para visualizar la brecha de aprovechamiento."
    )
    with solara.Row():
        with solara.Column(style="flex: 2"):
            solara.HTML(tag="div", unsafe_innerHTML=_barras_html(
                becarios_por_estrato(becas, ano_int),
                color="#1976D2", resaltar=["1", "2"],
            ))
        with solara.Column(style="flex: 1"):
            solara.DataFrame(becarios_por_estrato(becas, ano_int))

    # --- Distribución por género ---
    solara.Markdown(
        "## Distribución por género\n\n"
        "El género femenino está resaltado para evidenciar la brecha de género."
    )
    with solara.Row():
        with solara.Column(style="flex: 2"):
            solara.HTML(tag="div", unsafe_innerHTML=_barras_html(
                becarios_por_genero(becas, ano_int),
                color="#7B1FA2", resaltar="Femenino",
            ))
        with solara.Column(style="flex: 1"):
            solara.DataFrame(becarios_por_genero(becas, ano_int))

    # --- Distribución por nivel académico ---
    solara.Markdown("## Distribución por nivel académico")
    with solara.Row():
        with solara.Column(style="flex: 2"):
            solara.HTML(tag="div", unsafe_innerHTML=_barras_html(
                becarios_por_nivel(becas, ano_int),
                color="#388E3C",
            ))
        with solara.Column(style="flex: 1"):
            solara.DataFrame(becarios_por_nivel(becas, ano_int))

    # --- Distribución por país ---
    solara.Markdown(
        "## Distribución por país de destino\n\n"
        "Se muestran los 15 países con más becarios."
    )
    with solara.Row():
        with solara.Column(style="flex: 2"):
            solara.HTML(tag="div", unsafe_innerHTML=_barras_html(
                becarios_por_pais(becas, ano_int),
                color="#E64A19",
            ))
        with solara.Column(style="flex: 1"):
            solara.DataFrame(becarios_por_pais(becas, ano_int))

    # --- Vista privada ---
    solara.Markdown("---")
    solara.InputText("Clave de administración", value=clave, password=True)
    if CLAVE_ADMIN and clave.value == CLAVE_ADMIN:
        solara.Markdown("## Vista privada — tabla completa")
        d = becas if ano_int is None else becas[becas["ano_seleccion"] == ano_int]
        solara.DataFrame(d)

    solara.Markdown(FUENTE)