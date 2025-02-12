import pandas as pd 
import os

feature_name_dict = {'Sidewalk width': 'sidewalk_width',
                    'Pedestrian density': 'pedestrian_density',
                    'Density of street furniture (e.g. garbage, poles)': 'street_furniture_density',
                    'Sidewalk / Surface roughness': 'sidewalk_roughness',
                    'Surface condition': 'surface_condition',
                    'Wireless communication infrastructure (e.g. 5G, IoT, Wi-Fi)': 'communication_infrastructure',
                    'Slope gradient (i.e. elevation change)': 'slope_gradient',
                    'Proximity to charging stations': 'charging_station_proximity',
                    'Local attitudes towards robots': 'local_attitudes',
                    'Curb ramp availability': 'curb_ramp_availability',
                    'Weather conditions': 'weather_conditions',
                    'Crowd dynamics - purpose with which people navigate': 'crowd_dynamics',
                    'Traffic management systems': 'traffic_management',
                    'Surveillance coverage (CCTV)': 'surveillance_coverage',
                    'Zoning laws and regulation': 'zoning_laws',
                    'Bike lane availability': 'bike_lane_availability',
                    'Street lighting': 'street_lighting',
                    'Existence of shade (e.g., trees)': 'shade_availability',
                    'GPS signal strength': 'gps_signal_strength',
                    'Pedestrian flow': 'pedestrian_flow',
                    'Bicycle traffic': 'bicycle_traffic',
                    'Vehicle traffic': 'vehicle_traffic',
                    'Existence of detailed digital maps of the area': 'digital_map_existence',
                    'Intersection safety': 'intersection_safety'}

# Read all CSV files
all_weights = pd.read_csv("weights_forpaper/all_weights.csv", index_col=0)
industry_weights = pd.read_csv("weights_forpaper/industry_weights.csv", index_col=0)
academia_weights = pd.read_csv("weights_forpaper/academia_weights.csv", index_col=0)
other_weights = pd.read_csv("weights_forpaper/other_weights.csv", index_col=0)
trashbot_weights = pd.read_csv("weights_forpaper/trashbot_weights.csv", index_col=0)
nycfig_weights = pd.read_csv("weights_forpaper/feature_weights.csv", index_col=0)

# Reverse the dictionary
feature_name_dict = {v: k for k, v in feature_name_dict.items()}

# Map indices
all_weights.index = all_weights.index.map(feature_name_dict)
industry_weights.index = industry_weights.index.map(feature_name_dict)
academia_weights.index = academia_weights.index.map(feature_name_dict)
other_weights.index = other_weights.index.map(feature_name_dict)
trashbot_weights.index = trashbot_weights.index.map(feature_name_dict)
nycfig_weights.index = nycfig_weights.index.map(feature_name_dict)

# Rename columns
all_weights = all_weights.rename(columns={'Weight': 'All'})
industry_weights = industry_weights.rename(columns={'Weight': 'Industry'})
academia_weights = academia_weights.rename(columns={'Weight': 'Academia'})
other_weights = other_weights.rename(columns={'Weight': 'Other'})
trashbot_weights = trashbot_weights.rename(columns={'Weight': 'Trashbot'})
nycfig_weights = nycfig_weights.rename(columns={'Weight': 'NYC POC'})

# Merge all dataframes
all_weights = all_weights.merge(industry_weights, left_index=True, right_index=True, how='outer')
all_weights = all_weights.merge(academia_weights, left_index=True, right_index=True, how='outer')
all_weights = all_weights.merge(other_weights, left_index=True, right_index=True, how='outer')
all_weights = all_weights.merge(trashbot_weights, left_index=True, right_index=True, how='outer')
all_weights = all_weights.merge(nycfig_weights, left_index=True, right_index=True, how='outer')

# Sort by 'All' column
all_weights = all_weights.sort_values(by='All', ascending=False).reset_index()

# Create a DataFrame to store highlighting information
highlight_df = pd.DataFrame(index=all_weights.index, columns=all_weights.columns, data=False)

# Store original numeric values before formatting
numeric_df = all_weights.copy()

# For each column (except 'index'), find top 3 values
for col in all_weights.columns[1:]:  # Skip the 'index' column
    values = numeric_df[col].fillna(-1)  # Handle NaN values
    top3_idx = values.nlargest(3).index
    highlight_df.loc[top3_idx, col] = True

# Format numbers and add arrows
def format_value_with_highlight(value, is_highlight, col_name=None, all_value=None):
    if pd.isna(value):
        return '-'
    
    formatted = f"{abs(float(value)):.3f}"
    
    # Only add arrows for Academia, Industry, and Other columns
    if col_name in ['Academia', 'Industry', 'Other'] and all_value is not None:
        if abs(float(value) - float(all_value)) < 1e-10:  # Using small epsilon for float comparison
            arrow = "-"
        elif float(value) > float(all_value):
            arrow = r"\textcolor{ForestGreen}{↑}"
        else:
            arrow = r"\textcolor{red}{↓}"
        formatted = f"{arrow} {formatted}"
    
    if is_highlight:
        return f"\\cellcolor{{lightgray}}{formatted}"
    return formatted

# Format all columns
all_weights_formatted = all_weights.copy()
for col in all_weights.columns[1:]:  # Skip the 'index' column
    if col != 'All':
        all_weights_formatted[col] = [
            format_value_with_highlight(val, highlight_df.loc[idx, col], col, numeric_df.loc[idx, 'All'])
            for idx, val in numeric_df[col].items()
        ]
    else:
        all_weights_formatted[col] = [
            format_value_with_highlight(val, highlight_df.loc[idx, col])
            for idx, val in numeric_df[col].items()
        ]

# reorder columns by specified order 
order=['Feature','All', 'Academia', 'Industry', 'Other', 'NYC POC', 'Trashbot']

# prepend index in place 
all_weights_formatted = all_weights_formatted[order]

print(all_weights_formatted)

# Generate LaTeX table
latex_table = all_weights_formatted.to_latex(index=False, escape=False)

# Save to file
os.makedirs('../chi24_roving_whiteboards/tables', exist_ok=True)
with open('../chi24_roving_whiteboards/tables/feature_weights.tex', 'w') as f:
    f.write(latex_table)