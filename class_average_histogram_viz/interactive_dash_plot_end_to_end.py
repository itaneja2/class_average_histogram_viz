import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_extensions.snippets import send_file
import pandas as pd
import plotly.express as px
import base64
import pickle5 as pickle
from pathlib import Path
import numpy as np
import io
import subprocess 
import os, time
import shutil 
from zipfile import ZipFile
import glob

#UPDATE THIS DEPENDING ON ITS LOCATION
python_program_filepath = '/home_local/landeradmin/class_average_clustering/class_average_clustering' #path to where python programs are located. needs to be updated depending on where your programs are located


def load_obj(name):
    with open(name, 'rb') as f:
        return pickle.load(f)



def get_dataset_community_dist_df(hist_data_dict, cluster_num, edge_corr_str):
        
    threshold_data = hist_data_dict[edge_corr_str][1][cluster_num]
    dataset_community_dist_data = hist_data_dict[edge_corr_str][2][cluster_num]
    idx = range(0,len(threshold_data))
    optimal_community_num = hist_data_dict[edge_corr_str][-1][cluster_num]

    dataset_community_dist_data = np.array(dataset_community_dist_data)
    threshold_data = np.array(threshold_data)

    relevant_idx = np.where(dataset_community_dist_data < 1)

    dataset_community_dist_data = dataset_community_dist_data[relevant_idx]
    threshold_data = threshold_data[relevant_idx]
    dataset_community_dist_data = list(dataset_community_dist_data)
    threshold_data = list(threshold_data)
 
    optimal_community_list = []
    for i in idx:
        if i == optimal_community_num:
            optimal_community_list.append('optimal')
        else:
            optimal_community_list.append('non-optimal')

    optimal_community_list = np.array(optimal_community_list)
    optimal_community_list = optimal_community_list[relevant_idx]
    optimal_community_list = list(optimal_community_list)

    idx = np.array(idx)
    idx = idx[relevant_idx]
    idx = list(idx)

    ret = pd.DataFrame({'idx': idx, 'threshold': threshold_data, 'mean_dist': dataset_community_dist_data, 'optimal_community': optimal_community_list})
            
    return(ret)
           

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        
        html.Div([
            dcc.Upload(
                id='upload-mrc-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select *.mrc File')
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
                ), html.Div(id='mrc-data'),
            dcc.Upload(
                id='upload-metadata-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select *.star/*.cs OR *.star.zip/*.cs.zip File')
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
                ), html.Div(id='metadata-data'),
            html.Div([
                html.H4('Mirror Value',style={'display':'inline-block','margin-right':20}),
                dcc.Dropdown(id='mirror-val',options=[{'label': 0, 'value': 0}, {'label': 1, 'value': 1}], value=1, style={'display':'inline-block'}),
            ], style={'display':'inline-block', 'width': '100%'}),
            html.Div([
                html.H4('Sampling Factor Value',style={'display':'inline-block','margin-right':20}),
                dcc.Input(id='sampling-factor-val',type='number',value=None, style={'display':'inline-block', 'border': '1px solid black'}),
            ], style={'display':'inline-block', 'width': '100%'}),
            html.Div([
                html.H4('Number of Clusters',style={'display':'inline-block','margin-right':20}),
                dcc.Input(id='num-clusters-val',type='number',value=None, style={'display':'inline-block', 'border': '1px solid black'}),
            ], style={'display':'inline-block', 'width': '100%'}),
            html.Button('Generate Input Data', id='input-submit-val', n_clicks=0),
            html.Div(id='container-button-basic'),
            html.Div(children='Upload data and click button to generate input data'),
            html.Button('Generate Visualization Data', id='viz-submit-val', n_clicks=0),
            html.Div(children='Click button to generate histograms'),
 
            dcc.Dropdown(
                id='edge-corr',
                options=[],
                value=None,
            ),
            dcc.Dropdown(
                id='cluster-nums',
                options=[],
                value=None
            ),
            html.Button("Download Sorted .mrc File Corresponding to Selected Cluster", id="mrc_btn_image", n_clicks=0),
            dcc.Download(id="download-mrc"),
            html.Button("Download Sorted .png File Corresponding to Selected Cluster", id="png_btn_image", n_clicks=0),
            dcc.Download(id="download-png"),

            dcc.RadioItems(
                id='avg-or-median',
                options=[
                    {'label': 'Display Median Image', 'value': 'median'},
                    {'label': 'Display Average Image', 'value': 'average'}
                ],
                value='average',
                labelStyle={'display': 'inline-block'}
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




def get_mrc_upload_output(contents, filename):
            
    if '.mrc' not in filename:
        return html.Div([
            'File must be of type *.mrc'
        ])
    

    return html.Div([
    html.H5('Loaded %s' % filename),
    html.Hr() # horizontal line
    ])


def get_metadata_upload_output(contents, filename):
         
    if ('.star' not in filename) and ('.cs' not in filename):
        return html.Div([
            'File must be of type *.star/*.cs'
        ])
    

    return html.Div([
    html.H5('Loaded %s' % filename),
    html.Hr()  # horizontal line
    ])
    

def get_hist_dict(tmp_dir, mrc_filename):    

    output_data_dir = ''
    mrc_filename_wo_extension = mrc_filename.split('.')[0]
    all_output_data_dir = [os.path.join(tmp_dir, item) for item in os.listdir(tmp_dir) if os.path.isdir(os.path.join(tmp_dir, item))]
    for o in all_output_data_dir:
        if mrc_filename_wo_extension in o:
           output_data_dir = o 
           break 

    hist_data_path = '%s/histogram_plots/raw_data/hist_data.pkl' % output_data_dir

    print("Histogram Data Path: %s" % hist_data_path)
    
    if Path(hist_data_path).is_file():
        return load_obj(hist_data_path), output_data_dir
    else:
        print('%s not found' % hist_data_path)
    

@app.callback(dash.dependencies.Output('mrc-data', 'children'),
              dash.dependencies.Input('upload-mrc-data', 'contents'),
              dash.dependencies.Input('upload-mrc-data', 'filename'))
def update_mrc_output(contents, filename):
    if contents:
        return get_mrc_upload_output(contents, filename)

    
@app.callback(dash.dependencies.Output('metadata-data', 'children'),
              dash.dependencies.Input('upload-metadata-data', 'contents'),
              dash.dependencies.Input('upload-metadata-data', 'filename'))
def update_metadata_output(contents, filename):
    if contents:
        return get_metadata_upload_output(contents, filename)




@app.callback(
    dash.dependencies.Output('container-button-basic', 'children'),
    dash.dependencies.Input('input-submit-val', 'n_clicks'),
    dash.dependencies.Input('upload-mrc-data', 'contents'),
    dash.dependencies.Input('upload-mrc-data', 'filename'),
    dash.dependencies.Input('upload-metadata-data', 'contents'),
    dash.dependencies.Input('upload-metadata-data', 'filename'),
    dash.dependencies.Input('mirror-val', 'value'),
    dash.dependencies.Input('sampling-factor-val', 'value'),
    dash.dependencies.Input('num-clusters-val', 'value'))
def update_output(n_clicks, mrc_contents, mrc_filename, metadata_contents, metadata_filename, mirror_value, sf_value, num_clusters_value):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'input-submit-val' in changed_id:
        mrc_filename_wo_extension = mrc_filename.split('.')[0]

        content_type, content_string = mrc_contents.split(',')
        mrc_decoded = base64.b64decode(content_string)

        tmp_dir = '/tmp/dash_tmp_storage'
        #delete old contents in this folder
        if os.path.isdir(tmp_dir):
            all_files_and_folders =['%s/%s' % (tmp_dir,x) for x in os.listdir(tmp_dir)]
            for f in all_files_and_folders:
                f_info = os.stat(f)
                time_delta_in_days = (time.time_ns()*1e-6 - f_info.st_atime*1e3)*1.15741e-8
                if time_delta_in_days >= 7: #only delete if directory was made more than 1 week ago
                    if os.path.isdir(f):
                        shutil.rmtree(f, ignore_errors=True)
                    else:
                        os.remove(f)
        Path(tmp_dir).mkdir(parents=True, exist_ok=True)

        mrc_copy = '%s/%s' % (tmp_dir,mrc_filename)
        with open(mrc_copy, 'wb') as f:
            f.write(mrc_decoded)


        if '.zip' in metadata_filename:
            content_type, content_string = metadata_contents.split(',')
            metadata_decoded = base64.b64decode(content_string)
            zip_str = io.BytesIO(metadata_decoded)

            with ZipFile(zip_str) as zf:
                zf.extractall(tmp_dir)
            
            metadata_copy = '%s/%s' % (tmp_dir, metadata_filename.replace('.zip',''))

            if Path(metadata_copy).exists() == False:
                print('.star or .cs file not found')
        else:
            content_type, content_string = metadata_contents.split(',')
            metadata_decoded = base64.b64decode(content_string)

            metadata_copy = '%s/%s' % (tmp_dir,metadata_filename)
            with open(metadata_copy, 'wb') as f:
                f.write(metadata_decoded)

        if sf_value is not None:
            command = "python3 %s/gen_dist_matrix.py --mrc_file %s --metadata_file %s --mirror %d --scale_factor %f" % (python_program_filepath, mrc_copy, metadata_copy, mirror_value, sf_value)
        else:
            command = "python3 %s/gen_dist_matrix.py --mrc_file %s --metadata_file %s --mirror %d" % (python_program_filepath, mrc_copy, metadata_copy, mirror_value)

        print('Running %s' % command)
        subprocess.call(command, shell=True)
        print('Finished Running %s' % command)


        all_output_data_dir = [os.path.join(tmp_dir, item) for item in os.listdir(tmp_dir) if os.path.isdir(os.path.join(tmp_dir, item))]
        for o in all_output_data_dir:
            if mrc_filename_wo_extension in o:
               output_data_dir = o 
               break 

        print("Fetching data from directory %s" % output_data_dir)

        if num_clusters_value is not None:
            command = "python3 %s/plot_clusters.py --input_dir %s --num_clusters %d" % (python_program_filepath, output_data_dir, num_clusters_value)
        else:
            command = "python3 %s/plot_clusters.py --input_dir %s" % (python_program_filepath, output_data_dir)

        print('Running %s' % command)
        subprocess.call(command, shell=True)
        print('Finished Running %s' % command)

        return html.Div([html.H5('Completed Data Processing'),html.Hr()])



@app.callback(
    dash.dependencies.Output('cluster-nums', 'options'),
    dash.dependencies.Input('viz-submit-val', 'n_clicks'),
    dash.dependencies.Input('upload-mrc-data', 'filename'))
def update_cluster_num_options(n_clicks, mrc_filename):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if 'viz-submit-val' in changed_id:
        tmp_dir = '/tmp/dash_tmp_storage'
        hist_data_dict, output_data_dir = get_hist_dict(tmp_dir, mrc_filename)
        cluster_nums = sorted(hist_data_dict['edge'][0].keys())
        lst = [{'label': i, 'value': i} for i in cluster_nums]
        return lst
    else:
        return []

    
@app.callback(
    dash.dependencies.Output('edge-corr', 'options'),
    dash.dependencies.Input('viz-submit-val', 'n_clicks'),
    dash.dependencies.Input('upload-mrc-data', 'filename'))
def update_edge_corr_options(n_clicks, mrc_filename):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'viz-submit-val' in changed_id:
        tmp_dir = '/tmp/dash_tmp_storage'
        hist_data_dict, output_data_dir = get_hist_dict(tmp_dir, mrc_filename)
        edge_corr_keys = sorted(hist_data_dict.keys())
        lst = [{'label': i, 'value': i} for i in edge_corr_keys]
        return lst
    else:
        return []  




@app.callback(
    dash.dependencies.Output("download-mrc", "data"),
    dash.dependencies.Input("mrc_btn_image", "n_clicks"),
    dash.dependencies.Input('cluster-nums', 'value'),
    dash.dependencies.Input('upload-mrc-data', 'filename'),
    prevent_initial_call=True,
)
def func(n_clicks, cluster_num, mrc_filename):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'mrc_btn_image' in changed_id:
        tmp_dir = '/tmp/dash_tmp_storage'
        hist_data_dict, output_data_dir = get_hist_dict(tmp_dir, mrc_filename)
        path_to_mrc = '%s/class_average_panel_plots/cluster_%d.mrc' % (output_data_dir, cluster_num)

        if Path(path_to_mrc).is_file():
            return send_file(path_to_mrc)
        else:
            print('%s not found' % path_to_mrc)

@app.callback(
    dash.dependencies.Output("download-png", "data"),
    dash.dependencies.Input("png_btn_image", "n_clicks"),
    dash.dependencies.Input('cluster-nums', 'value'),
    dash.dependencies.Input('upload-mrc-data', 'filename'),
    prevent_initial_call=True,
)
def func(n_clicks, cluster_num, mrc_filename):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'png_btn_image' in changed_id:
        tmp_dir = '/tmp/dash_tmp_storage'
        hist_data_dict, output_data_dir = get_hist_dict(tmp_dir, mrc_filename)
        path_to_png = '%s/class_average_panel_plots/cluster_%d.png' % (output_data_dir, cluster_num)

        if Path(path_to_png).is_file():
            return send_file(path_to_png)
        else:
            print('%s not found' % path_to_png)

    

@app.callback(
    dash.dependencies.Output('sil-scatter', 'figure'),
    [dash.dependencies.Input('cluster-nums', 'value'),
     dash.dependencies.Input('edge-corr', 'value'),
     dash.dependencies.Input('upload-mrc-data', 'filename')])
def update_scatter(cluster_num, edge_corr_str, mrc_filename):
    

    tmp_dir = '/tmp/dash_tmp_storage'                 
    hist_data_dict, output_data_dir = get_hist_dict(tmp_dir, mrc_filename)
    dataset_community_dist_df = get_dataset_community_dist_df(hist_data_dict, cluster_num, edge_corr_str)
    
    fig = px.scatter(x=dataset_community_dist_df['threshold'],
            y=dataset_community_dist_df['mean_dist'],
            color=dataset_community_dist_df['optimal_community'],
            hover_name=dataset_community_dist_df['idx']
            )

    fig.update_traces(customdata=dataset_community_dist_df['idx'])

    fig.update_layout(yaxis_title = 'Mean Distance',
                      xaxis_title = 'Distance Threshold',
                      hovermode='closest',
                      margin={'l': 0, 'b': 10, 't': 40, 'r': 0})

    return(fig)


@app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    [dash.dependencies.Input('sil-scatter', 'clickData'),
     dash.dependencies.Input('cluster-nums', 'value'),
     dash.dependencies.Input('edge-corr', 'value'),
     dash.dependencies.Input('avg-or-median', 'value'),
     dash.dependencies.Input('upload-mrc-data', 'filename')])
