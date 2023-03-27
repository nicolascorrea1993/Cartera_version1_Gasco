import streamlit as st
from multiapp import MultiApp
from apps import inicio, asignacion_cupo , reevalucion_cupo, analisis_cumplimiento


app = MultiApp()


# Add all your applications here
app.add_app("Inicio", inicio.app)
app.add_app("Reevaluación de cupo", reevalucion_cupo.app)
app.add_app("Asignación de cupo", asignacion_cupo.app)
app.add_app("Análisis de cumplimiento", analisis_cumplimiento.app)

# The main app
app.run()
