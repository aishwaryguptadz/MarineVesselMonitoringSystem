from .router import detect_intent
from .query_engine import analyze_dataset
from .prediction_engine import predict_trends
from .maintenance_engine import maintenance_advice
from .navigation_engine import optimal_route
from .operational_engine import recommended_speed
from .rag_engine import search_regulation

from .anomaly_detector import detect_anomalies
from .root_cause_analyzer import analyze_root_cause
from .explanation_engine import generate_report

from .semantic_engine import detect_metric


def answer_question(question):

    try:

        intent = detect_intent(question)

        if intent == "prediction":

            predictions = predict_trends()

            metric = detect_metric(question)

            result = predictions.get(metric)

            if not result:
                return {"message":"Prediction unavailable"}

            answer = (
                f"Yes, {metric.replace('_',' ')} is likely to increase."
                if result["trend"]=="increase"
                else f"No, {metric.replace('_',' ')} is likely to decrease."
            )

            return {
                "intent":"prediction",
                "metric":metric,
                "current_average":result["current_average"],
                "predicted_value":result["predicted_value"],
                "trend":result["trend"],
                "answer":answer
            }

        if intent=="maintenance":
            return {"intent":"maintenance","maintenance_advice":maintenance_advice()}

        if intent=="navigation":
            return {"intent":"navigation","route_recommendation":optimal_route()}

        if intent=="operation":
            return {"intent":"operation","recommended_speed":recommended_speed()}

        if intent=="knowledge":
            return {"intent":"knowledge","imo_regulation":search_regulation(question)}

        data = analyze_dataset()
        anomalies = detect_anomalies()
        causes = analyze_root_cause()

        report = generate_report(data,causes,anomalies)

        return {
            "intent":"analysis",
            "analysis":data,
            "anomalies":anomalies,
            "root_causes":causes,
            "report":report
        }

    except Exception as e:

        return {
            "error":"AI processing failed",
            "details":str(e)
        }