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
    filtrar_por_nivel,
    niveles_academicos,
)

# Configuración: viene del entorno, no del código.
NOMBRE = os.environ.get("NOMBRE_APP", "Becas en el exterior")
CLAVE_ADMIN = os.environ.get("CLAVE_ADMIN", "")  # secreto: nunca escriba su valor aquí

# Lo que la app le dice a quien la abre.
NECESIDAD = (
    "Para estudiantes, universidades y quienes diseñan políticas de becas: "
    "De las becas en el exterior que ICETEX otorga a colombianos, "
    "¿qué estratos, niveles académicos y países concentran el aprovechamiento, "
    "y qué grupos quedan por fuera?"
)
FUENTE = (
    "Datos abiertos: [Becas en el exterior para colombianos]"
    "(https://www.datos.gov.co/d/g85v-p2ik), ICETEX, convocatorias 2018–2025. "
    "Licencia CC BY-SA 4.0. "
    "Cada fila del conjunto de datos se cuenta como un becario; "
    "no se eliminan filas repetidas porque el archivo no trae identificador."
)

becas_todas = cargar_becas()
lista_anos = anos(becas_todas)
opciones_ano = ["Todos los años"] + [str(a) for a in lista_anos]
opciones_nivel = ["Todos los niveles"] + niveles_academicos(becas_todas)
ano = solara.reactive("Todos los años")
nivel = solara.reactive("Todos los niveles")
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


ESTILOS = """
body, .v-application { background: #F4F6FA !important; }
.encabezado { background: #1565C0; color: #fff;
  padding: 28px 32px; border-radius: 0; font-family: sans-serif; }
.encabezado h1 { margin: 0 0 8px 0; font-size: 30px; }
.encabezado p { margin: 0; font-size: 16px; line-height: 1.5; opacity: .95; }
.kpis { display: flex; flex-wrap: wrap; gap: 14px; font-family: sans-serif; }
.kpi { flex: 1 1 190px; background: #fff; border-radius: 0; padding: 16px 18px;
  border-left: 6px solid var(--c); border-radius: 0; }
.kpi .t { font-size: 13px; color: #666; text-transform: uppercase; letter-spacing: .4px; }
.kpi .v { font-size: 34px; font-weight: 700; color: #222; margin: 4px 0 2px 0; }
.kpi .d { font-size: 13px; color: #888; }
.nota { background: #FFF8E1; border-left: 5px solid #F9A825; color: #5D4037;
  padding: 10px 14px; border-radius: 0; font-family: sans-serif; font-size: 14px; }
.pie { color: #666; font-size: 13px; }
"""


def _kpi(titulo, valor, detalle="", color="#1976D2"):
    """Tarjeta de indicador en HTML."""
    return (
        f"<div class='kpi' style='--c:{color}'>"
        f"<div class='t'>{titulo}</div><div class='v'>{valor}</div>"
        f"<div class='d'>{detalle}</div></div>"
    )


def _seccion(titulo, descripcion, html_barras, df_tabla):
    """Sección con título, descripción, barras y tabla dentro de una tarjeta."""
    with solara.Card(title=titulo, subtitle=descripcion, margin=0, style="margin-top: 18px"):
        with solara.Row(style="flex-wrap: wrap; gap: 16px"):
            with solara.Column(style="flex: 2 1 380px; min-width: 300px"):
                solara.HTML(tag="div", unsafe_innerHTML=html_barras)
            with solara.Column(style="flex: 1 1 260px; min-width: 240px"):
                solara.DataFrame(df_tabla)


@solara.component
def Page():
    solara.Title(NOMBRE)
    solara.Style(ESTILOS)
    ano_int = _ano_a_int(ano.value)
    becas = filtrar_por_nivel(becas_todas, nivel.value)
    total = total_becarios(becas, ano_int)

    # --- Encabezado ---
    solara.HTML(tag="div", unsafe_innerHTML=(
        f"<div class='encabezado'><h1>{NOMBRE}</h1><p>{NECESIDAD}</p></div>"
    ))

    # --- Filtros ---
    with solara.Card(margin=0, style="margin-top: 18px"):
        with solara.Row(style="flex-wrap: wrap; gap: 16px"):
            solara.Select(label="Año de selección", value=ano, values=opciones_ano)
            solara.Select(label="Nivel académico", value=nivel, values=opciones_nivel)

    # --- Indicadores ---
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

    solara.HTML(tag="div", style="margin-top: 18px", unsafe_innerHTML=(
        "<div class='kpis'>"
        + _kpi("Becarios", f"{total:,}", "cada fila cuenta como un becario", "#1976D2")
        + _kpi("Femenino", f"{pct_fem}%", "del total del filtro", "#7B1FA2")
        + _kpi("Estratos 1–2", f"{pct_baja}%", "estratos más bajos", "#F57C00")
        + _kpi("País top", top_pais, f"{pct_top}% de las becas", "#388E3C")
        + "</div>"
    ))

    # --- Secciones ---
    _seccion(
        "Distribución por estrato socioeconómico",
        "Los estratos 1 y 2 (los más bajos) están resaltados en naranja para ver la brecha.",
        _barras_html(becarios_por_estrato(becas, ano_int), color="#1976D2", resaltar=["1", "2"]),
        becarios_por_estrato(becas, ano_int),
    )
    _seccion(
        "Distribución por género",
        "El género femenino está resaltado para ver la brecha de género.",
        _barras_html(becarios_por_genero(becas, ano_int), color="#7B1FA2", resaltar="Femenino"),
        becarios_por_genero(becas, ano_int),
    )
    _seccion(
        "Distribución por nivel académico",
        "Cuántos becarios hay en cada tipo de programa.",
        _barras_html(becarios_por_nivel(becas, ano_int), color="#388E3C"),
        becarios_por_nivel(becas, ano_int),
    )
    _seccion(
        "Distribución por país de destino",
        "Se muestran los 15 países con más becarios.",
        _barras_html(becarios_por_pais(becas, ano_int), color="#E64A19"),
        becarios_por_pais(becas, ano_int),
    )

    # Nota sobre filas con Colombia como destino (así viene en la fuente).
    base = becas if ano_int is None else becas[becas["ano_seleccion"] == ano_int]
    n_col = int((base["pais_de_destino"] == "Colombia").sum())
    if n_col:
        solara.HTML(tag="div", style="margin-top: 14px", unsafe_innerHTML=(
            f"<div class='nota'><b>Nota:</b> {n_col:,} registros de este filtro tienen "
            "<b>Colombia</b> como país de destino. Así vienen en la fuente de ICETEX, "
            "que no explica el motivo; se mantienen y no se eliminan.</div>"
        ))

    # --- Vista privada ---
    solara.Markdown("---")
    solara.InputText("Clave de administración", value=clave, password=True)
    if CLAVE_ADMIN and clave.value == CLAVE_ADMIN:
        solara.Markdown("## Vista privada — tabla completa")
        d = becas if ano_int is None else becas[becas["ano_seleccion"] == ano_int]
        solara.DataFrame(d)

    solara.Markdown(FUENTE, style="margin-top: 8px")