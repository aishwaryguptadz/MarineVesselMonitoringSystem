"""
MAIN PIPELINE - Ship Part Lifetime Prediction System (FIXED VERSION)
=====================================================
Run this file to:
  1. Load existing sensor data from CSV
  2. Train models for all 6 ship parts
  3. Run predictions
  4. Generate visual dashboard + maintenance report
"""

print("=" * 60)
print("INITIALIZING PROGRAM...")
print("=" * 60)

import os
import sys
import logging
import traceback
import numpy as np
import pandas as pd
import warnings

print("[OK] Basic imports loaded")

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

print("[OK] Logging configured")

sys.path.insert(0, os.path.dirname(__file__))

# Track module availability
MODEL_AVAILABLE = False
VISUALIZER_AVAILABLE = False

# Try to import model module
try:
    from model import ShipPartLifetimePredictor
    MODEL_AVAILABLE = True
    print("[OK] model.py imported successfully")
except ImportError as e:
    print("[ERROR] model.py not found - ImportError")
    print("        " + str(e))
except Exception as e:
    print("[ERROR] model.py import failed - " + str(type(e).__name__))
    print("        " + str(e))

# Try to import visualizer module
try:
    from visualizer import (
        plot_health_dashboard,
        plot_sensor_trends,
        plot_rul_prediction,
        generate_maintenance_report,
    )
    VISUALIZER_AVAILABLE = True
    print("[OK] visualizer.py imported successfully")
except ImportError as e:
    print("[WARN] visualizer.py not found - ImportError")
    print("       " + str(e))
except Exception as e:
    print("[ERROR] visualizer.py import failed - " + str(type(e).__name__))
    print("        " + str(e))

print("")
print("Module Status:")
print("  MODEL_AVAILABLE      : " + str(MODEL_AVAILABLE))
print("  VISUALIZER_AVAILABLE : " + str(VISUALIZER_AVAILABLE))
print("=" * 60)

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
SIMULATION_HOUR = 8500
REQUIRED_SENSOR_COLS = [
    'vibration', 'oil_pressure', 'exhaust_temp',
    'coolant_temp', 'rpm', 'oil_quality',
]


