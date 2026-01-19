import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load the data
# Note: Ensure 'TelecomCustomerChurn.csv' is in the same directory
df = pd.read_csv('TelecomCustomerChurn.csv')

# Pre-calculate global stats
total_customers = len(df)
churn_rate = (df['Churn'] == 'Yes').mean() * 100
avg_tenure = df['Tenure'].mean()

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# THIS LINE IS CRUCIAL FOR RENDER
server = app.server

COLORS = {'Yes': '#FF4B4B', 'No': '#00CC96', 'bg': '#f4f7f6', 'text': '#2c3e50'}

app.layout = html.Div(style={'backgroundColor': COLORS['bg'], 'minHeight': '100vh', 'padding': '20px'}, children=[
    
    # Header Section
    html.Div([

        html.H1(
    "Cyber Hybrid",
    style={
        "margin": "0",
        "fontWeight": "700",
        "letterSpacing": "0.5px"
    }
)
,
                        html.Img(
                            src="/assets/Cyber Hybrid Logo.png", 
                            style={"height": "60px", "marginBottom": "20px", "borderRadius": "50px"}
                        ),
        html.H1("Telecom Customer Retention Insights", style={'textAlign': 'left', 'color': COLORS['text'], 'fontWeight': 'bold'}),
        html.P("Deep dive analysis into customer churn patterns and behavioral drivers.", style={'color': '#7f8c8d'}),
        
        # Insights List
        html.Ul([
            html.Li("Month-to-month contracts show significantly higher churn risk."),
            html.Li("Customers with low tenure churn disproportionately within the first year."),
            html.Li("Electronic check users churn more than other payment methods."),
            html.Li("Higher monthly charges correlate with early churn behavior.")
        ], style={'color': '#34495e', 'fontSize': '14px'}),

        # Global Filter
        html.Label("Global Contract Filter:"),
        dcc.Dropdown(
            id='contract-filter',
            options=[{'label': c, 'value': c} for c in df['Contract'].unique()],
            multi=True,
            placeholder="Filter by Contract Type"
        )
    ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),

    # KPI Row
    html.Div(id='kpi-container', className="row", style={'marginBottom': '20px'}),

    # Tabs Container
    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        dcc.Tab(label='Executive Overview', value='tab-1'),
        dcc.Tab(label='Demographics', value='tab-2'),
        dcc.Tab(label='Service Portfolio', value='tab-3'),
        dcc.Tab(label='Billing & Contract', value='tab-4'),
        dcc.Tab(label='Financial Deep Dive', value='tab-5'),
    ]),

    html.Div(id='tabs-content-inline', style={'padding': '20px', 'backgroundColor': 'white', 'border': '1px solid #d6d6d6', 'borderRadius': '0 0 10px 10px'})
])

@app.callback(
    [Output('tabs-content-inline', 'children'),
     Output('kpi-container', 'children')],
    [Input('tabs-styled-with-inline', 'value'),
     Input('contract-filter', 'value')]
)
def render_content(tab, selected_contracts):
    # Filter data based on dropdown
    filtered_df = df.copy()
    if selected_contracts:
        filtered_df = df[df['Contract'].isin(selected_contracts)]

    # Update KPIs based on filter
    cur_total = len(filtered_df)
    cur_churn = (filtered_df['Churn'] == 'Yes').mean() * 100 if cur_total > 0 else 0
    
    kpi_layout = [
        html.Div([html.H4(f"{cur_total:,}"), html.P("Customers")], className="three columns", style={'backgroundColor': 'white', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '10px'}),
        html.Div([html.H4(f"{cur_churn:.1f}%", style={'color': COLORS['Yes']}), html.P("Churn Rate")], className="three columns", style={'backgroundColor': 'white', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '10px'}),
        html.Div([html.H4(f"{filtered_df['Tenure'].mean():.1f} mo"), html.P("Avg Tenure")], className="three columns", style={'backgroundColor': 'white', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '10px'}),
        html.Div([html.H4(f"${filtered_df['MonthlyCharges'].mean():.2f}"), html.P("Avg Bill")], className="three columns", style={'backgroundColor': 'white', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '10px'}),
    ]

    # Tab Logic
    if tab == 'tab-1':
        fig_pie = px.pie(filtered_df, names='Churn', title='Churn Proportion', hole=0.5, color='Churn', color_discrete_map=COLORS)
        fig_tenure = px.histogram(filtered_df, x='Tenure', color='Churn', title='Tenure Distribution (Months)', color_discrete_map=COLORS)
        content = html.Div([
            html.Div([dcc.Graph(figure=fig_pie)], className="six columns"),
            html.Div([dcc.Graph(figure=fig_tenure)], className="six columns")
        ], className="row")
        
    elif tab == 'tab-2':
        cols = ['Gender', 'SeniorCitizen', 'Partner', 'Dependents']
        graphs = []
        for col in cols:
            temp = filtered_df.groupby([col, 'Churn']).size().reset_index(name='count')
            fig = px.bar(temp, x=col, y='count', color='Churn', barmode='group', title=f'Churn by {col}', color_discrete_map=COLORS)
            graphs.append(html.Div([dcc.Graph(figure=fig)], className="six columns"))
        content = html.Div([html.Div([graphs[0], graphs[1]], className="row"), html.Div([graphs[2], graphs[3]], className="row")])

    elif tab == 'tab-3':
        services = ['InternetService', 'OnlineSecurity', 'TechSupport', 'StreamingTV']
        graphs = [html.Div([dcc.Graph(figure=px.histogram(filtered_df, x=s, color='Churn', barmode='group', title=f'Impact of {s}', color_discrete_map=COLORS))], className="six columns") for s in services]
        content = html.Div([html.Div([graphs[0], graphs[1]], className="row"), html.Div([graphs[2], graphs[3]], className="row")])

    elif tab == 'tab-4':
        fig_contract = px.histogram(filtered_df, x='Contract', color='Churn', barmode='group', title='Churn by Contract Type', color_discrete_map=COLORS)
        fig_payment = px.histogram(filtered_df, x='PaymentMethod', color='Churn', barmode='group', title='Churn by Payment Method', color_discrete_map=COLORS)
        content = html.Div([html.Div([dcc.Graph(figure=fig_contract)], className="six columns"), html.Div([dcc.Graph(figure=fig_payment)], className="six columns")], className="row")

    elif tab == 'tab-5':
        fig_scatter = px.scatter(filtered_df, x='Tenure', y='TotalCharges', color='Churn', opacity=0.5, title='Tenure vs Total Charges', color_discrete_map=COLORS)
        fig_box = px.box(filtered_df, x='Contract', y='MonthlyCharges', color='Churn', title='Monthly Charge Distribution', color_discrete_map=COLORS)
        content = html.Div([html.Div([dcc.Graph(figure=fig_scatter)], className="six columns"), html.Div([dcc.Graph(figure=fig_box)], className="six columns")], className="row")

    return content, kpi_layout

if __name__ == '__main__':
    app.run(debug=True)