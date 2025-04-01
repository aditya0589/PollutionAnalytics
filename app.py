from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)

# Load Dataset
DATASET_PATH = os.path.join('Notebooks', 'data', 'carbon_footprint_india.csv')

if os.path.exists(DATASET_PATH):
    df = pd.read_csv(DATASET_PATH)

    # Ensure only numeric columns are converted
    df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '')  # Normalize column names
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print(f"Dataset Loaded: {df.shape}")
else:
    df = None
    print("Dataset not found!")

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Analytics Page
@app.route('/analytics', methods=['GET'])
def analytics():
    if df is None or df.empty:
        return render_template('analytics.html', error="Dataset is empty or not found.")
    
    columns = df.columns.tolist() if df is not None else []
    return render_template('analytics.html', columns=columns)

# Plot Generation Route
@app.route('/plot', methods=['POST'])
def plot():
    if df is None or df.empty:
        return render_template('analytics.html', error="Dataset is empty or not found.")

    x_axis = request.form.get('x_axis')
    y_axis = request.form.get('y_axis')
    plot_type = request.form.get('plot_type')

    print(f"DEBUG: Received X-axis = {x_axis}, Y-axis = {y_axis}, Plot Type = {plot_type}")

    # Normalize column names to avoid special character issues
    df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    x_axis = x_axis.replace(' ', '_').replace('(', '').replace(')', '')
    y_axis = y_axis.replace(' ', '_').replace('(', '').replace(')', '')

    # Validate input
    if not x_axis or not y_axis or not plot_type:
        return render_template('analytics.html', error="Please select valid X, Y, and plot type.")

    if x_axis not in df.columns or y_axis not in df.columns:
        return render_template('analytics.html', error="Selected columns not found in dataset.")

    # Ensure selected columns are numeric
    df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')

    # Generate plot
    try:
        plot_functions = {
            'scatter': px.scatter,
            'line': px.line,
            'bar': px.bar,
            'histogram': px.histogram
        }

        if plot_type in plot_functions:
            fig = plot_functions[plot_type](df, x=x_axis, y=y_axis, title=f"{plot_type.capitalize()} Plot")
            graph_html = fig.to_html(full_html=False)
            print(f"DEBUG: Plot generated successfully for {plot_type} with {x_axis} vs {y_axis}")
            return render_template('analytics.html', columns=df.columns.tolist(), graph_html=graph_html)
        else:
            return render_template('analytics.html', error="Invalid plot type selected.")

    except Exception as e:
        print(f"Error generating plot: {str(e)}")
        return render_template('analytics.html', error=f"Error generating plot: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
