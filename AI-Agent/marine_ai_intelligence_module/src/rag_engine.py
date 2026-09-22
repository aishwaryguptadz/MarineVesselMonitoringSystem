from .config import IMO_FILE


def search_regulation(question):

    try:
        with open(IMO_FILE, "r", encoding="utf8") as f:
            text = f.read().lower()

        q = question.lower()

        # Sulphur regulation
        if "sulphur" in q or "sulfur" in q:
            return "IMO global sulphur cap is 0.5% under MARPOL Annex VI."

        # Carbon Intensity Indicator
        if "cii" in q or "carbon intensity" in q:
            return "CII (Carbon Intensity Indicator) measures the carbon efficiency of ships based on CO2 emissions per transport work."

        # Energy Efficiency Existing Ship Index
        if "eexi" in q:
            return "EEXI (Energy Efficiency Existing Ship Index) regulates the design energy efficiency of existing ships."

        # NOx emissions
        if "nox" in q or "nitrogen oxide" in q:
            return "IMO Tier III standards regulate nitrogen oxide (NOx) emissions from marine engines."

        # Ballast water regulations
        if "ballast" in q:
            return "IMO Ballast Water Management Convention prevents the spread of invasive aquatic species."

        # Generic fallback search
        for word in q.split():
            if word in text:
                return "Relevant regulation found in IMO MARPOL Annex VI. Please consult the regulation document."

        return "No specific IMO regulation found for this query."

    except Exception as e:
        return {"error": str(e)}