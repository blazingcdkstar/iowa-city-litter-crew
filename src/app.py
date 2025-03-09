

#%% load libraries
# dash libraries
from dash import Dash, dcc, html, Input, Output, dash_table # pip install dash
import dash_bootstrap_components as dbc 
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from dash import dash_table
import dash_ag_grid as dag



# import data libraries
import pandas as pd  # pip install pandas
import datetime as dt # pip install datetime
import numpy as np    # pip install numpy


# plotting packages
import plotly.graph_objects as go #pip install plotly
import plotly.express as px


# load data wrangling module
import app_data as ad
#from app_data import pl_name

# for heroku app
import pathlib
PATH=pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('data').resolve()


#%% load data
df = ad.litter
df_piv = ad.litter_sum
brands = ad.litter_ct_brands_piv
places = ad.pl_name_fin

columnDefs = [{"field": i} for i in ["Business Location", "Litter Count"]]
columnDefsBrands = [{"field": i} for i in ["Brand Name", "Litter Count"]]

#%% create function

def mysum(main_category):

    temp = df.loc[df['main_category'] == main_category]
    temp_sum = temp['litter_count'].sum()
    temp_sum = int(temp_sum)

    return(temp_sum)


#%% Set Variables
# mapbox token
mytoken = 'pk.eyJ1IjoiY2RrZWxsZXIiLCJhIjoiY2x5bmFnc3J2MDQ1bTJrcHN3bWI3ajNwcyJ9.16DwzQZpCPZbBlkcZg57eA'

color_discrete_map = {'Softdrinks': '#3366CC',
                            'Food': '#DC3912',
                            'Other':'#FF9900',
                            'Smoking': '#109618',
                            'Alcohol': '#990099',
                            'Coffee': '#0099C6',
                            'Sanitary': '#DD4477',
                            'Custom_Litter_Type': '#66AA00',
                            'Industrial': '#B82E2E'}

# get totals by main category

total_litter = df['litter_count'].sum()
total_litter = int(total_litter)

bag_count = 30

total_softdrinks = mysum('Softdrinks')
total_food = mysum('Food')
total_other = mysum('Other')
total_smoking = mysum('Smoking')
total_alcohol = mysum('Alcohol')
total_coffee = mysum('Coffee')
total_sanitary = mysum('Sanitary')
total_custom = mysum('Custom_Litter_Type')
total_industrial = mysum('Industrial')
total_dogshit = mysum('Pet_Waste')

total_small_constributors = total_sanitary + total_custom + total_industrial + total_dogshit

# average duration
myaverage = 'Average time spent picking up litter: ' + str(ad.avg_duration) + ' minutes'
myavglitter_min = 'Average count of litter picked up per minute: ' + str(ad.avg_litter_per_min) + ' litter'


#%% Density for at least 3 pickups
df_piv_three = df_piv[df_piv['total_count_pickup_dates'] >= 3].nlargest(10, 'avg_litter_pickedup')


density_bar_three = px.bar(df_piv_three, x='avg_litter_pickedup', 
       y= 'add_block_num_st',
       hover_data={'add_block_num_st': True,
                   'avg_litter_pickedup': True,
                   'total_count_pickup_dates': True},
        labels={'add_block_num_st': 'Street Block',
                'avg_litter_pickedup': 'Average Litter Picked Up',
                'total_count_pickup_dates': 'Count of Outings'},
        color = 'avg_litter_pickedup',
        color_continuous_scale=['steelblue', 'darkorange'])

density_bar_three.update_layout(yaxis_title=None, xaxis_title = 'Average Litter Picked Up', plot_bgcolor = 'lightgrey')
density_bar_three.update_layout(font=dict(size=15))
density_bar_three.update_layout(yaxis=dict(autorange = 'reversed'))