def step1_load_data(path=DATA_PATH):
    """Load and validate sensor data, aligning operational degradation with fleet health."""
    log.info("STEP 1: Loading sensor data...")
    print("\n" + "=" * 60)
    print("STEP 1: LOADING DATA")
    print("=" * 60)

    if not os.path.exists(path):
        log.warning("Data file not found: '%s'" % path)
        print("[WARN] Primary data file not found: " + path)
        if os.path.exists(FALLBACK_DATA_PATH):
            log.warning("Using fallback dataset: '%s'" % FALLBACK_DATA_PATH)
            print("[INFO] Using fallback: " + FALLBACK_DATA_PATH)
            path = FALLBACK_DATA_PATH
        else:
            log.error("Please provide sensor data CSV")
            print("[ERROR] No data files found!")
            print("        Checked: " + DATA_PATH)
            print("        Checked: " + FALLBACK_DATA_PATH)
            return None

    try:
        df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
        print("[OK] Data loaded successfully")
    except Exception:
        try:
            df = pd.read_csv(path, encoding='latin-1', on_bad_lines='skip')
            log.info("Loaded with latin-1 encoding")
            print("[OK] Data loaded with latin-1 encoding")
        except Exception as e:
            log.error("Failed to read CSV: %s" % str(e))
            print("[ERROR] Failed to read CSV: " + str(e))
            return None

    log.info("Dataset shape: %s" % str(df.shape))
    print("[INFO] Dataset shape: " + str(df.shape))

    # 1. Handle part_name column
    if 'part_name' not in df.columns:
        if 'ship_type' in df.columns:
            df['part_name'] = df['ship_type'].astype(str)
            log.warning("Using ship_type as part_name")
            print("[WARN] Using ship_type as part_name")
        else:
            df['part_name'] = 'default_part'
            print("[WARN] No part_name column, using default")

    # 2. Establish max lifetime baseline
    max_ref_life = 10000.0
    if 'max_lifetime_hours' not in df.columns:
        df['max_lifetime_hours'] = max_ref_life

    # 3. Derive cumulative operating 'hour' aligned with real dataset health
    if 'hour' not in df.columns:
        if 'fleet_avg_health_pct' in df.columns:
            # Map low health -> late operational lifecycle hours
            health_series = pd.to_numeric(df['fleet_avg_health_pct'], errors='coerce').clip(0.0, 100.0)
            df['hour'] = max_ref_life * (1.0 - (health_series / 100.0))
            log.info("Derived operating hour from fleet_avg_health_pct")
            print("[INFO] Derived cumulative operating hours from fleet_avg_health_pct")
        elif 'voyage_hours' in df.columns:
            df['hour'] = pd.to_numeric(df['voyage_hours'], errors='coerce')
            log.warning("Using voyage_hours as hour")
            print("[WARN] Using voyage_hours as hour")
        else:
            df['hour'] = np.arange(len(df), dtype=float)
            print("[WARN] No hour column, generating sequence")

    # Clean any NaN hours (using modern pandas syntax)
    if df['hour'].isna().any():
        df['hour'] = df['hour'].ffill().bfill().fillna(0.0)

    # 4. Generate synthetic sensor data correlated with true degradation
    missing_sensors = [c for c in REQUIRED_SENSOR_COLS if c not in df.columns]
    if missing_sensors:
        log.warning("Missing sensor columns: %s" % str(missing_sensors))
        print("[WARN] Missing sensors: " + str(missing_sensors))
        print("[INFO] Generating synthetic sensor degradation data...")

        # Base RPM
        if 'rpm' in df.columns:
            rpm = pd.to_numeric(df['rpm'], errors='coerce').fillna(100.0)
        else:
            rpm = pd.Series(np.random.uniform(80, 130, len(df)))
        rpm = np.clip(rpm, 50.0, 150.0)

        # Base health and degradation factors
        if 'fleet_avg_health_pct' in df.columns:
            health_ratio = (pd.to_numeric(df['fleet_avg_health_pct'], errors='coerce').fillna(50.0) / 100.0).clip(0.0, 1.0)
        else:
            health_ratio = np.clip(1.0 - (df['hour'] / max_ref_life), 0.0, 1.0)
            
        degradation = 1.0 - health_ratio
        np.random.seed(42)

        for col in missing_sensors:
            if col == 'vibration':
                # Vibration climbs as part wears out and with higher engine RPM
                df[col] = 1.5 + (degradation * 4.5) + ((rpm / 100.0) * 0.5) + np.random.normal(0, 0.2, len(df))
                df[col] = np.clip(df[col], 0.5, 8.0)
            elif col == 'oil_pressure':
                # Oil pressure drops as seals, bearings, and pumps degrade
                df[col] = 4.8 - (degradation * 3.0) + ((rpm / 100.0) * 0.4) + np.random.normal(0, 0.15, len(df))
                df[col] = np.clip(df[col], 1.0, 6.0)
            elif col == 'exhaust_temp':
                # Exhaust temperature rises with wear and combustion inefficiency
                df[col] = 340.0 + (degradation * 90.0) + ((rpm / 100.0) * 50.0) + np.random.normal(0, 8, len(df))
                df[col] = np.clip(df[col], 300.0, 550.0)
            elif col == 'coolant_temp':
                # Coolant temperature increases under degraded heat transfer
                df[col] = 72.0 + (degradation * 20.0) + ((rpm / 100.0) * 8.0) + np.random.normal(0, 2, len(df))
                df[col] = np.clip(df[col], 50.0, 120.0)
            elif col == 'oil_quality':
                # Oil quality directly tracks health degradation
                df[col] = np.clip(health_ratio + np.random.normal(0, 0.04, len(df)), 0.0, 1.0)

        print("[OK] Synthetic degradation sensor data generated")

    # 5. Clean invalid rows
    df_before = len(df)
    df = df.dropna(subset=['part_name', 'hour'], how='any')
    if len(df) < df_before:
        log.warning("Removed %d rows with missing data" % (df_before - len(df)))
        print("[WARN] Removed %d rows with missing data" % (df_before - len(df)))

    parts_in_data = set(df['part_name'].dropna().unique())
    if not parts_in_data or df.empty:
        log.error("Dataset is empty or has no parts")
        print("[ERROR] Dataset empty after cleaning")
        return None

    print("[OK] Loaded %d rows" % len(df))
    print("[INFO] Parts found: " + str(sorted(parts_in_data)))

    df = df.sort_values(['part_name', 'hour']).reset_index(drop=True)
    return df


