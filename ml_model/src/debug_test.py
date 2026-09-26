"""
MAIN PIPELINE - Ship Part Lifetime Prediction System (NO ENCODING FIX VERSION)
=====================================================
Run this file to:
  1. Load existing sensor data from CSV
  2. Train models for all 6 ship parts
  3. Run predictions
  4. Generate visual dashboard + maintenance report
"""
 
import os
import sys
import logging
import traceback
import numpy as np
import pandas as pd
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
 
sys.path.insert(0, os.path.dirname(__file__))
 
# Track module availability
MODEL_AVAILABLE = False
VISUALIZER_AVAILABLE = False
 
try:
    from model import ShipPartLifetimePredictor
    MODEL_AVAILABLE = True
except ImportError:
    log.warning("Model module not available")
 
try:
    from visualizer import (
        plot_health_dashboard,
        plot_sensor_trends,
        plot_rul_prediction,
        generate_maintenance_report,
    )
    VISUALIZER_AVAILABLE = True
except ImportError:
    log.warning("Visualizer module not available")
 
# Configuration
PART_LIFETIME_DEFAULTS = {
    "Main Engine Bearing": 12000,
    "Turbocharger": 10000,
    "Fuel Pump": 9000,
    "Gearbox": 11000,
    "Cooling System": 9500,
    "Exhaust Valve": 8000,
}
 
for folder in ("models", "outputs"):
    os.makedirs(folder, exist_ok=True)
 
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sensor_data.csv')
FALLBACK_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'new_maritime_dataset.csv')
SIMULATION_HOUR = 1500
REQUIRED_SENSOR_COLS = [
    'vibration', 'oil_pressure', 'exhaust_temp',
    'coolant_temp', 'rpm', 'oil_quality',
]
 
 
def step1_load_data(path: str = DATA_PATH):
    """Load and validate sensor data."""
    log.info("STEP 1: Loading sensor data...")
 
    if not os.path.exists(path):
        log.warning("Data file not found: '%s'" % path)
        if os.path.exists(FALLBACK_DATA_PATH):
            log.warning("Using fallback dataset: '%s'" % FALLBACK_DATA_PATH)
            path = FALLBACK_DATA_PATH
        else:
            log.error("Please provide sensor data CSV")
            return None
 
    try:
        df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
    except Exception:
        try:
            df = pd.read_csv(path, encoding='latin-1', on_bad_lines='skip')
            log.info("Loaded with latin-1 encoding")
        except Exception as e:
            log.error("Failed to read CSV: %s" % str(e))
            return None
 
    log.info("Dataset columns: %s" % str(list(df.columns)))
    log.info("Dataset shape: %s" % str(df.shape))
 
    # Handle part_name column
    if 'part_name' not in df.columns:
        if 'ship_type' in df.columns:
            df['part_name'] = df['ship_type'].astype(str)
            log.warning("Using ship_type as part_name")
        else:
            df['part_name'] = 'default_part'
 
    # Handle hour column
    if 'hour' not in df.columns:
        if 'voyage_hours' in df.columns:
            df['hour'] = pd.to_numeric(df['voyage_hours'], errors='coerce')
            log.warning("Using voyage_hours as hour")
        else:
            df['hour'] = np.arange(len(df))
 
    # Handle NaN in hour column
    if df['hour'].isna().any():
        log.warning("Filling NaN values in hour column")
        df['hour'] = df['hour'].fillna(method='ffill').fillna(method='bfill').fillna(0)
 
    # Generate synthetic sensor data
    missing_sensors = [c for c in REQUIRED_SENSOR_COLS if c not in df.columns]
    if missing_sensors:
        log.warning("Missing sensor columns: %s" % str(missing_sensors))
        log.info("Generating synthetic sensor data...")
        
        if 'rpm' in df.columns:
            rpm = pd.to_numeric(df['rpm'], errors='coerce').fillna(100)
        else:
            rpm = pd.Series(np.random.uniform(80, 130, len(df)))
        
        rpm = np.clip(rpm, 50, 150)
        np.random.seed(42)
        
        for col in missing_sensors:
            if col == 'vibration':
                df[col] = 2.0 + (rpm / 100.0) * 2.0 + np.random.normal(0, 0.3, len(df))
                df[col] = np.clip(df[col], 0.5, 8.0)
            elif col == 'oil_pressure':
                df[col] = 2.0 + (rpm / 100.0) * 2.5 + np.random.normal(0, 0.2, len(df))
                df[col] = np.clip(df[col], 1.0, 6.0)
            elif col == 'exhaust_temp':
                df[col] = 350.0 + (rpm / 100.0) * 80.0 + np.random.normal(0, 10, len(df))
                df[col] = np.clip(df[col], 300.0, 550.0)
            elif col == 'coolant_temp':
                df[col] = 75.0 + (rpm / 100.0) * 10.0 + np.random.normal(0, 2, len(df))
                df[col] = np.clip(df[col], 50.0, 120.0)
            elif col == 'oil_quality':
                df[col] = 0.95 - (df['hour'] / (df['hour'].max() + 1)) * 0.3 + np.random.normal(0, 0.05, len(df))
                df[col] = np.clip(df[col], 0.0, 1.0)
        
        log.info("Generated synthetic data for: %s" % str(missing_sensors))
 
    # Remove rows with critical NaN
    df_before = len(df)
    df = df.dropna(subset=['part_name', 'hour'], how='any')
    if len(df) < df_before:
        log.warning("Removed %d rows with missing data" % (df_before - len(df)))
 
    parts_in_data = set(df['part_name'].dropna().unique())
    if not parts_in_data:
        log.error("No part_name values found")
        return None
 
    if df.empty:
        log.error("CSV file is empty")
        return None
 
    log.info("Loaded %d rows" % len(df))
    log.info("Parts found: %s" % str(sorted(parts_in_data)))
    
    df = df.sort_values(['part_name', 'hour']).reset_index(drop=True)
    return df
 
 
