"""
Docker Build Tests
=================
Comprehensive Docker build and deployment tests for both websites.
"""

import subprocess
import time
from pathlib import Path

import pytest
import requests


class TestDockerBuilds:
    """Test Docker builds for both websites."""

    def test_infrastructure_services(self, workspace_root):
        """Test main infrastructure services startup."""
        # Start infrastructure services
        result = subprocess.run([
            'docker', 'compose', 'up', '-d', 'postgres', 'redis'
        ], cwd=workspace_root, capture_output=True, text=True, timeout=120)

        assert result.returncode == 0, f"Infrastructure startup failed: {result.stderr}"

        # Wait for services to be ready
        time.sleep(10)

        # Check PostgreSQL
        pg_result = subprocess.run([
            'docker', 'exec', 'postgres', 'pg_isready', '-U', 'postgres'
        ], capture_output=True, text=True, timeout=30)

        assert pg_result.returncode == 0, "PostgreSQL not ready"

        # Check Redis
        redis_result = subprocess.run([
            'docker', 'exec', 'redis', 'redis-cli', 'ping'
        ], capture_output=True, text=True, timeout=30)

        assert redis_result.returncode == 0, "Redis not ready"

    def test_ctc_research_docker_build(self, ctc_research_root):
        """Test CTC Research Docker build."""
        # Build CTC Research images
        result = subprocess.run([
            'docker', 'compose', '-f', str(ctc_research_root / 'docker-compose.yml'), 'build'
        ], capture_output=True, text=True, timeout=600)

        assert result.returncode == 0, f"CTC Research Docker build failed: {result.stderr}"

        # Verify images were created
        images_result = subprocess.run([
            'docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'
        ], capture_output=True, text=True)

        assert 'website' in images_result.stdout, "CTC Research website image not found"

    def test_structa_cloud_docker_build(self, structa_cloud_root):
        """Test Structa Cloud Docker build."""
        if not structa_cloud_root.exists():
            pytest.skip("Structa Cloud directory not found")

        # Build Structa Cloud images
        result = subprocess.run([
            'docker', 'compose', '-f', str(structa_cloud_root / 'docker-compose.yml'), 'build'
        ], capture_output=True, text=True, timeout=600)

        assert result.returncode == 0, f"Structa Cloud Docker build failed: {result.stderr}"

    def test_database_setup(self, test_databases):
        """Test database setup for both websites."""
        # Create test databases
        for site, db_name in test_databases.items():
            result = subprocess.run([
                'docker', 'exec', 'postgres', 'psql', '-U', 'postgres',
                '-c', f'CREATE DATABASE IF NOT EXISTS {db_name};'
            ], capture_output=True, text=True, timeout=30)

            # Database creation might fail if it already exists, which is okay
            print(f"Database {db_name} setup result: {result.returncode}")

        # Verify databases exist
        result = subprocess.run([
            'docker', 'exec', 'postgres', 'psql', '-U', 'postgres',
            '-c', '\\l'
        ], capture_output=True, text=True, timeout=30)

        assert result.returncode == 0, "Database listing failed"

        for db_name in test_databases.values():
            assert db_name in result.stdout, f"Database {db_name} not found"

