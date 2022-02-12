import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from percent_change import reformat_to_pct_change

app = dash.Dash(__name__)

# extract each state's data
data = pd.read_csv('bullying_viz_data.csv')
data = reformat_to_pct_change(data)
dates = [col[1] for col in data.columns]

# states = data.groupby('state')
# states_names = states.groups

# all_states = {}
# for s in states_names:
#     all_states[s] = states.get_group(s)


app.layout = html.Div(children=[
    html.H1(children='Wheelock Dashboard'),

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
    )
    
])

@app.callback(
    Output('graph', 'figure'),
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

    if value == 'US':
        value = 'the US'
    layouts = go.Layout(
        title='School Bullying Searches Over The Years in ' + value,

        xaxis=dict(
            title='Time',
            showgrid=True,
            # showline=True,
            color='black',
            showticklabels= True,
            tickangle= 45,
            tickvals=['Mar-01-16', 'Jun-01-16', 'Sep-01-16', 'Dec-01-16', 'Mar-01-17', 'Jun-01-17', 'Sep-01-17', 'Dec-01-17', 'Mar-01-18', 'Jun-01-18', 'Sep-01-18', 'Dec-01-18', 'Mar-01-19', 'Jun-01-19','Sep-01-19', 'Dec-01-19', 'Mar-01-20', 'Jun-01-20','Sep-01-20', 'Dec-01-20'],
            ticktext=['Mar 01 2016', 'Jun 01 2016', 'Sep 01 2016', 'Dec 01 2016', 'Mar 01 2017', 'Jun 01 2017', 'Sep 01 2017', 'Dec 01 2017', 'Mar 01 2018', 'Jun 01 2018', 'Sep 01 2018', 'Dec 01 2018', 'Mar 01 2019', 'Jun 01 2019', 'Sep 01 2019', 'Dec 01 2019', 'Mar 01 2020', 'Jun 01 2020', 'Sep 01 2020', 'Dec 01 2020'],
        ),
        yaxis=dict(
            title= 'Percent Change',
            showgrid=True,
            showline=True,
            color='black',
            range = [-200,500],
        )
    )

    fig = go.Figure(
        data = datas,
        layout = layouts
    )

    # fig.add_annotation(
    #     x='Sep-01-16',
    #     y=136.3637,
    #     xref="x",
    #     yref="y",
    #     text="start of school",
    #     showarrow=True,
    #     font=dict(
    #         family="Courier New, monospace",
    #         size=16,
    #         color="#ffffff"
    #         ),
    #     align="center",
    #     arrowhead=2,
    #     arrowsize=1,
    #     arrowwidth=2,
    #     arrowcolor="#636363",
    #     ax=20,
    #     ay=-30,
    #     bordercolor="#c7c7c7",
    #     borderwidth=2,
    #     borderpad=4,
    #     bgcolor="#ff7f0e",
    #     opacity=0.8
    #     )

    return fig

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


if __name__ == '__main__':
    app.run_server(debug=True)