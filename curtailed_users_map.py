import pandas as pd
import numpy as np
import cartopy.feature as cpf
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.io.img_tiles as cimgt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

'''Get all rights and decrees of each WDID'''
rights = pd.read_csv('./hist_files/iwr_admin.csv')
groupbyadmin = rights.groupby('WDID')
rights_per_wdid = groupbyadmin.apply(lambda x: x['Admin'].values)
decrees_per_wdid = groupbyadmin.apply(lambda x: x['Decree'].values)

no_rights = [5, 10, 20]

threshold_admins = [np.percentile(rights['Admin'].values, 100 - p, interpolation='nearest') for p in no_rights]
rights_to_curtail = [rights.loc[rights['Admin'] > t] for t in threshold_admins]
users_per_threshold = [np.unique(rights_to_curtail[x]['WDID'].values) for x in range(3)]

structures = pd.read_csv('./structures_files/modeled_diversions.csv',index_col=0)
curtailed_structures = structures.loc[users_per_threshold[2]]

highlight_structures = structures.loc[['36_ADC017', '3704614']]

extent = [-109.069,-105.6,38.85,40.50]
extent_large = [-111.0,-101.0,36.5,41.5]
rivers_10m = cpf.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m')
stamen_terrain = cimgt.Stamen('terrain-background')
shape_feature = ShapelyFeature(Reader('./structures_files/Shapefiles/Water_Districts.shp').geometries(), ccrs.PlateCarree(), edgecolor='black', facecolor='None')
flow_feature = ShapelyFeature(Reader('./structures_files/Shapefiles/UCRBstreams.shp').geometries(), ccrs.PlateCarree(), edgecolor='royalblue', facecolor='None')


fig = plt.figure(figsize=(18, 9))
ax = plt.axes(projection=stamen_terrain.crs)
ax.set_extent(extent, crs=ccrs.PlateCarree())
ax.add_image(stamen_terrain, 9)
ax.add_feature(shape_feature, facecolor='#a1a384', alpha=0.6)
ax.add_feature(flow_feature, alpha=0.6, linewidth=1.5, zorder=4)
points = ax.scatter(structures['X'], structures['Y'], marker='.',
                    s=200, c='blue', transform=ccrs.PlateCarree(), zorder=5)
curtailed_points = ax.scatter(curtailed_structures['X'], curtailed_structures['Y'], marker='.',
                    s=300, c='red', transform=ccrs.PlateCarree(), zorder=5)
highlight_points = ax.scatter(highlight_structures['X'], highlight_structures['Y'], marker='.',
                    s=1000, c='yellow', transform=ccrs.PlateCarree(), zorder=5)
fig.savefig('highlight_users.png')