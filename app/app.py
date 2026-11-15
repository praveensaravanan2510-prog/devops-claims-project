import re
from datetime import datetime, timezone

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

app = Flask(__name__)

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
)


# Count every request (used later by Prometheus/Grafana)
@app.after_request
def count_requests(response):
    route = request.url_rule.rule if request.url_rule else "unmatched"
    HTTP_REQUESTS.labels(request.method, route, response.status_code).inc()
    return response


# Used by Kubernetes liveness/readiness probes
@app.get("/health")
def health():
    return jsonify(status="ok")


# Sample business endpoint: claim ID + state ID -> generated file info
@app.get("/claims/<state_id>/<claim_id>")
def get_claim(state_id, claim_id):
    if not re.fullmatch(r"[A-Za-z]{2}", state_id) or not re.fullmatch(r"\d+", claim_id):
        return (
            jsonify(error="state_id must be 2 letters and claim_id must be numeric"),
            400,
        )

    state = state_id.upper()
    return jsonify(
        claimId=claim_id,
        stateId=state,
        status="PROCESSED",
        generatedFile=f"claim_{state}_{claim_id}.edi",
        generatedAt=datetime.now(timezone.utc).isoformat(),
    )


# Prometheus scrapes this endpoint
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
