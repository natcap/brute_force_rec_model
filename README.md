### rec_model_aoi_cuts.py 

This script will make a batch of calls to the InVEST Recreation model server - one call for each feature in an Area of Interest shapefile. It returns photo-user-day counts per feature.

#### Why use this script?  
The Recreation model does support AOI shapefiles with multiple features, but it's spatial queries are not optimized for AOI's that have very large extents (continental) and sparse features within that extent. For AOIs that fit that description, this brute force approach of making a seperate call for each feature will be faster.

