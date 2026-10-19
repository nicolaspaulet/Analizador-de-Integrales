import numpy as np
import plotly.graph_objects as go
import streamlit as st
from sympy import *
import re as regex
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

x = Symbol('x')

# Función auxiliar para logaritmo en base 10.
def log10(valor):
    return log(valor, 10)


# Nombres matemáticos aceptados en las entradas del usuario.
# e/E son constantes de Euler.
NOMBRES_MATEMATICOS = {
    "x": x,
    "e": E,
    "E": E,
    "Euler": E,
    "pi": pi,
    "Pi": pi,
    "π": pi,
    "oo": oo,
    "inf": oo,
    "sqrt": sqrt,
    "factorial": factorial,  # factorial: factorial(5) o notación 5!
    "log": log,      # logaritmo natural si no se indica base
    "ln": log,       # sinónimo del logaritmo natural
    "log10": log10,  # logaritmo en base 10
    "abs": Abs,
    "Abs": Abs,
    "sin": sin,
    "sen": sin,
    "cos": cos,
    "tan": tan,
    "cot": cot,
    "sec": sec,
    "csc": csc,
    "asin": asin,
    "arcsin": asin,
    "arcsen": asin,
    "acos": acos,
    "arccos": acos,
    "atan": atan,
    "arctan": atan,
    "acot": acot,
    "arccot": acot,
    "asec": asec,
    "arcsec": asec,
    "acsc": acsc,
    "arccsc": acsc,
    "sinh": sinh,
    "cosh": cosh,
    "tanh": tanh,
    "coth": coth,
    "sech": sech,
    "csch": csch,
    "asinh": asinh,
    "acosh": acosh,
    "atanh": atanh,
    "acoth": acoth,
    "asech": asech,
    "acsch": acsch,
}


def parsear_expresion(texto, transformations):
    """Convierte texto del usuario a una expresión de SymPy."""
    texto = texto.strip()
    if not texto:
        raise ValueError("Hay un campo vacío. Completa la función y los límites.")

    # Convertir ángulos numéricos en grados a radianes: 36° -> 36*pi/180 = pi/5.
    # El símbolo ° es opcional solo para esta conversión; sin él se usan radianes.
    texto = regex.sub(
        r"(?<![A-Za-z0-9_.])(\d+(?:\.\d+)?)\s*°",
        r"(\1*pi/180)",
        texto
    )

    # La función exp no forma parte de la sintaxis admitida por esta calculadora.
    if regex.search(r"\bexp\b", texto, flags=regex.IGNORECASE):
        raise ValueError("La función 'exp' no está admitida. Escribe la exponencial usando e^(...).")

    # Aceptar |expresión| como notación de valor absoluto.
    # Para expresiones más complejas también se puede escribir abs(expresión).
    if texto.count("|") % 2 != 0:
        raise ValueError("El valor absoluto debe escribirse entre dos barras: |x|.")
    texto = regex.sub(r"\|([^|]+)\|", r"Abs(\1)", texto)

    # Aceptar ^ como símbolo de potencia, igual que **.
    texto = texto.replace("^", "**")

    return parse_expr(
        texto,
        transformations=transformations,
        local_dict=NOMBRES_MATEMATICOS
    )

# ==========================================================
# FUNCIONES DEL ANALIZADOR
# ==========================================================

def detectar_singularidades(f, a, b):

    puntos = []

    try:

        sing = singularities(f, x)

        for s in sing:

            if not s.is_real:
                continue

            if a == -oo and b == oo:
                puntos.append(s)

            elif a == -oo:
                if s < b:
                    puntos.append(s)

            elif b == oo:
                if s > a:
                    puntos.append(s)

            else:
                if a < s < b:
                    puntos.append(s)

    except:
        pass

    return sorted(
        puntos,
        key=lambda z: float(z.evalf())
    )

def resolver_intervalo(f, izquierda, derecha):

    t = Symbol("t", real=True)

    if izquierda == -oo:

        return limit(
            integrate(f, (x, t, derecha)),
            t,
            -oo
        )

    elif derecha == oo:

        return limit(
            integrate(f, (x, izquierda, t)),
            t,
            oo
        )

    else:

        return simplify(
            integrate(f, (x, izquierda, derecha))
        )

def resolver_integral(f, a, b):

    puntos = detectar_singularidades(f, a, b)

    # Si no hay discontinuidades
    if len(puntos) == 0:

        return resolver_intervalo(f, a, b)

    resultado = 0

    izquierda = a

    for s in puntos:

        # límite por la izquierda
        eps = Symbol("eps", positive=True)

        parte = limit(
            integrate(f, (x, izquierda, s - eps)),
            eps,
            0
        )

        if parte.has(oo, -oo, zoo, nan):
            return oo

        resultado += parte

        # límite por la derecha
        izquierda = s + eps

    # último intervalo

    if izquierda != b:

        if izquierda.has(Symbol("eps")):

            parte = limit(
                integrate(f, (x, izquierda, b)),
                eps,
                0
            )

        else:

            parte = resolver_intervalo(f, izquierda, b)

        if parte.has(oo, -oo, zoo, nan):
            return oo

        resultado += parte

    return simplify(resultado)



