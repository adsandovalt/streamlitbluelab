import io
#from multiprocessing.sharedctypes import Value
#from logging import _Level
#from tkinter import Y
#from turtle import position, right
from unicodedata import name
import pandas as pd 
import plotly.express as px
import streamlit as st
from statistics import mode
import pingouin as pg


#Configuración de forma de la página
st.set_page_config(page_title="Humedad Blue LAB",
                   page_icon=":bar_chart:",
                   layout="wide"
                   )

#Lectura de los datos del excel
data = pd.read_excel(io="DVISTA.xlsx", engine='openpyxl', sheet_name='Hoja1')
data2 = pd.read_excel(io="Seguimiento Finca Vista BLOQUES.xlsx", engine='openpyxl', sheet_name='RIEGO', usecols="A,B,C,D,F,G,H,I,K,L,N,M,O")
#st.dataframe(data)

#"SLIDE BAR......................................................................................................................................................................................................................."
#Definición de los filtros para requeridos para el dataframe cargado
st.sidebar.header("Inserte los filtros: ")

#Campo de busqueda del BLOQUE
greenhouse = st.sidebar.multiselect(
    'Seleccione el BLOQUE: ',
    options = data["BLOQUE"].unique(),
    #default = data["BLOQUE"].unique()
)

#Campo de busqueda del VÁLVULA
valve = st.sidebar.multiselect(
    'Seleccione la VÁLVULA: ',
    options = data["VÁLVULA"].unique(),
    #default = data["VÁLVULA"].unique()
)

#Campo de busqueda del FECHA
date = st.sidebar.multiselect(
    'Seleccione la FECHA: ',
    options = data["FECHA"].unique(),
    default = data["FECHA"].unique()
)


#"QUERY ........................................................................................................................................................................................................................"
#Creación de dataframe FILTRADO POR BLOQUE, VÁLVULA Y FECHA. Este se utiliza en el análisis de la dipsersiones y demás en un DÍA PUNTUAL
df_filter = data.query(
    "BLOQUE == @greenhouse & VÁLVULA == @valve & FECHA == @date"
)
#Creación de dataframe FILTRADO POR BLOQUE, VÁLVULA. Datos vienen de base de drenajes y demás en un DÍA PUNTUAL
df_filter2 = data2.query(
    "BLOQUE == @greenhouse & VÁLVULA == @valve & FECHA == @date"
)


#Creación de dataframe FILTRADO POR BLOQUE, VÁLVULA. Este se utiliza en el análisis de las TENDENCIAS DE LOS DATOS
df_plot = data.query(
    "BLOQUE == @greenhouse & VÁLVULA == @valve"
)
#Creación de dataframe FILTRADO POR BLOQUE, VÁLVULA. Datos vienen de base de drenajes y demás
df_plot2= data2.query(
   "BLOQUE == @greenhouse & VÁLVULA == @valve"
)


#Agrupa las variables por  VÁLVULA y FECHA
prue = pd.DataFrame(df_plot).groupby(["VÁLVULA", "FECHA"]).mean()

#Saca la FECHA  de cada uno de los registros
x2 = pd.DataFrame(prue.index.get_level_values('FECHA'))
#Saca la válvula de cada uno de los registros
x3 = pd.DataFrame(prue.index.get_level_values('VÁLVULA'))

#Concatena la fecha de medición y la respectva válvula, sin importar si se repiten las fechas
pruebafinal = pd.concat([x2, x3], axis=1)

#Creación de dataframe que agrupa por fecha. Este ya esta filtrado por el BLOQUE y la VÁLVULA. DATOS DE SENSOR 
data_f = pd.DataFrame(df_plot).groupby("FECHA").mean()

#Creación de dataframe que agrupa por fecha. Este ya esta filtrado por el BLOQUE y la VÁLVULA. DATOS DE DRENAJES Y DEMÁS
data_f2 = pd.DataFrame(df_plot2).groupby("FECHA").mean()

#data_total = pd.merge(data_f,df_plot2, on='FECHA')
#data_total = data_total.groupby("FECHA").mean()

#Encabezado de inicio
st.title("Datos de sensor")

#"MAINPAGE--------------------------------------"
#Calculo de promedio y desviación estándar de los datos DE HUMEDAD. 
moisture = round(df_filter["θv C (%)"].mean()*100,2)
moisture_des = round(df_filter["θv C (%)"].std()*100,2)
#Calculo de la cantidad DE DATOS análizados. 
moisture_num = round(df_filter["θv C (%)"].count(),0)

#Calculo de promedio y desviación estándar de los datos DE CONDUCTIVIDAD. 
condutivity = round(df_filter["CE C (dS/m)"].mean(),2)
condutivity_des = round(df_filter["CE C (dS/m)"].std(),2)

#Calculo de promedio y desviación estándar de los datos DE TEMPERATURA. 
temperature = round(df_filter["T (°C)"].mean(),2)
temperature_des = round(df_filter["T (°C)"].std(),2)

