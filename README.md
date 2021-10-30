class\_average\_histogram\_viz
==============================

Web application to visualize the relative particle count distributions of distinct views from a set of class averages. In a nutshell, the purpose of this application is to determine the minimal set of class averages that best represents the data. By doing so, you can get a high level summary of the dominant views from a series of class averages and also get information regarding the percentage of particles assigned to those representative views. 


### Installation


1.	Make sure you first have the package [class\_average\_clustering](https://github.com/itaneja2/class_average_clustering) installed on your machine.

2. Clone the git repository to your local machine and move into that directory

		git clone https://github.com/itaneja2/class_average_histogram_viz.git
		cd class_average_histogram_viz

3. Install class\_average\_histogram_viz using `pip`

		pip install .

4. Then, whenever you want to check for updates simply run

		git pull
		pip install .
		
	The first command (`git pull`) checks the [git repo](https://github.com/itaneja2/class_average_histogram_viz) for updates and then the second command installs the updated version.
	
5.  Update the file `interactive_dash_plot_end_to_end.py ` to reflect where the programs from the package [class\_average\_clustering](https://github.com/itaneja2/class_average_clustering) are located. This is demarcated in the beginning of the file. 

### Usage



1.  Starting the web application
	
		python interactive_dash_plot_end_to_end.py
	
	Running this command will create a server with the web application running on http://\*\*\*\*.\*\*.\*\*.\*\*\*:****. 
	
2.  Uploading input to the web application:
	* Upload a *.mrc file  to the web application.
	* Upload a metadata file to the web applications. This will be either:
		* .star file (RELION)
		* ._particles.cs file (CryoSPARC) 
	* If you aren't running this server locally, I would recommend to compress the metadata file as a .zip file and then upload it. (It's a large file and can take a while to upload otherwise). 

3.  Enter input parameters:
	* `mirror`: Whether or not to run calculations for original class average and its mirror image (defaults to 1). 
	* `scale_factor`: Factor [between (0,1)] by which to downsample images. By default, this value is 1, so there is no need to update this parameter if you don't want to downsample. 
	* `num_clusters`: Number of clusters to separate class averages into. By default, this value determines the 'optimal' number of clusters to split the class average into. This is useful to split junk from non-junk class avearges. If there is a minor amount of junk in your class averages, I'd recommend setting this number to 1. 
	* See [class\_average\_clustering](https://github.com/itaneja2/class_average_clustering) for more information on these parameters. 
	

4. Click `Generate Input`. Once complete, you will see text below the button indicating that the data processing is complete. The amount of time this takes to run depends on the size of your input, but generally takes between 2-4 minutes. 
5. Click `Generate Visualization Data`. This actually renders the visualizations. 
6. You will see two dropdown menus. The first corresponds to which distance metric you want to use find similar class averages. `corr` corresponds to the rotational/reflectional invariant normalized cross correlation while `edge` corresponds to a shape based distance metric. You can find more details about these distance metrics [here](https://docs.google.com/document/d/1KYschE8r3YAb4bSrK9QIjiIVuh4YR_jJ4uS37zUM7VI/edit). The second dropdown menu corresponds to which cluster you want to view. 
7. You will see two radio buttons below this. One corresponds to displaying the median image of a set of representative views while the other corresponds to displaying the weighted average of a set of representative views. 
8. Finally, you will see two plots rendered: 
	* The plot on the left lets you click on different points corresponding to different thresholds used to group together similar class averages. Lower thresholds correspond to grouping together more similar class averages while higher thresholds correspond to grouping together less similar averages. The y-axis can be thought of as a measure of how near the representative class averages are to the entire dataset. Lower values are better in this case. 
	* The plot on the right displays a histogram corresponding to the relative particle count distributions assigned to each set of representative views. Hovering over each bar displays which class averages are in that set of representative views. (Note that the numberings correspond to the ones in the sorted .mrc file) In addition, the median image in that set is specified (as ref_image). For displaying the averaged image, images are aligned to the median image. 

           
 
### Results

See this [clip](https://www.youtube.com/watch?v=dNzlPQB8aWc) for a working demo. 
