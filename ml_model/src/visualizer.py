"""Simple visualizer stubs for lifetime predictions."""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_health_dashboard(predictions: list, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tags = [p['part_name'] for p in predictions]
    values = [p['health_score'] for p in predictions]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(tags, values, color='tab:blue')
    ax.set_ylim(0, 100)
    ax.set_ylabel('Health %')
    ax.set_title('Component health dashboard')
    plt.xticks(rotation=45, ha='right')
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_sensor_trends(df: pd.DataFrame, part_name: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    part_df = df[df['part_name'] == part_name]
    if part_df.empty:
        return
    if 'hour' in part_df.columns and 'vibration' in part_df.columns:
        ax.plot(part_df['hour'], part_df['vibration'], label='vibration')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Vibration')
        ax.set_title(f'Sensor trend for {part_name}')
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_rul_prediction(df: pd.DataFrame, part_name: str, predicted_ruls: list, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not predicted_ruls:
        with open(output_path, 'w') as f:
            f.write('No RUL predictions available')
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(predicted_ruls)
    ax.set_title(f'RUL Prediction Timeline - {part_name}')
    ax.set_ylabel('RUL hours')
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def generate_maintenance_report(predictions: list, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('Maintenance Report\n')
        f.write('===================\n')
        for p in predictions:
            f.write(f"{p['part_name']}: {p['alert_level']} - {p['recommendation']}\n")
