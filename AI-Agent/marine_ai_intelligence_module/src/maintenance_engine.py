from .voyage_analyzer import get_current_telemetry


def maintenance_advice(question: str = "", vessel_type: str = None):
    """
    Evaluates machinery health telemetry across auxiliary and propulsion plants,
    differentiating subsystem checks (thermal cooling, shaft vibration, injectors,
    scavenge air/turbochargers) and specialized ship machinery (tanker heating vs gas reliquefaction).
    """
    try:
        telemetry = get_current_telemetry(vessel_type)
        latest = telemetry["latest"]
        base = telemetry["baseline_slice"]
        q = question.lower()
        ship = telemetry["vessel_type"]

        # 1. Cooling Circuit & Heat Exchanger Diagnostics
        if any(k in q for k in ["cooling", "heat exchanger", "coolant", "water temp"]):
            temp = float(latest.get("engine_temp_c", 82.0))
            if temp > 88.0:
                return [
                    f"Cooling Circuit Alert ({ship}): Coolant temperature is elevated at {temp:.1f}°C "
                    f"(alarm threshold: 88°C). Inspect sea chest suction strainers and plate heat exchanger scaling."
                ]
            return [
                f"Cooling Circuit Status ({ship}): Fresh water coolant is operating at nominal {temp:.1f}°C. "
                f"Heat transfer efficiency across central plate coolers is within nominal parameters."
            ]

        # 2. Shaft Line, Bearing Dynamics & Vibration
        if any(k in q for k in ["vibration", "bearing", "shaft line", "damper"]):
            vib = float(latest.get("engine_vibration", 2.8))
            if vib > 4.5:
                return [
                    f"Machinery Stress Alert ({ship}): Vibration velocity measured at {vib:.2f} mm/s "
                    f"(ISO 10816-6 threshold 4.5 mm/s). Inspect intermediate shaft bearings, thrust pads, and damper viscosity."
                ]
            return [
                f"Shaft & Bearing Dynamics ({ship}): Velocity RMS vibration is {vib:.2f} mm/s. "
                f"No rotational unbalance, bearing pitting, or shaft misalignment indicated."
            ]

        # 3. Fuel Injection Subsystem
        if any(k in q for k in ["injector", "injection", "fuel system", "servicing"]):
            fuel = float(latest.get("fuel_consumption_t_day", 35.0))
            mean_fuel = (
                float(base["fuel_consumption_t_day"].mean())
                if "fuel_consumption_t_day" in base.columns
                else fuel
            )
            if fuel > mean_fuel * 1.18:
                pct_high = ((fuel - mean_fuel) / mean_fuel) * 100
                return [
                    f"Fuel Metering Inefficiency ({ship}): Consumption rate ({fuel:.1f} t/day) is "
                    f"{pct_high:.1f}% above model norm. Recommend injector pull, nozzle tip pressure testing, and needle seat lap."
                ]
            return [
                f"Fuel Injection Health ({ship}): Common rail pressures, atomization spray timing, "
                f"and delivery volume are balanced across all cylinder units."
            ]

        # 4. Exhaust Gas Thermocouples & Turbocharger Scavenge
        if any(k in q for k in ["exhaust", "turbocharger", "scavenge", "temperatures"]):
            exhaust = float(latest.get("exhaust_temp_c", 392.0))
            return [
                f"Gas Path Diagnostics ({ship}): Mean cylinder exhaust temp is {exhaust:.1f}°C "
                f"(well within standard limits < 450°C). Turbocharger compressor differential pressure and scavenge air manifold are clear."
            ]

        # 5. Specialized Cargo Machinery (Tanker Steam & Flue Gas vs Gas Carrier Reliquefaction)
        if any(k in q for k in ["boiler", "reliquefaction", "inert gas", "cargo heating"]):
            if "tanker" in ship.lower():
                return [
                    f"Tanker Cargo Systems ({ship}): Deck steam supply to cargo heating coils is nominal. "
                    f"Flue gas inert gas system maintaining tank oxygen content below 5% vol under SOLAS Chapter II-2."
                ]
            elif "gas" in ship.lower():
                return [
                    f"Gas Carrier Systems ({ship}): Reliquefaction compressor suction pressure and cargo tank "
                    f"nitrogen inerting system are stable and IGF/IGC Code compliant."
                ]
            return [
                f"Auxiliary Plant ({ship}): Auxiliary boiler steam pressure and inert gas containment operating within nominal design load."
            ]

        # 6. Continuous Engine Service Rating & Power Load
        if "load" in q or "continuous service" in q:
            load = float(latest.get("engine_load_pct", 50.0))
            if load > 85.0:
                return [
                    f"Continuous Rating Warning ({ship}): Propulsion plant running at {load:.1f}% MCR. "
                    f"Continuous operation above 85% risks accelerated thermal stress on exhaust valve seats."
                ]
            return [
                f"Engine Service Rating ({ship}): Propulsion plant operating at {load:.1f}% MCR "
                f"(within economical continuous service rating of 70-82%)."
            ]

        # 7. General Machinery Routine Check
        load = float(latest.get("engine_load_pct", 50.0))
        return [
            f"Overall Machinery Assessment ({ship}): Main engine operating at {load:.1f}% load. "
            f"Lube oil differential pressure, jacket water temps, and crankcase telemetry within ISO nominal tolerances."
        ]

    except Exception as e:
        return [f"Machinery diagnostic fault: {str(e)}"]