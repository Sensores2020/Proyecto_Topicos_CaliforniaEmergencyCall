from flask import Flask
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import leafmap.foliumap as leafmap
from dash import Dash, dash_table
from collections import OrderedDict
import makemap as mkp
import json
server=Flask(__name__)

app= dash.Dash(__name__, server=server,external_stylesheets=[dbc.themes.CYBORG])
def conectarDB():
    con = create_engine("postgresql://meexscxpivvupa:043b79c27a38f3a8cd91c8158309cc23d4271e6bdc651f8782643b55bbaed8d3@ec2-23-23-151-191.compute-1.amazonaws.com:5432/d91o57bci3t4g3")
    return con


con=conectarDB()
paratabla = OrderedDict(
    [
        ("NOMBRE", ["Tuolumne", "Yuba", "Humboldt", "Santa Mónica", "Marin", " Santa Cruz"," Napa"," Nevado","Del norte"," Butte"," Madera"," El Dorado"," Fresno"," Plumas"," Shasta"," Lassen"," placer"," Sierra"," Mendocino"," Alpine"," Tulare"," Glenn"," Modoc"," Colusa"," Lake"," Siskiyou"," Trinity"," Amador"," Tehama"," Calaveras"," Sonoma"]),
        ("INICIALES", ["TUO ", " YUB ", "HUM", "SMO", "MAR", "SCR","NAP","NEV","DEL","BUT","MAD","ELD","FRE","PLU","SHA","LAS","PLA","SIE","MEN","ALP","TUL","GLE","MOD","COL","LAK","SIS","TRI","AMA","TEH","CAL","SON"]),
    ]
)
tabla = pd.DataFrame(paratabla)

app.layout = html.Div([



        dbc.Row(dbc.Col(html.Div(html.H1("Llamadas de Emergencia California", style={"color":"red", "font-family":"Gill Sans Extrabold"})), width={"size":"auto", "offset":2} )),
        dbc.Row(
            [
                dbc.Col(html.Div([
                    html.B("LLamadas por:"),
                    dcc.Checklist([ {"label": html.Div([  html.Img(src="/assets/img/fuego.webp", style={'width':40, 'height':40}),
                    html.Div("INCENDIO", style={'font-size': 15, 'padding-left': 10}),], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            "value": "INCENDIO", },
        { "label": html.Div([ html.Img(src="/assets/img/insect.png", style={'width':40, 'height':40}), html.Div("INSECTOS", style={'font-size': 15, 'padding-left': 10}),
                ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),"value": "INSECTOS",},
        {"label": html.Div([html.Img(src="/assets/img/gasolina.png", style={'width':40, 'height':40}),html.Div("COMBUSTIBLE", style={'font-size': 15, 'padding-left': 10}),
                ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),"value": "COMBUSTIBLE",},], ["INCENDIO"],inline=False, id="Checklist"),
                    html.Div([html.Br(), html.B("Nombre de condados"),
                        dash_table.DataTable(data=tabla.to_dict('records'), columns=[{'id': c, 'name': c} for c in tabla.columns],   style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'center'
        } for c in ['NOMBRE', 'INICIALES']
    ],
    style_data={
        'color': 'black',
        'backgroundColor': 'white'
    },
    style_table={
    'width': '200', 
    'height': '300px',
    'overflowY': 'scroll'

    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(220, 220, 220)',
        }
    ],
    style_header={
        'backgroundColor': 'rgb(210, 210, 210)',
        'color': 'black',
        'fontWeight': 'bold'
    })


                        ]) #para la tabla 

            ] ),  width={"size": 2, "order": 1, "offset": 1}),

                dbc.Col(html.Div([
                    html.B("CONDADOS:"), 
                    dcc.Dropdown(['TODOS','TUO','YUB','HUM','SMO','MAR','SCR','NAP','NEV','DEL',
                        'BUT','MAD','ELD','FRE','PLU','SHA','LAS','PLA','SIE','MEN','ALP','TUL','GLE',
                        'MOD','COL','LAK','SIS','TRI','AMA','TEH','CAL','SON'], 'TODOS', id="eleccion_condado"),
                    html.Div(html.Br()),
                    html.Div(html.Iframe(id="mapa_grafico",width=550, height=400),style={"width":"800", "height":"500"}),
                    html.B("AÑO 20"),
                    dcc.RangeSlider(19, 22, 1, value=[19, 20], id="rango_año") 
                    ]), width={"size": 5, "order": 2}), #Div before Col

                dbc.Col(html.Div([html.Br(),html.Br(),html.Br(), html.Br(),
                    dcc.Graph(id="grafica_datos")
                    ]), width={"size": 3, "order": 3}),
            ]
        ),
    ]




 )
server = app.server
app.title='Call Fire Emergency'

@app.callback( [Output("mapa_grafico", "srcDoc"),
    Output("grafica_datos", "figure")],
    [Input("Checklist", "value"),
    Input("eleccion_condado", "value"),
    Input("rango_año", "value") ])

