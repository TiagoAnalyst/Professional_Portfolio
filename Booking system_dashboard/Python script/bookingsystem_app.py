# %%
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import requests
from io import StringIO

# %%
#URL of the the raw CSV files from GitHub

url="https://raw.githubusercontent.com/TiagoAnalyst/Professional_Portfolio/main/Booking%20system_dashboard/Data%20files/Recycling%20centre%20A%20-%20bookings.csv"
url2="https://raw.githubusercontent.com/TiagoAnalyst/Professional_Portfolio/main/Booking%20system_dashboard/Data%20files/Recycling%20centre%20A%20-%20max.%20capacity.csv"
url3="https://raw.githubusercontent.com/TiagoAnalyst/Professional_Portfolio/main/Booking%20system_dashboard/Data%20files/Mapping-template-london-ward-map-2018.csv" #source: https://data.london.gov.uk/dataset/excel-mapping-template-for-london-boroughs-and-wards


# Attempt to fetch the CSV files using requests
try:
    response = requests.get(url, timeout=10) # timeout
    response2 = requests.get(url2, timeout=10) #timeout increased
    response3 = requests.get(url3, timeout=10)
    url_data = response.content.decode('utf-8')
    url2_data =  response2.content.decode('utf-8')
    url3_data = response3.content.decode('utf-8')

    #Read the CSV data into a DataFrame
    Main_dataset = pd.read_csv(StringIO(url_data))
    Capacity_dataset = pd.read_csv(StringIO(url2_data))
    wards_boroughs_source = pd.read_csv(StringIO(url3_data),usecols=['Ward name','Borough name'])

except requests.exceptions.RequestException as e:
    print(f"Error fetching the file: {e}")

# %%
Capacity_dataset_amended = (
    Capacity_dataset
    .rename(columns={'Group':'Transport type'
            ,'Date':'Booking_date'})
    .assign(**{'Transport type': lambda c: c['Transport type'].apply(lambda c: c[c.find('(')+1:c.find(')')])})
    .assign(
        Booking_dayofweek = lambda z: pd.to_datetime(z['Booking_date'], format='%d/%m/%Y').dt.day_name(),
        Booking_month = lambda a: pd.to_datetime(a['Booking_date'], format='%d/%m/%Y').dt.month_name()
    )
)

# %%
#check the names of the west London Boroughs
West_London_boroughs=['Brent','Ealing','Harrow','Hillingdon','Hounslow','Richmond upon Thames']

West_London_wards=(
    wards_boroughs_source
    .loc[wards_boroughs_source['Borough name'].isin(West_London_boroughs)].reset_index(drop=True)
)