def update_bar_chart(clickData, cluster_num, edge_corr_str, avg_median_str, mrc_filename):
    

    tmp_dir = '/tmp/dash_tmp_storage'                 
    hist_data_dict, output_data_dir = get_hist_dict(tmp_dir, mrc_filename)

    idx = clickData['points'][0]['hovertext']
    
    cluster_community = hist_data_dict[edge_corr_str][0][cluster_num][idx]
    cluster_community_count = hist_data_dict[edge_corr_str][3][cluster_num][idx]
    cluster_ref_img = hist_data_dict[edge_corr_str][4][cluster_num][idx]
    cluster_max_community_weight = hist_data_dict[edge_corr_str][5][cluster_num][idx]
    
 
    y=cluster_community_count/(np.sum(cluster_community_count))
    x=np.linspace(1,len(y),len(y))

    all_imgs_cluster_c = []
    for community_img in cluster_community:
        all_imgs_cluster_c.append("-".join(str(x) for x in sorted(community_img)))
    
    plot_df = pd.DataFrame({'x': x, 'y': y, 'ref_img': cluster_ref_img, 'all_img': all_imgs_cluster_c})

    ref_img_loc = '%s/histogram_plots/ref_img/%s/cluster_%s' % (output_data_dir, edge_corr_str, str(int(cluster_num)))
    
    ref_img_list = []
    for img in cluster_ref_img:
        ref_img_list.append('%s/%s.png' % (ref_img_loc, str(int(img))))
    
    average_img_wrt_ref_loc = '%s/histogram_plots/average_image_wrt_ref/%s/cluster_%s' % (output_data_dir, edge_corr_str, str(int(cluster_num)))

    average_img_wrt_ref_list = []
    for i in range(0,len(ref_img_list)):
        average_img_wrt_ref_list.append('%s/%s_%s.png' % (average_img_wrt_ref_loc, str(int(idx)), str(i)))

    
    plot_title = 'Maximum Community Weight = %s' % str(cluster_max_community_weight) 

    fig = px.bar(plot_df, x='x', y='y',
                hover_data=['ref_img', 'all_img'])

    fig.update_layout(yaxis_range=[0,np.max(y)*2], title = plot_title,
                      yaxis_title = 'Fraction of Particles in Cluster %d' % cluster_num, xaxis_title = 'Community Number')

    # add images
    if avg_median_str == 'median':
        img_display_list = ref_img_list
    else:
        img_display_list = average_img_wrt_ref_list

    for i,src,yy in zip(range(0,len(img_display_list)),img_display_list,y):
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
    app.run_server(host="0.0.0.0", port="8050")
