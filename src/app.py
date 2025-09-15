from dash import Dash, dcc, html, Input, Output, dash_table # pip install dash
import dash_bootstrap_components as dbc 
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from dash import dash_table
import dash_ag_grid as dag
from dash_extensions import BeforeAfter
from dash_extensions.enrich import DashProxy, html

# import data libraries
import pandas as pd  # pip install pandas
import datetime as dt # pip install datetime
import numpy as np    # pip install numpy


# plotting packages
import plotly.graph_objects as go #pip install plotly
import plotly.express as px


# load data wrangling module
import app_data as ad

df = ad.litter
df_piv = ad.litter_sum
brands = ad.litter_ct_brands_piv
places = ad.pl_name_fin
events = ad.litter_event


myblue = '#072B51'


#%% palette

myblue = '#072B51'
mygreen = '#479F4D'

mypurple = '#510750'
mybrown = '#512d07'
mydarkgreen = '#075108'
mylightblue = '#647a92'
mylightbrown = '#aa5d18'
mylightgreen = '#a1c87c'
mylightpurple = '#702545'
myaqua = '#649092'
mylightaqua = '#2a385b'
myrose = '#9b6c70'
myyellow = '#9d8d07'

mygrey = '#f4f6f6'
mycardgrey = '#d6dbdf'

# palette for litter types

color_discrete_map = {'Softdrinks': mypurple,
                            'Food': myaqua,
                            'Other': myrose,
                            'Smoking': mydarkgreen,
                            'Alcohol': mybrown,
                            'Coffee': mylightbrown,
                            'Sanitary': mylightaqua,
                            'Custom_Litter_Type': myaqua,
                            'Industrial': 'lightgrey',
                            'Plastic Bags': mylightgreen,
                            'Pet_Waste': myyellow}

color_discrete_map_bs = {'Yes': '#00ff00',
                         'No': '#dc143c'}


# column definitions for tables
columnDefs = [{"field": i} for i in ["Business Location", "Litter Count"]]
columnDefsBrands = [{"field": i} for i in ["Brand Name", "Litter Count"]]


# beforeAfter image urls


img_b4a_4 = "https://github.com/blazingcdkstar/iowa-city-litter-crew/blob/main/src/assets/A_After_WMW.jpg"


# tab styles

tabs_styles = {
    'height': '60px'
}
tab_style = {
    'height': '80px',
    'borderBottom': '2px solid #479F4D',
    'borderTop': '3px solid #479F4D',
    'borderLeft': '3px solid #479F4D',
    'borderRight': '3px solid #479F4D',
    'padding': '6px',
    'fontWeight': 'bold',
    'backgroundColor':'lightgrey',
    'color': myblue,
    'padding': '6px',
    'fontWeight': 'bold',
    'font-size': '1.4em'
}

tab_selected_style = {
    'height': '80px',
    'borderBottom': '2px solid #479F4D',
    'borderTop': '3px solid #479F4D',
    'borderLeft': '3px solid #479F4D',
    'borderRight': '3px solid #479F4D',
    'padding': '6px',
    'fontWeight': 'bold',
    'backgroundColor':'#abb2b9',
    'color': myblue,
    'padding': '6px',
    'fontWeight': 'bold',
    'font-size': '1.4em'
}


#%%
#%% create function

def mysum(main_category):

    temp = df.loc[df['main_category'] == main_category]
    temp_sum = temp['litter_count'].sum()
    temp_sum = int(temp_sum)

    return(temp_sum)

#%%

# litter data totals
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
total_plastic_bags = mysum('Plastic Bags')
total_litter = total_softdrinks + total_food + total_other + total_smoking + total_alcohol + total_coffee + total_sanitary + total_custom + total_industrial + total_dogshit + total_plastic_bags
total_litter = int(total_litter)

total_small_constributors = total_sanitary + total_custom + total_industrial + total_dogshit

# average duration
myaverage = 'Average time spent picking up litter: ' + str(ad.avg_duration) + ' minutes'
myavglitter_min = 'Average count of litter picked up per minute: ' + str(ad.avg_litter_per_min) + ' litter'


#%%
# mapbox token
mytoken = 'pk.eyJ1IjoiY2RrZWxsZXIiLCJhIjoiY2x5bmFnc3J2MDQ1bTJrcHN3bWI3ajNwcyJ9.16DwzQZpCPZbBlkcZg57eA'

