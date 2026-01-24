#!/bin/bash

# Quick start script for Keycloak authentication testing

set -e

echo "========================================="
echo "Farm Connect - Keycloak Quick Start"
echo "========================================="
echo ""

# Check if Keycloak is running
echo "1. Checking Keycloak status..."
if ! curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "❌ Keycloak is not running!"
    echo ""
    echo "Starting Keycloak with Docker Compose..."
    docker-compose up -d keycloak
    echo "⏳ Waiting for Keycloak to start (60 seconds)..."
    sleep 60
else
    echo "✅ Keycloak is running"
fi

echo ""
echo "2. Testing authentication endpoints..."
echo ""

# Test auth info
echo "📍 Testing /api/v1/auth/info..."
curl -s http://localhost:8000/api/v1/auth/info | python3 -m json.tool || echo "❌ Failed"

echo ""
echo "📍 Testing /api/v1/auth/health..."
curl -s http://localhost:8000/api/v1/auth/health | python3 -m json.tool || echo "❌ Failed"

echo ""
echo "========================================="
echo "✅ Quick start complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Import keycloak_import.json into Keycloak (see KEYCLOAK_SETUP.md)"
echo "2. Create test users in Keycloak"
echo "3. Get a token and test protected endpoints"
echo ""
echo "Useful URLs:"
echo "- Keycloak Admin: http://localhost:8080 (admin/admin)"
echo "- API Docs: http://127.0.0.1:8000/docs"
echo "- Auth Info: http://localhost:8000/api/v1/auth/info"
echo ""
