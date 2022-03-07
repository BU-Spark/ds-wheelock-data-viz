import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from percent_change import get_map_pct_change_data, pct_change_calculation

"""See https://plotly.com/ for deployment instructions"""

app = dash.Dash(__name__)
server = app.server
app.css.config.serve_locally = True

# data for line plot

data = pd.read_csv("bullying_viz_data.csv")
data = data.fillna(0)
data['date'] = pd.to_datetime(data['date'])
data['date'] = data['date'].dt.strftime("%b %Y")

states = data.groupby('state')
states_names = states.groups

all_states = {}
for s in states_names:
    all_states[s] = states.get_group(s)

for state in all_states:
    s = all_states[state]
    
    # get baseline values for school bullying and cyberbullying searches in March 2020
    baseline_sch_bly = s.loc[s['date']=='Mar 2020']['sch_bly'].values[0]
    baseline_cy_bly = s.loc[s['date']=='Mar 2020']['cy_bly'].values[0]
    
    # get percent change value for each month in comparison to baseline value
    s['pct_change_sch'] = s['sch_bly'].apply(lambda x: pct_change_calculation(x, baseline_sch_bly))
    s['pct_change_cy'] = s['cy_bly'].apply(lambda x: pct_change_calculation(x, baseline_cy_bly))


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
    x_axis = all_states[value]['date']
    y_axis_sch = all_states[value]['pct_change_sch']
    y_axis_cy = all_states[value]['pct_change_cy']
    y_axis_sch_us = all_states['US']['pct_change_sch']
    y_axis_cy_us = all_states['US']['pct_change_cy']

    if value == 'US':
        value = 'the US'

        datas = [go.Scatter(
                    x=x_axis, 
                    y=y_axis_sch,
                    name='School Bullying',
                    hovertemplate = '%{x}, %{y}%',
                    line=dict(color='#cc1900')),
                go.Scatter(
                    x=x_axis, 
                    y=y_axis_cy,
                    name='Cyberbullying',
                    hovertemplate = '%{x}, %{y}%',
                    line=dict(color='#004876'))]

    else:
        datas = [go.Scatter(
                    x=x_axis, 
                    y=y_axis_sch,
                    name='School Bullying',
                    hovertemplate = '%{x}, %{y}%',
                    line=dict(color='#cc1900')),
                go.Scatter(
                    x=x_axis, 
                    y=y_axis_cy,
                    name='Cyberbullying',
                    hovertemplate = '%{x}, %{y}%',
                    line=dict(color='#004876')),
                go.Scatter(
                    x=x_axis, 
                    y=y_axis_sch_us,
                    opacity=0.3,
                    name='School Bullying Nationwide',
                    hovertemplate = '%{x}, %{y}%',
                    line=dict(color='#cc1900',dash='dash')),
                go.Scatter(
                    x=x_axis, 
                    y=y_axis_cy_us,
                    opacity=0.3,
                    name='Cyberbullying Nationwide',
                    hovertemplate = '%{x}, %{y}%',
                    line=dict(color='#004876',dash='dash'))]

    
    layouts = go.Layout(
        title='Percent Change of Bullying Searches in ' + value + ' in Comparison to March, 2020',
        font={"family":"Whitney"},
        titlefont={"size":21},
        
        xaxis=dict(
            title='Date',
            showgrid=True,
            # showline=True,
            color='black',
            showticklabels= True,
            tickangle= 0,
            #tickvals=['Mar-01-16', 'Jun-01-16', 'Sep-01-16', 'Dec-01-16', 'Mar-01-17', 'Jun-01-17', 'Sep-01-17', 'Dec-01-17', 'Mar-01-18', 'Jun-01-18', 'Sep-01-18', 'Dec-01-18', 'Mar-01-19', 'Jun-01-19','Sep-01-19', 'Dec-01-19', 'Mar-01-20', 'Jun-01-20','Sep-01-20', 'Dec-01-20'],
            #tickvals=['Mar-01-16', 'Sep-01-16', 'Mar-01-17', 'Sep-01-17', 'Mar-01-18', 'Sep-01-18', 'Mar-01-19', 'Sep-01-19', 'Mar-01-20', 'Sep-01-20'],
            tickvals=['Mar 2016', 'Sep 2016', 'Mar 2017', 'Sep 2017', 'Mar 2018', 'Sep 2018', 'Mar 2019', 'Sep 2019', 'Mar 2020', 'Sep 2020'],
            ticktext=['Mar 2016', 'Sep 2016', 'Mar 2017', 'Sep 2017', 'Mar 2018', 'Sep 2018', 'Mar 2019', 'Sep 2019', 'Mar 2020', 'Sep 2020'],
            #ticktext=['Mar \'16', 'Jun \'16', 'Sep \'16', 'Dec \'16', 'Mar \'17', 'Jun \'17', 'Sep \'17', 'Dec \'17', 'Mar \'18', 'Jun \'18', 'Sep \'18', 'Dec \'18', 'Mar \'19', 'Jun \'19', 'Sep \'19', 'Dec \'19', 'Mar \'20', 'Jun \'20', 'Sep \'20', 'Dec \'20'],
            #ticktext=['Spring 2016', 'Summer 2016', 'Fall 2016', 'Winter 2016','Spring 2017', 'Summer 2017', 'Fall 2017', 'Winter 2017','Spring 2018', 'Summer 2018', 'Fall 2018', 'Winter 2018','Spring 2019', 'Summer 2019', 'Fall 2019', 'Winter 2019','Spring 2020', 'Summer 2020', 'Fall 2020', 'Winter 2020']
        ),

        yaxis=dict(
            title= 'Percent Change',
            showgrid=True,
            # showline=True,
            color='black',
            autorange=True,
        ),
    )

    fig = go.Figure(
        data = datas,
        layout = layouts
    )

    # fig.update_traces(hovertemplate=None)
    # fig.update_layout(hovermode="closest")

    fig.update_coloraxes(colorbar={"len": 0.7})
    fig.add_vline(x='Mar 2020', line_width=2, line_dash="dot", line_color="grey")

    children = [html.P(
                f"Note: This line plot captures data taken from the frequency of Google searches for the terms \"school bullying\" and \"cyberbullying\". Using March, 2020 as a baseline for the search frequency value (indicated by dotted line), we calculated the percent change in searches for each month from 2016 to 2021 in comparison to March, 2020. Please select a state from the dropdown menu on top of the figure to see data from that state. Click on the labels to the right of the figure to select which data to view. Hover over a point on the lines to see specific values. Please note, some states may have missing data from March, 2020.",
                id='footnote',
                style={"color": "#054c75", "font-family": "Whitney"}
            ),]

    return fig, children


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


        fig.layout.title="Percent Change of Bullying Searches From Pre-Pandemic Levels"

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

        fig.layout.font={"family":"Whitney"}
        fig.layout.titlefont={"size":21}
        fig.update_coloraxes(colorbar={"len": 0.7})

        # define the children variable to return in callback
        children = [html.P(
                f"Note: This heat map shows the difference (as percent change) between Google searches for the search terms \"school bullying\" and \"cyberbullying\" from before and during the pandemic. The pre-pandemic levels are determined by aggregating and averaging the monthly search intensities from 2016 to 2018. For each month from March 2019 to February 2021, the percent change is calculated between the search intensity of that month and the corresponding month from the aggregate pre-pandemic data. Use the scroll at the bottom to navigate over time. Hover over an individual state to see specific values.",
                id='map_caption',
                className="map-caption",
                style={"color": "#054c75", "font-family": "Whitney"}
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
        fig.layout.font={"family":"Whitney"}
        fig.layout.titlefont={"size":21}
        fig.update_coloraxes(colorbar={"len": 0.7})
        children = [html.P(
                f"Note: This heat map shows the difference (as percent change) between Google searches for the search term \"school bullying\" from before and during the pandemic. The pre-pandemic levels are determined by aggregating and averaging the monthly search intensities from 2016 to 2018. For each month from March 2019 to February 2021, the percent change is calculated between the search intensity of that month and the corresponding month from the aggregate pre-pandemic data. Use the scroll at the bottom to navigate over time. Hover over an individual state to see specific values.",                
                id='map_caption',
                className="map-caption",
                style={"color": "#054c75", "font-family": "Whitney"}
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
        fig.layout.font={"family":"Whitney"}
        fig.layout.titlefont={"size":21}
        fig.update_coloraxes(colorbar={"len": 0.7})

        children = [html.P(
                f"Note: This heat map shows the difference (as percent change) between Google searches for the search term \"cyber bullying\" from before and during the pandemic. The pre-pandemic levels are determined by aggregating and averaging the monthly search intensities from 2016 to 2018. For each month from March 2019 to February 2021, the percent change is calculated between the search intensity of that month and the corresponding month from the aggregate pre-pandemic data. Use the scroll at the bottom to navigate over time. Hover over an individual state to see specific values.",                
                id='map_caption',
                className="map-caption",
                style={"color": "#054c75", "font-family": "Whitney"}
            ),]
        return fig, children


if __name__ == '__main__':
    app.run_server(debug=True)