# Density Map
density_fig = px.scatter_mapbox(df_piv_three, lat="min_lat", lon="min_lon",    
                        color='avg_litter_pickedup', 
                        size="avg_litter_pickedup",
                        #size = df_piv_three['avg_litter_pickedup'] * 2,
                        color_continuous_scale=['steelblue', 'darkorange'],
                        #color_continuous_midpoint=10,
                        zoom=12,
                        hover_data={'avg_litter_pickedup': True,
                                    'min_lat': False,
                                    'min_lon': False,
                                    'add_block_num_st': True,
                                    'total_count_pickup_dates': True},
                        labels = {'add_block_num_st': 'Street Block',
                                  'total_count_pickup_dates': 'Count of Outings',
                                  'avg_litter_pickedup': 'Average Litter Picked Up'}
                        )

density_fig.update_layout(font=dict(size=15))
density_fig.update_layout(mapbox_accesstoken = mytoken)
density_fig.update(layout_coloraxis_showscale=False)

#%% Create durations scatter plot
# Duration Scatter Plot

duration_scatter = px.scatter(ad.durations_piv, 
           x='duration_mins', 
           y = 'sum_litter', 
           symbol_sequence=['circle'], 
           size = 'sum_litter',
           color = 'sum_litter',
           color_continuous_scale=['steelblue', 'darkorange'],
           hover_data={'min_date': True,
                       'duration_mins': True,
                       'sum_litter': True
                   },
           labels={'min_date': 'Date',
                   'duration_mins': 'Time to Pick Up Litter in Minutes',
                   'sum_litter': 'Total Litter Picked Up'
                },
            title= 'Count of Litter Picked Up versus Time Spent Picking Up Litter')

duration_scatter.update_traces(marker = dict(line = dict(width = 2,
                                                        color = 'DarkSlateGrey')))

duration_scatter.update_layout(plot_bgcolor = 'lightgrey',
                               yaxis_title='Litter Picked UP',
                               xaxis_title = 'Pick Up Time in Minutes',
                               font=dict(size=15),
                               )

#%% Create Cards

card_duration = dbc.Card(
    [
    dbc.CardHeader(html.H3('How long does it take to pick up litter?')),
    dbc.Row([
        dbc.Col([
            dbc.CardImg(src="/assets/event.jpg", bottom=True, 
                style = {'height':'100%',
                         'width': '100%'}
                )


        ])
    ]),
   
    dbc.CardBody(
        [
        #html.H3('How Long Does it Take to Pick Up Litter?', className = 'card-title'),
        html.Br(),
        html.H4(myaverage, className='card-text'),
        html.H4(myavglitter_min, className = 'card-text'),
        html.Br(),
        html.H4('Sometimes I pick up 1 piece of litter while running an errand, or fill a bag with my helpful dog Kipper, or while making new friends at a pick up event.'),
        #html.Br(),
        #html.H4(dcc.Markdown("Data is collected by taking a picture, then uploading and tagging using the tools available at [Open Litter Map.](https://openlittermap.com/)"))
        ]
    )
    ],class_name='w-75'
    
)


card_graph = dbc.Card(
    dcc.Graph(id = 'duration_graph',
              figure = duration_scatter),
              body = True
)



# %% app instantiation

