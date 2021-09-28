class\_average\_histogram\_viz
==============================

Web application to visualize particle count distributions of distinct views from a set of class averages. 


### Installation


1. Clone the git repository to your local machine and move into that directory

		git clone https://github.com/itaneja2/class_average_histogram_viz.git
		cd class_average_histogram_viz

3. Install class\_average\_histogram_viz using `pip`

		pip install .

4. Then, whenever you want to check for updates simply run

		git pull
		pip install .
		
	The first command (`git pull`) checks the [git repo](https://github.com/itaneja2/class_average_histogram_viz) for updates and then the second command installs the updated version.

### Usage

1.  Starting the web application
	
		python interactive_dash_plot.py
	
	Running this command will create a local server with the web application running on http://127.0.0.1:8050/ (or whatever url is displayed next to 'Dash is running on *****'). 
	
2.  Uploading files to the web application

	Upload the file `filepath.txt` to the web application. 

###### File Structure
    50S_ribosome_summary_mirror=1_scale=1
    |
    +----> class_average_panel_plots
           |
           +----> cluster_0.mrc
           +----> cluster_1.mrc
    |
    +----> filepath.txt [upload this]
    |
    +----> hierarchical_clustering
           |
           +----> 
    +----> histogram_plots
           |
           +----> 
    +----> input
           |
           +---->        
    +----> pairwise_matrix
           |
           +---->   
    +----> spectral_clustering
           |
           +---->  
           
 
