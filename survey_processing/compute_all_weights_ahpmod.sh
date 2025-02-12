python calculate_weights_ahp.py --survey_path survey_54.csv --exclude_features [8,10,16,17,19,21,23,14,12] --write_features --out trashbot_weights.csv

python calculate_weights_ahp.py --survey_path survey_54.csv --exclude_features [8,10,16,17,19] --write_features --out feature_weights.csv

python calculate_weights_ahp.py --survey_path survey_academia.csv --write_features --out academia_weights.csv

python calculate_weights_ahp.py --survey_path survey_industry.csv --write_features --out industry_weights.csv

python calculate_weights_ahp.py --survey_path survey_54.csv --write_features --out all_weights.csv