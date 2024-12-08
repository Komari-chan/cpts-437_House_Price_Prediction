import os
import re
import numpy as np

def process_metrics(directory):
    # Initialize storage for metrics
    metrics = {
        "GBM": {"RMSE": [], "R2": [], "MAE": []},
        "XGBoost": {"RMSE": [], "R2": [], "MAE": []},
        "Random Forest": {"RMSE": [], "R2": [], "MAE": []},
    }
    
    # Updated pattern for extracting metrics
    metric_pattern = re.compile(r"([A-Za-z\s]+)\sMetrics:\n\s+RMSE:\s([\d.]+)\n\s+R2:\s([\d.]+)\n\s+MAE:\s([\d.]+)")
    
    # Process all txt files in the directory
    for filename in os.listdir(directory):
        if filename.startswith("results_seed_") and filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r") as file:
                content = file.read()
                matches = metric_pattern.findall(content)
                for model, rmse, r2, mae in matches:
                    model = model.strip()  # Remove extra spaces
                    if model in metrics:  # Ensure the model is valid
                        metrics[model]["RMSE"].append(float(rmse))
                        metrics[model]["R2"].append(float(r2))
                        metrics[model]["MAE"].append(float(mae))
    
    # Compute statistics
    results = {}
    for model, model_metrics in metrics.items():
        results[model] = {}
        for metric, values in model_metrics.items():
            if values:  # Avoid processing empty lists
                results[model][metric] = {
                    "Range": (min(values), max(values)),
                    "Average": np.mean(values),
                    "Median": np.median(values),
                }
    
    return results

# Example usage:
directory_path = "./"  # Replace with the path to your directory containing txt files
statistics = process_metrics(directory_path)

# Print results
for model, model_stats in statistics.items():
    print(f"{model} Metrics:")
    for metric, stats in model_stats.items():
        print(f"  {metric}:")
        print(f"    Range: {stats['Range']}")
        print(f"    Average: {stats['Average']:.2f}")
        print(f"    Median: {stats['Median']:.2f}")
    print()
