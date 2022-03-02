import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from percent_change import reformat_to_pct_change, get_map_pct_change_data

"""See https://plotly.com/ for deployment instructions"""

app = dash.Dash(__name__)
app.css.config.serve_locally = True

# extract each state's data
data = pd.read_csv('bullying_viz_data.csv')
data = reformat_to_pct_change(data)
dates = [col[1] for col in data.columns]

# create map data for all types of bullying

def reshape_group(g):
    """Helper method for generating map data"""
    g = g.unstack('state')
    g.columns = g.columns.droplevel()
    g['state'] = [g.columns[0] for i in range(len(g))]
    g = g.rename_axis("newhead").reset_index()
    g.columns.name = None
    g.columns = ['date', 'pctChange', 'state']
    return g


def generate_map_data(bullying_type):
    """Used to generate the data for all maps upon loading site"""
    map_data = get_map_pct_change_data(pd.read_csv('bullying_viz_data.csv'), bullying_type)

    groupby = pd.DataFrame(map_data.stack()).groupby(by='state')
    reshaped_groups = []
    for group in groupby.groups:
        reshaped_groups.append(reshape_group(groupby.get_group(group)))
    
    reformatted_data = pd.concat(reshaped_groups)
    reformatted_data['sorting_col'] = pd.to_datetime(reformatted_data['date'])
    reformatted_data = reformatted_data.sort_values(by=['sorting_col'], ascending=True)
    return reformatted_data


combined_map_data = generate_map_data("sch_cy_bly_sum")
cyber_map_data = generate_map_data("cy_bly")
school_map_data = generate_map_data("sch_bly")

# states = data.groupby('state')
# states_names = states.groups

# all_states = {}
# for s in states_names:
#     all_states[s] = states.get_group(s)

app.layout = html.Div(children=[
    html.H1(children='Bullying Dashboard', className="app-header", style={"color": "#054c75", "text-align": "center"}),
    
    html.Div(
        children=[
            dcc.Dropdown(
                id="map_dropdown",
                options=[
                    {'label': "School Bullying", "value": "school bullying"},
                    {'label': "Cyberbullying", "value": "cyberbullying"},
                    {'label': "School Bullying + Cyberbullying", "value": "school bullying + cyberbullying"},
                ],
                placeholder='School Bullying + Cyberbullying'
            ),
            html.Div(
                dcc.Graph(id="map"),
            ),
            # has the same id as the children variable inside the map callback
            html.P(id="map_caption")
        ]
    ),

    html.Div([
        dcc.Dropdown(
            id='dropdown',
            options=[
                {'label': 'United States', 'value': 'US'},
                {'label': 'Alaska', 'value': 'AK'},
                {'label': 'Alabama', 'value': 'AL'},
                {'label': 'Arkansas', 'value': 'AR'},
                {'label': 'Arizona', 'value': 'AZ'},
                {'label': 'California', 'value': 'CA'},
                {'label': 'Colorado', 'value': 'CO'},
                {'label': 'Connecticut', 'value': 'CT'},
                {'label': 'Delaware', 'value': 'DE'},
                {'label': 'Florida', 'value': 'FL'},
                {'label': 'Georgia', 'value': 'GA'},
                {'label': 'Hawaii', 'value': 'HI'},
                {'label': 'Idaho', 'value': 'ID'},
                {'label': 'Illinois', 'value': 'IL'},
                {'label': 'Indiana', 'value': 'IN'},
                {'label': 'Iowa', 'value': 'IA'},
                {'label': 'Kansas', 'value': 'KS'},
                {'label': 'Kentucky', 'value': 'KY'},
                {'label': 'Louisiana', 'value': 'LA'},
                {'label': 'Maine', 'value': 'ME'},
                {'label': 'Maryland', 'value': 'MD'},
                {'label': 'Massachusetts', 'value': 'MA'},
                {'label': 'Michigan', 'value': 'MI'},
                {'label': 'Minnesota', 'value': 'MN'},
                {'label': 'Mississippi', 'value': 'MS'},
                {'label': 'Missouri', 'value': 'MO'},
                {'label': 'Montana', 'value': 'MT'},
                {'label': 'Nebrasks', 'value': 'NE'},
                {'label': 'Nevada', 'value': 'NV'},
                {'label': 'New Hampshire', 'value': 'NH'},
                {'label': 'New Jersey', 'value': 'NJ'},
                {'label': 'New Mexico', 'value': 'NM'},
                {'label': 'New York', 'value': 'NY'},
                {'label': 'North Carolina', 'value': 'NC'},
                {'label': 'North Dakota', 'value': 'ND'},
                {'label': 'Ohio', 'value': 'OH'},
                {'label': 'Oklahoma', 'value': 'OK'},
                {'label': 'Oregon', 'value': 'OR'},
                {'label': 'Pennsylvania', 'value': 'PA'},
                {'label': 'Rhode Island', 'value': 'RI'},
                {'label': 'South Carolina', 'value': 'SC'},
                {'label': 'South Dakota', 'value': 'SD'},
                {'label': 'Tennessee', 'value': 'TN'},
                {'label': 'Texas', 'value': 'TX'},
                {'label': 'Utah', 'value': 'UT'},
                {'label': 'Vermont', 'value': 'VT'},
                {'label': 'Virginia', 'value': 'VA'},
                {'label': 'Washington', 'value': 'WA'},
                {'label': 'West Virginia', 'value': 'WV'},
                {'label': 'Wisconsin', 'value': 'WI'},
                {'label': 'Wyoming', 'value': 'WY'}
            ],
            placeholder="Select",
        ),
    ]),
    

    html.Div(
        dcc.Graph(
            id='graph',
            className='dropgraph'
        ),
    ),

    html.P(id="footnote")
    
])

