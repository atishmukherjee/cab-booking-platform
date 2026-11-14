import os
from celery import Celery
from weasyprint import HTML

CELERY_REDIS_URL = "redis://localhost:6379/1"

celery_app = Celery(
    "cab_worker",
    broker=CELERY_REDIS_URL,
    backend=CELERY_REDIS_URL
)

@celery_app.task(name="generate_ride_invoice")
def generate_ride_invoice(ride_id: str, fare: float, distance_km: float):
    os.makedirs("invoices", exist_ok=True)
    file_path = f"invoices/receipt_{ride_id}.pdf"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 30px;">
        <h2 style="color: #1a73e8;">Cab Booking Platform - Trip Receipt</h2>
        <hr>
        <p><strong>Ride ID:</strong> {ride_id}</p>
        <p><strong>Distance Covered:</strong> {distance_km} km</p>
        <p><strong>Total Fare Paid:</strong> ₹{fare}</p>
        <p><strong>Status:</strong> PAID</p>
        <hr>
        <p style="font-size: 12px; color: gray;">Generated asynchronously via Celery + WeasyPrint</p>
    </body>
    </html>
    """
    HTML(string=html_content).write_pdf(file_path)
    return f"Invoice saved at {file_path}"