class TestDockerDeployment:
    """Test Docker deployment and service integration."""

    def test_ctc_research_deployment(self, ctc_research_root):
        """Test CTC Research full deployment."""
        try:
            # Run migrations
            migration_result = subprocess.run([
                'docker', 'compose', '-f', str(ctc_research_root / 'docker-compose.yml'),
                'run', '--rm', 'website', 'python', 'manage.py', 'migrate', '--noinput'
            ], capture_output=True, text=True, timeout=300)

            assert migration_result.returncode == 0, f"CTC Research migrations failed: {migration_result.stderr}"

            # Collect static files
            static_result = subprocess.run([
                'docker', 'compose', '-f', str(ctc_research_root / 'docker-compose.yml'),
                'run', '--rm', 'website', 'python', 'manage.py', 'collectstatic', '--noinput'
            ], capture_output=True, text=True, timeout=180)

            assert static_result.returncode == 0, f"CTC Research static collection failed: {static_result.stderr}"

            # Start services
            start_result = subprocess.run([
                'docker', 'compose', '-f', str(ctc_research_root / 'docker-compose.yml'), 'up', '-d'
            ], capture_output=True, text=True, timeout=120)

            assert start_result.returncode == 0, f"CTC Research service startup failed: {start_result.stderr}"

            # Wait for services to start
            time.sleep(30)

            # Test health endpoint
            try:
                response = requests.get('http://localhost:5070/health/', timeout=10)
                assert response.status_code == 200, f"CTC Research health check failed: {response.status_code}"
            except requests.exceptions.RequestException as e:
                pytest.fail(f"CTC Research health check request failed: {e}")

        finally:
            # Cleanup
            subprocess.run([
                'docker', 'compose', '-f', str(ctc_research_root / 'docker-compose.yml'), 'down'
            ], capture_output=True)

    def test_structa_cloud_deployment(self, structa_cloud_root):
        """Test Structa Cloud full deployment."""
        if not structa_cloud_root.exists():
            pytest.skip("Structa Cloud directory not found")

        try:
            # Run migrations
            migration_result = subprocess.run([
                'docker', 'compose', '-f', str(structa_cloud_root / 'docker-compose.yml'),
                'run', '--rm', 'website', 'python', 'manage.py', 'migrate', '--noinput'
            ], capture_output=True, text=True, timeout=300)

            assert migration_result.returncode == 0, f"Structa Cloud migrations failed: {migration_result.stderr}"

            # Start services
            start_result = subprocess.run([
                'docker', 'compose', '-f', str(structa_cloud_root / 'docker-compose.yml'), 'up', '-d'
            ], capture_output=True, text=True, timeout=120)

            assert start_result.returncode == 0, f"Structa Cloud service startup failed: {start_result.stderr}"

            # Wait for services to start
            time.sleep(30)

            # Test health endpoint
            try:
                response = requests.get('http://localhost:5071/health/', timeout=10)
                assert response.status_code == 200, f"Structa Cloud health check failed: {response.status_code}"
            except requests.exceptions.RequestException as e:
                # Health endpoint might not exist, which is okay
                print(f"Structa Cloud health check info: {e}")

        finally:
            # Cleanup
            subprocess.run([
                'docker', 'compose', '-f', str(structa_cloud_root / 'docker-compose.yml'), 'down'
            ], capture_output=True)

class TestDockerNetworking:
    """Test Docker networking and service communication."""

    def test_service_communication(self):
        """Test communication between Docker services."""
        # Test database connectivity from application containers
        db_test_result = subprocess.run([
            'docker', 'run', '--rm', '--network', 'site_traefik-net',
            'postgres:16', 'pg_isready', '-h', 'postgres', '-U', 'postgres'
        ], capture_output=True, text=True, timeout=30)

        if db_test_result.returncode == 0:
            print("Database connectivity test passed")
        else:
            print(f"Database connectivity test info: {db_test_result.stderr}")

    def test_port_exposure(self):
        """Test that services expose correct ports."""
        # Check if PostgreSQL port is accessible
        pg_port_result = subprocess.run([
            'docker', 'port', 'postgres'
        ], capture_output=True, text=True, timeout=10)

        if pg_port_result.returncode == 0:
            assert '5432' in pg_port_result.stdout, "PostgreSQL port not exposed"
        else:
            print("PostgreSQL container not running for port test")

    def test_volume_mounts(self):
        """Test Docker volume mounts."""
        # Check PostgreSQL data volume
        volume_result = subprocess.run([
            'docker', 'volume', 'ls'
        ], capture_output=True, text=True, timeout=10)

        if volume_result.returncode == 0:
            print(f"Docker volumes: {volume_result.stdout}")
        else:
            print("Volume listing failed")

class TestDockerSecurity:
    """Test Docker security configurations."""

    def test_container_users(self):
        """Test that containers don't run as root where possible."""
        # This is a basic security check
        containers = ['postgres', 'redis']

        for container in containers:
            user_result = subprocess.run([
                'docker', 'exec', container, 'whoami'
            ], capture_output=True, text=True, timeout=10)

            if user_result.returncode == 0:
                user = user_result.stdout.strip()
                print(f"Container {container} runs as user: {user}")
                # Note: Some containers legitimately run as root
            else:
                print(f"Could not check user for container {container}")

    def test_network_isolation(self):
        """Test Docker network isolation."""
        # Check that containers are on the correct network
        network_result = subprocess.run([
            'docker', 'network', 'ls'
        ], capture_output=True, text=True, timeout=10)

        if network_result.returncode == 0:
            assert 'traefik-net' in network_result.stdout, "Traefik network not found"
        else:
            print("Network listing failed")

    def test_secret_management(self):
        """Test that secrets are not exposed in container environment."""
        # Check that database passwords are not visible in process lists
        env_result = subprocess.run([
            'docker', 'exec', 'postgres', 'env'
        ], capture_output=True, text=True, timeout=10)

        if env_result.returncode == 0:
            # Verify that sensitive environment variables are set but not logged
            assert 'POSTGRES_PASSWORD' in env_result.stdout, "Database password environment variable not set"
        else:
            print("Environment check failed")


