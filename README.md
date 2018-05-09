# GeoTools
Tools for interpreting, analyzing, and viewing geologic data

Age_Freq.py - Calculates the probability of age distributions given a set of min and max ages using a Bayesian aproach, and multithreading to speed up the process

beachball.py - Makes a KMZ of moment tensor solutions from input csv of earthquake data. Currently configured for the Montana Regional Seismic Network.

Field_Trip_KMZ.py - Takes a csv of lats, longs, point names, and point descriptions and makes a KMZ of the points and metadata. Currently formatted to produce field trips for the Tobacco Root Gelogical Society.

Plot_Anim.py - Takes a csv of age, lat, and long data and makes an animation with a geographic basemap.

Plot_Anim_Hexbin.py - Same as Plot_Anim but makes hexbins of data. Implementation is different as hexbin is not iterable for matplotlib's animation toolbox. Instead prints each frame and combines them into a movie using the moviepy library.

Plot_Anim_Hexbin_median_Val.py - Same as Plot_Anim_Hexbin but calculates median value in each hexbin.

Plot_Anim_Hexbin_median_Val_Tibet.py - Same as Plot_Anim_Hexbin_median_Val but configured to work for data from Tibet.

Plot_Anim_Tibet.py - Takes a csv of age, lat, and long data and makes an animation with a geographic basemap. Set for data from Tibet.

Plot_Anim_Tibet_Colors.py - Creates an animation of point data on a map, animated by time. Has a colored legend to differentiate points based on a field. Colors are set to fade over time.

Point_Poly.py - Takes a list of polygons, and a list of data with min/max ages, and lat/long data. Then estimates frequency of samples in each polygon, using a Bayesean approach.
