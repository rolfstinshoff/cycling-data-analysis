import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import pandas as pd
import numpy as np
import six, webbrowser
import plotter.activitymapper as am

# function that plots the ride analysis
def plot_analysis_adjusted(df, sf, filename, log_file):
    x = df['distance']
    possible_data = ['altitude', 'speed', 'heart_rate']
    
    i = 0
    for item in possible_data:
        if item in df.columns:
            i += 1
    try:
        if i > 0:
            with open(log_file, 'a+') as log:
                log.write('\nPlotting data...')
    except Exception as e:
        with open(log_file, 'a+') as log:
            log.write(f'\nThere was no data to plot. Exception raised: {e}')

    fig, ax = plt.subplots(i, figsize=(10,7))
    fig.tight_layout(pad=2.0, rect=[0, 0.03, 1, 0.95])
    fig.suptitle(f'Ride summary ({filename[:10]})', fontsize=16)

    if 'altitude' in df.columns:
        df.plot.area(ax=ax[0], x='distance', y='altitude', legend=False, title='Elevation',color='grey', alpha=1)
        ax[0].set_ylim(0, df.altitude.max() + 20)
        ax[0].set_yticks([i if df.altitude.max() < 1000 else 2*i for i in range(0, df.altitude.max().astype('int') + 20, 100)])
        ax[0].grid(which='major', linestyle='-', linewidth='0.5', color='grey', alpha=0.4)
        ax[0].grid(which='minor', linestyle=':', linewidth='0.5', color='grey', alpha=0.4)

        fig_hm_3d, ax_hm_3d = plt.subplots(1,1, figsize=(10, 7))
        x1, y1, z1 = df.position_long, df.position_lat, df.altitude
        sc = ax_hm_3d.scatter(x1, y1, c=z1, cmap=cmx.get_cmap('inferno_r'), marker=".", s=1)
        fig_hm_3d.colorbar(sc, ax=ax_hm_3d)
        fig_hm_3d.suptitle('Altitude distribution', fontsize=16)
        ax_hm_3d.set_xlabel('Lattitude')
        ax_hm_3d.set_ylabel('Longitude')
        ax_hm_3d.set_ylim(df.position_lat.min()-0.01, df.position_lat.max()+0.01)
        ax_hm_3d.set_xlim(df.position_long.min()-0.01, df.position_long.max()+0.01)

    if 'speed' in df.columns:
        df.plot.area(ax=ax[1], x='distance', y='speed', legend=False, title='Speed', color='blue')
        avg_speed = [sf.at[0, 'avg_speed'] for i in df.distance]
        ax[1].plot(x, avg_speed, color='black', linestyle='--')
        ax[1].set_ylim(0, df.speed.max() + 5)
        ax[1].set_yticks([i if df.speed.max() < 100 else 2*i for i in range(0, df.speed.max().astype('int') + 5, 10)])
        ax[1].grid(which='major', linestyle='-', linewidth='0.5', color='grey', alpha=0.4)
        ax[1].grid(which='minor', linestyle=':', linewidth='0.5', color='grey', alpha=0.4)

    if 'heart_rate' in df.columns and not df['heart_rate'].isnull().all():
        df.plot.area(ax=ax[2], x='distance', y='heart_rate', legend=False, title='Heart rate', color='red')
        avg_hr = [sf.at[0, 'avg_heart_rate'] for i in df.distance]
        ax[2].plot(x, avg_hr, color='black', linestyle='--')
        ax[2].set_ylim(100, df.heart_rate.max() + 5)
        ax[2].set_yticks([i for i in range(100, df.heart_rate.max().astype('int') + 5, 20)])
        ax[2].grid(which='major', linestyle='-', linewidth='0.5', color='grey', alpha=0.4)
        ax[2].grid(which='minor', linestyle=':', linewidth='0.5', color='grey', alpha=0.4)

        fig_hr_3d, ax_hr_3d = plt.subplots(1,1, figsize=(10, 7))
        x2, y2, z2 = df.position_long, df.position_lat, df.heart_rate
        sc2 = ax_hr_3d.scatter(x2, y2, c=z2, cmap=cmx.get_cmap('Reds'), marker=".", s=1)
        fig_hr_3d.colorbar(sc2, ax=ax_hr_3d)
        fig_hr_3d.suptitle('Heart rate distribution')
        ax_hr_3d.set_xlabel('Lattitude')
        ax_hr_3d.set_ylabel('Longitude')
        ax_hr_3d.set_ylim(df.position_lat.min()-0.01, df.position_lat.max()+0.01)
        ax_hr_3d.set_xlim(df.position_long.min()-0.01, df.position_long.max()+0.01)
        
    for a in fig.get_axes():
        a.set_xlabel('')
    plt.setp(ax[-1], xlabel='km')
    plt.setp(ax, xlim=(0, x.max()), xticks=[i if x.max() < 60 else 2*i for i in range(0, x.max().astype('int'), 5)])

    if 'time_in_hr_zone' in sf:
        labels = []
        sizes = []
        colors = ['#ff4c4c', '#ff0000', '#cc0000', '#7f0000', '#4c0000']
        i = 1
        for n in sf.at[0, 'time_in_hr_zone']:
            if n > 0.0:
                labels.append(f'Zone {i}')
                sizes.append(n)
                i += 1
            else: i += 1

        fig2, ax2 = plt.subplots(figsize=(7,7))
        fig2.suptitle('Heart rate zone analysis', fontsize=16)
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=0, pctdistance=0.55, colors=colors, wedgeprops={'linewidth':3, 'edgecolor':'white'})
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig3 = plt.gcf()
        fig3.gca().add_artist(centre_circle)
        ax2.axis('equal') 

