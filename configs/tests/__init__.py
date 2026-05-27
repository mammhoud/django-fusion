"""
VResume Testing Suite
=====================

Comprehensive testing framework for VResume pages and endpoints.

Modules:
- runner: Main test execution engine
- data_populator: Unified data generation and population (test data + pages)
- requests.http: HTTP request definitions for REST Client
- test_pages.sh: Shell-based page testing script

Quick Start:
    # Populate all data
    python -m tests.data_populator
    
    # Run tests
    python -m tests.runner
    
    # Or use Makefile
    make populate-data
    make test
"""

__version__ = "2.0.0"
__author__ = "VResume Team"
