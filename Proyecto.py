import streamlit as st
from sympy import *
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

x = Symbol('x')

st.title("Analizador de Integrales")

st.write("""
Este programa analiza una integral definida y determina:

• Si la integral es Propia o Impropia.
         
• Si la integral Converge o Diverge.
         
• El valor de la integral cuando converge.

Instrucciones:

• Potencias: ^

• Raíces: sqrt()

• Infinito positivo: oo

• Multiplicaciones: *


""")

funcion = st.text_input("Función f(x)", "")
a_txt = st.text_input("Límite inferior", "")
b_txt = st.text_input("Límite superior", "")

if st.button("Analizar"):

    try:

        transformations = (
            standard_transformations +
            (implicit_multiplication_application,)
        )

        funcion = funcion.replace("^", "**")

        f = parse_expr(
            funcion,
            transformations=transformations
        )

        # Convertir límites
        if a_txt == "oo":
            a = oo
        elif a_txt == "-oo":
            a = -oo
        else:
            a = sympify(a_txt)

        if b_txt == "oo":
            b = oo
        elif b_txt == "-oo":
            b = -oo
        else:
            b = sympify(b_txt)

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
        resultado = integrate(f, (x, a, b))

        # Determinar convergencia
        if resultado.has(oo, -oo, zoo, nan):
            estado = "Diverge"
        else:
            estado = "Converge"

        st.subheader("Resultado")

        if tipo == "Propia":
            st.success("Tipo: Propia")
        else:
            st.warning("Tipo: Impropia")

        if estado == "Converge":
            st.success("Comportamiento: Converge")
            st.info(f"Valor de la integral: {resultado}")
        else:
            st.error("Comportamiento: Diverge")

    except Exception as e:
        st.error(f"Error: {e}")