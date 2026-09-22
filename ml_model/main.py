"""
SyntheticAI – Smart Maritime Route Optimization System
CLI entry point for training models and finding optimal routes.

Usage:
    # Train route models
    python main.py train

    # Train route models (fast, no GridSearch)
    python main.py train --fast

    # Find best routes
    python main.py route --origin "Jebel Ali" --destination "Guangzhou" --ship_type "Tanker"

    # List available ports
    python main.py ports

    # Run ship part lifetime prediction pipeline
    python main.py lifetime

    # Run lifetime prediction with custom data path or simulation hour
    python main.py lifetime --data-path "data/new_maritime_dataset.csv" --simulation-hour 2000
"""
import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def cmd_train(args):
    """Train both fuel and ETA models."""
    from train_fuel_model import main as train_fuel
    from train_eta_model import main as train_eta

    print("\n" + "█" * 60)
    print("  SyntheticAI – Training Pipeline")
    print("█" * 60)

    tune = not args.fast
    if args.fast:
        print("\n  ⚡ Fast mode: skipping GridSearchCV\n")

    print("\n─── STEP 1/2: Fuel Prediction Model ───")
    fuel_model, fuel_metrics = train_fuel(tune=tune)

    print("\n─── STEP 2/2: ETA Prediction Model ───")
    eta_model, eta_metrics = train_eta(tune=tune)

    print("\n" + "█" * 60)
    print("  TRAINING COMPLETE")
    print("█" * 60)
    print(f"\n  Fuel Model R²:  {fuel_metrics['r2']:.4f}")
    print(f"  ETA  Model R²:  {eta_metrics['r2']:.4f}")
    print(f"\n  Models saved to: models/")
    print(f"  Evaluation plots saved to: evaluation/")
    print("█" * 60)


def cmd_route(args):
    """Find optimal routes between two ports."""
    from predict import MaritimePredictor

    predictor = MaritimePredictor()
    routes = predictor.recommend_routes(
        origin=args.origin,
        destination=args.destination,
        ship_type=args.ship_type,
        top_k=3,
    )

    if not routes:
        print(f"\n❌ No routes found from {args.origin} to {args.destination}")
        ports = predictor.get_ports()
        print(f"\nAvailable origins: {', '.join(ports['origins'])}")
        print(f"Available destinations: {', '.join(ports['destinations'])}")


def cmd_ports(args):
    """List all available ports."""
    from predict import MaritimePredictor

    predictor = MaritimePredictor()
    ports = predictor.get_ports()

    print("\n" + "=" * 50)
    print("  Available Ports")
    print("=" * 50)
    print(f"\n  Origin Ports ({len(ports['origins'])}):")
    for p in ports['origins']:
        print(f"    • {p}")
    print(f"\n  Destination Ports ({len(ports['destinations'])}):")
    for p in ports['destinations']:
        print(f"    • {p}")
    print("=" * 50)


def cmd_lifetime(args):
    """Run the ship part lifetime prediction pipeline."""
    from train_lifetime_model_OLD import main as run_lifetime

    # Resolve data path — prefer CLI arg, then auto-detect
    data_path = args.data_path
    if data_path is None:
        base = os.path.dirname(__file__)
        candidates = [
            os.path.join(base, 'data', 'sensor_data.csv'),
            os.path.join(base, 'data', 'new_maritime_dataset.csv'),
            os.path.join(base, '..', 'data', 'new_maritime_dataset.csv'),
        ]
        for path in candidates:
            if os.path.exists(path):
                data_path = path
                break

    if data_path is None:
        print("\n❌  No dataset found. Provide one with --data-path.")
        print("    Example: python main.py lifetime --data-path data/sensor_data.csv")
        return

    print(f"\n  Using dataset  : {data_path}")
    print(f"  Simulation hour: {args.simulation_hour}")

    run_lifetime(
        data_path=data_path,
        simulation_hour=args.simulation_hour,
    )


def main():
    parser = argparse.ArgumentParser(
        description='SyntheticAI – Smart Maritime Route Optimization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py train                              Train route models
  python main.py train --fast                       Train without GridSearch
  python main.py route -o "Jebel Ali" -d "Guangzhou" -s "Tanker"
  python main.py ports                              List available ports
  python main.py lifetime                           Run lifetime prediction
  python main.py lifetime --data-path "data/new_maritime_dataset.csv"
  python main.py lifetime --simulation-hour 2000
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Train command
    train_parser = subparsers.add_parser('train', help='Train fuel & ETA models')
    train_parser.add_argument('--fast', action='store_true',
                              help='Skip GridSearchCV for quick training')

    # Route command
    route_parser = subparsers.add_parser('route', help='Find best routes')
    route_parser.add_argument('-o', '--origin', required=True, help='Origin port name')
    route_parser.add_argument('-d', '--destination', required=True, help='Destination port name')
    route_parser.add_argument('-s', '--ship_type', default=None, help='Ship type filter')

    # Ports command
    subparsers.add_parser('ports', help='List available ports')

    # Lifetime prediction command
    lifetime_parser = subparsers.add_parser('lifetime', help='Run ship part lifetime prediction')
    lifetime_parser.add_argument('--data-path', type=str, default=None,
                                 help='Path to sensor data CSV (default: auto-detect)')
    lifetime_parser.add_argument('--simulation-hour', type=int, default=1500,
                                 help='Operating hour to simulate predictions at (default: 1500)')

    args = parser.parse_args()

    if args.command == 'train':
        cmd_train(args)
    elif args.command == 'route':
        cmd_route(args)
    elif args.command == 'ports':
        cmd_ports(args)
    elif args.command == 'lifetime':
        cmd_lifetime(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()