@app.callback(
    [Output('graph', 'figure'),
    Output('footnote', 'children')],
    [Input('dropdown', 'value')]
) 
def update_graph(value):

    if value == None:
        #default plot displayed is US
        value = 'US'

    '''
    print(data.loc["AK"])
    sum_alaska = [data.loc["AK"][("sch_cy_bly_sum", dates)]]
    '''
    
    #get plot based on selection
    x_axis = dates
    y_axis1 = [data.loc[value][("sch_bly", date)] for date in dates]
    y_axis2 = [data.loc[value][("cy_bly", date)] for date in dates]
    y_axis_standard1 = [data.loc['US'][("sch_bly", date)] for date in dates]
    y_axis_standard2 = [data.loc['US'][("cy_bly", date)] for date in dates]

    if value == 'US':
        value = 'the US'

        datas = [go.Scatter(
                    x=x_axis, 
                    y=y_axis1,
                    name='school bullying searches',
                    line=dict(color='#cc1900')),
                go.Scatter(
                    x=x_axis, 
                    y=y_axis2,
                    name='cyberbullying searches',
                    line=dict(color='#004876'))]

    else:
        datas = [go.Scatter(
                    x=x_axis, 
                    y=y_axis1,
                    name='school bullying searches',
                    line=dict(color='#cc1900')),
                go.Scatter(
                    x=x_axis, 
                    y=y_axis2,
                    name='cyberbullying searches',
                    line=dict(color='#004876')),
                go.Scatter(
                    x=x_axis, 
                    y=y_axis_standard1,
                    opacity=0.3,
                    name='school bullying searches nationwide',
                    line=dict(color='#7f7f7f')),
                go.Scatter(
                    x=x_axis, 
                    y=y_axis_standard2,
                    opacity=0.3,
                    name='cyberbullying searches nationwide',
                    line=dict(color='#7f7f7f'))]

    
    layouts = go.Layout(
        title='Percent Change of All Bullying Searches in ' + value + ' from Month to Month',
        font={"family":"Droid Serif"},
        titlefont={"size":21},
        
        xaxis=dict(
            title='Date',
            showgrid=True,
            # showline=True,
            color='black',
            showticklabels= True,
            tickangle= 45,
            tickvals=['Mar-01-16', 'Jun-01-16', 'Sep-01-16', 'Dec-01-16', 'Mar-01-17', 'Jun-01-17', 'Sep-01-17', 'Dec-01-17', 'Mar-01-18', 'Jun-01-18', 'Sep-01-18', 'Dec-01-18', 'Mar-01-19', 'Jun-01-19','Sep-01-19', 'Dec-01-19', 'Mar-01-20', 'Jun-01-20','Sep-01-20', 'Dec-01-20'],
            ticktext=['Mar 01 2016', 'Jun 01 2016', 'Sep 01 2016', 'Dec 01 2016', 'Mar 01 2017', 'Jun 01 2017', 'Sep 01 2017', 'Dec 01 2017', 'Mar 01 2018', 'Jun 01 2018', 'Sep 01 2018', 'Dec 01 2018', 'Mar 01 2019', 'Jun 01 2019', 'Sep 01 2019', 'Dec 01 2019', 'Mar 01 2020', 'Jun 01 2020', 'Sep 01 2020', 'Dec 01 2020'],
            #ticktext=['Spring 2016', 'Summer 2016', 'Fall 2016', 'Winter 2016','Spring 2017', 'Summer 2017', 'Fall 2017', 'Winter 2017','Spring 2018', 'Summer 2018', 'Fall 2018', 'Winter 2018','Spring 2019', 'Summer 2019', 'Fall 2019', 'Winter 2019','Spring 2020', 'Summer 2020', 'Fall 2020', 'Winter 2020']
        ),
        yaxis=dict(
            title= 'Percent Change',
            showgrid=True,
            showline=True,
            color='black',
            autorange=True,
        ),
    )

    fig = go.Figure(
        data = datas,
        layout = layouts
    )

    fig.update_coloraxes(colorbar={"len": 0.7})

    children = [html.P(
                f"Note: This line plot captures data taken from the frequency of Google searches for the terms \"school bullying\" and \"cyberbullying\". It shows the percent change in searches from month to month between the years 2016 and 2020. Each labeled month holds the percent change value from the previous month (i.e. March 01, 2016 shows a change in -3% in searches from February 01, 2016 to March 01, 2016). Please select a state from the dropdown menu on top of the figure to see data from that state. Click on the labels to the right of the figure to select which data to view. Hover over a point on the lines to see specific values.",
                id='footnote',
                style={"color": "#054c75", "font-family": "Droid Serif"}
            ),]

    return fig, children

    '''
    return {'data': [go.Scatter(
                x=x_axis, 
                y=y_axis1,
                name='sch_bly',
                line=dict(color='#cc1900')),
                
                go.Scatter(
                x=x_axis, 
                y=y_axis2,
                name='cy_bly',
                line=dict(color='#004876'))
                ],
            'layout': go.Layout(
                title='School Bullying Searches Over The Years in ' + value,

                xaxis=dict(
                    title='Time',
                    showgrid=True,
                    # showline=True,
                    color='black',
                    showticklabels= True,
                    tickangle= 45,
                    tickvals=['Sep-01-16', 'Jan-01-17', 'Sep-01-17', 'Jan-01-18', 'Sep-01-18', 'Jan-01-19', 'Sep-01-19', 'Jan-01-20', 'Sep-01-20', 'Jan-01-21'],
                    ticktext=['Sep 01 2016', 'Jan 01 2017', 'Sep 01 2017', 'Jan 01 2018', 'Sep 01 2018', 'Jan 01 2019', 'Sep 01 2019', 'Jan 01 2020', 'Sep 01 2020', 'Jan 01 2021'],
                ),
                yaxis=dict(
                    title= 'True Value',
                    showgrid=True,
                    showline=True,
                    color='black',
                    range = [-200,500],
                ),
                
            )
    }
    '''


