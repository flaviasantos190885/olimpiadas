import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# ====================
# Leitura dos dados
# ====================
df = pd.read_csv('Summer_olympic_Medals.csv')
df['Country_Name'] = df['Country_Name'].replace('United States', 'United States of America')
df = df[(df['Year'] >= 1992) & (df['Year'] <= 2020)]
df['Total_Medals'] = df['Gold'] + df['Silver'] + df['Bronze']

# ====================
# Inicialização do app
# ====================
app = dash.Dash(__name__)
server = app.server  

# ====================
# Layout
app.layout = html.Div(
    style={'backgroundColor': '#111111', 'color': 'white', 'fontFamily': 'Roboto, sans-serif', 'padding': '20px'},
    children=[
        html.H1("Dashboard de Medalhas Olímpicas - 1992 a 2020", style={'textAlign': 'center'}),

        html.Div([
            html.H3("Gráfico de Pizza - Medalhas por País"),
            html.Label("Selecione o país:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df['Country_Name'].unique())],
                value='United States of America',
                style={'color': 'black'}
            ),
            dcc.Graph(id='pie-chart')
        ], style={'margin-bottom': '50px'}),

        html.Div([
            html.H3("Gráfico de Área - Evolução por Medalhas"),
            html.Label("Tipo de medalha:"),
            dcc.RadioItems(
                id='area-medal-filter',
                options=[
                    {'label': 'Todos', 'value': 'All'},
                    {'label': 'Ouro', 'value': 'Gold'},
                    {'label': 'Prata', 'value': 'Silver'},
                    {'label': 'Bronze', 'value': 'Bronze'}
                ],
                value='All',
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            ),
            dcc.Graph(id='area-chart')
        ], style={'margin-bottom': '50px'}),

        html.Div([
            html.H3("Gráfico de Barra - Top Países em um Ano"),
            html.Label("Ano Olímpico (País sede):"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(y), 'value': y} for y in sorted(df['Year'].unique())],
                value=2016,
                style={'color': 'black'}
            ),
            html.Label("Tipo de medalha:"),
            dcc.RadioItems(
                id='bar-medal-filter',
                options=[
                    {'label': 'Todos', 'value': 'All'},
                    {'label': 'Ouro', 'value': 'Gold'},
                    {'label': 'Prata', 'value': 'Silver'},
                    {'label': 'Bronze', 'value': 'Bronze'}
                ],
                value='All',
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            ),
            dcc.Graph(id='bar-chart')
        ])
    ]
)



# ====================
# Callbacks
# ====================
@app.callback(
    Output('pie-chart', 'figure'),
    Input('country-dropdown', 'value')
)
def update_pie_chart(selected_country):
    country_data = df[df['Country_Name'] == selected_country]
    fig = px.pie(
        names=['Ouro', 'Prata', 'Bronze'],
        values=[country_data['Gold'].sum(), country_data['Silver'].sum(), country_data['Bronze'].sum()],
        title=f'Medalhas de {selected_country}',
        color_discrete_sequence=['gold', 'silver', '#cd7f32']  # Bronze
    )
    fig.update_layout(
        paper_bgcolor='#111111',
        plot_bgcolor='#111111',
        font_color='white'
    )
    return fig
@app.callback(
    Output('area-chart', 'figure'),
    Input('area-medal-filter', 'value')
)
def update_area_chart(medal_filter):
    df_area = df.copy()
    if medal_filter == 'All':
        df_area['Value'] = df_area['Total_Medals']
    else:
        df_area['Value'] = df_area[medal_filter]

    top_countries = df_area.groupby('Country_Name')['Value'].sum().nlargest(10).index
    df_top = df_area[df_area['Country_Name'].isin(top_countries)]
    df_top_grouped = df_top.groupby(['Country_Name', 'Year'])['Value'].sum().reset_index()

    fig = px.area(
        df_top_grouped,
        x='Year',
        y='Value',
        color='Country_Name',
        title=f'Top 10 países por medalhas ({medal_filter if medal_filter != "All" else "Todas"})'
    )
    fig.update_layout(
        paper_bgcolor='#111111',
        plot_bgcolor='#111111',
        font_color='white'
    )
    return fig
@app.callback(
    Output('bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('bar-medal-filter', 'value')
)
def update_bar_chart(selected_year, medal_filter):
    df_year = df[df['Year'] == selected_year].copy()
    df_year['Value'] = df_year['Total_Medals'] if medal_filter == 'All' else df_year[medal_filter]

    top_countries = df_year.groupby('Country_Name')['Value'].sum().nlargest(10).reset_index()

    fig = px.bar(
        top_countries,
        x='Country_Name',
        y='Value',
        color='Value',
        color_continuous_scale='cividis',
        title=f'Top 10 países em {selected_year} por medalhas ({medal_filter if medal_filter != "All" else "Todas"})'
    )
    fig.update_layout(
        paper_bgcolor='#111111',
        plot_bgcolor='#111111',
        font_color='white'
    )
    return fig