app = Dash(__name__,
           external_stylesheets=[dbc.themes.COSMO],
           meta_tags=[{'name': 'viewport',
                      'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}]
                )

# for heroku app
server = app.server

#%% app layout

app.layout = html.Div([

    html.Br(),

    dbc.Col([

        
        
        #dbc.Row([html.H1('Litter and Litter Data Collected in Iowa City'),
        #                #html.Img(src = "/assets/bottle.jpg")
        #                   ], className = "banner"),
        
        dbc.Row([
                dbc.CardImg(src="/assets/logo.jpg", bottom=True,                             
                            style = {'height':'30%',
                            'width': '40%',
                             }
                ), 


        ], justify = 'center')
    ]),
        
    


    #html.H1('Litter and Litter Data Collected in Iowa City',
    #        style={'textAlign':'center'}),

    html.Br(),

    html.H1('Litter Collected',
            style = {'textAlign': 'center'}),
    
    html.Br(),

            dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Bags of Litter Collected by Iowa City Litter Crew at Pick Up Events', className='card-title'),
                               
                                DashIconify(icon="f7:trash",
                                    width=30), 
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                DashIconify(icon="f7:trash",
                                    width=30),
                                html.Br(),
                                html.Br(),
                                dbc.Button('Join Iowa City Litter Crew',
                                   href = 'https://www.meetup.com/iowa-city-litter-crew/',
                                   external_link=True,
                                   target='_blank',
                                   style={'background-color':'white',
                                          'color': 'steelblue',
                                          'font-size':'25px',
                                          'font-face':'bold'})                          
                            ]),
                            
                            dbc.Col([
                                html.P(bag_count, 
                                       className= 'card-text',
                                       style={'textAlign': 'right',
                                              'fontSize': 40},
                                       )
                            ]), 
                        ])
                        
                    ]
                )
        ],color = 'lightgrey', inverse = False)
        ]),

    html.Br(),

    html.H1('Litter Data',
           style = {'textAlign': 'center'}),
    
    html.Br(),

    html.H3(dcc.Markdown("Data is collected by taking a picture, then uploading and tagging using the tools available at [Open Litter Map.](https://openlittermap.com/)",
                         link_target='_blank'),
            style = {'textAlign':'center'}),

    dbc.Row([


        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Total Litter Collected', className='card-title'),
                                DashIconify(icon="f7:trash",
                                    width=30)                            
                            ]),
                            dbc.Col([
                                html.P(total_litter, 
                                       className= 'card-text',
                                       style={'textAlign': 'right',
                                              'fontSize': 40},
                                       )
                            ]), 
                        ])
                        
                    ]
                )
        ],color = 'lightgrey', inverse = False)
        ]),

        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Soft Drinks', className='card-title'),
                                DashIconify(icon="mdi:bottle-soda-classic-outline",
                                    width=30)
                            ]),
                            dbc.Col([
                                html.P(total_softdrinks, 
                                       className= 'card-text',
                                       style={'textAlign': 'right',
                                              'fontSize': 40},
                                       )
                            ]),
                        ])
                        
                    ]
                )
            ],color = 'lightgrey', inverse = False)
        ]),

        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Food', className='card-title'),
                                DashIconify(icon="pajamas:food",
                                    width=30)
                            ]),
                            dbc.Col([
                                html.P(total_food, 
                                       className= 'card-text',
                                       style={'textAlign': 'right',
                                              'fontSize': 40},
                                       )
                            ]),
                        ])
                        
                    ]
                )
            ],color = 'lightgrey', inverse = False)
        ]),


        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Other', className='card-title'),
                                DashIconify(icon="material-symbols:shopping-bag-outline",
                                    width=30)
                            ]),
                            dbc.Col([
                                html.P(total_other, 
                                        className= 'card-text',
                                        style={'textAlign': 'right',
                                                'fontSize': 40},
                                        )
                            ]),
                        ])
                        
                    ]
                )
            ],color = 'lightgrey', inverse = False)
        ]),


    ]),


    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Smoking', className='card-title'),
                                DashIconify(icon="mdi:smoking",
                                    width=30)
                            ]),
                            dbc.Col([
                                html.P(total_smoking, 
                                        className= 'card-text',
                                        style={'textAlign': 'right',
                                                'fontSize': 40},
                                        )
                            ]),
                        ])
                        
                    ]
                )
            ],color = 'lightgrey', inverse = False)
        ]),

        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Alcohol', className='card-title'),
                                DashIconify(icon="streamline:champagne-party-alcohol",
                                    width=30)
                            ]),
                            dbc.Col([
                                html.P(total_alcohol, 
                                        className= 'card-text',
                                        style={'textAlign': 'right',
                                                'fontSize': 40},
                                        )
                            ]),
                        ])
                        
                    ]
                )
            ],color = 'lightgrey', inverse = False)
        ]),

        
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Coffee', className='card-title'),
                                DashIconify(icon="ep:coffee",
                                    width=30)
                            ]),
                            dbc.Col([
                                html.P(total_coffee, 
                                        className= 'card-text',
                                        style={'textAlign': 'right',
                                                'fontSize': 40},
                                        )
                            ]),
                        ])
                        
                    ]
                )
            ],color = 'lightgrey', inverse = False)
        ]),




     

        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Sanitary and Custom', className='card-title'),
                                DashIconify(icon="f7:facemask",
                                    width=30),
                                    #DashIconify(icon="mdi:industrial",
                                    #width=30),
                                    DashIconify(icon="fluent:phone-48-regular",
                                    width=30)
                            ]),
                            dbc.Col([
                                html.P(total_small_constributors, 
                                        className= 'card-text',
                                        style={'textAlign': 'right',
                                                'fontSize': 40},
                                        )
                            ]),
                        ])
                        
                    ]
                )
            ],color = 'lightgrey', inverse = False)
        ]),

    ]),

    html.Br(),
    html.Br(),

    html.Br(),
    html.Br(),
    html.H1('Top 10 Litter Density by Street Block',
            style = {'textAlign': 'center'}),
    
    html.Br(),
    html.H3('Top 10 street blocks with highest average litter picked up',
            style = {'textAlign': 'center'}),

     dbc.Row([
        dbc.Col([
            dcc.Graph(figure=density_fig,
              style = {'width': '50vw', 'height': '50vh'},
              config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                   "autoScale2d" "select2d", "lasso2d"]})
        ], xs=8, sm=8, md=12, lg=6, xl=5),

        dbc.Col([
            dcc.Graph(figure=density_bar_three,
              style = {'width': '50vw', 'height': '50vh'},
              config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                   "autoScale2d" "select2d", "lasso2d"]})
        ], xs=8, sm=8, md=12, lg=6, xl=5),
    
    html.Br(),

    #html.H1('Business Locations and Brands',
    #        style = {'textAlign': 'center'}),
    html.Br(),
    html.Br(),
    

    dbc.Row([

        dbc.Col([html.H2("Business Locations With Litter"),

            dag.AgGrid(
                id = 'test_pagination_grid',
                columnDefs = columnDefs,
                rowData = places.to_dict('records'),
                #columnSize = 'sizeToFit',
                defaultColDef={'filter': True,
                               'sortable': True,
                               'minWidth': 600},
                rowStyle={"backgroundColor": "darkgrey", "color": "white"},
                dashGridOptions = {"pagination": True, 
                "paginationPageSize": 10,
                "suppressPaginationPanel": False,
                "suppressScrollOnNewData": False,
                "animateRows": False},
                className="ag-theme-alpine",
                style={
                "height": "550px",
                "width": "70%",
            },
                
            ), 

            html.Br(),
            html.Br(),            

    ]),

    html.Br(),
    html.Br(),

     dbc.Col([html.H2("Brands Littered"),
              
            dag.AgGrid(
                id = 'test_pagination_grid_brands',
                columnDefs = columnDefsBrands,
                rowData = brands.to_dict('records'),
                #columnSize = 'sizeToFit',
                defaultColDef={'filter': True,
                               'sortable': True,
                               'minWidth': 450},
                rowStyle={"backgroundColor": "darkgrey", "color": "white"},
                #className = 'ag-theme-alpine',
                dashGridOptions = {"pagination": True, 
                "paginationPageSize": 10,
                "suppressPaginationPanel": False,
                "suppressScrollOnNewData": False,
                "animateRows": False},
                className="ag-theme-alpine",
                style={
                "height": "550px",
                "width": "60%",
            },
                
                
            )             

    ]),

       
    ]),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    
     html.H1('Litter Quantity versus Time - How long does it take to pick up litter?',
            style = {'textAlign': 'center'}), 

    ]),

    html.Br(),

    dbc.Row(
        [dbc.Col(dcc.Graph(figure=duration_scatter,
               style = {'width': '65vw','height': '50vh'},
               config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                    "autoScale2d" "select2d", "lasso2d"]})),
        dbc.Col(card_duration, width=4,
                )]
    ),

 
    html.Br(),
    html.Br(),

    html.H1('Litter Location, Composition and Timeline Based on Your Selections',
            style = {'textAlign': 'center'}), 
    html.Br(),

    html.H5('Add or remove item(s) from the drop down.'),
    dcc.Dropdown(
        id = 'litter_type_dd',
        placeholder = 'Select a litter type...',
        multi=True,
        value = ['Alcohol','Coffee', 'Custom_Litter_Type','Food', 'Industrial',
                 'Other', 'Pet_Waste', 'Sanitary', 'Smoking', 'Softdrinks'],
        clearable = True,
        searchable = True,
        options = [{'label': main_category,
                   'value': main_category}
                   for main_category in sorted(df['main_category'].unique())], style={'width': '70%',
                                                                                      'height': '100%',
                                                                                      'font-size': 25}),

    html.Br(),
    
    html.Br(),

    html.H5('Select the date range.'),    

    dcc.DatePickerRange(
        id = 'date_range',
        min_date_allowed = df['date_taken_date'].min(),
        max_date_allowed = df['date_taken_date'].max(),
        initial_visible_month = dt.date(2023,8,1),
        start_date = df['date_taken_date'].min(),
        end_date = df['date_taken_date'].max()
        
    ), 

    html.Br(),
    html.Br(),

    dbc.Row([

        dbc.Col([
            html.H4('Litter Quantity',
                    style = {'textAlign': 'center',
                             'paddingRight':'125px'}),

            dash_table.DataTable(
                
                id = 'mytable',
                fill_width=False,
                style_cell={'fontSize': 20,
                            'text_align': 'center',
                            'padding': '5px'},
                style_header={'fontWeight': 'bold'},
                style_table={'paddingLeft':'50px',
                             'paddingTop': '10px'})
                
    ,
                ]),
        

        dbc.Col([
            html.H4('Litter Composition',
                    style = {'textAlign':'center'}),


            dcc.Graph(id = 'sunburst_chart',
                           style = {'height': '40vh',
                                    'width' : '30vw',
                                    'paddingLeft':'0px',
                                    'paddingTop':'0px'})
        
        ]) ,

        dbc.Col([

            html.H4('Litter Location',
                    style = {'textAlign':'center'}),

            dcc.Graph(id = 'litter_density_map',
                      style = {'height': '45vh',
                               'width': '50vw'},
            config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                   "autoScale2d" "select2d", "lasso2d"]})

        ]),



    ]),  

    html.H4('Litter Timeline',
                    style = {'textAlign':'center'}),
    
    dcc.Graph(id = 'bar_chart',
            style = {'height': '35vh'},
            config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                   "autoScale2d" "select2d", "lasso2d"]}),   
    
    html.Br(),
    html.H1("Links",
            style = {'textAlign': 'center'}),

    html.Br(),
    dbc.Row([
        dbc.Col(dbc.Button('Join Iowa City Litter Crew on Meetup'  ,
                                   href = 'https://www.meetup.com/iowa-city-litter-crew/',
                                   external_link=True,
                                   target='_blank',
                                   style={'background-color':'white',
                                          'color': 'steelblue',
                                          'font-size':'25px',
                                          'font-face':'bold'}),
        width='auto'),

        dbc.Col(dbc.Button('Iowa City Litter Crew on Facebook',
                                   href = 'https://www.facebook.com/groups/iowacitylittercrew/',
                                   external_link=True,
                                   target='_blank',
                                   style={'background-color':'white',
                                          'color': 'steelblue',
                                          'font-size':'25px',
                                          'font-face':'bold'}),
        width='auto'),

        dbc.Col(dbc.Button('Bottle Bill Map',
                                   href = 'https://www.google.com/maps/d/u/0/edit?mid=1G0sMOiwBknVO1LEJeHDcq4wbbwVhNXc&usp=sharing',
                                   external_link=True,
                                   target='_blank',
                                   style={'background-color':'white',
                                          'color': 'steelblue',
                                          'font-size':'25px',
                                          'font-face':'bold'}),
        width='auto'),

        dbc.Col(dbc.Button('Open Litter Map',
                                   href = 'https://openlittermap.com/',
                                   external_link=True,
                                   target='_blank',
                                   style={'background-color':'white',
                                          'color': 'steelblue',
                                          'font-size':'25px',
                                          'font-face':'bold'}),
        width='auto'),

        dbc.Col(dbc.Button('Open Litter Map - Map of Iowa City',
                                   href = 'https://openlittermap.com/global?lat=41.64373708513251&lon=-91.51480972932332&zoom=13.48',
                                   external_link=True,
                                   target='_blank',
                                   style={'background-color':'white',
                                          'color': 'steelblue',
                                          'font-size':'25px',
                                          'font-face':'bold'}),
        width='auto'),

        dbc.Col(dbc.Button('Litter Bingo Card',
                                   href = 'https://carbonear.ca/wp-content/uploads/2022/05/Litter-Bingo-2022.png',
                                   external_link=True,
                                   target='_blank',
                                   style={'background-color':'white',
                                          'color': 'steelblue',
                                          'font-size':'25px',
                                          'font-face':'bold'}),
        width='auto'),
    ], justify = 'center'),     


    html.Br(),
    html.Br(),

        dbc.Row([
                dbc.CardImg(src="/assets/bottle.jpg", bottom=True,                             
                            style = {'height':'10%',
                            'width': '10%',
                             }
                ), 
                dbc.CardImg(src="/assets/bottle.jpg", bottom=True,                             
                            style = {'height':'10%',
                            'width': '10%',
                             }
                ),
                dbc.CardImg(src="/assets/bottle.jpg", bottom=True,                             
                            style = {'height':'20%',
                            'width': '10%',
                             }
                ),


        ], justify='center')



])

