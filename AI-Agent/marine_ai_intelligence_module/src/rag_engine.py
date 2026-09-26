def search_regulation(question: str) -> str:
    q = question.lower()
    
    # Direct statutory mapping for standard MARPOL / IMO inquiries
    if "annex i" in q or "oil tanker" in q or "discharge" in q:
        return (
            "MARPOL Annex I Regulation 34: Prohibits oily discharge into the sea except when the tanker is en route, "
            "located >50 NM from land, instantaneous rate of discharge of oil does not exceed 30 L/NM, total oil "
            "discharged does not exceed 1/30,000 of total cargo, and vessel is operating an approved ODME system."
        )
    if "carbon intensity" in q or "cii" in q:
        return "CII (Carbon Intensity Indicator) measures operational carbon efficiency (A through E ratings) per transport work (gCO2/dwt-nm)."
    if "sulphur" in q or "sulfur" in q:
        if "eca" in q:
            return "Under MARPOL Annex VI Reg 14, fuel sulfur content inside Emission Control Areas (ECAs) cannot exceed 0.10% m/m."
        return "IMO global sulphur cap is 0.50% m/m under MARPOL Annex VI Regulation 14 for ships operating outside ECAs."
    if "nox" in q or "tier iii" in q:
        return "IMO Tier III standards require an 80% NOx reduction compared to Tier I when operating in NOx Emission Control Areas (NECAs)."
    if "eexi" in q:
        return "EEXI (Energy Efficiency Existing Ship Index) mandates technical carbon design efficiency thresholds verified via technical files or EPL."
    if "ballast" in q:
        return "IMO Ballast Water Management Convention (D-2 Standard) mandates type-approved BWMS treatment before discharge."

    return "Relevant maritime standard found under IMO MARPOL regulations. Consult the technical statutory documentation."