# %%
Main_dataset_amended = (
    Main_dataset
    .rename(
        columns={
            'Mattresses (from your home only)':'Mattresses',
            'Clothes and textiles (mixed)':'clothes and textiles',
            'Site':'Transport type',
            'Ward':'Ward name'
        }
    )
    .assign(
        Booking_date = lambda x: pd.to_datetime(x['Booking date/time']).dt.strftime('%d/%m/%Y'),
        Booking_time = lambda y: pd.to_datetime(y['Booking date/time']).dt.strftime('%H:%M')
    )
    .drop(columns=['Booking date/time'])
    .assign(
        **{'Booking created': pd.to_datetime(Main_dataset['Booking created']).dt.date},
        Booking_dayofweek = lambda z: pd.to_datetime(z['Booking_date'], format='%d/%m/%Y').dt.day_name(),
        Booking_month = lambda a: pd.to_datetime(a['Booking_date'], format='%d/%m/%Y').dt.month_name(),
        Booking_year= lambda x: pd.to_datetime(x['Booking_date'], format='%d/%m/%Y').dt.year
    )
    .assign(
        **{
        'Transport type': lambda b: b['Transport type'].apply(lambda b: b[b.find('(')+1:b.find(')')]).str.lower()
        }
    )
    .merge(
        West_London_wards[['Ward name','Borough name']],
        on=['Ward name'],
        how='left'
    )   
    .assign(
        **{
            'Borough name': lambda other_wards: other_wards['Borough name']
            .mask(
                   other_wards['Ward name'].notnull() &
                   (other_wards['Borough name'].isnull()),
                   'Other Boroughs'
                )
        }
    )
    .assign(
        **{
            'Ward name': lambda empty_cell: empty_cell['Ward name']
               .mask(
                   empty_cell['Ward name'].isnull(),
                   'No info'
               )
        }
    )
    .assign(
        **{
            'Borough name': lambda empty_cells: empty_cells['Borough name']
               .mask(
                   empty_cells['Borough name'].isnull(),
                   'No info'
               )
        }
    )
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

Main_dataset_amended_details=Main_dataset_amended[
    [
        'Booking_date',
        'Booking_month',
        'Booking_year',
        'Booking_dayofweek',
        'Borough name',
        'Type of vehicle',
        'Transport type',
        'Registration plate',
        'ClosureReason',
        'Ward name'
    ]
]

#--------------------------------------------
# Web app layout

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
                html.H1("Booking system dashboard - Financial year 2023-2024", style={'text-align':'center'}),
                html.Br()
            ], width=12
            ) 
    ]),
    dbc.Row([
        dbc.Col([
            html.Div('Please choose a month:'),
            dcc.Dropdown(id='slct_month',
                            options=[x for x in Main_dataset_amended_details['Booking_month'].unique()],
                            multi=False,
                            value= "April"),
            html.Div(id='output_month',children=[])
        ],width=4)
    ]), 
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='chart3',
                        figure={})
        ], width=5),
        dbc.Col([
            dcc.Graph(id='chart1',
                        figure={})
        ], width=7)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='chart2',
                        figure={})
        ], width=6),
        dbc.Col([
            dcc.Graph(id='chart4',
                        figure={}) 
        ] , width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='chart5',
                        figure={}) 
        ] , width=6)
    ])
])

#--------------------------------------------------------------------
#Connect the Plotly graphs with Dash Components -- callback
@app.callback(
    [
        Output(component_id='output_month',component_property='children'),
        Output(component_id='chart1',component_property='figure'),
        Output(component_id='chart2',component_property='figure'),
        Output(component_id='chart3',component_property='figure'),
        Output(component_id='chart4',component_property='figure'),
        Output(component_id='chart5',component_property='figure')
    ],
    [Input(component_id='slct_month', component_property='value')]
)

