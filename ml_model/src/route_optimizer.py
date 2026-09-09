"""
SyntheticAI – Route Optimization Engine
Evaluates all possible routes (direct + multi-hop) between origin and
destination ports and returns the top 3 ranked routes.
"""
import os
import itertools
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

RAW_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw', 'new_maritime_dataset.csv')


class RouteOptimizer:
    """
    Builds a port connectivity graph from the dataset, evaluates all feasible
    routes (direct + multi-hop via intermediate ports), and returns top 3.
    """

    ROUTE_TYPES = ['moderate', 'safest', 'shortest']

    def __init__(self, data_path: str = RAW_PATH):
        self.df = pd.read_csv(data_path)
        self._build_port_graph()


    def _haversine_nm(self, lat1, lon1, lat2, lon2):
        R = 3440.065  # Earth radius in nautical miles

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    # ── Port graph ───────────────────────────────────────────────────────
    def _build_port_graph(self):
        """Build adjacency info from dataset: which ports connect to which."""
        self.all_ports = set()
        self.port_pairs = {}          # (origin, dest) → list of route records
        self.port_coords = {}         # port_name → (lat, lon)

        for _, row in self.df.iterrows():
            for rt in self.ROUTE_TYPES:
                origin = row[f'origin_port__{rt}']
                dest = row[f'destination_port__{rt}']
                o_lat = row[f'origin_lat__{rt}']
                o_lon = row[f'origin_lon__{rt}']
                d_lat = row[f'destination_lat__{rt}']
                d_lon = row[f'destination_lon__{rt}']

                self.all_ports.add(origin)
                self.all_ports.add(dest)
                self.port_coords[origin] = (o_lat, o_lon)
                self.port_coords[dest] = (d_lat, d_lon)

                key = (origin, dest)
                if key not in self.port_pairs:
                    self.port_pairs[key] = []
                self.port_pairs[key].append({
                    'route_type': rt,
                    'distance_nm': row[f'route_distance_nm__{rt}'],
                    'fuel_total_t': row[f'fuel_total_t__{rt}'],
                    'fuel_cost_usd': row[f'fuel_cost_usd__{rt}'],
                    'voyage_days': row[f'voyage_days__{rt}'],
                    'efficiency_score': row[f'efficiency_score__{rt}'],
                    'composite_risk': row[f'composite_risk_score__{rt}'],
                    'storm_risk': row[f'storm_risk_score__{rt}'],
                    'piracy_risk': row[f'piracy_risk_score__{rt}'],
                    'is_recommended': row[f'is_recommended__{rt}'],
                    'passes_suez': row.get(f'passes_suez__{rt}', 0),
                    'passes_panama': row.get(f'passes_panama__{rt}', 0),
                    'passes_malacca': row.get(f'passes_malacca__{rt}', 0),
                    'passes_cape_good_hope': row.get(f'passes_cape_good_hope__{rt}', 0),
                    'passes_gulf_aden': row.get(f'passes_gulf_aden__{rt}', 0),
                    'ship_type': row['ship_type'],
                    'vessel_id': row['vessel_id'],
                })

        # Build adjacency: port → set of reachable ports
        self.adjacency = {}
        for (o, d) in self.port_pairs:
            if o not in self.adjacency:
                self.adjacency[o] = set()
            self.adjacency[o].add(d)

        '''print(f"[RouteOptimizer] Built graph: {len(self.all_ports)} ports, "
              f"{len(self.port_pairs)} unique port-pair routes")
        
        print("\nAdjacency example:")
        for k in list(self.adjacency.keys())[:5]:
            print(k, "→", self.adjacency[k])'''

        possible_hubs = [
            "Colombo",
            "Singapore",
            "Port Klang",
            "Tanjung Pelepas",
            "Jakarta"
        ]

        # keep only hubs that exist in dataset
        self.major_hubs = [h for h in possible_hubs if h in self.all_ports]

    # ── Route aggregation ────────────────────────────────────────────────
    def _get_best_leg(self, origin: str, dest: str, ship_type: str = None,
                      route_type: str = None) -> dict | None:
        """Get the best route record for a single leg (origin → dest)."""
        key = (origin, dest)
        if key not in self.port_pairs:
            return None

        candidates = self.port_pairs[key]

        # Filter by ship type if specified
        if ship_type:
            filtered = [r for r in candidates if r['ship_type'] == ship_type]
            if filtered:
                candidates = filtered

        # Filter by route type if specified
        if route_type:
            filtered = [r for r in candidates if r['route_type'] == route_type]
            if filtered:
                candidates = filtered

        if not candidates:
            return None

        # Aggregate: take median of all matching records for robustness
        agg = {
            'origin': origin,
            'destination': dest,
            'route_type': route_type or 'mixed',
            'distance_nm': np.median([r['distance_nm'] for r in candidates]),
            'fuel_total_t': np.median([r['fuel_total_t'] for r in candidates]),
            'fuel_cost_usd': np.median([r['fuel_cost_usd'] for r in candidates]),
            'voyage_days': np.median([r['voyage_days'] for r in candidates]),
            'efficiency_score': np.median([r['efficiency_score'] for r in candidates]),
            'composite_risk': np.median([r['composite_risk'] for r in candidates]),
            'storm_risk': np.median([r['storm_risk'] for r in candidates]),
            'piracy_risk': np.median([r['piracy_risk'] for r in candidates]),
            'total_risk': np.median([r['composite_risk'] + r['storm_risk'] + r['piracy_risk']
                                     for r in candidates]),
            'n_records': len(candidates),
        }
        return agg
    
    # -- Estimate a Missing leg ---------------------------------------------
    def _estimate_leg(self, origin, destination):
        """Estimate a route leg using geographic distance."""

        if origin not in self.port_coords or destination not in self.port_coords:
            return None

        lat1, lon1 = self.port_coords[origin]
        lat2, lon2 = self.port_coords[destination]

        distance_nm = self._haversine_nm(lat1, lon1, lat2, lon2)

        # simple fuel model (rough maritime estimate)
        fuel_per_nm = 0.18
        fuel = distance_nm * fuel_per_nm

        days = distance_nm / 350  # ~14.5 knots typical tanker

        risk = 0.5

        return {
            'origin': origin,
            'destination': destination,
            'route_type': 'estimated',
            'distance_nm': distance_nm,
            'fuel_total_t': fuel,
            'fuel_cost_usd': fuel * 600,
            'voyage_days': days,
            'efficiency_score': 0.5,
            'composite_risk': risk,
            'storm_risk': 0,
            'piracy_risk': 0,
            'total_risk': risk,
            'n_records': 0
        }

    # ── Multi-hop path finding ───────────────────────────────────────────
    def _find_all_paths(self, origin: str, destination: str, max_hops: int = 3) -> list:
        """Find all feasible paths using BFS traversal."""
    
        paths = set()

        # direct
        if destination in self.adjacency.get(origin, set()):
            paths.add(tuple([origin, destination]))
            

        # hub routing
        for hub in self.major_hubs:
            if hub != origin and hub != destination:
                paths.add(tuple([origin, hub, destination]))  

        queue = [[origin]]

        while queue:
            path = queue.pop(0)
            last = path[-1]

            if len(path) > max_hops + 1:
                continue

            if last == destination and len(path) > 1:
                paths.add(tuple(path))
                continue

            for next_port in self.adjacency.get(last, []):
                if next_port not in path:  # avoid cycles
                    new_path = path + [next_port]
                    queue.append(new_path)

        return [list(p) for p in paths]

    # ── Route evaluation ─────────────────────────────────────────────────
    def _evaluate_route(self, path: list, ship_type: str = None,
                        route_type: str = None) -> dict | None:
        """Evaluate a full route (list of ports) by summing leg metrics."""
        legs = []
        total_fuel = 0
        total_distance = 0
        total_days = 0
        total_cost = 0
        total_risk = 0

        for i in range(len(path) - 1):
            leg = self._get_best_leg(path[i], path[i + 1], ship_type, route_type)
            if leg is None:
                leg = self._estimate_leg(path[i], path[i + 1])
                if leg is None:
                    return None
            legs.append(leg)
            total_fuel += leg['fuel_total_t']
            total_distance += leg['distance_nm']
            total_days += leg['voyage_days']
            total_cost += leg['fuel_cost_usd']
            total_risk += leg['total_risk']

        n_legs = len(legs)
        avg_risk = total_risk / n_legs if n_legs > 0 else 0

        return {
            'path': path,
            'path_str': ' → '.join(path),
            'n_legs': n_legs,
            'legs': legs,
            'total_fuel_t': round(total_fuel, 1),
            'total_distance_nm': round(total_distance, 1),
            'total_voyage_days': round(total_days, 1),
            'total_fuel_cost_usd': round(total_cost, 0),
            'avg_risk_score': round(avg_risk, 4),
            'total_risk_score': round(total_risk, 4),
            'route_type_used': route_type or 'mixed',
        }

    # ── Scoring & ranking ────────────────────────────────────────────────
    def _score_routes(self, routes: list) -> list:
        """Normalise and score routes: 0.5*fuel + 0.3*risk + 0.2*time."""
        if not routes:
            return []

        fuels = [r['total_fuel_t'] for r in routes]
        risks = [r['total_risk_score'] for r in routes]
        days = [r['total_voyage_days'] for r in routes]

        def normalise(vals):
            mn, mx = min(vals), max(vals)
            if mx == mn:
                return [0.5] * len(vals)
            return [(v - mn) / (mx - mn) for v in vals]

        n_fuel = normalise(fuels)
        n_risk = normalise(risks)
        n_days = normalise(days)

        for i, r in enumerate(routes):
            r['score'] = round(0.5 * n_fuel[i] + 0.3 * n_risk[i] + 0.2 * n_days[i], 4)

        routes.sort(key=lambda x: x['score'])

        # Assign labels
        best_fuel_idx = int(np.argmin(fuels))
        best_risk_idx = int(np.argmin(risks))
        best_time_idx = int(np.argmin(days))

        for i, r in enumerate(routes):
            labels = []
            if i == 0:
                labels.append('🟢 Best Overall')
            if i == best_fuel_idx:
                labels.append('⛽ Most Fuel-Efficient')
            if i == best_risk_idx:
                labels.append('🛡️ Safest')
            if i == best_time_idx:
                labels.append('⚡ Fastest')
            r['labels'] = labels if labels else ['Route Option']

        return routes

    # ── Main API ─────────────────────────────────────────────────────────
    def find_best_routes(self, origin: str, destination: str,
                         ship_type: str = None, top_k: int = 3) -> list:
        """
        Find and return the top-K best routes between origin and destination.

        Parameters
        ----------
        origin : str – Origin port name
        destination : str – Destination port name
        ship_type : str – Filter by ship type (optional)
        top_k : int – Number of top routes to return

        Returns
        -------
        list of dict – Ranked routes with full breakdown
        """
        print(f"\n{'=' * 60}")
        print(f"  Route Optimisation: {origin} → {destination}")
        if ship_type:
            print(f"  Ship type: {ship_type}")
        print(f"{'=' * 60}")

        # Find all feasible paths
        all_paths = self._find_all_paths(origin, destination, max_hops=2)
        '''print(f"[RouteOptimizer] Found {len(all_paths)} feasible paths")

        print("\n[RouteOptimizer] Paths discovered:")
        for p in all_paths:
            print(" → ".join(p))'''

        # Evaluate each path × each route type
        all_routes = []
        for path in all_paths:
            for rt in self.ROUTE_TYPES:
                route = self._evaluate_route(path, ship_type, rt)
                if route:
                    all_routes.append(route)
            # Also evaluate with mixed (best per leg)
            route = self._evaluate_route(path, ship_type, None)
            if route:
                all_routes.append(route)

        #print(f"[RouteOptimizer] Evaluated {len(all_routes)} route variants")

        if not all_routes:
            print("[RouteOptimizer] No feasible routes found!")
            return []

        # Remove duplicates (same path + same scores)
        seen = set()
        unique_routes = []
        for r in all_routes:
            key = (r['path_str'], r['total_fuel_t'], r['total_voyage_days'])
            if key not in seen:
                seen.add(key)
                unique_routes.append(r)

        # Score and rank
        ranked = self._score_routes(unique_routes)
        # ensure at least one multi-hop route is shown
        multi_hop = [r for r in ranked if r['n_legs'] > 1]
        direct = [r for r in ranked if r['n_legs'] == 1]

        top_routes = []

        # always include best overall
        if ranked:
            top_routes.append(ranked[0])

        # include best multi-hop if available
        if multi_hop:
            top_routes.append(multi_hop[0])

        # fill remaining slots
        for r in ranked:
            if r not in top_routes:
                top_routes.append(r)
            if len(top_routes) >= top_k:
                break


        # Print results
        for i, r in enumerate(top_routes):
            print(f"\n  {'─' * 50}")
            print(f"  ROUTE #{i + 1}: {', '.join(r['labels'])}")
            print(f"  {'─' * 50}")
            print(f"  Path:         {r['path_str']}")
            print(f"  Route Type:   {r['route_type_used']}")
            print(f"  Legs:         {r['n_legs']}")
            print(f"  Distance:     {r['total_distance_nm']:,.0f} NM")
            print(f"  Fuel:         {r['total_fuel_t']:,.1f} tonnes")
            print(f"  Cost:         ${r['total_fuel_cost_usd']:,.0f}")
            print(f"  Voyage Time:  {r['total_voyage_days']:.1f} days")
            print(f"  Risk Score:   {r['avg_risk_score']:.4f}")
            print(f"  Overall Score: {r['score']:.4f} (lower = better)")

            if r['n_legs'] > 1:
                print(f"\n  Per-leg breakdown:")
                for j, leg in enumerate(r['legs']):
                    print(f"    Leg {j + 1}: {leg['origin']} → {leg['destination']} | "
                          f"{leg['distance_nm']:,.0f} NM | "
                          f"{leg['fuel_total_t']:,.1f}t fuel | "
                          f"{leg['voyage_days']:.1f} days | "
                          f"risk={leg['total_risk']:.3f}")

        return top_routes

    def get_available_ports(self) -> dict:
        """Return available origin and destination ports."""
        origins = set()
        destinations = set()
        for (o, d) in self.port_pairs:
            origins.add(o)
            destinations.add(d)
        return {
            'origins': sorted(origins),
            'destinations': sorted(destinations),
        }


def main():
    """Demo run of the route optimizer."""
    optimizer = RouteOptimizer()

    '''ports = optimizer.get_available_ports()
    print(f"\nAvailable origin ports: {ports['origins']}")
    print(f"Available destination ports: {ports['destinations']}")'''

    # Demo query
    routes = optimizer.find_best_routes(
        origin='Jebel Ali',
        destination='Guangzhou',
        ship_type='Tanker',
        top_k=3,
    )


if __name__ == '__main__':
    main()