st.title("Analizador de Integrales")

st.write("""
Este programa analiza una integral definida y determina:

• Si la integral es Propia o Impropia.
         
• Si la integral Converge o Diverge.
         
• El valor de la integral cuando converge.

Instrucciones:

• Potencias: ^ o **

• Raíces: sqrt(...)

• Valor absoluto: abs(x) o |x|

• Infinito: oo o -oo

• Multiplicaciones: *

• Número de Euler: e o E (por ejemplo, e^(-x))

• Logaritmo natural: log(x) o ln(x)

• Logaritmo en base 10: log10(x)

• Factoriales: 5! o factorial(5)

• Logaritmo en otra base: log(x, base), por ejemplo log(x, 2)

• Pi: pi, Pi o π

• Trigonométricas: sin(x), sen(x), cos(x), tan(x), cot(x), sec(x), csc(x)

• Inversas: arcsin(x), arccos(x), arctan(x), arccot(x), arcsec(x), arccsc(x)

• Hiperbólicas: sinh(x), cosh(x), tanh(x)

• Ángulos en grados: escribe el símbolo °, por ejemplo sin(36°); se convierten a radianes automáticamente
• Si no escribes °, el ángulo se interpreta en radianes


""")

funcion = st.text_input("Función f(x)", "")
coef_txt = st.text_input("Coeficiente multiplicador", "1")
a_txt = st.text_input("Límite inferior", "")
b_txt = st.text_input("Límite superior", "")

