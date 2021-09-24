import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import base64
import pickle5 as pickle
from pathlib import Path
import numpy as np
import io


def load_obj(name):
    with open(name, 'rb') as f:
        return pickle.load(f)


def get_sil_score_df(hist_data_dict, cluster_num, edge_corr_str):
        
    threshold_data = hist_data_dict[edge_corr_str][1][cluster_num]
    sil_data = hist_data_dict[edge_corr_str][2][cluster_num]
    idx = range(0,len(threshold_data))
    optimal_community_num = hist_data_dict[edge_corr_str][-1][cluster_num]
    
    sil_data = np.array(sil_data)
    sil_data[sil_data == -1] = 0 
    sil_data = list(sil_data)
    
    optimal_community_list = []
    for i in idx:
        if i == optimal_community_num:
            optimal_community_list.append('optimal')
        else:
            optimal_community_list.append('non-optimal')
            
    return(pd.DataFrame({'idx': idx, 'threshold': threshold_data, 'sil_score': sil_data, 'optimal_community': optimal_community_list}))
           
           

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
                ), html.Div(id='output-data-upload'),
            dcc.Dropdown(
                id='edge-corr',
                options=[],
                value=None,
            ),
            dcc.Dropdown(
                id='cluster-nums',
                options=[],
                value=None
            )
        ],
        style={'width': '49%', 'display': 'inline-block'})
        
    ]),

    html.Div([
        dcc.Graph(
            id='sil-scatter',
            clickData={'points': [{'customdata': 0}]}
        )
    ], style={'width': '49%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Graph(id='bar-chart'),
    ], style={'display': 'inline-block', 'width': '49%'})
    
])




def get_html_upload_output(contents, filename):
        
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    
    if 'filepath.txt' not in filename:
        return html.Div([
            'File must be named filepath.txt, whose contents is simply the absolute path of the parent folder containing this file'
        ])
    
    filepath_name = np.loadtxt(io.StringIO(decoded.decode('utf-8')), dtype='str')
    
    if Path('%s/filepath.txt' % filepath_name).exists() == False:
        return html.Div([
            'Contents of filepath.txt does not contain the absolute path of the parent folder'
        ])        
                            
    hist_data = '%s/histogram_plots/raw_data/hist_data.pkl' % filepath_name
    
    if Path(hist_data).exists() == False:
        return html.Div([
            '%s does not exist' % hist_data
        ])  

    return html.Div([
    html.H5('Loaded %s' % filename),
    html.Hr(),  # horizontal line
    ])
    

def get_hist_dict(contents, filename):
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    filepath_name = np.loadtxt(io.StringIO(decoded.decode('utf-8')), dtype='str')      
                            
    hist_data = '%s/histogram_plots/raw_data/hist_data.pkl' % filepath_name
    
    return(load_obj(hist_data), filepath_name)
    

@app.callback(dash.dependencies.Output('output-data-upload', 'children'),
              dash.dependencies.Input('upload-data', 'contents'),
              dash.dependencies.Input('upload-data', 'filename'))
def update_output(contents, filename):
    if contents:
        return get_html_upload_output(contents, filename)
    


@app.callback(
    dash.dependencies.Output('cluster-nums', 'options'),
    [dash.dependencies.Input('upload-data', 'contents'),
     dash.dependencies.Input('upload-data', 'filename')])
def update_cluster_num_options(contents, filename):
    if contents:
        hist_data_dict, filepath_name = get_hist_dict(contents, filename)
        cluster_nums = sorted(hist_data_dict['edge'][0].keys())
        lst = [{'label': i, 'value': i} for i in cluster_nums]
        return lst
    else:
        return []    
    
@app.callback(
    dash.dependencies.Output('edge-corr', 'options'),
    [dash.dependencies.Input('upload-data', 'contents'),
     dash.dependencies.Input('upload-data', 'filename')])
