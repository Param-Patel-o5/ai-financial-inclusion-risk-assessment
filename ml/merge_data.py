"""
Wrapper script to execute data merge and feature engineering pipeline.
Calls ml.build_features.build_model_table().
"""

from ml.build_features import build_model_table

if __name__ == "__main__":
    build_model_table()
