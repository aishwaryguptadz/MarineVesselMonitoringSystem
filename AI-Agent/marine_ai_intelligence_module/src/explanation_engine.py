def generate_report(data, causes, anomalies):

    report = "Ship Intelligence Report\n\n"

    report += "Operational Metrics:\n"

    for k,v in data.items():
        report += f"{k}: {v}\n"

    report += "\nDetected Anomalies:\n"

    for a in anomalies:
        report += f"- {a}\n"

    report += "\nPossible Root Causes:\n"

    for c in causes:
        report += f"- {c}\n"

    return report