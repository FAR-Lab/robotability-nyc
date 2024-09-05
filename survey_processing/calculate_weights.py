import numpy as np
import pandas as pd
import argparse
import sys
import json
import warnings
import ast

warnings.filterwarnings('ignore')

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
                        'Crowd dynamics - purpose with which people navigate in the space': 'crowd_dynamics',
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

def parse_list(s):
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        raise argparse.ArgumentTypeError("Invalid list format. Please use [x,y,z] format.")

def calculate_weights(survey_path=None, contingency_matrix_path=None, exclude_features=None):
    """
    Calculates weights from the survey path. Optionally can just process the contingency matrix
    """

    indicator_list = ['Sidewalk width','Pedestrian density','Density of street furniture (e.g. garbage, poles)','Sidewalk / Surface roughness',
                      'Surface condition','Wireless communication infrastructure (e.g. 5G, IoT, Wi-Fi)',
                      'Slope gradient (i.e. elevation change)','Proximity to charging stations',
                      'Local attitudes towards robots','Curb ramp availability','Weather conditions',
                      'Crowd dynamics - purpose with which people navigate in the space','Traffic management systems',
                      'Surveillance coverage (CCTV)','Zoning laws and regulation','Bike lane availability','Street lighting',
                      'Existence of shade (e.g., trees)','GPS signal strength','Pedestrian flow','Bicycle traffic','Vehicle traffic',
                      'Existence of detailed digital maps of the area','Intersection safety']

    # Dictionary of indicators
    indicators = {}
    indicators_inv = {}
    for i in range(len(indicator_list)):
        indicators[i] = indicator_list[i]
        indicators_inv[indicator_list[i]] = i

    if survey_path is None:
        if contingency_matrix_path is None:
            print('Please input a path to the survey data or the contingency matrix')
            return

    if contingency_matrix_path is None:
        df = pd.read_csv(survey_path)
        # Remove first 4 columns, and first 2 rows
        df = df.iloc[1:, 4:]
        # Remove unnecessary columns
        df = df.drop(['RecordedDate', 'ResponseId', 'RecipientLastName', 'RecipientFirstName', 'RecipientEmail',
                      'ExternalReference', 'LocationLatitude', 'LocationLongitude', 'DistributionChannel', 'UserLanguage',
                      'Q_RecaptchaScore', 'Instruction'], axis=1)

        new_cols = []
        for col in df.columns:
            # Remove empty spaces
            col = col.strip()
            new_cols.append(col)

        df.columns = new_cols
        df = df.iloc[1:, :]

        # Remove samples where "Q5" is nan
        print('Shape with non-valid answers:')
        print(df.shape)
        df = df.dropna(subset=['Q5'])
        print('Post exclusion of nan in Q5', df.shape)

        # Get correspondence dictionary
        with open('correspondence.json') as f:
            correspondence = json.load(f)

        # Save existing columns in a new DataFrame, track non-corresponding columns
        new_df = pd.DataFrame(np.nan, index=range(len(df)), columns=[])
        no_correspondence = []
        not_indicator = []
        count = 0
        for key in correspondence.keys():
            if str(key) in df.columns:
                new_df[key] = pd.concat([df[str(key)]], axis=1)
                count += 1
            else:
                if correspondence[key][0] not in indicators.values() or correspondence[key][1] not in indicators.values():
                    if correspondence[key][0] not in indicators.values():
                        not_indicator.append(correspondence[key][0])
                    elif correspondence[key][1] not in indicators.values():
                        not_indicator.append(correspondence[key][1])
                else:
                    no_correspondence.append(correspondence[key])
                    new_df[key] = np.nan

        print('total number of combinations: ', count)
        print('total number of combinations without answers: ', len(no_correspondence))
        if len(no_correspondence) > 0:
            print('combinations: ')
            print(no_correspondence)

        # Create contingency table
        contingency_table = np.zeros((len(indicators), len(indicators)))
        contingency_table = pd.DataFrame(contingency_table)
        contingency_table.columns = indicators.values()
        contingency_table.index = indicators.values()

        for i in range(len(new_df.columns)):
            ind1 = correspondence[new_df.columns[i]][0]
            ind2 = correspondence[new_df.columns[i]][1]
            count = new_df[new_df.columns[i]].count()
            value_counts = new_df[new_df.columns[i]].value_counts()
            for value in value_counts.index:
                count_value = value_counts[value]
                value = value.rstrip()
                if value == ind1:
                    contingency_table.loc[ind1, ind2] = count_value / count
                elif value == ind2:
                    contingency_table.loc[ind2, ind1] = count_value / count
                else:
                    print('UH OH')
                    print(value_counts)

        for i in range(len(indicators)):
            for j in range(len(indicators)):
                if i == j:
                    if contingency_table.iloc[i, j] == 1:
                        print(indicators[i], indicators[j])
                    else:
                        contingency_table.iloc[i, j] = 1
    else:
        # Load the contingency matrix
        contingency_table = pd.read_csv(contingency_matrix_path, index_col=0)

    # Make contingency columns and indexes correspond to numbers
    cols = contingency_table.columns
    new_cols = [indicators_inv[col] for col in cols]
    contingency_table.columns = cols
    contingency_table.index = cols

    if exclude_features is not None:
        exclude_indices = list(exclude_features)
        print(f"Excluding features: {list(map(lambda x: indicator_list[x], exclude_indices))}")
        include_indices = [i for i in range(len(indicator_list)) if i not in exclude_indices]

        # Reduce the matrix to the features not excluded
        contingency_table = contingency_table.iloc[include_indices, include_indices]

    # Convert to numpy array for eigenvalue calculation
    matrix_array = contingency_table.to_numpy()

    # Calculate the principal eigenvector
    eigvals, eigvecs = np.linalg.eig(contingency_table)
    max_eigval_index = np.argmax(eigvals)
    print("Max eigenvalue:", eigvals[max_eigval_index])
    weights = eigvecs[:, max_eigval_index]
    weights = np.real(weights)  # In case of complex numbers
    weights = weights / np.sum(weights)  # Normalize weights

    print("Weights:", weights)



    # Create a dictionary mapping feature names to weights
    # feature names should not include features that are excluded
    # use include_indices to map the weights to the correct feature names
    feature_names = [indicator_list[i] for i in include_indices]
    feature_names = [feature_name_dict[feature] for feature in feature_names]
    weight_dict = dict(zip(feature_names, weights))

    return weight_dict