#%% Event Density map

litter_event_piv = events.groupby(['Location']).agg({
    'lat': 'first',
    'lon': 'first',
    'Bags Picked Up': 'sum',
    'Attendee Count': 'sum'
}).reset_index()


bag_count = litter_event_piv['Bags Picked Up'].sum()
event_density_fig = px.scatter_mapbox(litter_event_piv, lat="lat", lon="lon",    
                        color='Bags Picked Up', 
                        size= 'Bags Picked Up',
                        #size = df_piv_three['avg_litter_pickedup'] * 2,
                        color_continuous_scale=[myblue, mygreen],
                        #color_continuous_midpoint=10,
                        zoom=12,
                        hover_data={'Bags Picked Up': True,
                                    'lat': False,
                                    'lon': False,
                                    'Location': True,
                                    'Attendee Count': True},
                        #labels = {'add_block_num_st': 'Street Block',
                        #          'total_count_pickup_dates': 'Count of Outings',
                        #          'avg_litter_pickedup': 'Average Litter Picked Up'}
                        )

event_density_fig.update_layout(font=dict(size=15),
                                title={
                                'text': 'Litter Event Locations',
                                'x': 0.5, # Title position (0-1, where 0.5 is the center)
                                'xanchor': 'center', # Title alignment ('center', 'left', 'right')
                                'font': {'size': 20} # Title font size
    })
event_density_fig.update_layout(mapbox_accesstoken = mytoken)


events['year'] = events['Date'].dt.year
litter_event_yr = events.groupby(['year']).agg('Bags Picked Up').sum().reset_index()


tick_labels = litter_event_yr['year'].unique()
fig_bar_yr = px.bar(data_frame=litter_event_yr, 
                    x = 'year', y = 'Bags Picked Up',
                    text=litter_event_yr['Bags Picked Up'])
fig_bar_yr.update_traces(marker_color = myblue,
                         hoverinfo = 'none', hovertemplate=None)
fig_bar_yr.update_layout(
    xaxis=dict(
        tickvals=tick_labels,
        ticktext=tick_labels,
        showgrid = False,
        
        
    ),
    yaxis = dict(
        showgrid = False
    ),
    width = 750, height = 600, bargap = 0.70,
    xaxis_title = 'Year',
    yaxis_title = None,
    plot_bgcolor = mygrey,
    font=dict(size = 20),
    title={
        'text': 'Bags of Litter Collected per Year',
        'x': 0.5, # Title position (0-1, where 0.5 is the center)
        'xanchor': 'center', # Title alignment ('center', 'left', 'right')
        'font': {'size': 20} # Title font size
    }

)


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
        color_continuous_scale=[myblue, mygreen])

density_bar_three.update_layout(yaxis_title=None, xaxis_title = 'Average Litter Picked Up', plot_bgcolor = mygrey)
density_bar_three.update_layout(font=dict(size=15),
                                    title={
                                    'text': 'Top 10 Average Litter Picked Up by Street Block',
                                    'x': 0.5, # Title position (0-1, where 0.5 is the center)
                                    'xanchor': 'center', # Title alignment ('center', 'left', 'right')
                                    'font': {'size': 20} # Title font size
                                },
                                xaxis = dict(showgrid = False),
                                yaxis = dict(showgrid = False))
density_bar_three.update_layout(yaxis=dict(autorange = 'reversed'))