def switch(case):
    switcher = {
            'total_ascent': 'Elevation Gain\n[m]',
            'max_altitude': 'Max Elevation\n[m]',
            'avg_speed': 'Avg Speed\n[km/h]',
            'max_speed': 'Max Speed\n[km/h]',
            'total_timer_time': 'Moving Time',
            'total_elapsed_time': 'Elapsed Time',
            'total_distance': 'Distance\n[km]',
            'avg_heart_rate': 'Avg HR\n[bpm]',
            'max_heart_rate': 'Max HR\n[bpm]',
            'total_calories': 'Calories\n[kcal]'
    }
    return switcher.get(case, 'Invalid input')

def create_data_table(df):
    summary = ['total_ascent', 'max_altitude', 'avg_speed', 'max_speed', 'total_timer_time', 'total_elapsed_time', 'total_distance', 'avg_heart_rate', 'max_heart_rate', 'total_calories']
    arr = []
    for item in summary:
        if item in df.columns:
            if item == 'total_timer_time' or item == 'total_elapsed_time':
                df[item] = pd.to_datetime(df[item], unit='s').dt.time 
            df.rename(columns={item: switch(item)}, inplace=True)
            arr.append(switch(item))
    if len(arr) != 0:
        result = df[arr].round(2).rename(index={0: 'Value'})
        result.index.name = 'Property'
        return result.T
    else:
        return pd.DataFrame({'No data': 0})

def render_data_table(data, col_width=3.0, row_height=0.625, font_size=10,
                     header_color='#40466e', row_colors=['w', '#f1f1f2'], edge_color='w',
                     bbox=[0.1, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, rowLabels=data.index, cellLoc='center', bbox=bbox, colLabels=data.columns, **kwargs)
    w, h = mpl_table[0,0].get_width(), mpl_table[0,0].get_height()
    mpl_table.add_cell(0, -1, w,h, text=data.index.name)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors)])
    return ax

def plot_google_map(df, log_file):
    gmap = am.Map()
    try:    
        df.apply(lambda row: gmap.add_point((row['position_lat'], row['position_long'], row['heart_rate'])), axis=1)
        with open('activity_map.html', "w") as out:
            print(gmap, file=out)
        webbrowser.get('open -a Chromium.app %s').open_new_tab('activity_map.html')
        with open(log_file, 'a+') as log:
            log.write('\nCreating Google Maps Heatmap...')
    except Exception as e:
        with open(log_file, 'a+') as log:
            log.write(f'\nCould not create the heatmap. The following error occured: {e}')