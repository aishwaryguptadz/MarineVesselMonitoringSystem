def safe_mean(series):
    try:
        return float(series.mean())
    except:
        return None