def update_graphs(slct_month): 
    
    #container
    container_month = "The month chosen by user was: {}".format(slct_month)

    #Chart 1 - no.bookings vs total capacity

    Booking_capacity = Capacity_dataset_amended.copy()
    Booking_capacity = Booking_capacity[Booking_capacity['Booking_month'] == slct_month]

        # Ensure 'Booking_date' is in datetime format and sort by 'Booking_date'

    Booking_capacity['Booking_date'] = pd.to_datetime(Booking_capacity['Booking_date'],format='%d/%m/%Y', dayfirst=True)

        #Group total spaces and total bookings data by Booking_date

    dff_capacity_grouped = Booking_capacity.groupby('Booking_date').sum('Total spaces')
    dff_total_bookings = Booking_capacity.groupby('Booking_date').sum('Total booked')
    
        #Create figure with secondary y-axis
    Bookings_capacity = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces

    Bookings_capacity.add_trace(
        go.Bar(
            x=dff_total_bookings.index,
            y=dff_total_bookings['Total booked'],
            name='No. of bookings'
        ),
        secondary_y=False,
    )

    Bookings_capacity.add_trace(
        go.Scatter(
            x=dff_capacity_grouped.index,
            y=dff_capacity_grouped['Total spaces'],
            name='Daily capacity',
            ),
        secondary_y=True
    )

        #Configure chart
    Bookings_capacity.update_layout(
        title_text="Number of bookings made vs bookings capacity",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

        # Set x-axis title
    Bookings_capacity.update_xaxes(title_text="Date")

        # Set y-axes titles
    Bookings_capacity.update_yaxes(title_text="<b>Bookings capacity</b>", secondary_y=False)
    Bookings_capacity.update_yaxes(title_text="<b>No. of bookings</b>", secondary_y=True)
    Bookings_capacity.update_yaxes(range = [0,500])
    Bookings_capacity.update_xaxes(
        tickformat='%d',
        tickmode='array',
        tickvals=Booking_capacity['Booking_date']

    )
  

    # Chart2 - closure reason distribution
    
    filtered_dataset_by_month = Main_dataset_amended_details.loc[Main_dataset_amended_details['Booking_month'] == slct_month]
    
        #Get the value counts of "ClosureReason"

    bookings_classification = filtered_dataset_by_month['ClosureReason'].value_counts().reset_index()
    bookings_classification.columns=['ClosureReason','Count']
    
        #Create the pie
    
    closure_reason =px.pie(bookings_classification, 
                           names = 'ClosureReason',
                           values='Count',
                           title='Closure Reason distribution'
                        )
    
    closure_reason.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )  
    

    #Create the gauge chart
    Gauge_chart = (Booking_capacity['Total booked'].sum()/Booking_capacity['Total spaces'].sum())*100


    gauge_chart = go.Figure(
            go.Indicator(
                mode= "gauge+number",
                value=Gauge_chart,
                number = {'suffix':"%"},
                domain={'x':[0,1],'y':[0,1]},
                title ={'text':"Bookings capacity usage"},
                gauge ={'axis': {'range': [0,100]},
                        'bar':{'color':'grey'},
                        'steps':[
                            {'range':[0,80],'color':"lightgreen"},
                            {'range':[80,90],'color':"yellow"},
                            {'range':[90,100],'color':"red"}
                            ]
                }
            )
        )
   

    #chart 4 - busiest weekdays 
        #data  manipulation

    Ordered_weekday = ['Monday','Thursday','Friday','Saturday','Sunday']
    Bookings_dayofweek = Booking_capacity['Booking_dayofweek'].unique()

    Bookings_dayofweek_table=[]

    for i in Bookings_dayofweek:
        var_temp = Booking_capacity.loc[Booking_capacity['Booking_dayofweek']==i].copy()
        var_temp2 = var_temp['Total booked'].sum()/var_temp['Booking_date'].nunique()
        Bookings_dayofweek_table.append({'Booking_dayofweek':i,'Average no. of bookings': var_temp2})

    Bookings_dayofweek_table_df = pd.DataFrame(Bookings_dayofweek_table)
    Bookings_dayofweek_table_df = Bookings_dayofweek_table_df.set_index('Booking_dayofweek').reindex(Ordered_weekday).reset_index()

        #determine the day with the highest average
    max_avg_booking_day = Bookings_dayofweek_table_df.loc[Bookings_dayofweek_table_df['Average no. of bookings'].idxmax(),'Booking_dayofweek']

    #colours

    colors=['blue']*len(Bookings_dayofweek_table_df)
    max_day_index = Bookings_dayofweek_table_df.index[Bookings_dayofweek_table_df['Booking_dayofweek']== max_avg_booking_day].tolist()[0]
    colors[max_day_index] = 'crimson'

    average_bookings = go.Figure(
        go.Bar(
                x=Bookings_dayofweek_table_df['Booking_dayofweek'],
                y=Bookings_dayofweek_table_df['Average no. of bookings'],
                marker_color = colors
        )
    )

    average_bookings.update_layout(title_text='Average no. of bookings per day of week')

    #table 1 - most frequent visitors

    filtered_data = filtered_dataset_by_month['Registration plate'].value_counts().reset_index()
    filtered_data.columns=['Registration plate','No. of visits']

    table_most_visitors = go.Figure(
        data=[go.Table(
            header=dict(values=list(filtered_data.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[filtered_data['Registration plate'],filtered_data['No. of visits']],
                       fill_color='lavender',
                       align='left')
        )]
    )
    
    return container_month, Bookings_capacity, closure_reason, gauge_chart, average_bookings, table_most_visitors
#--------------------------------------------------------------------

if __name__=='__main__':
    app.run_server()



# %%