#%% Map Chart
@app.callback(Output('litter_density_map','figure'),
              Input('litter_type_dd','value'),
              Input('date_range', 'start_date'),
              Input('date_range', 'end_date'))
              #Input('top_10_filter', 'value'))


def density_map(mycategory, start_date, end_date):

    if not start_date or not end_date or not mycategory:
        raise PreventUpdate   
    
    temp_df = df.loc[df['main_category'].isin(mycategory)]


    temp_df = temp_df.loc[temp_df['date_taken_date'].between(pd.to_datetime(start_date), 
                                                                 pd.to_datetime(end_date),
                                                                 inclusive='both')]
    
  
    fig = px.scatter_mapbox(temp_df, lat="lat", lon="lon",    
                            color="main_category", 
                            size="litter_count",
                            zoom=11,
                            color_discrete_map=color_discrete_map,
                            hover_data={'litter_count': True,
                                    'lat': False,
                                    'lon': False,
                                    'main_category': True},
                            labels = {'litter_count': 'Litter Count',
                                      'main_category': 'Litter Type'})
    
    fig.update_layout(legend=dict(bgcolor = 'LightGrey',
                                  bordercolor = 'Black',
                                  orientation = 'v',
                                  yanchor='top',
                                  x=0.01)),
    
    fig.update_layout(legend_title = 'Litter Type',
                      font=dict(size = 15))
    
    fig.update_layout(mapbox_accesstoken = mytoken)
    return fig