@app.callback(
    [Output("map", "figure"),
    Output('map_caption', 'children')],
    [Input('map_dropdown', 'value')]
)
def load_map(value):
    """Note: For demo plots and full pipeline of how maps are generated, see map_generation.ipynb"""

    if value == None or value == "school bullying + cyberbullying":
        reformatted_data = combined_map_data
        scale = [[0.0, '#00B2EE'], [0.18, 'white'], [0.4, "#ff0000"], [1, "#7C0D0E"]]

        layout = dict(geo=dict(scope='usa',
                            projection={'type': 'albers usa'}),
                    title="Percent Change in Sum of Bullying Searches From Pre-Pandemic Levels", # have to change this when adding 
        )


        fig = px.choropleth(reformatted_data,
                            locations="state",
                            color="pctChange",
                            color_continuous_scale = scale,
                            scope ="usa",
                            locationmode='USA-states',
                            animation_frame="date",
                        range_color=[min(reformatted_data.pctChange), max(reformatted_data.pctChange)])


        fig.layout.title="Percent Change all Bullying Searches From Pre-Pandemic Levels"

        # hover 
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
            )
        )

        customdata = np.stack((reformatted_data['pctChange'], reformatted_data['state']), axis=-1)
        hovertemplate = ('Percent Change: %{customdata[0]}%<br>' + 
            'State: %{customdata[1]}<br>' + 
            '<extra></extra>')
        fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)

        fig.layout.font={"family":"Droid Serif"}
        fig.layout.titlefont={"size":21}
        fig.update_coloraxes(colorbar={"len": 0.7})

        # define the children variable to return in callback
        children = [html.P(
                f"Note: This heat map shows the difference (as percent change) between Google searches for the search terms \"school bullying\" and \"cyberbullying\" from before and during the pandemic. The pre-pandemic levels are determined by aggregating and averaging the monthly search intensities from 2016 to 2018. For each month from March 2019 to February 2021, the percent change is calculated between the search intensity of that month and the corresponding month from the aggregate pre-pandemic data. Use the scroll at the bottom to navigate over time. Hover over an individual state to see specific values.",
                id='map_caption',
                className="map-caption",
                style={"color": "#054c75", "font-family": "Droid Serif"}
            ),]
        return fig, children

    elif value == "school bullying":
        reformatted_data = school_map_data

        # color scale
        scale = [[0.0, '#00B2EE'], [0.15, 'white'], [0.28, "#ff0000"], [1, "#7C0D0E"]]

        # define layout and figure
        layout = dict(geo=dict(scope='usa',
                            projection={'type': 'albers usa'}),)

        fig = px.choropleth(reformatted_data,
                            locations="state",
                            color="pctChange",
                            hover_name ="state", 
                            color_continuous_scale = scale,
                            scope ="usa",
                            locationmode='USA-states',
                            animation_frame ="date",
                        range_color=[min(reformatted_data.pctChange), max(reformatted_data.pctChange)])

        # hover 
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
            )
        )

        # have to reference data by using another df
        customdata = np.stack((reformatted_data['pctChange'], reformatted_data['state']), axis=-1)
        hovertemplate = ('Percent Change: %{customdata[0]}%<br>' + 
            'State: %{customdata[1]}<br>' + 
            '<extra></extra>')
        fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)


        fig.layout.title="Percent Change of \"School Bullying\" Searches From Pre-Pandemic Levels"
        fig.layout.font={"family":"Droid Serif"}
        fig.layout.titlefont={"size":21}
        fig.update_coloraxes(colorbar={"len": 0.7})
        children = [html.P(
                f"Note: This heat map shows the difference (as percent change) between Google searches for the search term \"school bullying\" from before and during the pandemic. The pre-pandemic levels are determined by aggregating and averaging the monthly search intensities from 2016 to 2018. For each month from March 2019 to February 2021, the percent change is calculated between the search intensity of that month and the corresponding month from the aggregate pre-pandemic data. Use the scroll at the bottom to navigate over time. Hover over an individual state to see specific values.",                
                id='map_caption',
                className="map-caption",
                style={"color": "#054c75", "font-family": "Droid Serif"}
            ),]
        return fig, children
    
    else:
        reformatted_data = cyber_map_data

        # color scale
        scale = [[0.0, '#00B2EE'], [0.14, 'white'], [0.30, "#ff0000"], [1, "#7C0D0E"]]

        # define layout and figure
        layout = dict(geo=dict(scope='usa',
                            projection={'type': 'albers usa'}),)

        fig = px.choropleth(reformatted_data,
                            locations="state",
                            color="pctChange",
                            hover_name ="state", 
                            color_continuous_scale = scale,
                            scope ="usa",
                            locationmode='USA-states',
                            animation_frame ="date",
                        range_color=[min(reformatted_data.pctChange), max(reformatted_data.pctChange)])

        # hover 
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
            )
        )

        customdata = np.stack((reformatted_data['pctChange'], reformatted_data['state']), axis=-1)
        hovertemplate = ('Percent Change: %{customdata[0]}%<br>' + 
            'State: %{customdata[1]}<br>' + 
            '<extra></extra>')
        fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)


        fig.layout.title="Percent Change of \"Cyberbullying\" Searches From Pre-Pandemic Levels"
        fig.layout.font={"family":"Droid Serif"}
        fig.layout.titlefont={"size":21}
        fig.update_coloraxes(colorbar={"len": 0.7})

        children = [html.P(
                f"Note: This heat map shows the difference (as percent change) between Google searches for the search term \"cyber bullying\" from before and during the pandemic. The pre-pandemic levels are determined by aggregating and averaging the monthly search intensities from 2016 to 2018. For each month from March 2019 to February 2021, the percent change is calculated between the search intensity of that month and the corresponding month from the aggregate pre-pandemic data. Use the scroll at the bottom to navigate over time. Hover over an individual state to see specific values.",                
                id='map_caption',
                className="map-caption",
                style={"color": "#054c75", "font-family": "Droid Serif"}
            ),]
        return fig, children


if __name__ == '__main__':
    app.run_server(debug=True)