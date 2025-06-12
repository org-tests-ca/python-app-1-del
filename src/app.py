from flask import Flask, jsonify
import time
import os
import socket

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Configura o tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Exporta via OTLP (Tempo deve aceitar HTTP OTLP na porta 4318)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://tempo-distributor.grafana.svc.cluster.local:4318/v1/traces",
    insecure=True
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Inicializa app Flask com instrumentação
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/api/v1/info")
def info():
    return jsonify({
        "message": "LGTM Stack com Tracing OpenTelemetry!",
        "hostname": socket.gethostname(),
        "time": time.strftime("%H:%M:%S")
    })

@app.route("/api/v1/error")
def error():
    raise Exception("Erro proposital para testes de tracing")

@app.route('/api/v1/healthz')
def health():
    app.logger.info("Health check passed.")
    return jsonify({'status': 'up'}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