#%% Sunburst Chart

@app.callback(Output('sunburst_chart','figure'),
              Input('litter_type_dd','value'),
              Input('date_range', 'start_date'),
              Input('date_range', 'end_date'))
              #Input('top_10_filter', 'value'))

def sunburst_chart(mycategory, start_date, end_date):

    if not start_date or not end_date or not mycategory:
        raise PreventUpdate
    
        
   
    temp_df = df.loc[df['main_category'].isin(mycategory)]


    temp_df = temp_df.loc[temp_df['date_taken_date'].between(pd.to_datetime(start_date), 
                                                                 pd.to_datetime(end_date),
                                                                 inclusive='both')]
    
    # if my_add_blocknum:
    #     temp_df = temp_df.loc[temp_df['add_blocknum_street'].eq(my_add_blocknum)]
    
    temp_piv = pd.DataFrame(temp_df.groupby(['main_category', 'sub_category'])['litter_count'].sum().reset_index())



    fig = px.sunburst(temp_piv, 
                  path = ['main_category', 'sub_category'], 
                  values='litter_count', 
                  hover_name='main_category', 
                  color = 'main_category',
                  color_discrete_map=color_discrete_map)
             
    
    
    fig.update_traces(textinfo="label+percent parent")
    #fig.update_traces(hovertemplate = "Main Category: %{parent}: <br>Sub Category: %{label} </br>Count:%{value} </br>Percentage:%{percentParent:.02f}")
    fig.update_traces(hovertemplate = "Main Category: %{parent}: <br>Sub Category: %{label} </br>Count:%{value}")
    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))
    #fig.layout.coloraxis.colorbar['thickness'] = 200
    fig.update_layout(font=dict(size=15))
    #fig.layout.paper_bgcolor = 'lightgrey'
    return fig

