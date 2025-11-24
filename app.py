from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import os

app = Flask(__name__)

# Global variables for model and data
MODEL = None
DATA_DF = None

# Load and prepare the model
def load_and_train_model():
    """Load data and train the Random Forest model"""
    global MODEL, DATA_DF
    
    csv_path = os.path.join(os.path.dirname(__file__), "Dataset", "Video Game Sale.csv")
    
    if not os.path.exists(csv_path):
        return None, None
    
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["Global_Sales"])
    df = df.dropna()
    
    # Feature selection - USE ONLY CATEGORICAL AND YEAR (not regional sales)
    X = df[[
        "Platform",
        "Year",
        "Genre",
        "Publisher",
    ]]
    y = df["Global_Sales"]
    
    categorical = ["Platform", "Genre", "Publisher"]
    numerical = ["Year"]
    
    # Create preprocessing pipeline
    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", "passthrough", numerical),
    ])
    
    # Create model pipeline
    model = Pipeline([
        ("prep", preprocessor),
        ("model", RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)),
    ])
    
    model.fit(X, y)
    
    MODEL = model
    DATA_DF = df
    return model, df

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/train-model', methods=['POST'])
def train_model():
    """Train the model on demand"""
    try:
        model, df = load_and_train_model()
        if model is None:
            return jsonify({"success": False, "error": "Dataset not found"}), 500
        
        return jsonify({
            "success": True,
            "message": "✅ Model trained successfully!"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/get-years')
def get_years():
    """Get available years from the dataset - including future years for predictions"""
    if DATA_DF is None:
        return jsonify({"error": "Model not trained. Please click 'Train Model' first"}), 400
    
    # Get years from dataset
    dataset_years = sorted(DATA_DF["Year"].unique().tolist())
    min_year = min(dataset_years)
    max_year = max(dataset_years)
    
    # Generate years from dataset range plus future years (up to 20 years ahead)
    all_years = list(range(min_year, max_year + 21))  # Historical data + 20 years future
    
    return jsonify({"years": all_years})

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict top games for a given year"""
    if MODEL is None or DATA_DF is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.json
        year_input = int(data.get('year'))
        max_games = int(data.get('max_games', 6))
        
        # Always show top 6
        top_n_display = 6
        
        # Get all unique platform, genre, publisher combinations
        combinations = DATA_DF[["Platform", "Genre", "Publisher"]].drop_duplicates().copy()
        
        # For each combination, make prediction using ONLY Platform, Genre, Publisher, Year
        results = []
        for idx, combo in combinations.iterrows():
            # Find similar games in dataset to get regional breakdown patterns
            mask = (
                (DATA_DF["Platform"] == combo["Platform"]) &
                (DATA_DF["Genre"] == combo["Genre"]) &
                (DATA_DF["Publisher"] == combo["Publisher"])
            )
            similar_games = DATA_DF[mask]
            
            if len(similar_games) > 0:
                # Use historical average for regional breakdown
                na_avg = similar_games["NA_Sales"].mean()
                eu_avg = similar_games["EU_Sales"].mean()
                jp_avg = similar_games["JP_Sales"].mean()
                other_avg = similar_games["Other_Sales"].mean()
            else:
                # Use global averages
                na_avg = DATA_DF["NA_Sales"].mean()
                eu_avg = DATA_DF["EU_Sales"].mean()
                jp_avg = DATA_DF["JP_Sales"].mean()
                other_avg = DATA_DF["Other_Sales"].mean()
            
            # Prepare features for prediction (ONLY categorical + year)
            X_pred = pd.DataFrame({
                "Platform": [combo["Platform"]],
                "Year": [year_input],
                "Genre": [combo["Genre"]],
                "Publisher": [combo["Publisher"]],
            })
            
            # Make prediction
            predicted_global = MODEL.predict(X_pred)[0]
            
            # Calculate growth factor based on year difference
            current_avg_year = DATA_DF["Year"].mean()
            year_diff = year_input - current_avg_year
            
            # Apply modest growth (2% per year for future predictions)
            if year_diff > 0:
                growth_factor = 1 + (0.02 * year_diff)
                predicted_global = predicted_global * growth_factor
            
            # Calculate regional sales based on predicted global
            total_regional = na_avg + eu_avg + jp_avg + other_avg
            if total_regional > 0:
                na_sales = predicted_global * (na_avg / total_regional)
                eu_sales = predicted_global * (eu_avg / total_regional)
                jp_sales = predicted_global * (jp_avg / total_regional)
                other_sales = predicted_global * (other_avg / total_regional)
            else:
                na_sales = predicted_global * 0.45
                eu_sales = predicted_global * 0.25
                jp_sales = predicted_global * 0.20
                other_sales = predicted_global * 0.10
            
            results.append({
                "combination": combo,
                "na_sales": na_sales,
                "eu_sales": eu_sales,
                "jp_sales": jp_sales,
                "other_sales": other_sales,
                "predicted_global": predicted_global,
            })
        
        # Convert to dataframe and sort
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values("predicted_global", ascending=False).reset_index(drop=True)
        top_games_df = results_df.head(top_n_display)
        
        # Prepare response
        games_list = []
        for idx, row in top_games_df.iterrows():
            combo = row["combination"]
            # Generate descriptive game name
            game_name = f"{combo['Genre']} - {combo['Platform']}"
            
            games_list.append({
                "rank": idx + 1,
                "name": game_name,
                "platform": str(combo["Platform"]),
                "genre": str(combo["Genre"]),
                "publisher": str(combo["Publisher"]),
                "predicted_sales": round(float(row["predicted_global"]), 2),
                "na_sales": round(float(row["na_sales"]), 2),
                "eu_sales": round(float(row["eu_sales"]), 2),
                "jp_sales": round(float(row["jp_sales"]), 2),
                "other_sales": round(float(row["other_sales"]), 2),
            })
        
        return jsonify({
            "success": True,
            "year": year_input,
            "requested_stock": max_games,
            "games": games_list,
            "all_predictions": [],
            "total_games": len(results_df),
            "message": f"Top 6 recommended games out of {max_games} stocks requested"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
