# Marine AI Copilot – Vessel Intelligence Module

The **Marine AI Copilot** is an AI-powered maritime analytics module designed to analyze ship operational data and provide intelligent insights about vessel performance.

The system can detect anomalies, analyze voyage conditions, identify root causes of operational issues, and generate a complete **ship intelligence report**.

This module is part of the **Smart Automation for Marine Vessel Operations** project.

---

# Key Features

The AI Copilot provides the following capabilities:

• Carbon emission analysis  
• Fuel consumption monitoring  
• Engine load analysis  
• Ship speed monitoring  
• Wind speed and wave height analysis  
• Sea temperature monitoring  
• Voyage condition detection  
• Operational anomaly detection  
• Root cause analysis  
• Correlation analysis between ship parameters  
• Multi-topic question understanding  
• Conversation memory for follow-up questions  

The system generates a **comprehensive vessel intelligence report** to help operators understand what is happening with the ship and why.

---

# System Architecture


User Question
↓
Question Router (Keyword + Multi-topic detection)
↓
Ship Data Analysis Engine
↓
Voyage Condition Analyzer
↓
Anomaly Detector
↓
Root Cause Analyzer
↓
Correlation Analyzer
↓
Explanation Generator
↓
AI Copilot Response


---

# Project Structure

```

marine\_ai\_intelligence\_module
│
├── data
│   └── master\_maritime\_dataset.csv
│
├── models
│   └── carbon\_emission\_model.pkl
│
├── src
│   ├── \_\_init\_\_.py
│   ├── config.py
│   ├── safe\_utils.py
│   ├── train\_carbon\_model.py
│   ├── carbon\_predictor.py
│   ├── router.py
│   ├── query\_engine.py
│   ├── anomaly\_detector.py
│   ├── voyage\_analyzer.py
│   ├── root\_cause\_analyzer.py
│   ├── correlation\_analyzer.py
│   ├── explanation\_engine.py
│   ├── memory\_manager.py
│   └── intelligence\_layer.py
│
├── requirements.txt
└── README.md

Installation

Install the required Python dependencies.

pip install -r requirements.txt
Training the Carbon Emission Model

Before using the system, train the emission prediction model.

Run:

python -m src.train_carbon_model

This will generate:

models/carbon_emission_model.pkl
Running the AI Copilot

Example usage:

from src.intelligence_layer import answer_question

response = answer_question("Why did fuel consumption increase during rough sea conditions?")
print(response)
Sample Output

Example system response:

{
  "question": "Why did fuel consumption increase during rough sea conditions?",

  "detected_topics": ["fuel", "weather"],

  "analysis": {
    "carbon_emission": 1240.6,
    "fuel_consumption": 56.3,
    "engine_load": 82.1,
    "ship_speed": 15.4,
    "wave_height": 2.2,
    "wind_speed": 17.3,
    "sea_temperature": 19.6
  },

  "voyage_condition": {
    "sea_state": "Moderate Sea",
    "wind_speed": 17.3
  },

  "anomalies": [
    "High engine load anomaly",
    "Rough sea condition"
  ],

  "root_causes": [
    "High engine load increased fuel usage",
    "Rough sea increased propulsion demand"
  ],

  "correlations": [
    "Fuel consumption strongly correlates with engine load",
    "Carbon emissions increase with fuel consumption"
  ],

  "report": "Ship Intelligence Report\n\nCarbon Emission: 1240 tonnes\nFuel Consumption: 56 tons/day\nEngine Load: 82%\nShip Speed: 15 knots\nWind Speed: 17 knots\nWave Height: 2.2 meters"
}
Integration with Backend API

Backend developers can integrate this module easily.

Example:

from marine_ai_intelligence_module.src.intelligence_layer import answer_question

response = answer_question(user_question)

The response can then be returned to the React dashboard or Android application.

Author

Akhand Pratap Singh
AI Intelligence Layer Developer
Marine Smart Automation Project