if st.button("Analizar"):

    try:

        transformations = (
            standard_transformations +
            (implicit_multiplication_application,)
        )

        # Validar entradas antes de interpretarlas
        funcion = funcion.strip()
        a_txt = a_txt.strip()
        b_txt = b_txt.strip()
        coef_txt = coef_txt.strip() or "1"

        if not funcion:
            raise ValueError("Escribe la función f(x).")
        if not a_txt:
            raise ValueError("Escribe el límite inferior.")
        if not b_txt:
            raise ValueError("Escribe el límite superior.")

        # Interpretar función, límites y coeficiente con los mismos alias
        f = parsear_expresion(funcion, transformations)

        if a_txt == "oo":
            a = oo
        elif a_txt == "-oo":
            a = -oo
        else:
            a = parsear_expresion(a_txt, transformations)

        if b_txt == "oo":
            b = oo
        elif b_txt == "-oo":
            b = -oo
        else:
            b = parsear_expresion(b_txt, transformations)

        coef = parsear_expresion(coef_txt, transformations)
        # ============================
        # Mostrar la integral ingresada
        # ============================

        st.subheader("Integral ingresada")

        if coef == 1:
            st.latex(
                r"\int_{%s}^{%s} %s\,dx"
             % (latex(a), latex(b), latex(f))
            )
        else:
         st.latex(
              r"%s\int_{%s}^{%s} %s\,dx"
             % (latex(coef), latex(a), latex(b), latex(f))
         )

        # Determinar si es propia o impropia
        impropia = False

        if a in [oo, -oo] or b in [oo, -oo]:
            impropia = True

        try:
            sing = singularities(f, x)

            for s in sing:
                if s.is_real:

                    if a == -oo or b == oo:
                        impropia = True

                    elif a <= s <= b:
                        impropia = True

        except:
            pass

        tipo = "Impropia" if impropia else "Propia"

        # Resolver integral
        primitiva = integrate(f, x)

        hay_primitiva = not primitiva.has(Integral)

        if hay_primitiva:
            primitiva = simplify(primitiva)

        # Resolver la integral aunque SymPy no encuentre una primitiva elemental
        resultado = resolver_integral(f, a, b)

        # Aplicar el coeficiente multiplicador
        resultado = simplify(coef * resultado)

        # Determinar convergencia
        if resultado.has(oo, -oo, zoo, nan):
            estado = "Diverge"
        else:
            estado = "Converge"
        
        # ============================
        # Mostrar la primitiva
        # ============================

        st.subheader("Primitiva")

        if hay_primitiva:

         st.latex(
                r"F(x)=%s+C"
             % latex(primitiva)
         )

        else:

         st.warning(
              "No existe una primitiva elemental para esta función."
          )

         st.latex(
              latex(primitiva)
           )
        # ============================
        # Procedimiento
        # ============================

        st.subheader("Procedimiento")

        st.write("1. Se calcula la primitiva:")
        if not hay_primitiva:

         st.info(
             "La integral no posee una primitiva elemental, por lo que no puede desarrollarse mediante el Teorema Fundamental del Cálculo en términos de funciones elementales."
         )

        else:
         st.latex(
          r"F(x)=%s"
           % latex(primitiva)
        )

         st.write("2. Se aplica el Teorema Fundamental del Cálculo:")

        if a not in [oo, -oo] and b not in [oo, -oo]:

         st.latex(
             r"\int_a^b f(x)\,dx = F(b)-F(a)"
         )

         Fa = primitiva.subs(x, a)
         Fb = primitiva.subs(x, b)

         st.latex(
                r"F(%s)=%s"
                % (latex(a), latex(Fa))
         )

         st.latex(
              r"F(%s)=%s"
              % (latex(b), latex(Fb))
         )

         st.latex(
                r"%s-(%s)=%s"
              % (
                  latex(Fb),
                 latex(Fa),
                 latex(resultado)
               )
         )

        elif b == oo and a != -oo:

         st.write("La integral es impropia porque el límite superior es infinito.")

         st.latex(
                r"\int_{%s}^{\infty}%s\,dx"
                % (latex(a), latex(f))
            )

         st.latex(
              r"=\lim_{t\to\infty}\int_{%s}^{t}%s\,dx"
              % (latex(a), latex(f))
          )

         st.latex(
               r"=%s"
                % latex(resultado)
         )

        elif a == -oo and b != oo:

         st.write("La integral es impropia porque el límite inferior es infinito.")

         st.latex(
             r"\int_{-\infty}^{%s}%s\,dx"
             % (latex(b), latex(f))
          )

         st.latex(
             r"=\lim_{t\to-\infty}\int_{t}^{%s}%s\,dx"
             % (latex(b), latex(f))
         )

         st.latex(
                r"=%s"
                % latex(resultado)
            )

        else:

         st.write("La integral tiene ambos límites infinitos.")

         st.latex(
              r"\int_{-\infty}^{\infty}%s\,dx"
              % latex(f)
          )

         st.write("Se divide en dos integrales impropias y se evalúan mediante límites.")

         st.latex(
               r"=%s"
              % latex(resultado)
            )


        st.subheader("Resultado")

        if tipo == "Propia":
            st.success("Tipo: Propia")
        else:
            st.warning("Tipo: Impropia")

        if estado == "Converge":
          st.success("Comportamiento: Converge")

          st.info(f"Valor exacto: {resultado}")

          st.info(f"Valor aproximado: {N(resultado, 10)}")

        else:
         st.error("Comportamiento: Diverge")
            
        # =====================================================
        # GRAFICAR LA FUNCIÓN
        # =====================================================

        st.subheader("Gráfica de la función")

        # Convertir la función de SymPy a NumPy
        f_numpy = lambdify(x, f, "numpy")

        # Elegir intervalo de dibujo
        if a not in [oo, -oo] and b not in [oo, -oo]:

            ancho = abs(float(b) - float(a))

            margen = max(2, ancho)

            xmin = float(a) - margen
            xmax = float(b) + margen

        elif a not in [oo, -oo] and b == oo:

            xmin = float(a) - 5
            xmax = float(a) + 20

        elif b not in [oo, -oo] and a == -oo:

            xmin = float(b) - 20
            xmax = float(b) + 5

        else:

            xmin = -10
            xmax = 10
        # Crear puntos
        x_vals = np.linspace(xmin, xmax, 10000)

        # Evaluar función
        try:
            y_vals = f_numpy(x_vals)
        except:
         y_vals = np.full_like(x_vals, np.nan)

        # Evitar valores enormes
        y_vals = np.where(np.abs(y_vals) > 100, np.nan, y_vals)

        fig = go.Figure()

        # Curva
        fig.add_trace(
            go.Scatter(
               x=x_vals,
               y=y_vals,
              mode="lines",
             name="f(x)"
          )
        )

        # =====================================================
        # ÁREA DE LA INTEGRAL
        # =====================================================

        if a not in [oo, -oo] and b not in [oo, -oo]:

            mascara = (x_vals >= float(a)) & (x_vals <= float(b))

        elif a not in [oo, -oo] and b == oo:

          mascara = (x_vals >= float(a))

        elif b not in [oo, -oo] and a == -oo:

         mascara = (x_vals <= float(b))

        else:

          mascara = np.full_like(x_vals, False)

        fig.add_trace(
          go.Scatter(
             x=x_vals[mascara],
               y=y_vals[mascara],
              fill="tozeroy",
              mode="none",
               name="Área"
          )
        )

# =====================================================
# LÍMITES DE INTEGRACIÓN
# =====================================================

        if a not in [oo, -oo]:
            fig.add_vline(
             x=float(a),
                line_dash="dash"
         )

        if b not in [oo, -oo]:
          fig.add_vline(
               x=float(b),
              line_dash="dash"
          )

        # =====================================================
        # DISCONTINUIDADES
        # =====================================================

        try:

         sing = singularities(f, x)

         for s in sing:

             if s.is_real:

                 try:

                     fig.add_vline(
                        x=float(s),
                        line_dash="dot",
                        line_color="red"
                      )

                 except:
                     pass

        except:
            pass

        fig.update_layout(

         title="f(x)",

            xaxis_title="x",

         yaxis_title="f(x)",

         height=600

        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        **Leyenda de la gráfica**

        - **Líneas negras discontinuas:** límites de integración.
        - **Líneas rojas punteadas:** discontinuidades de la función.
        """)


    except Exception as e:
     st.error(f"Error: {e}")