#%% Top 10 Litter Density by Street Block
# Density Map
density_fig = px.scatter_mapbox(df_piv_three, lat="min_lat", lon="min_lon",    
                        color='avg_litter_pickedup', 
                        #size="avg_litter_pickedup",
                        size = df_piv_three['avg_litter_pickedup'] * 2,
                        color_continuous_scale=[myblue, mygreen],
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

density_fig.update_layout(font=dict(size=15),
                          title={
                                    'text': 'Locations of Top 10 Average Litter Picked Up by Street Block',
                                    'x': 0.5, # Title position (0-1, where 0.5 is the center)
                                    'xanchor': 'center', # Title alignment ('center', 'left', 'right')
                                    'font': {'size': 20} # Title font size
                                })
density_fig.update_layout(mapbox_accesstoken = mytoken)
density_fig.update(layout_coloraxis_showscale=False)


#%%

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__,
           #transforms=[ServersideOutputTransform()],
           external_stylesheets=[dbc.themes.COSMO],
           meta_tags=[{'name': 'viewport',
                      'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}]
                )

server = app.server
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Home',style = tab_style, selected_style = tab_selected_style,
                children=[
                html.Br(),
                dbc.Row([  

                    dbc.Col([
                        #html.Br(),
                        #html.Br(),
                        #html.Br(),
                        html.Br(),
                        html.H3('Upcoming Events',
                                style = {'textAlign': 'left',
                                'paddingLeft':'20px',
                                'font-weight':'bold'}),
                        html.H4(dcc.Markdown('10/5/2025: Cleanup at [Terry Trueblood.](https://www.meetup.com/iowa-city-litter-crew/events/310860787/?eventOrigin=rsvp_confirmation_suggested_events)',
                                              link_target="_blank"),
                                style = {'textAlign': 'left',
                                'paddingLeft':'30px'}),


                        #html.H4(dcc.Markdown('5/17/2025: Learn How to Use Open Litter Map - [Event Details.](https://www.meetup.com/iowa-city-litter-crew/events/307700150/?eventOrigin=group_upcoming_events)',
                        #                      link_target="_blank"),
                        #        style = {'textAlign': 'left',
                        #        'paddingLeft':'30px'}),

                        html.Br(),
                        html.Br(),
                        html.H3('Upcoming Events Hosted by Other Groups',
                                style = {'textAlign': 'left',
                                'paddingLeft':'20px',
                                'font-weight':'bold'}),
                        html.H4(dcc.Markdown('9/27/2025: [Coralville Trash Pick Up](https://www.facebook.com/events/1324939625881503)',
                                              link_target="_blank"),
                                style = {'textAlign': 'left',
                                'paddingLeft':'30px'}),
                        html.H4(dcc.Markdown('10/11/2025: [The Iowa River Clean Up](https://www.johnsoncountyiowa.gov/iowa-river-clean)',
                                              link_target="_blank"),
                                style = {'textAlign': 'left',
                                'paddingLeft':'30px'}),
                        #html.Br(),
                        #html.Br(),
                        
                        
                        html.Br(),
                        html.Br(),
                        html.H3('Past Collaborations',
                                style = {'textAlign': 'left',
                                'paddingLeft':'20px',
                                'font-weight':'bold'}),
                        html.H4(dcc.Markdown('4/27/2025: South of 6 District Team Up to Clean Up',
                                              link_target="_blank"),
                                style = {'textAlign': 'left',
                                'paddingLeft':'30px'}),


                        html.H4(dcc.Markdown('4/19/2025: Coralville Litter Crew Kickoff and Cleanup',
                                              link_target="_blank"),
                                style = {'textAlign': 'left',
                                'paddingLeft':'30px'}),
                        

                        



                    ]),      
                    dbc.Col([
                        dbc.CardImg(src="/assets/logo.jpg", bottom=True,                             
                                #style = {'height':'30%',
                                #'width': '40%',
                                #}
                                    ), 


                    ]), # row


                    dbc.Col([
                        dbc.CardImg(src="/assets/Melissa and Cara.jpg", bottom=True,                             
                                style = {'height':'80%',
                                #'width': '40%',
                                'paddingLeft': '20px'}
                                    ), 

                        dbc.CardBody(
                                html.P(["Cara Keller and Melissa Serenda", html.Br(), "Iowa City Litter Crew Leadership"], className="card-title",
                                       style={'font-size':'25px',
                                              'font_family':'helvetica'})
                            ),


                    ]) # row
                ]), # col


                html.Br(),
                html.Br(),

                    dbc.Row([
                         html.H2("Connect with ICLC online!!",
                        style = {'textAlign': 'left',
                                'paddingLeft':'25px'}),
                        html.Br(),
                        html.Br(),
                        dbc.Col([dbc.Button('Iowa City Litter Crew on Meetup',
                                                href = 'https://www.meetup.com/iowa-city-litter-crew/',
                                                external_link=True,
                                                target='_blank',
                                                style={'background-color':myblue,
                                                        'color': 'white',
                                                        'font-size':'25px',
                                                        'font-face':'bold'}),
                        ], className="d-grid gap-2 col-3 mx-auto"),

                        dbc.Col([dbc.Button('Iowa City Litter Crew on Facebook',
                                                href = 'https://www.facebook.com/groups/iowacitylittercrew/',
                                                external_link=True,
                                                target='_blank',
                                                style={'background-color':myblue,
                                                        'color': 'white',
                                                        'font-size':'25px',
                                                        'font-face':'bold'}) 
                    ], className="d-grid gap-2 col-3 mx-auto"),

                        dbc.Col([dbc.Button('Iowa City Litter Crew on Bluesky',
                                                    href = 'https://bsky.app/profile/iowacitylittercrew.bsky.social',
                                                    external_link=True,
                                                    target='_blank',
                                                    style={'background-color':myblue,
                                                            'color': 'white',
                                                            'font-size':'25px',
                                                            'font-face':'bold'}) 
                        ], className="d-grid gap-2 col-3 mx-auto"),    


                        dbc.Col([dbc.Button('Email the Iowa City Litter Crew',
                                                    href = 'mailto:iowacitylittercrew@gmail.com',
                                                    external_link=True,
                                                    target='_blank',
                                                    style={'background-color':myblue,
                                                            'color': 'white',
                                                            'font-size':'25px',
                                                            'font-face':'bold'}) 
                        ], className="d-grid gap-2 col-3 mx-auto"),          
                    
                    ]),


                    html.Br(),
                    html.Br(),

                    dbc.Row([

                        html.H2("Get started with Open Litter Map and Litter Bingo!!",
                        style = {'textAlign': 'left',
                                'paddingLeft':'25px'}),
                        html.Br(),
                        html.Br(),
                        dbc.Col([dbc.Button('Open Litter Map',
                                                href = 'https://openlittermap.com/',
                                                external_link=True,
                                                target='_blank',
                                                style={'background-color':myblue,
                                                        'color': 'white',
                                                        'font-size':'25px',
                                                        'font-face':'bold'}),
                        ],className="d-grid gap-2 col-3 mx-auto"),

                        dbc.Col([dbc.Button('Open Litter Map Quick Start Guide',
                                                href = 'https://drive.google.com/file/d/10nVfxFRvPqmi5Kvg9IVpNe6AOnfu_4Kb/view?usp=drive_link',
                                                external_link=True,
                                                target='_blank',
                                                style={'background-color':myblue,
                                                        'color': 'white',
                                                        'font-size':'25px',
                                                        'font-face':'bold'}) 
                    ],className="d-grid gap-2 col-3 mx-auto"),

                    dbc.Col([dbc.Button('Printer Friendly Litter Bingo',
                                                href = '/assets/Litter_Bingo_text-only.pdf',
                                                external_link=True,
                                                target='_blank',
                                                style={'background-color':myblue,
                                                        'color': 'white',
                                                        'font-size':'25px',
                                                        'font-face':'bold'}) 
                    ],className="d-grid gap-2 col-3 mx-auto"),

                    
         
                    
                    ], justify = 'center')
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    ] #children
                
            ),  # tab
              #tabs
        dcc.Tab(label='Celebrate Litter Crew Wins', style = tab_style, selected_style = tab_selected_style,
                children=[
                
                html.Br(),

                html.H1('Litter Picked Up at Iowa City Litter Crew Clean Up Events',
                    style = {'textAlign': 'center'}),
            
                dbc.Col([
                dbc.Card([
                    dbc.CardBody(
                        [
                            dbc.Row([
                                dbc.Col([
                                    html.H4('Total Bags of Litter Collected', 
                                            className='card-title',
                                            style={'textAlign': 'center',
                                                'fontSize': 40})
                                ]),                              
                                dbc.Col([
                                    html.P(bag_count, 
                                        className= 'card-text',
                                        style={'textAlign': 'center',
                                                'fontSize': 40},
                                        )
                                ]), 
                            ])
                            
                        ]
                    )
                ],color = myblue, inverse = True)
            ]), # col 300

                html.Br(),

                dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=fig_bar_yr,
                            style = {'width': '50vw', 'height': '50vh'},
                            config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                                "autoScale2d" "select2d", "lasso2d"]})
                        ], xs=8, sm=8, md=12, lg=6, xl=5),

                        dbc.Col([
                            dcc.Graph(figure=event_density_fig,
                            style = {'width': '50vw', 'height': '50vh'},
                            config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                                "autoScale2d" "select2d", "lasso2d"]})
                        ], xs=8, sm=8, md=12, lg=6, xl=5),
                        ]), # row 327

            html.Br(),
            html.Br(),
            html.H3("Spring 2025 Cleanups",
                    style = {'textAlign': 'center'}),
                
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                    #html.H3("Spring 2025 Cleanups"),
                    html.H4("Whispering Meadows Wetland & Coralville Litter Crew Kickoff"),
                    dbc.Carousel(
                        items=[
                            {
                                "key": "1",
                                "src": "/assets/test.jpg",
                                #"img_style":{"width":"500px","height":"300px"},
                                "font_face":"bold",
                                #"header": "March 16th 2025",
                                'img_style':{'max-height':'750px'},
                                "caption": "1st Pickup at Whispering Meadows Wetlands 3/16/2025",
                            },
                            {
                                "key": "2",
                                "src": "/assets/Melissa and Cara.jpg",
                                'img_style':{'max-height':'750px'},
                                "header": "Cara and Melissa, Leaders of Iowa City Litter Crew",
                                "caption": " Week 2 at Whispering Meadows Wetlands 3/23/2025",
                            },
                            {
                                "key": "3",
                                "src": "/assets/2025-04-19_CoralvilleLitterCrewKickoff.jpg",
                                'img_style':{'max-height':'750px'},
                                #"header": "March ",
                                "caption": "Coralville Litter Crew Kickoff Cleanup 4/19/2025",
                                "hover": "Coralville Litter Crew Kickoff Cleanup 4/19/2025",
                            },

                              {
                                "key": "4",
                                "src": "/assets/South of 6 Cleanup.jpg",
                                'img_style':{'max-height':'750px'},
                                #"header": "March ",
                                "caption": "Cleanup at Pepperwood Plaza 3/9/2025",
                                "hover": "Cleanup at Pepperwood Plaza 3/9/2025",
                            },

                        ], controls=True, 
                        indicators=True 
                        #interval=3000,
                        #ride='carousel'
                        #, variant = 'dark'
                    ),  # carousel 351

                    
                    ], width=6), # col 348


                    dbc.Col([
                            #html.Br(),
                            html.H4("Coralville Litter Crew Kickoff Cleanup - April 2025"),
                            BeforeAfter(
                            before=dict(src="/assets/2025-04-19_b4.jpg"),
                            after=dict(src="/assets/2025-04-19_after.jpg"),
                            #width="256",
                            height="750",
                            hover='March 2025: Whispering Meadows Wetland'
                        )
                    ], width = 6),
                ]), # row 347
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),

                html.H3('Before and After Photos - Whispering Meadows Wetland, March 2025',
                style = {'textAlign': 'center'}),

            html.Br(),
            html.Br(),
            html.Br(),


                dbc.Row([
                    dbc.Col([
                            #html.H4("Whispering Meadows Wetland - March 2025"),
                            BeforeAfter(
                            before=dict(src="/assets/A_Before_WMW.jpg"),
                            after=dict(src="/assets/A_After_WMW.jpg"),
                            #width="256",
                            height="500",
                            hover='March 2025: Whispering Meadows Wetland'
                        )
                    ], width = 4),

                        dbc.Col([
                        #html.H4("Whispering Meadows Wetland - March 2025"),
                            BeforeAfter(
                            before=dict(src="/assets/B_Before_WMW.jpg"),
                            after=dict(src="/assets/B_After_WMW.jpg"),
                            #width="256",
                            height="500",
                            hover='March 2025: Whispering Meadows Wetland'
                        )
                    ], width = 4),

                dbc.Col([
                        #html.H4("Whispering Meadows Wetland - March 2025"),
                        BeforeAfter(
                        before=dict(src="/assets/C_Before_WMW.jpg"),
                        after=dict(src="/assets/C_After_WMW.jpg"),
                        #width="256",
                        height="500",
                        hover='March 2025: Whispering Meadows Wetland'
                    )
                ], width = 4),  # row 401

                 ]),
        
            html.Br(),
            html.Br(),
     
    ]), # tab closure 294



        dcc.Tab(label='Explore Litter Data', style = tab_style, selected_style = tab_selected_style,
                children=[
            html.Br(),
            html.H1('Litter AND Litter Data Collected by Individual Contributors',
                    style = {'textAlign': 'center'}),
        
            html.Br(),
            html.Br(),


                
            dbc.Row([


            dbc.Col([
                dbc.Card([
                    dbc.CardBody(
                        [
                            dbc.Row([
                                dbc.Col([
                                    html.H4('Total Litter Collected', className='card-title',
                                            style={'textAlign': 'center',
                                                'fontSize': 40})                         
                                ]),
                                dbc.Col([
                                    html.P(total_litter, 
                                        className= 'card-text',
                                        style={'textAlign': 'center',
                                                'fontSize': 40},
                                        )
                                ]), 
                            ]) 
                            
                        ]) 
                    
            ],color = myblue, inverse = True)
            ]),
                ]),  #row 461

                dbc.Row([    

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
                                                        'fontSize': 30},
                                                )
                                        ]),
                                    ])
                                    
                                ])
                            
                        ],color = mycardgrey, inverse = False)
                    ]),  # col 491

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
                                                    'fontSize': 30},
                                            )
                                    ]),
                                ])
                                
                            ]
                        )
                    ],color = mycardgrey, inverse = False)
                ]),  # col 515


                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            [
                                dbc.Row([
                                    dbc.Col([
                                        html.H4('Other', className='card-title'),
                                        DashIconify(icon="flowbite:teddy-bear-outline",
                                            width=30)
                                    ]),
                                    dbc.Col([
                                        html.P(total_other, 
                                                className= 'card-text',
                                                style={'textAlign': 'right',
                                                        'fontSize': 30},
                                                )
                                    ]),
                                ])
                                
                            ]
                        )
                    ],color = mycardgrey, inverse = False)
                ]), # col 540


                dbc.Col([
                dbc.Card([
                    dbc.CardBody(
                        [
                            dbc.Row([
                                dbc.Col([
                                    html.H4('Plastic Bags', className='card-title'),
                                    DashIconify(icon="material-symbols:shopping-bag-outline",
                                        width=30)
                                ]),
                                dbc.Col([
                                    html.P(total_plastic_bags, 
                                            className= 'card-text',
                                            style={'textAlign': 'right',
                                                    'fontSize': 30},
                                            )
                                ]),
                            ])
                            
                        ]
                    )
                ],color = mycardgrey, inverse = False)
            ]), # col 565


            ]), # row 489

            html.Br(),

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
                                                        'fontSize': 30},
                                                )
                                    ]),
                                ])
                                
                            ]
                        )
                    ],color = mycardgrey, inverse = False)
                ]), # col 596

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
                                                        'fontSize': 30},
                                                )
                                    ]),
                                ])
                                
                            ]
                        )
                    ],color = mycardgrey, inverse = False)
                ]), # col 620

                
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
                                                        'fontSize': 30},
                                                )
                                    ]),
                                ])
                                
                            ]
                        )
                    ],color = mycardgrey, inverse = False)
                ]), # col 645




            

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
                                                        'fontSize': 30},
                                                )
                                    ]),
                                ])
                                
                            ]
                        )
                    ],color = mycardgrey, inverse = False)
                ]), # col 674
                
            ]), # row 594



        html.Br(),
        html.Br(),
        html.H1('Top 10 Litter Density by Street Block',
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
        ]),
        

        html.Br(),
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
                    'Other', 'Pet_Waste','Plastic Bags' ,'Sanitary', 'Smoking', 'Softdrinks'],
            clearable = True,
            searchable = True,
            options = [{'label': main_category,
                    'value': main_category}
                    for main_category in sorted(df['main_category'].unique())], style={'width': '80%',
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
                                'font_family':'helvetica',
                                'text_align': 'right',
                                'padding': '5px'},
                    style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'left'
                                    } for c in ['Main Category']
                                ],
                    style_as_list_view = True,
                    style_header={'fontWeight': 'bold',
                                      'backgroundColor': mycardgrey,
                                      'color': myblue},
                    style_table={'paddingLeft':'50px',
                                    'paddingTop': '10px',
                                    'overflowY': 'auto'})
                    
        ,
                    ]), # col 766
        

            dbc.Col([
                html.H4('Litter Composition',
                        style = {'textAlign':'center'}),


                dcc.Graph(id = 'sunburst_chart',
                            style = {'height': '40vh',
                                        'width' : '30vw',
                                        'paddingLeft':'0px',
                                        'paddingTop':'0px'})
            
            ]) , # col 786



        ]),   # row 764

        dbc.Col([

                html.H4('Litter Location',
                        style = {'textAlign':'center'}),

                dcc.Graph(id = 'litter_density_map',
                        style = {'height': '100vh'},
                        #         'width': '50vw'},
                config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                    "autoScale2d" "select2d", "lasso2d"]})

            ]), # col 803

        html.H4('Litter Timeline',
                        style = {'textAlign':'center'}),
        
        dcc.Graph(id = 'bar_chart',
                style = {'height': '35vh'},
                config = {'modeBarButtonsToRemove': ['select','zoom', "pan2d", "autoScale",
                                                    "autoScale2d" "select2d", "lasso2d"]}),



                ]), # tab closure 451


        dcc.Tab(label='Brands & Businesses', style = tab_style, selected_style = tab_selected_style,
                children=[
        
        html.Br(),
        html.H3('Brands of Litter Picked Up & Business Locations with Litter Picked Up',
        style = {'textAlign':'center'}),

        html.Br(),
        html.Br(),

        dbc.Row([
                dbc.Col([
                #html.H2("Litter by Brands",
                #        style = {'padding': '5px'}),
                dash_table.DataTable(brands.to_dict('records'), 
                                    [{"name": i, "id": i} for i in brands.columns],
                                   # page_current=0,
                                    page_size=20,
                                    fill_width=False,
                        style_cell={'fontSize': 20,
                                    'font_family':'helvetica',
                                    'text_align': 'right',
                                    'padding': '5px'},
                        style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'left'
                                    } for c in ['Brand Name']
                                ],
                        style_as_list_view = True,
                        style_header={'fontWeight': 'bold',
                                      'backgroundColor': mycardgrey,
                                      'color': myblue},
                        style_table={'paddingLeft':'50px',
                                    'paddingTop': '10px',
                                    'overflowY': 'auto'}
                        )
                ], width = 4),


                dbc.Col([
                        dbc.CardImg(src="/assets/Fireball.jpg", bottom=True,                             
                                style = {'height':'70%',
                                'width': '68%',
                                'paddingLeft': '20px'}
                                    ), 
                ]),

                    dbc.Col([
                #html.H2("Business Locations with Litter"),
                dash_table.DataTable(places.to_dict('records'), 
                                    [{"name": i, "id": i} for i in places.columns],
                                   # page_current=0,
                                    page_size=20,
                                    #theme = 'Miller',
                                    fill_width=False,
                        style_cell={'fontSize': 20,
                                    'font_family': 'helvetica',
                                    'text_align': 'right',
                                    'padding': '5px'},
                        style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'left'
                                    } for c in ['Business Location']
                                ],
                        style_as_list_view = True,
                        style_header={'fontWeight': 'bold',
                                      'backgroundColor': mycardgrey},
                        style_table={'paddingLeft':'50px',
                                    'paddingTop': '10px',
                                    'overflowY': 'auto'})
                ], width = 4)
            ]), # row 833

                ]), # tab closure 831
        
        #dcc.Tab(label='How to Get Started', style = tab_style, selected_style = tab_selected_style,
        #        children=[
        #            dbc.Col([        
        #            dbc.Row([
        #                dbc.CardImg(src="/assets/litter_bingo.jpg", bottom=True,                             
        #                        style = {'height':'50%',
        #                        'width': '50%',
        #                        }
        #                            ), 


        #            ], justify = 'center') # row
        #        ]), # col
        #       ]) # tab closure 1138

            ], id='mytabs'), # tabs closure 230


        ]) # html div closure 229




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
                            #size="litter_count",
                            size = temp_df['litter_count'] * 2,
                            zoom=11,
                            color_discrete_map=color_discrete_map,
                            hover_data={'litter_count': True,
                                    'lat': False,
                                    'lon': False,
                                    'main_category': True},
                            labels = {'litter_count': 'Litter Count',
                                      'main_category': 'Litter Type'})
    
    fig.update_layout(legend=dict(bgcolor = mygrey,
                                  bordercolor = 'Black',
                                  orientation = 'v',
                                  yanchor='top',
                                  x=0.01)),
    
    fig.update_layout(legend_title = 'Litter Type',
                      font=dict(size = 15),
                      mapbox = dict(zoom = 13))
    
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
    fig.update_layout(plot_bgcolor = mygrey)
    fig.update_layout(font=dict(size=15),
                       xaxis = dict(showgrid = False),
                       yaxis = dict(showgrid = False))
    return fig






if __name__ == '__main__':
    app.run(debug=False)
    #app.run()
    #app.run_server(
    #    ssl_context = 'adhoc'
    #)