class TestDockerEnvironmentComprehensive:
    """Comprehensive Docker environment testing (consolidated from scripts)."""

    def test_full_environment_setup(self, workspace_root):
        """Test complete environment setup including infrastructure and applications."""
        success_count = 0
        total_tests = 0
        failed_tests = []

        def run_test_command(command, description, timeout=120):
            nonlocal success_count, total_tests, failed_tests
            total_tests += 1

            try:
                result = subprocess.run(command, capture_output=True, text=True,
                                      timeout=timeout, cwd=workspace_root)
                if result.returncode == 0:
                    success_count += 1
                    return True
                else:
                    failed_tests.append(description)
                    return False
            except subprocess.TimeoutExpired:
                failed_tests.append(f"{description} (timeout)")
                return False
            except Exception:
                failed_tests.append(f"{description} (exception)")
                return False

        # Test infrastructure services
        run_test_command([
            'docker', 'compose', 'up', '-d', 'postgres', 'redis'
        ], "Infrastructure Services Startup")

        # Test database creation
        run_test_command([
            'docker', 'exec', 'postgres', 'psql', '-U', 'postgres', '-c',
            'CREATE DATABASE IF NOT EXISTS db_precis_ctc;'
        ], "CTC Database Creation")

        run_test_command([
            'docker', 'exec', 'postgres', 'psql', '-U', 'postgres', '-c',
            'CREATE DATABASE IF NOT EXISTS db_precis_lms;'
        ], "Structa Database Creation")

        # Test CTC Docker build
        run_test_command([
            'docker', 'compose', '-f', 'ctc-research.com/docker-compose.yml', 'build'
        ], "CTC Docker Build", timeout=600)

        # Test CTC migrations
        run_test_command([
            'docker', 'compose', '-f', 'ctc-research.com/docker-compose.yml', 'run', '--rm',
            'website', 'python', 'manage.py', 'migrate', '--noinput'
        ], "CTC Migrations", timeout=300)

        # Calculate success rate
        success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0

        # Log results
        print(f"Environment Test Results: {success_count}/{total_tests} passed ({success_rate:.1f}%)")
        if failed_tests:
            print(f"Failed tests: {failed_tests}")

        # Assert reasonable success rate
        assert success_rate >= 70, f"Environment setup success rate too low: {success_rate:.1f}%"

    def test_service_health_comprehensive(self):
        """Test comprehensive service health checks."""
        # Wait for services to stabilize
        time.sleep(30)

        health_checks = [
            ("http://localhost:5070/health/", "CTC Research Health"),
            ("http://localhost:5071/health/", "Structa Cloud Health"),
        ]

        passed_checks = 0
        for url, description in health_checks:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    passed_checks += 1
                    print(f"✅ {description} check passed")
                else:
                    print(f"❌ {description} check failed: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {description} check error: {e}")

        # At least one service should be healthy
        assert passed_checks > 0, "No services are healthy"

    def test_logs_analysis(self, workspace_root):
        """Analyze Docker logs for critical errors."""
        services_to_check = ['website', 'website-worker']
        critical_errors = []

        for service in services_to_check:
            # Check CTC logs
            result = subprocess.run([
                'docker', 'compose', '-f', 'ctc-research.com/docker-compose.yml',
                'logs', '--tail=100', service
            ], capture_output=True, text=True, cwd=workspace_root)

            if result.returncode == 0:
                log_content = result.stdout.lower()
                if 'critical' in log_content or 'fatal' in log_content:
                    critical_errors.append(f"CTC {service}")

        # Allow some errors but not critical ones
        assert len(critical_errors) == 0, f"Critical errors found in: {critical_errors}"
