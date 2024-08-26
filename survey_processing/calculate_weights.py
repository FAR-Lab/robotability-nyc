import numpy as np
import pandas as pd
import argparse
import sys
import json
import warnings
import ast

warnings.filterwarnings('ignore')

def parse_list(s):
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        raise argparse.ArgumentTypeError("Invalid list format. Please use [x,y,z] format.")

def calculate_weights(survey_path=None, contingency_matrix_path=None, exclude_features=None):
    """
    Calculates weights from the survey path. Optionally can just process the contingency matrix.
    """

    indicator_list = ['Sidewalk width','Pedestrian density','Density of street furniture (e.g. garbage, poles)',
                      'Sidewalk / Surface roughness', 'Surface condition',
                      'Wireless communication infrastructure (e.g. 5G, IoT, Wi-Fi)', 'Slope gradient (i.e. elevation change)',
                      'Proximity to charging stations', 'Local attitudes towards robots', 'Curb ramp availability',
                      'Weather conditions', 'Crowd dynamics - purpose with which people navigate in the space',
                      'Traffic management systems', 'Surveillance coverage (CCTV)', 'Zoning laws and regulation',
                      'Bike lane availability', 'Street lighting', 'Existence of shade (e.g., trees)', 'GPS signal strength',
                      'Pedestrian flow', 'Bicycle traffic', 'Vehicle traffic', 'Existence of detailed digital maps of the area',
                      'Intersection safety']

    indicators = {i: indicator_list[i] for i in range(len(indicator_list))}
    indicators_inv = {indicator_list[i]: i for i in range(len(indicator_list))}

    if survey_path is None and contingency_matrix_path is None:
        print('Please input a path to the survey data or the contingency matrix')
        return

    if contingency_matrix_path is None:
        # Existing code for handling survey data...
        # [Rest of your original code here]

        contingency_table = # Build your contingency table as per original logic...

    else:
        # Load the contingency matrix
        contingency_table = pd.read_csv(contingency_matrix_path, index_col=0)

    # Make contingency columns and indexes correspond to numbers
    contingency_table.columns = [indicators_inv[col] for col in contingency_table.columns]
    contingency_table.index = contingency_table.columns

    if exclude_features:
        exclude_indices = list(exclude_features)
        include_indices = [i for i in range(len(indicator_list)) if i not in exclude_indices]
        
        # Reduce the matrix to the features not excluded
        contingency_table = contingency_table.iloc[include_indices, include_indices]

    # Convert to numpy array for eigenvalue calculation
    matrix_array = contingency_table.to_numpy()
    
    # Calculate the principal eigenvector
    eigvals, eigvecs = np.linalg.eig(matrix_array)
    max_eigval_index = np.argmax(eigvals)
    weights = eigvecs[:, max_eigval_index]
    weights = np.real(weights)  # In case of complex numbers
    weights = weights / np.sum(weights)  # Normalize weights

    feature_name_dict = {'Sidewalk width': 'sidewalk_width',
                         'Pedestrian density': 'pedestrian_density',
                         # [Add all other features here]
                        }

    feature_names = [feature_name_dict[indicator_list[i]] for i in include_indices]
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

    args = parser.parse_args()

    try:
        result = calculate_weights(args.survey_path, args.contingency_matrix_path, args.exclude_features)
        print("Calculated weights:")
        for feature, weight in result.items():
            print(f"{feature}: {weight}")
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