#Toma los valores filtrados del día seleccionado. Estos datos vienen de la base de seguimiento
drenaje = round(df_filter2["DRENAJE (%)"].mean()*100,2)
lamina = round(df_filter2["VOLUMEN REGADO (L)"].mean(),1)
eficiencia = round(df_filter2["EFICIENCIA (%)"].mean()*100,2)

#Cálculo de la moda para el día puntual de análisis
try:    
    moisture_mod = round(mode(df_filter["θv C (%)"]*100),2)
    conductivity_mod = round(mode(df_filter["CE C (dS/m)"]),2)
    temperature_mod = round(mode(df_filter["T (°C)"]),2)
except ValueError:
    #Cuando falla cálculando la moda es porque NO hay DATOS
    st.subheader(f'Sin datos')
    moisture_mod = "Sin datos"
    conductivity_mod = "Sin datos"
    temperature_mod = "Sin datos"

#Impresión de número de datos que se están análizando
st.subheader(f'Número de datos:  {moisture_num}')
st.markdown("---")


#Creación de tres columnas en el dashboard
left_column, middle_column, right_column = st.columns(3)

#Impresión de los datos de interes de HUMEDAD
with left_column:
    #st.subheader(f'θv (%) promedio:  {moisture}')
    st.metric(label='θv (%) promedio:', value = moisture, delta=f"{round(moisture-50, 2)}", delta_color="inverse")
    #st.subheader(f'θv (%) std:  {moisture_des}')
    st.metric(label='θv (%) std:', value = moisture_des)

    try:
        st.metric(label='θv (%) moda:', value = moisture_mod)
        #st.subheader(f'θv (%) moda:  {moisture_mod}')
    except ValueError:
        st.subheader(f'Sin datos')

    try:
        st.metric(label='Drenaje (%):', value = drenaje)
    except ValueError:
        st.subheader(f'Seleccione un día')



#Impresión de los datos de interes de CONDUCTIVIDAD
with middle_column:
    #st.subheader(f'CE (dS/m) promedio:  {condutivity}')
    st.metric(label="CE (dS/m) promedio:", value = condutivity, delta=f"{round(condutivity-2.5, 2)}", delta_color="inverse")
    #st.subheader(f'CE (dS/m) std:  {condutivity_des}')
    st.metric(label="CE (dS/m) std:", value=condutivity_des)
    try:
        #st.subheader(f'CE (dS/m) moda:  {conductivity_mod}')
        st.metric(label="CE (dS/m) moda:", value=conductivity_mod)
    except ValueError:
        st.subheader(f'Sin datos')

    try:    
        st.metric(label='Lámina regada (L):', value = lamina)
    except ValueError:
        st.subheader(f'Seleccione un día')


#Impresión de los datos de interes de TEMPERATURA
with right_column:
    #st.subheader(f'T (°C) promedio:  {temperature}')
    st.metric(label="T (°C) promedio:", value=temperature, delta=f"{round(temperature-15, 2)}")
    #st.subheader(f'T (°C) std:  {temperature_des}')
    st.metric(label="T (°C) std:", value=temperature_des)
    try:
        #st.subheader(f'T (°C) moda:  {temperature_mod}')
        st.metric(label= "T (°C) moda:", value=temperature_mod)
    except ValueError:
        st.subheader(f'Sin datos')

    try:
        st.metric(label='Eficiencia de riego (%):', value = eficiencia)
    except ValueError:
        st.subheader(f'Seleccione un día')

st.markdown("---")

#Creación de tres columnas en el dashboard HUMEDAD VOLUMÉTRICA
left_column,  right_column = st.columns(2)

#Impresión de los boxplot de las tres variables análizadas
with left_column:

    fig_boxplor_moisture = px.violin(df_filter, y = round(df_filter["θv C (%)"]*100, 2), title=f"<b>HUMEDAD VOLUMÉTRICA del sustrato<b> {valve}", width=500, range_y=[0,100], color="VÁLVULA", box=True)
    fig_boxplor_moisture.update_layout(xaxis_title="Válvula", yaxis_title="θv (%)")
    st.plotly_chart(fig_boxplor_moisture)

    
    fig_boxplor_ce = px.violin(df_filter, y = round(df_filter["CE C (dS/m)"], 2), title= f"<b>CONDUCTIVIDAD ELÉCTRICA del sustrato<b> {valve}", width=500, range_y=[0,5], color="VÁLVULA", box=True)
    fig_boxplor_moisture.update_layout(xaxis_title="Válvula", yaxis_title="CE (dS/m)")
    st.plotly_chart(fig_boxplor_ce) 