#%%


#%% Summary Table

@app.callback(Output('mytable','data'),
              Input('litter_type_dd','value'),
              Input('date_range', 'start_date'),
              Input('date_range', 'end_date'))
              #Input('top_10_filter', 'value'))



def get_my_table(mycategory, start_date, end_date):

    if not start_date or not end_date or not mycategory:
        raise PreventUpdate   
    
    mytable = df.loc[df['main_category'].isin(mycategory)]


    mytable = mytable.loc[mytable['date_taken_date'].between(pd.to_datetime(start_date), 
                                                                 pd.to_datetime(end_date),
                                                                 inclusive='both')]
    
    # if top_10_filter:
    #     mytable = mytable.loc[mytable['add_blocknum_street'].eq(top_10_filter)]
    
    mytable = pd.DataFrame(mytable.groupby(['main_category'])['litter_count'].sum().reset_index())
    mytable = mytable.sort_values(by = 'litter_count', ascending=False)

    mytable = (pd.DataFrame([*mytable.values, ['Total', *mytable.sum(numeric_only=True).values]], 
              columns=mytable.columns))
    
    mytable = mytable.rename(columns={'main_category': 'Main Category',
                                      'litter_count': 'Litter Count'})
    
    

    return mytable.to_dict('records')




#%% bar chart

