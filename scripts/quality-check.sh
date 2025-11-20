#!/bin/bash
# Code Quality Check Script
# T168-T173: Run all code quality checks

set -e

echo "========================================="
echo "Running Backend Code Quality Checks"
echo "========================================="

cd backend

echo ""
echo "1. Running flake8 linting..."
flake8 app/ tests/ || echo "⚠️  Flake8 found issues"

echo ""
echo "2. Running mypy type checking..."
mypy app/ || echo "⚠️  MyPy found type errors"

echo ""
echo "3. Running pytest with coverage..."
pytest --cov=app --cov-report=term-missing --cov-report=html tests/ || echo "⚠️  Tests failed"

echo ""
echo "========================================="
echo "Running Frontend Code Quality Checks"
echo "========================================="

cd ../frontend

echo ""
echo "1. Running ESLint..."
npm run lint || echo "⚠️  ESLint found issues"

echo ""
echo "2. Running Prettier check..."
npm run format:check || echo "⚠️  Prettier found formatting issues"

echo ""
echo "3. Running Vitest with coverage..."
npm run test:coverage || echo "⚠️  Tests failed"

echo ""
echo "========================================="
echo "Code Quality Check Complete!"
echo "========================================="
echo "Check coverage reports:"
echo "  Backend:  backend/htmlcov/index.html"
echo "  Frontend: frontend/coverage/index.html"