def update_dash(lista, condado, rango):

    if(len(lista)==0):
        print("lista vacia")
    else:
        if(len(lista)==3):
            busqueda="""SELECT "EM_NUM", "EM_YEAR", "COUNTY" AS "CONDADO", "FIRE" AS "FUEGO", "INSECT" AS "INSECTOS", "FUEL_HAZRD" AS "PELIGRO_COMBUSTUTIBLE", 
            "ACCEPTED" AS "ACEPTADA", "EXPIRATION"  AS "VENCIMIENTO",  "geom"
            FROM CALL_FIRE WHERE ("FIRE" = 1 OR "INSECT" = 1 OR "FUEL_HAZRD" = 1) AND "EM_YEAR"  BETWEEN '20{}' AND '20{}'

            """.format(rango[0], rango[1])
        if(len(lista)==2):

            if(("INCENDIO" in lista) and ("INSECTOS" in lista)):
                busqueda="""SELECT "EM_NUM", "EM_YEAR", "COUNTY" AS "CONDADO", "FIRE" AS "FUEGO", "INSECT" AS "INSECTOS", "FUEL_HAZRD" AS "PELIGRO_COMBUSTUTIBLE", 
            "ACCEPTED" AS "ACEPTADA", "EXPIRATION"  AS "VENCIMIENTO",  "geom"
                from call_fire where ("FIRE" = 1  OR "INSECT" = 1) and "EM_YEAR"   BETWEEN '20{}' and '20{}'
            """.format(rango[0], rango[1])

            if(("INCENDIO" in lista) and ("COMBUSTIBLE" in lista)):
                busqueda="""SELECT "EM_NUM", "EM_YEAR", "COUNTY" AS "CONDADO", "FIRE" AS "FUEGO", "INSECT" AS "INSECTOS", "FUEL_HAZRD" AS "PELIGRO_COMBUSTUTIBLE", 
            "ACCEPTED" AS "ACEPTADA", "EXPIRATION"  AS "VENCIMIENTO",  "geom"
                from call_fire where ("FIRE" = 1 OR "FUEL_HAZRD" = 1)  and "EM_YEAR"  BETWEEN '20{}' and '20{}'
            """.format(rango[0], rango[1])

            if(("INSECTOS" in lista) and ("COMBUSTIBLE" in lista)):
                busqueda="""SELECT "EM_NUM", "EM_YEAR", "COUNTY" AS "CONDADO", "FIRE" AS "FUEGO", "INSECT" AS "INSECTOS", "FUEL_HAZRD" AS "PELIGRO_COMBUSTUTIBLE", 
            "ACCEPTED" AS "ACEPTADA", "EXPIRATION"  AS "VENCIMIENTO",  "geom"
                from call_fire where ("FUEL_HAZRD" = 1 OR "INSECT" = 1) and "EM_YEAR"  BETWEEN '20{}' and '20{}'
            """.format(rango[0], rango[1])

        if(len(lista)==1):
            if("INCENDIO" in lista):
                busqueda="""SELECT "EM_NUM", "EM_YEAR", "COUNTY" AS "CONDADO", "FIRE" AS "FUEGO", "INSECT" AS "INSECTOS", "FUEL_HAZRD" AS "PELIGRO_COMBUSTUTIBLE", 
            "ACCEPTED" AS "ACEPTADA", "EXPIRATION"  AS "VENCIMIENTO",  "geom"
                from call_fire where "FIRE" = 1 and "EM_YEAR"  BETWEEN '20{}' and '20{}'
            """.format(rango[0], rango[1])

            if("INSECTOS" in lista):
                busqueda="""SELECT "EM_NUM", "EM_YEAR", "COUNTY" AS "CONDADO", "FIRE" AS "FUEGO", "INSECT" AS "INSECTOS", "FUEL_HAZRD" AS "PELIGRO_COMBUSTUTIBLE", 
            "ACCEPTED" AS "ACEPTADA", "EXPIRATION"  AS "VENCIMIENTO",  "geom"
                from call_fire where ("INSECT" = 1 and "FIRE"=0) and "EM_YEAR"  BETWEEN '20{}' and '20{}'
            """.format(rango[0], rango[1])

            if("COMBUSTIBLE" in lista):
                busqueda="""SELECT "EM_NUM", "EM_YEAR", "COUNTY" AS "CONDADO", "FIRE" AS "FUEGO", "INSECT" AS "INSECTOS", "FUEL_HAZRD" AS "PELIGRO_COMBUSTUTIBLE", 
            "ACCEPTED" AS "ACEPTADA", "EXPIRATION"  AS "VENCIMIENTO",  "geom"

                from call_fire Where "FUEL_HAZRD" = 1  and "EM_YEAR"  BETWEEN '20{}' and '20{}'
            """.format(rango[0], rango[1])

        informacion=gpd.read_postgis(busqueda, con=con)
        if(condado=="TODOS"):
            final=informacion
        else:
            final=informacion[informacion.CONDADO=="{}".format(condado)]
        #informacion=gpd.read_postgis(busqueda, con)




        mapa= mkp.crearMapa(final)
        trace5= go.Bar(y=final['EM_NUM'], name="fuego", x=final['EM_YEAR'],marker=dict(
        color='rgba(249, 8, 4, 0.6)',line=dict(color='rgba(249, 8, 4, 1.0)', width=3)))

        grafica=figure={'data': [trace5],'layout': go.Layout(title="California Call Emergency")}
        return  mapa._repr_html_(), grafica

        






if __name__ == "__main__":
    app.run_server(debug=True)

#dev_tools_ui=False,dev_tools_props_check=False
