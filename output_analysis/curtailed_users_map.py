import pandas as pd
import numpy as np
import cartopy.feature as cpf
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import argparse
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import pickle

def draw_curtailed_users(users_number, curtailment_level):
    '''Get all rights and decrees of each WDID'''
    rights = pd.read_csv('../hist_files/diversions_admin.csv')
    groupbyadmin = rights.groupby('WDID')
    rights_per_wdid = groupbyadmin.apply(lambda x: x['Admin'].values)
    decrees_per_wdid = groupbyadmin.apply(lambda x: x['Decree'].values)

    with open("../users_per_threshold.pkl", "rb") as fp:
        users_per_threshold = pickle.load(fp)
    with open("../curtailment_per_threshold.pkl", "rb") as fp:
        curtailment_per_threshold = pickle.load(fp)

    curtailment_levels = np.loadtxt('../curtailment_levels.txt')
    no_rights = list(np.arange(10, 110, 10))

    # Get structure locations
    structures = pd.read_csv('../structures_files/modeled_diversions.csv', index_col=0)
    structures['sizes'] = [np.sum(decrees_per_wdid.get(ID)) for ID in structures.index.values]
    extent = [-109.069,-105.6,38.85,40.50]
    extent_large = [-111.0,-101.0,36.5,41.5]
    rivers_10m = cpf.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m')
    shape_feature = ShapelyFeature(Reader('../structures_files/Shapefiles/Water_Districts.shp').geometries(), ccrs.PlateCarree(), edgecolor='white', facecolor='None')
    flow_feature = ShapelyFeature(Reader('../structures_files/Shapefiles/UCRBstreams.shp').geometries(), ccrs.PlateCarree(), edgecolor='#1d3557', facecolor='None')


    fig = plt.figure(figsize=(18, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.imshow(np.tile(np.array([[[255, 255, 255]]], dtype=np.uint8), [2, 2, 1]),
          origin='upper',
          transform=ccrs.PlateCarree(),
          extent=extent)
    ax.add_feature(shape_feature, facecolor='#D3D3D3', alpha=0.6)
    ax.add_feature(flow_feature, alpha=0.6, linewidth=1.5, zorder=4)
    points = ax.scatter(structures['X'], structures['Y'], marker='.',
                        s=structures['sizes']*10, c='#457b9d', alpha=0.4,
                        transform=ccrs.PlateCarree(), edgecolors=None, zorder=5)

    number_of_users_level = users_number
    curtailment_applied = curtailment_level
    users_to_draw = structures[structures.index.isin(users_per_threshold[number_of_users_level])]
    users_to_draw.reindex(list(users_per_threshold[number_of_users_level]))
    users_to_draw['adjusted sizes'] = pd.Series(dtype=float)
    for i, row in users_to_draw.iterrows():
        index = np.where(users_per_threshold[number_of_users_level]==i)[0][0]
        original_demand = row['sizes']
        adjusted_demand = original_demand - (original_demand * curtailment_per_threshold[number_of_users_level][index] *
                                             curtailment_levels[curtailment_applied] / 100)
        users_to_draw.at[i, 'adjusted sizes'] = adjusted_demand
    ax.scatter(users_to_draw['X'], users_to_draw['Y'], marker='.',
                        s=users_to_draw['adjusted sizes']*10, c='#457b9d', alpha=1, transform=ccrs.PlateCarree(), zorder=6)
    ax.set_title(label=f'Reduction in demands in {no_rights[number_of_users_level]}% of rights '
                       f'by {curtailment_levels[curtailment_applied]}% of their demand', fontfamily='sans-serif',
                 fontsize=26, loc='left')
    min_size=17.6
    max_size=1942
    marker1 = ax.scatter([], [], marker='.', s=min_size*10, c='#808080', alpha=0.4,
                          transform=ccrs.PlateCarree(), edgecolors=None)
    marker2 = ax.scatter([], [], marker='.', s=max_size*10, c='#808080', alpha=0.4,
                          transform=ccrs.PlateCarree(), edgecolors=None,)
    legend_markers = [marker1, marker2]
    labels = [str(round(min_size*0.028316847, 1)), str(round(max_size*0.028316847, 1))]
    plt.legend(handles=legend_markers, labels=labels, loc='upper left', fontsize=16, title_fontsize=20,
               labelspacing=2, handletextpad=2, borderpad=2, title='Decree size (m$^3$/s)')
    fig.savefig(f'highlight_users_{no_rights[number_of_users_level]}_{curtailment_levels[curtailment_applied]}.png',
                dpi=300)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create figure of user demand reduction')
    parser.add_argument('users_number', type=int,
                        help='Number of rights curtailed (level values between 0-9)')
    parser.add_argument('curtailment_level', type=int,
                        help='Level of curtailment to apply (level values between 0-9)')
    args = parser.parse_args()
    draw_curtailed_users(args.users_number, args.curtailment_level)