def step2_train_models(df):
    """Train prediction models."""
    log.info("STEP 2: Training prediction models...")
    print("\n" + "=" * 60)
    print("STEP 2: TRAINING MODELS")
    print("=" * 60)

    if not MODEL_AVAILABLE:
        log.warning("ShipPartLifetimePredictor module not available")
        print("[ERROR] Cannot train - model.py not available")
        return {}

    trained_models = {}
    all_metrics = []
    parts_in_data = sorted(df["part_name"].dropna().unique())

    if not parts_in_data:
        log.error("No parts found")
        print("[ERROR] No parts found in data")
        return {}

    print("[INFO] Training models for %d parts..." % len(parts_in_data))
    
    for part_name in parts_in_data:
        part_df = df[df["part_name"] == part_name].copy()

        if len(part_df) < 50:
            log.warning("Skipping '%s' - insufficient rows (%d < 50)" % (part_name, len(part_df)))
            print("[SKIP] %s - insufficient data (%d rows)" % (part_name, len(part_df)))
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
                print("[SKIP] %s - missing columns: %s" % (part_name, str(missing)))
                continue
            
            print("[....] Training: " + part_name)
            predictor = ShipPartLifetimePredictor(part_name=part_name, window_size=30)
            metrics = predictor.train(part_df)
            
            if metrics is None:
                log.error("Training failed for '%s'" % part_name)
                print("[FAIL] Training failed for: " + part_name)
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
            print("[OK] Trained: %s (R2=%.4f, Acc=%.1f%%)" % (part_name, r2, acc))
                 # ── LSTM training ──────────────────────────────
            try:
                from lstm_predictor import ShipPartLSTMPredictor
                print("[....] Training LSTM: " + part_name)
                lstm = ShipPartLSTMPredictor(part_name=part_name, window_size=30)
                lstm_metrics = lstm.train(part_df, epochs=50)
                lstm.save("models")
                print("[OK] LSTM trained: %s (R2=%.4f)" % (part_name, lstm_metrics['r2_score']))
                print("     RF   R²: %.4f" % r2)
                print("     LSTM R²: %.4f" % lstm_metrics['r2_score'])
            except Exception as e:
                print("[WARN] LSTM training failed for %s: %s" % (part_name, str(e)))
        except Exception as e:
            log.error("Training failed for '%s': %s" % (part_name, str(e)))
            print("[ERROR] Training failed for %s: %s" % (part_name, str(e)))
            continue

    if not trained_models:
        log.error("No models trained")
        print("[ERROR] No models were successfully trained")
        return {}

    print("\n" + "-" * 60)
    print("TRAINING SUMMARY")
    print("-" * 60)
    print("  Part                             R2 Score     Accuracy")
    print("  " + "-" * 55)
    for m in all_metrics:
        part = m.get('part', 'Unknown')
        r2 = m.get('r2_score', 0)
        acc = m.get('accuracy_pct', 0)
        print("  %-30s %10.4f %10.1f%%" % (part, r2, acc))
    print("-" * 60)
    
    log.info("Successfully trained %d model(s)" % len(trained_models))
    print("[OK] Successfully trained %d models" % len(trained_models))
    return trained_models


