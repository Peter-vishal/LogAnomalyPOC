import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load and process data
def load_data():
    df_metrics = pd.read_csv("App_DB_Metrics.csv")
    df_logs = pd.read_csv("Database_Logs.csv")
    
    # Ensure timestamps are parsed correctly
    df_metrics.rename(columns={'timestamp': 'Timestamp'}, inplace=True)
    df_metrics["Timestamp"] = pd.to_datetime(df_metrics["Timestamp"], errors='coerce')
    df_logs["Timestamp"] = pd.to_datetime(df_logs["Timestamp"], errors='coerce')
    
    return df_metrics, df_logs

def detect_anomalies(df, column):
    # Simple anomaly detection using z-score
    df['Z-Score'] = (df[column] - df[column].mean()) / df[column].std()
    df['Anomaly'] = df['Z-Score'].apply(lambda x: abs(x) > 2.5)  # Mark anomalies
    return df

def correlate_logs_with_anomalies(df_metrics, df_logs, column):
    anomalies = df_metrics[df_metrics['Anomaly']]
    correlated_logs = df_logs[df_logs['Timestamp'].isin(anomalies['Timestamp'])]
    return correlated_logs

def generate_rca_and_recommendations(anomalies, correlated_logs):
    root_causes = []
    recommendations = []
    
    if not anomalies.empty:
        root_causes.append("Sudden spikes/drops in metrics detected.")
        if not correlated_logs.empty:
            root_causes.append("Unexpected system behavior logged during anomalies.")
            recommendations.append("Investigate logs for root cause analysis.")
        else:
            recommendations.append("Monitor system performance and logs more closely.")
    
    return root_causes, recommendations

# Streamlit UI
st.title("🔍 Log Anomaly Detection POC")
df_metrics, df_logs = load_data()

# Display data previews
st.subheader("📊 Sample Metrics Data Preview")
st.dataframe(df_metrics.head())

st.subheader("📜 Sample Logs Data Preview")
st.dataframe(df_logs.head())

# Anomaly detection
metric_column = st.selectbox("Select a metric for anomaly detection:", df_metrics.columns[1:])
df_metrics = detect_anomalies(df_metrics, metric_column)

# Plot anomalies
fig, ax = plt.subplots()
anomalies = df_metrics[df_metrics['Anomaly']]
ax.scatter(df_metrics.index, df_metrics[metric_column], label='Normal', color='blue')
ax.scatter(anomalies.index, anomalies[metric_column], label='Anomaly', color='red')
ax.set_title("Anomalies in Metrics")
ax.set_xlabel("Index")
ax.set_ylabel(metric_column)
ax.legend()
st.pyplot(fig)

# Correlate logs with anomalies
correlated_logs = correlate_logs_with_anomalies(df_metrics, df_logs, metric_column)

# RCA and recommendations
root_causes, recommendations = generate_rca_and_recommendations(anomalies, correlated_logs)

st.subheader("📌 Root Cause Analysis & Recommendations")
st.markdown(f"⚠ Detected {len(anomalies)} anomalies in {metric_column}.")

st.write("**Possible Root Causes:**")
for cause in root_causes:
    st.write(f"- {cause}")

st.write("**Recommendations:**")
for rec in recommendations:
    st.write(f"✅ {rec}")