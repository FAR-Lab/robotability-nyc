import numpy as np
import pandas as pd
import argparse
import sys
import json

#eliminate warnings
import warnings
warnings.filterwarnings('ignore')

import ast

def parse_list(s):
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        raise argparse.ArgumentTypeError("Invalid list format. Please use [x,y,z] format.")

def calculate_weights(survey_path = None, contingency_matrix_path = None, exclude_features=None):

    """
    Calculates weights from the survey path. Optionally can just process the contigency matrix
    
    """


    indicator_list = ['Sidewalk width','Pedestrian density','Density of street furniture (e.g. garbage, poles)','Sidewalk / Surface roughness',
                'Surface condition','Wireless communication infrastructure (e.g. 5G, IoT, Wi-Fi)',
                'Slope gradient (i.e. elevation change)','Proximity to charging stations',
                'Local attitudes towards robots','Curb ramp availability','Weather conditions',
                'Crowd dynamics - purpose with which people navigate in the space','Traffic management systems',
                'Surveillance coverage (CCTV)','Zoning laws and regulation','Bike lane availability','Street lighting',
                'Existence of shade (e.g., trees)','GPS signal strength','Pedestrian flow','Bicycle traffic','Vehicle traffic',
                'Existence of detailed digital maps of the area','Intersection safety']

    #dictionary of indicators
    indicators = {}
    indicators_inv = {}
    for i in range(len(indicator_list)):
        indicators[i] = indicator_list[i]
        indicators_inv[indicator_list[i]] = i

    if survey_path == None:
        if contingency_matrix_path == None:
            print('Please input a path to the survey data or the contingency matrix')
            return

    if contingency_matrix_path == None:
        df = pd.read_csv(survey_path)
        #remove first 4 columns, and first 2 rows
        df = df.iloc[1:,4:]
        #remove RecordedDate,ResponseId,RecipientLastName,RecipientFirstName,RecipientEmail, ExternalReference	LocationLatitude	LocationLongitude	DistributionChannel	UserLanguage	Q_RecaptchaScore	Instruction	
        df = df.drop(['RecordedDate','ResponseId','RecipientLastName','RecipientFirstName','RecipientEmail','ExternalReference','LocationLatitude','LocationLongitude','DistributionChannel','UserLanguage','Q_RecaptchaScore','Instruction'],axis=1)

        new_cols = []
        for col in df.columns:
            #remove empty spaces
            col = col.strip()
            new_cols.append(col)

        df.columns = new_cols

        df = df.iloc[1:,:]

        #remove samples where "Q5" is nan
        print('Shape with non-valid answers:')
        print(df.shape)
        df = df.dropna(subset=['Q5'])
        print('Post exclusion of nan in Q5',df.shape)

        #get correspondence dictionary
        f = open('correspondence.json') 

        # returns JSON object as a dictionary 
        correspondence = json.load(f) 
        #correspondence = json.loads('./correspondence.json'



        #now, go through the correspondence dictionary and look at the columns of the df. save in a new df only the columns that exist, and save the columns with no correspondence in a list
        new_df = pd.DataFrame(np.nan, index=range(len(df)), columns=[])
        no_correspondence = []
        not_indicator = []
        count = 0
        #go through keys
        for key in correspondence.keys():
            #if the key is in the columns of the df
            
            if str(key) in df.columns:
                #add the column to the new df
                new_df[key] = pd.concat([df[str(key)]],axis=1)
                count = count + 1
            #if the key is not in the columns of the df
            else:
                #add the key to the list of no correspondence        
                if correspondence[key][0] not in indicators.values() or correspondence[key][1] not in indicators.values():
                    #print(correspondence[key], 'NOT IN INDICATORS')
                    if correspondence[key][0]  not in indicators.values():
                        not_indicator.append(correspondence[key][0])
                    elif correspondence[key][1]  not in indicators.values():
                        not_indicator.append(correspondence[key][1])
                else:
                    no_correspondence.append(correspondence[key])
                    #add empty column to new df
                    new_df[key] = np.nan
                #print(key)

        print('total number of combinations: ', count)
        print('total number of combinations without answers: ', len(no_correspondence))
        if len(no_correspondence)>0:
            print('combinations: ')
            print(no_correspondence)

        #now, get contingency table for each column: 
        #each column, get the 2 indicators it represents through correspondence dictionary
        #then, count answers for that column, and for each answer, count how many times each indicator appears
        #fill out the corresponding cell in the contingency table

        contingency_table = np.zeros((len(indicators),len(indicators)))
        contingency_table = pd.DataFrame(contingency_table)
        #columns and rows are indicators
        contingency_table.columns = indicators.values()
        contingency_table.index = indicators.values()
        #print(contingency_table.shape)


        for i in range(len(new_df.columns)):
            #get the 2 indicators
            ind1 = correspondence[new_df.columns[i]][0]
            ind2 = correspondence[new_df.columns[i]][1]
            #print(ind1,ind2)
            #count answers for that column
            count = new_df[new_df.columns[i]].count()
            #print(count)
            value_counts = new_df[new_df.columns[i]].value_counts()
            #print(value_counts)
            for value in value_counts.index:
                #eliminate empty space at end of string for value
                count_value = value_counts[value]   
                value = value.rstrip()
                #print(count_value,count)
                if value == ind1:
                    contingency_table.loc[ind1,ind2] = (count_value/count) * 10
                elif value == ind2:
                    contingency_table.loc[ind2,ind1] = (count_value/count) * 10
                else:
                    print('UH OH')
                    print(value_counts)

        for i in range(len(indicators)):
            for j in range(len(indicators)):
                if i == j:
                    if contingency_table.iloc[i,j] == 1:
                        print(indicators[i],indicators[j])
                    else:
                        contingency_table.iloc[i,j] = 1
        
        #now, for the lower matrix, fill out the values by being Mji = 1/Mij, but only lower triangle
        for i in range(len(indicators)):
            for j in range(len(indicators)):
                if i > j:
                    if contingency_table.iloc[i,j] == 0:
                        contingency_table.iloc[i,j] = 1/contingency_table.iloc[j,i]
                    elif contingency_table.iloc[j,i] == 0:
                        contingency_table.iloc[j,i] = 1/contingency_table.iloc[i,j]
                    else:
                        contingency_table.iloc[i,j] = 1/contingency_table.iloc[j,i]
        

        #print(contingency_table)  
        # Save the contingency matrix
        contingency_table.to_csv('contingency_matrix_ahp.csv') 

    else:
        # Load the contingency matrix
        contingency_table = pd.read_csv(contingency_matrix_path, index_col=0)
        

    #make contingency columns and indexes correspond to numbers

    cols = contingency_table.columns
    new_cols = [indicators_inv[col] for col in cols]
    contingency_table.columns = cols
    contingency_table.index = cols


    if exclude_features != None:
        feature_numbers = list(range(24))
        for feature in exclude_features:
            feature_numbers.remove(feature)
        print('TEST', feature_numbers)

        # Reduce the matrix to the specified features
        contingency_table = contingency_table.iloc[feature_numbers, feature_numbers]
    
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

    #now, calculate consistency index
    n = len(weights)
    lambda_max = eigvals[max_eigval_index]
    consistency_index = (lambda_max - n) / (n - 1)
    print("Consistency index:", consistency_index)
    

    feature_name_dict = {'Sidewalk width': 'sidewalk_width',
    'Pedestrian density':'pedestrian_density',
    'Density of street furniture (e.g. garbage, poles)':'street_furniture_density',
    'Sidewalk / Surface roughness':'sidewalk_roughness',
    'Surface condition':'surface_condition',
    'Wireless communication infrastructure (e.g. 5G, IoT, Wi-Fi)':'communication_infrastructure',
    'Slope gradient (i.e. elevation change)':'slope_gradient',
    'Proximity to charging stations':'charging_station_proximity',
    'Local attitudes towards robots':'local_attitudes',
    'Curb ramp availability':'curb_ramp_availability',
    'Weather conditions':'weather_conditions',
    'Crowd dynamics - purpose with which people navigate in the space':'crowd_dynamics',
    'Traffic management systems':'traffic_management',
    'Surveillance coverage (CCTV)':'surveillance_coverage',
    'Zoning laws and regulation':'zoning_laws',
    'Bike lane availability':'bike_lane_availability',
    'Street lighting':'street_lighting',
    'Existence of shade (e.g., trees)':'shade_availability',
    'GPS signal strength':'gps_signal_strength',
    'Pedestrian flow':'pedestrian_flow',
    'Bicycle traffic':'bicycle_traffic',
    'Vehicle traffic':'vehicle_traffic',
    'Existence of detailed digital maps of the area':'digital_map_existence',
    'Intersection safety':'intersection_safety'}

    
    # Create a dictionary mapping feature names to weights
    feature_names = feature_name_dict.values()
    weight_dict = dict(zip(feature_names, weights))

    #sort the dictionary
    weight_dict = dict(sorted(weight_dict.items(), key=lambda item: item[1], reverse=True))
    
    #print(weight_dict)

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

    
    parser = argparse.ArgumentParser(description="Calculate weights from the survey data for specified features.")
    parser.add_argument("--survey_path", help="Path to the CSV file containing the survey answers")
    parser.add_argument("--contingency_matrix_path", help="Path to the CSV file containing the contigency matrix")
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