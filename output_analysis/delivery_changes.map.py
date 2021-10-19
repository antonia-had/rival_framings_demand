import pandas as pd
import dask.dataframe as dd
import numpy as np
import cartopy.feature as cpf
import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from pathlib import Path


ids_of_interest = np.genfromtxt('../ids.txt', dtype='str').tolist()
realization_years = 105
months = 12

# Get structure locations
structures = pd.read_csv('../structures_files/modeled_diversions.csv', index_col=0)
extent = [-109.069, -105.6, 38.85, 40.50]
extent_large = [-111.0, -101.0, 36.5, 41.5]
rivers_10m = cpf.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m')
shape_feature = ShapelyFeature(Reader('../structures_files/Shapefiles/Water_Districts.shp').geometries(),
                               ccrs.PlateCarree(), edgecolor='white', facecolor='None')
flow_feature = ShapelyFeature(Reader('../structures_files/Shapefiles/UCRBstreams.shp').geometries(), ccrs.PlateCarree(),
                              edgecolor='#1d3557', facecolor='None')

# with open("../users_per_threshold.pkl", "rb") as fp:
#     users_per_threshold = pickle.load(fp)
# with open("../curtailment_per_threshold.pkl", "rb") as fp:
#     curtailment_per_threshold = pickle.load(fp)

rule_outputs = '../rules_parquet'
flow_experiment_outputs = '../xdd_parquet_flow'
figure_directory = '../delivery_changes_map'

def gen_arrow_head_marker(rot):
    """generate a marker to plot with matplotlib scatter, plot, ...

    Function taken from https://stackoverflow.com/questions/23345565/is-it-possible-to-control-matplotlib-marker-orientation
    rot=0: positive x direction
    Parameters
    ----------
    rot : float
        rotation in degree
        0 is positive x direction

    Returns
    -------
    arrow_head_marker : Path
        use this path for marker argument of plt.scatter
    scale : float
        multiply a argument of plt.scatter with this factor got get markers
        with the same size independent of their rotation.
        Paths are autoscaled to a box of size -1 <= x, y <= 1 by plt.scatter
    """
    arr = np.array([[.1, .3], [.1, -.3], [1, 0]])  # arrow shape
    angle = rot / 180 * np.pi
    rot_mat = np.array([
        [np.cos(angle), np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]
        ])
    arr = np.matmul(arr, rot_mat)  # rotates the arrow

    # scale
    x0 = np.amin(arr[:, 0])
    x1 = np.amax(arr[:, 0])
    y0 = np.amin(arr[:, 1])
    y1 = np.amax(arr[:, 1])
    scale = np.amax(np.abs([x0, x1, y0, y1]))

    arrow_head_marker = mpl.path.Path(arr)
    return arrow_head_marker, scale

def draw_delivery_change_per_rule(sow, rule):

    # Create figure to draw points on
    fig = plt.figure(figsize=(18, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.imshow(np.tile(np.array([[[255, 255, 255]]], dtype=np.uint8), [2, 2, 1]),
          origin='upper',
          transform=ccrs.PlateCarree(),
          extent=extent)
    ax.add_feature(shape_feature, facecolor='#D3D3D3', alpha=0.6)
    ax.add_feature(flow_feature, alpha=0.6, linewidth=1.5, zorder=4)

    # Read data for state of the world
    df_sow = dd.read_parquet(Path(f'{flow_experiment_outputs}/S{sow}_*.parquet'),
                         engine='pyarrow-dataset').compute()

    # Read data for state of the world and applied rule
    df_rule = pd.read_parquet(Path(f'{rule_outputs}/Rule_{rule}/S{sow}_{rule}.parquet'))

    #Create column in structures dataframe to store change, marker and marker scaling factor
    structures['change'] = 0
    structures['marker'] = 0
    structures['scale'] = 0

    #Calculate rule change for every structure
    for structure_id in ids_of_interest:
        if structure_id in structures.index:
            # Get value for structure in base SOW
            mask_sow = df_sow['structure_id'] == structure_id
            new_df_sow = df_sow[mask_sow]
            deliveries_sow = (new_df_sow['demand'].values - new_df_sow['shortage'].values) * 1233.4818 / 1000000
            base_value = np.mean(deliveries_sow)

            #Get value for structure in run with rule
            mask_rule = df_rule['structure_id'] == structure_id
            new_df_rule = df_rule[mask_rule]
            deliveries_rule = (new_df_rule['demand'].values - new_df_rule['shortage'].values) * 1233.4818 / 1000000
            adaptive_demands_value = np.mean(deliveries_rule)

            structures.at[structure_id, 'change'] = (adaptive_demands_value-base_value)*100/base_value

    #Use change to calculate marker rotation
    max_change = np.max(structures['change'].values)
    min_change = np.min(structures['change'].values)
    max_absolute_change = np.max(np.abs([max_change, min_change]))
    structures['rotation'] = [180*(max_absolute_change - value)/(max_absolute_change-min_change)
                              for value in structures['change'].values]

    #Loop through every structure again to create markers
    for structure_id in structures.index:
        structures.at[structure_id, 'marker'], \
        structures.at[structure_id, 'scale'] = gen_arrow_head_marker(structures.at[structure_id, 'rotation'])
        if structures.at[structure_id, 'rotation']==90:
            structures.at[structure_id, 'color'] = 'grey'
        elif structures.at[structure_id, 'rotation']>90:
            structures.at[structure_id, 'color'] = '#ee6c4d'
        elif structures.at[structure_id, 'rotation']<90:
            structures.at[structure_id, 'color'] = '#3d5a80'

        ax.scatter(structures.at[structure_id, 'X'], structures.at[structure_id, 'Y'],
                   marker=structures.at[structure_id, 'marker'], s=(structures.at[structure_id,'scale']*50)**2,
                   c=structures.at[structure_id,'color'], alpha=0.8, transform=ccrs.PlateCarree(),
                   edgecolors=None, zorder=5)

    marker, scale = gen_arrow_head_marker(180)
    marker1 = ax.scatter([], [], marker=marker, s=(scale*50)**2, c='#ee6c4d', alpha=0.8,
                          transform=ccrs.PlateCarree(), edgecolors=None,)
    marker, scale = gen_arrow_head_marker(90)
    marker2 = ax.scatter([], [], marker=marker, s=(scale*50)**2, c='grey', alpha=0.8,
                          transform=ccrs.PlateCarree(), edgecolors=None,)
    marker, scale = gen_arrow_head_marker(0)
    marker3 = ax.scatter([], [], marker=marker, s=(scale*50)**2, c='#3d5a80', alpha=0.8,
                          transform=ccrs.PlateCarree(), edgecolors=None)
    legend_markers = [marker1, marker2, marker3]
    labels = [f'-{round(max_absolute_change)}%', 'No change', f'+{round(max_absolute_change)}%']
    plt.legend(handles=legend_markers, labels=labels, loc='upper left', fontsize=16, title_fontsize=20, ncol=3,
               labelspacing=2, handletextpad=2, borderpad=2, title='Change in deliveries')

    fig.savefig(f'{figure_directory}/S{sow}_{rule}.png',
                dpi=300)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create figure of user demand reduction')
    parser.add_argument('sow', type=int,
                        help='Hydrologic scenario (SOW)')
    parser.add_argument('rule', type=int,
                        help='Adaptive rule')
    args = parser.parse_args()
    draw_delivery_change_per_rule(args.SOW, args.rule)