def step2_train_models(df):
    """Train prediction models."""
    log.info("STEP 2: Training prediction models...")
 
    if not MODEL_AVAILABLE:
        log.warning("ShipPartLifetimePredictor module not available")
        return {}
 
    trained_models = {}
    all_metrics = []
    parts_in_data = sorted(df["part_name"].dropna().unique())
 
    if not parts_in_data:
        log.error("No parts found")
        return {}
 
    for part_name in parts_in_data:
        part_df = df[df["part_name"] == part_name].copy()
 
        if len(part_df) < 50:
            log.warning("Skipping '%s' - insufficient rows (%d < 50)" % (part_name, len(part_df)))
            continue
 
        if 'max_lifetime_hours' in part_df.columns:
            try:
                max_lifetime_hours = float(part_df['max_lifetime_hours'].mode()[0])
            except:
                max_lifetime_hours = PART_LIFETIME_DEFAULTS.get(part_name, 10000)
        else:
            max_lifetime_hours = PART_LIFETIME_DEFAULTS.get(part_name, 10000)
 
        try:
            missing = [c for c in REQUIRED_SENSOR_COLS if c not in part_df.columns]
            if missing:
                log.warning("'%s': Missing columns, skipping" % part_name)
                continue
            
            predictor = ShipPartLifetimePredictor(part_name=part_name, window_size=30)
            metrics = predictor.train(part_df)
            
            if metrics is None:
                log.error("Training failed for '%s'" % part_name)
                continue
            
            all_metrics.append(metrics)
            
            try:
                predictor.save("models")
            except:
                pass
            
            trained_models[part_name] = {
                'predictor': predictor,
                'max_lifetime_hours': max_lifetime_hours,
            }
            
            r2 = metrics.get('r2_score', 0)
            acc = metrics.get('accuracy_pct', 0)
            log.info("Trained '%s' - R2=%.4f, Acc=%.1f%%" % (part_name, r2, acc))
        except Exception as e:
            log.error("Training failed for '%s': %s" % (part_name, str(e)))
            continue
 
    if not trained_models:
        log.error("No models trained")
        return {}
 
    print("\n  Part                             R2 Score     Accuracy")
    print("  " + "-" * 55)
    for m in all_metrics:
        part = m.get('part', 'Unknown')
        r2 = m.get('r2_score', 0)
        acc = m.get('accuracy_pct', 0)
        print("  %-30s %10.4f %10.1f%%" % (part, r2, acc))
    
    log.info("Successfully trained %d model(s)" % len(trained_models))
    return trained_models
 
 
def step3_predict(df, models, simulation_hour=SIMULATION_HOUR):
    """Run predictions."""
    log.info("STEP 3: Running predictions at hour %d..." % simulation_hour)
 
    if not models:
        log.warning("No models available")
        return []
 
    ALERT_EMOJI = {
        "HEALTHY": "[OK]",
        "CAUTION": "[CAUTION]",
        "WARNING": "[WARNING]",
        "CRITICAL": "[CRITICAL]",
    }
 
    all_predictions = []
 
    for part_name, info in models.items():
        try:
            predictor = info.get('predictor')
            if predictor is None:
                continue
            
            max_lifetime_hours = info.get('max_lifetime_hours', 10000)
            part_df = df[df["part_name"] == part_name].copy()
 
            if part_df.empty:
                continue
 
            window = part_df[part_df["hour"] <= simulation_hour].tail(30)
 
            if len(window) < 5:
                log.warning("Not enough data for '%s'" % part_name)
                continue
 
            try:
                pred = predictor.predict(recent_sensor_df=window, max_lifetime_hours=max_lifetime_hours)
            except Exception as e:
                log.error("Prediction failed for '%s': %s" % (part_name, str(e)))
                continue
 
            if pred is None:
                continue
 
            all_predictions.append(pred)
 
            alert_level = pred.get("alert_level", "UNKNOWN")
            alert_symbol = ALERT_EMOJI.get(alert_level, "?")
            
            print("\n  %s  %s" % (alert_symbol, part_name))
            print("     Health  : %s%%" % str(pred.get('health_score', 'N/A')))
            print("     RUL     : %s days (%s hours)" % (pred.get('rul_days', 'N/A'), pred.get('rul_hours', 'N/A')))
            print("     Alert   : %s" % alert_level)
            
            if pred.get("is_anomaly"):
                print("     [ALERT] ANOMALY DETECTED")
            
            print("     Action  : %s" % pred.get('recommendation', 'N/A'))
 
        except Exception as e:
            log.error("Error processing '%s': %s" % (part_name, str(e)))
            continue
 
    if not all_predictions:
        log.warning("No predictions generated")
 
    return all_predictions
 
 