def step3_predict(df, models, simulation_hour=SIMULATION_HOUR):
    """Run predictions."""
    log.info("STEP 3: Running predictions at hour %d..." % simulation_hour)
    print("\n" + "=" * 60)
    print("STEP 3: RUNNING PREDICTIONS (Hour: %d)" % simulation_hour)
    print("=" * 60)

    if not models:
        log.warning("No models available")
        print("[WARN] No models available for prediction")
        return []

    ALERT_SYMBOLS = {
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
                print("[SKIP] %s - insufficient recent data" % part_name)
                continue

            try:
                pred = predictor.predict(recent_sensor_df=window, max_lifetime_hours=max_lifetime_hours)
            except Exception as e:
                log.error("Prediction failed for '%s': %s" % (part_name, str(e)))
                print("[ERROR] Prediction failed for %s: %s" % (part_name, str(e)))
                continue

            if pred is None:
                continue

            all_predictions.append(pred)

            alert_level = pred.get("alert_level", "UNKNOWN")
            alert_symbol = ALERT_SYMBOLS.get(alert_level, "[?]")
            
            print("\n  %s  %s" % (alert_symbol, part_name))
            print("     Health  : %s%%" % str(pred.get('health_score', 'N/A')))
            print("     RUL     : %s days (%s hours)" % (pred.get('rul_days', 'N/A'), pred.get('rul_hours', 'N/A')))
            print("     Alert   : %s" % alert_level)
            
            if pred.get("is_anomaly"):
                print("     [ALERT] ANOMALY DETECTED")
            
            print("     Action  : %s" % pred.get('recommendation', 'N/A'))

        except Exception as e:
            log.error("Error processing '%s': %s" % (part_name, str(e)))
            print("[ERROR] Processing failed for %s: %s" % (part_name, str(e)))
            continue

    if not all_predictions:
        log.warning("No predictions generated")
        print("[WARN] No predictions were generated")

    return all_predictions


def step4_generate_outputs(df, predictions):
    """Generate outputs."""
    log.info("STEP 4: Generating visual outputs...")
    print("\n" + "=" * 60)
    print("STEP 4: GENERATING OUTPUTS")
    print("=" * 60)

    if not predictions:
        log.warning("No predictions to visualize")
        print("[WARN] No predictions to visualize")
        return
    
    if not VISUALIZER_AVAILABLE:
        log.warning("Visualizer not available")
        print("[WARN] Visualizer not available - skipping visual outputs")
        return

    try:
        plot_health_dashboard(predictions=predictions, output_path="outputs/health_dashboard.png")
        log.info("Saved --> outputs/health_dashboard.png")
        print("[OK] Saved: outputs/health_dashboard.png")
    except Exception as e:
        log.warning("Health dashboard failed: %s" % str(e))
        print("[ERROR] Health dashboard failed: " + str(e))

    part_names = sorted({p.get('part_name', 'Unknown') for p in predictions if 'part_name' in p})
    
    for part_name in part_names:
        safe_name = part_name.replace(" ", "_").replace("/", "_").lower()
        try:
            plot_sensor_trends(df=df, part_name=part_name, output_path="outputs/sensors_%s.png" % safe_name)
            log.info("Saved --> outputs/sensors_%s.png" % safe_name)
            print("[OK] Saved: outputs/sensors_%s.png" % safe_name)
        except Exception as e:
            log.warning("Sensor chart failed for '%s': %s" % (part_name, str(e)))
            print("[ERROR] Sensor chart failed for %s: %s" % (part_name, str(e)))
    
    try:
        plot_rul_prediction(df=df, part_name="Main Engine Bearing", predicted_ruls=[], output_path="outputs/rul_timeline_main_engine.png")
        log.info("Saved --> outputs/rul_timeline_main_engine.png")
        print("[OK] Saved: outputs/rul_timeline_main_engine.png")
    except Exception as e:
        log.warning("RUL timeline failed: %s" % str(e))
        print("[ERROR] RUL timeline failed: " + str(e))
    
    try:
        generate_maintenance_report(predictions=predictions, output_path="outputs/maintenance_report.txt")
        log.info("Saved --> outputs/maintenance_report.txt")
        print("[OK] Saved: outputs/maintenance_report.txt")
    except Exception as e:
        log.warning("Maintenance report failed: %s" % str(e))
        print("[ERROR] Maintenance report failed: " + str(e))

    print("\n" + "-" * 60)
    print("Output files saved to outputs/:")
    print("  - health_dashboard.png")
    print("  - sensors_*.png")
    print("  - rul_timeline_*.png")
    print("  - maintenance_report.txt")
    print("-" * 60)


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
        
        print("\n[INFO] Starting pipeline...")
        print("[INFO] Current directory: " + os.getcwd())

        # Check prerequisites
        if not MODEL_AVAILABLE:
            print("\n" + "=" * 60)
            print("ERROR: CANNOT PROCEED")
            print("=" * 60)
            print("The 'model.py' file is required but could not be imported.")
            print("Please ensure 'model.py' exists in the src/ folder and has no errors.")
            print("=" * 60)
            return
        
        # Load data
        if data_path:
            df = step1_load_data(data_path)
        else:
            df = step1_load_data(DATA_PATH)
        
        if df is None or df.empty:
            log.error("Failed to load data")
            print("\n" + "=" * 60)
            print("ERROR: DATA LOADING FAILED")
            print("=" * 60)
            return

        # Train models
        models = step2_train_models(df)
        
        if not models:
            log.error("No models trained")
            print("\n" + "=" * 60)
            print("ERROR: NO MODELS TRAINED")
            print("=" * 60)
            return

        # Run predictions
        predictions = step3_predict(df, models, simulation_hour=simulation_hour)

        if not predictions:
            log.warning("No predictions generated")
            print("[WARN] No predictions generated")

        # Generate outputs
        if predictions:
            step4_generate_outputs(df, predictions)

        # Final summary
        print("\n" + "=" * 60)
        print("  PIPELINE COMPLETE")
        print("=" * 60)
        print("\n  System capabilities:")
        print("  [+] Monitors ship components")
        print("  [+] Predicts remaining lifetime in days/hours")
        print("  [+] Detects anomalies in sensor readings")
        print("  [+] Actionable maintenance recommendations")
        print("  [+] Visual dashboard + full report")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        log.info("Pipeline interrupted by user")
        print("\n[INFO] Pipeline cancelled by user")
    except Exception as e:
        log.error("Unexpected error: %s" % str(e))
        log.debug(traceback.format_exc())
        print("\n" + "=" * 60)
        print("UNEXPECTED ERROR")
        print("=" * 60)
        print("Error: " + str(e))
        print("\nFull traceback:")
        print(traceback.format_exc())
        print("=" * 60)


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
    
    print("\n[INFO] Command line arguments:")
    print("       data_path      : " + str(args.data_path))
    print("       simulation_hour: " + str(args.simulation_hour))
    
    main(data_path=args.data_path, simulation_hour=args.simulation_hour)