@app.callback(Output('bar_chart','figure'),
              Input('litter_type_dd','value'),
              Input('date_range', 'start_date'),
              Input('date_range', 'end_date'))


def my_bar_chart(mycategory, start_date, end_date):

    if not start_date or not end_date or not mycategory:
        raise PreventUpdate

    temp_df = df.loc[df['main_category'].isin(mycategory)]


    temp_df = temp_df.loc[temp_df['date_taken_date'].between(pd.to_datetime(start_date), 
                                                                 pd.to_datetime(end_date),
                                                                 inclusive='both')]
    
    temp_df = pd.DataFrame(temp_df.groupby(['date_taken_date', 'main_category'])['litter_count'].sum().reset_index())

    fig = px.line(temp_df,
             x='date_taken_date',
             y = 'litter_count',
             markers=True,
            hover_data={'date_taken_date': True,
                        'main_category' : True,
                         'litter_count': True},
            labels = {
                'date_taken_date': 'Date Litter Picked Up',
                'litter_count': 'Litter Count',
                'main_category': 'Litter Type',
            },
            color = 'main_category',
            color_discrete_map=color_discrete_map)
    
    fig.update_layout(showlegend = False)
    fig.update_layout(plot_bgcolor = 'lightgrey')
    fig.update_layout(font=dict(size=15))
    return fig






#%% Run App
if __name__ == '__main__':
    app.run_server()