def step4_generate_outputs(df, predictions):
    """Generate outputs."""
    log.info("STEP 4: Generating visual outputs...")
 
    if not predictions:
        log.warning("No predictions to visualize")
        return
    
    if not VISUALIZER_AVAILABLE:
        log.warning("Visualizer not available")
        return
 
    try:
        plot_health_dashboard(predictions=predictions, output_path="outputs/health_dashboard.png")
        log.info("Saved --> outputs/health_dashboard.png")
    except Exception as e:
        log.warning("Health dashboard failed: %s" % str(e))
 
    part_names = sorted({p.get('part_name', 'Unknown') for p in predictions if 'part_name' in p})
    
    for part_name in part_names:
        safe_name = part_name.replace(" ", "_").replace("/", "_").lower()
        try:
            plot_sensor_trends(df=df, part_name=part_name, output_path="outputs/sensors_%s.png" % safe_name)
            log.info("Saved --> outputs/sensors_%s.png" % safe_name)
        except Exception as e:
            log.warning("Sensor chart failed for '%s': %s" % (part_name, str(e)))
    
    try:
        plot_rul_prediction(df=df, part_name="Main Engine Bearing", predicted_ruls=[], output_path="outputs/rul_timeline_main_engine.png")
        log.info("Saved --> outputs/rul_timeline_main_engine.png")
    except Exception as e:
        log.warning("RUL timeline failed: %s" % str(e))
    
    try:
        generate_maintenance_report(predictions=predictions, output_path="outputs/maintenance_report.txt")
        log.info("Saved --> outputs/maintenance_report.txt")
    except Exception as e:
        log.warning("Maintenance report failed: %s" % str(e))
 
    print("\n  Outputs saved to outputs/:")
    print("     - health_dashboard.png")
    print("     - sensors_*.png")
    print("     - rul_timeline_*.png")
    print("     - maintenance_report.txt")
 
 
def print_banner():
    """Print banner."""
    print("\n" + "=" * 60)
    print("   SHIP PART LIFETIME PREDICTION SYSTEM")
    print("       SIH1506 - Maritime AI Project")
    print("=" * 60)
 
 
def main(data_path=None, simulation_hour=SIMULATION_HOUR):
    """Main pipeline."""
    try:
        print_banner()
 
        if data_path:
            df = step1_load_data(data_path)
        else:
            df = step1_load_data(DATA_PATH)
        
        if df is None or df.empty:
            log.error("Failed to load data")
            return
 
        if MODEL_AVAILABLE:
            models = step2_train_models(df)
            if not models:
                log.error("No models trained")
                return
        else:
            log.warning("Cannot train models - model module not available")
            return

        predictions = step3_predict(df, models, simulation_hour=simulation_hour)

        if not predictions:
            log.warning("No predictions generated")

        if predictions:
            step4_generate_outputs(df, predictions)

        print("\n" + "=" * 60)
        print("  >>> PIPELINE COMPLETE <<<")
        print("=" * 60)
        print("\n  System capabilities:")
        print("  [+] Monitors ship components")
        print("  [+] Predicts remaining lifetime in days/hours")
        print("  [+] Detects anomalies in sensor readings")
        print("  [+] Actionable maintenance recommendations")
        print("  [+] Visual dashboard + full report")
        print("\n  Next steps:")
        print("  --> Connect to real MQTT sensor stream")
        print("  --> Add LSTM model for sequence-based prediction")
        print("  --> Build REST API with FastAPI")
        print("  --> Connect to React.js dashboard")
        print("=" * 60 + "\n")
 
    except KeyboardInterrupt:
        log.info("Pipeline interrupted by user")
        print("\n  Pipeline cancelled")
    except Exception as e:
        log.error("Unexpected error: %s" % str(e))
        log.debug(traceback.format_exc())
        print("\n  ERROR: %s" % str(e))
 
 
if __name__ == "__main__":
    import argparse
 
    parser = argparse.ArgumentParser(
        description='Ship Part Lifetime Prediction System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python train_lifetime_model.py
  python train_lifetime_model.py --data-path "new_maritime_dataset.csv"
  python train_lifetime_model.py --simulation-hour 2000
        """
    )
    parser.add_argument('--data-path', type=str, default=None, help='Path to dataset')
    parser.add_argument('--simulation-hour', type=int, default=SIMULATION_HOUR, help='Simulation hour')
 
    args = parser.parse_args()
    main(data_path=args.data_path, simulation_hour=args.simulation_hour)