def main():
    """
    Feature index dictionary

    {0: 'Sidewalk width',
     1: 'Pedestrian density',
     2: 'Density of street furniture (e.g. garbage, poles)',
     3: 'Sidewalk / Surface roughness',
     4: 'Surface condition',
     5: 'Wireless communication infrastructure (e.g. 5G, IoT, Wi-Fi)',
     6: 'Slope gradient (i.e. elevation change)',
     7: 'Proximity to charging stations',
     8: 'Local attitudes towards robots',
     9: 'Curb ramp availability',
    10: 'Weather conditions',
    11: 'Crowd dynamics - purpose with which people navigate in the space',
    12: 'Traffic management systems',
    13: 'Surveillance coverage (CCTV)',
    14: 'Zoning laws and regulation',
    15: 'Bike lane availability',
    16: 'Street lighting',
    17: 'Existence of shade (e.g., trees)',
    18: 'GPS signal strength',
    19: 'Pedestrian flow',
    20: 'Bicycle traffic',
    21: 'Vehicle traffic',
    22: 'Existence of detailed digital maps of the area',
    23: 'Intersection safety'}
    """

    parser = argparse.ArgumentParser(description="Calculate weights from the survey data, excluding specified features.")
    parser.add_argument("--survey_path", help="Path to the CSV file containing the survey answers")
    parser.add_argument("--contingency_matrix_path", help="Path to the CSV file containing the contingency matrix")
    parser.add_argument("--exclude_features", type=parse_list, help="List of feature numbers to exclude")
    parser.add_argument("--write_features", help="if set, will write the features to a file, feature_weights.csv", action='store_true')
    parser.add_argument("--out", help="Path to the output file", default="feature_weights.csv")

    args = parser.parse_args()

    try:
        result = calculate_weights(args.survey_path, args.contingency_matrix_path, args.exclude_features)
        print("Calculated weights:")
        for feature, weight in result.items():
            print(f"{feature}: {weight}")


        if args.write_features:
            features_df = pd.DataFrame(result.items(), columns=['Feature', 'Weight'])
            features_df.to_csv(args.out, index=False)
    except FileNotFoundError:
        print(f"Error: The file was not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()