def update_edge_corr_options(contents, filename):
    if contents:
        hist_data_dict, filepath_name = get_hist_dict(contents, filename)
        edge_corr_keys = sorted(hist_data_dict.keys())
        lst = [{'label': i, 'value': i} for i in edge_corr_keys]
        return lst
    else:
        return []  
    
    

@app.callback(
    dash.dependencies.Output('sil-scatter', 'figure'),
    [dash.dependencies.Input('upload-data', 'contents'),
     dash.dependencies.Input('upload-data', 'filename'),
     dash.dependencies.Input('cluster-nums', 'value'),
     dash.dependencies.Input('edge-corr', 'value')])
def update_scatter(contents, filename, cluster_num, edge_corr_str):
                                
    hist_data_dict, filepath_name = get_hist_dict(contents, filename)
    sil_score_df = get_sil_score_df(hist_data_dict, cluster_num, edge_corr_str)
    
    fig = px.scatter(x=sil_score_df['threshold'],
            y=sil_score_df['sil_score'],
            color=sil_score_df['optimal_community'],
            hover_name=sil_score_df['idx']
            )

    fig.update_traces(customdata=sil_score_df['idx'])

    fig.update_layout(yaxis_title = 'Silhouette Score',
                      xaxis_title = 'Distance Threshold',
                      hovermode='closest',
                      margin={'l': 0, 'b': 10, 't': 40, 'r': 0})

    return(fig)


@app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    [dash.dependencies.Input('sil-scatter', 'clickData'),
     dash.dependencies.Input('upload-data', 'contents'),
     dash.dependencies.Input('upload-data', 'filename'),
     dash.dependencies.Input('cluster-nums', 'value'),
     dash.dependencies.Input('edge-corr', 'value')])
def update_bar_chart(clickData, contents, filename, cluster_num, edge_corr_str):
    
    hist_data_dict, filepath_name = get_hist_dict(contents, filename)

    idx = clickData['points'][0]['hovertext']
    
    cluster_community = hist_data_dict[edge_corr_str][0][cluster_num][idx]
    cluster_community_count = hist_data_dict[edge_corr_str][3][cluster_num][idx]
    cluster_ref_img = hist_data_dict[edge_corr_str][4][cluster_num][idx]
    cluster_norm_dist = hist_data_dict[edge_corr_str][5][cluster_num][idx]
    
 
    y=cluster_community_count/(np.sum(cluster_community_count))
    x=np.linspace(1,len(y),len(y))

    all_imgs_cluster_c = []
    for community_img in cluster_community:
        all_imgs_cluster_c.append("-".join(str(x) for x in sorted(community_img)))
    
    plot_df = pd.DataFrame({'x': x, 'y': y, 'ref_img': cluster_ref_img, 'all_img': all_imgs_cluster_c})

    ref_img_loc = '%s/histogram_plots/ref_img/%s/cluster_%s' % (filepath_name, edge_corr_str, str(int(cluster_num)))
    
    ref_img_list = []
    for img in cluster_ref_img:
        ref_img_list.append('%s/%s.png' % (ref_img_loc, str(int(img))))
    
    plot_title = 'Normalized Community Distance = %s' % cluster_norm_dist    

    fig = px.bar(plot_df, x='x', y='y',
                hover_data=['ref_img', 'all_img'])

    fig.update_layout(yaxis_range=[0,np.max(y)*2], title = plot_title,
                      yaxis_title = 'Percentage of Particles in Cluster %d' % cluster_num, xaxis_title = 'Community Number')
    # add images
    for i,src,yy in zip(range(0,len(ref_img_list)),ref_img_list,y):
        logo = base64.b64encode(open(src, 'rb').read())
        fig.add_layout_image(
            source='data:image/png;base64,{}'.format(logo.decode()),
            xref="x",
            yref="y",
            x=x[i],
            y=yy+.02,
            xanchor="center",
            yanchor="bottom",
            sizex=.5,
            sizey=.5,
        )
    
    return(fig)



if __name__ == '__main__':
    app.run_server(debug=False)