#Impresión de los histogramas de las DOS variables análizadas (HUMEDAD Y CONDUCTIVIDAD ELÉCTRICA)
with right_column:

    fig_histo_moisture = px.histogram(df_filter, round(df_filter["θv C (%)"]*100, 0), title=f'<b>Histograma de HUMEDAD VOLUMÉTRICA {valve}<b>', width=500, nbins=10, range_x=[20,80], histfunc="count", text_auto=True, color="VÁLVULA")
    st.plotly_chart(fig_histo_moisture)

    fig_histo_ce = px.histogram(df_filter, round(df_filter["CE C (dS/m)"], 2), title= f"<b>Histograma de CONDUCTIVIDAD ELÉCTRICA<b> {valve}", width=500, nbins=10, range_x=[0,5],histfunc="count", text_auto=True, color="VÁLVULA")
    st.plotly_chart(fig_histo_ce)

st.markdown("---")

try:
    #Impresión de los datos historicos de HUMEDAD registrados para cada una de las válvulas. Provienen de dafa_f
    fig_plot_all_mostiure = px.line(x=pruebafinal["FECHA"], y = prue["θv C (%)"]*100,title= f"<b>Variación de HUMEDAD en el sustrato<b> {valve}", width=1200, markers=True, height=400, color=pruebafinal["VÁLVULA"], range_y=[30,60])
    fig_plot_all_mostiure.update_traces(textposition="top center")
    fig_plot_all_mostiure.update_layout(xaxis_title="Date", yaxis_title="θv (%)")
    st.plotly_chart(fig_plot_all_mostiure)


    #Impresión de los datos historicos de CONDUCTIVIDAD ELÉCTRICA registrados para cada una de las válvulas. Provienen de dafa_f
    fig_plot_all_CE = px.line(x=pruebafinal["FECHA"], y= prue["CE C (dS/m)"], title= f"<b>Variación de CONDUCTIVIDAD ELÉCTRICA en el sustrato<b> {valve}", range_y=[0.5,3.5], width=1200, markers=True, color=pruebafinal["VÁLVULA"], height=400)
    fig_plot_all_CE.update_traces(textposition="bottom center")
    fig_plot_all_CE.update_layout(xaxis_title="Date", yaxis_title="CE (dS/m)")
    st.plotly_chart(fig_plot_all_CE)
except ValueError:
    st.title(f"Seleccione un bloque y válvula")

try:
    #Impresión de los datos historicos de CONDUCTIVIDAD ELÉCTRICA registrados para cada una de las válvulas. Provienen de dafa_f
    fig_plot_all_DRENAJE = px.line(x = df_plot2["FECHA2"], y= df_plot2["DRENAJE (%)"], title= f"<b>Variación de DRENAJE (%) en el sustrato<b> {valve}", width=1200, height=400, color=df_plot2["VÁLVULA"], range_y=[0,1], markers=True)
    #fig_plot_all_DRENAJE.update_traces(textposition="bottom center")
    fig_plot_all_DRENAJE.update_layout(xaxis_title="Date", yaxis_title="DRENAJE (%)")
    st.plotly_chart(fig_plot_all_DRENAJE)

except ValueError:
    st.title(f"Seleccione un bloque y válvula")

try:
    #Impresión de los datos historicos de CONDUCTIVIDAD ELÉCTRICA registrados para cada una de las válvulas. Provienen de dafa_f
    fig_plot_all_TEM = px.line(x=pruebafinal["FECHA"], y = prue["T (°C)"] ,title= f"<b>Variación de TEMPERATURA en el sustrato<b> {valve}", range_y=[5,20], width=1200, markers=True, height=400, color=pruebafinal["VÁLVULA"] )
    fig_plot_all_TEM.update_traces(textposition="bottom center")
    fig_plot_all_TEM.update_layout(xaxis_title="Date", yaxis_title="T (°C)")
    st.plotly_chart(fig_plot_all_TEM)
except ValueError:
    st.title(f"Seleccione un bloque y válvula")

#correlacion = data_total.drop(["BLOQUE", "VÁLVULA", "EFICIENCIA (%)", "GOTERO (ml)", f'# GOTEROS', 'DRENAJE (L)'], axis=1).corr()
#correlacion.style.background_gradient(cmap="coolwarm")
#ant = px.imshow(round(correlacion,3), text_auto=True, title="<b>CORRELACIONES entre variables<b>", width=600, height=600, range_color=[-1,1])
#st.plotly_chart(ant)

#pruebasss = px.line(y=prue["θv C (%)"])
#st.plotly_chart(pruebasss)

#correlacion2 = pd.DataFrame(pg.pairwise_corr(data=data_total.drop(["BLOQUE", "VÁLVULA", "EFICIENCIA (%)", "GOTERO (ml)", f'# GOTEROS', 'DRENAJE (L)'], axis=1), method="pearson"))
#ant2 = px.imshow(round(correlacion2,3), text_auto=True, title="<b>CORRELACIONES entre variables<b>", width=600, height=600, range_color=[-1,1])
#st.dataframe(correlacion2)

st.markdown("---")
st.text("@adsandovalt")







