# Cab Booking Platform - Backend Architecture

A scalable, distributed backend engine for an on-demand ride-hailing system built with FastAPI, PostgreSQL + PostGIS, Redis, and Socket.IO.

## Features
- PostGIS spatial indexing & ST_DWithin nearby driver discovery
- Asynchronous REST APIs with FastAPI & SQLModel
- Real-time driver location streaming via Socket.IO & Redis Pub/Sub
- Schema versioning with Alembic

## Tech Stack
- Python, FastAPI, PostgreSQL, PostGIS, Redis, Socket.IO, Ubuntu (WSL 2)
