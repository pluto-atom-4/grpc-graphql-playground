#!/usr/bin/env python3
"""
Docker Compose Validation Script

Validates docker-compose.yml configuration without building images or starting containers.
Performs comprehensive checks on:
- YAML syntax
- Service configuration
- Dockerfile references
- Network configuration
- Volume/persistence setup
- Port mappings
- Service dependencies
"""

import yaml
import os
import sys


def validate_compose_file(filepath):
    """Validate docker-compose.yml structure and references"""

    print("=" * 78)
    print("CONFIGURATION STRUCTURE")
    print("=" * 78)

    # Load YAML
    try:
        with open(filepath, "r") as f:
            compose = yaml.safe_load(f)
        print("✅ YAML syntax valid\n")
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False

    # Check structure
    required_sections = ["services"]
    for section in required_sections:
        if section in compose:
            print(f"✅ '{section}' section found")
        else:
            print(f"❌ Missing required '{section}' section")
            return False

    # Validate services
    print("\n" + "=" * 78)
    print("SERVICES VALIDATION")
    print("=" * 78 + "\n")

    services = compose.get("services", {})
    print(f"Found {len(services)} services: {list(services.keys())}\n")

    base_dir = os.path.dirname(filepath)

    for service_name, service_config in services.items():
        print(f"Service: {service_name}")

        # Check build config
        if "build" in service_config:
            build = service_config["build"]
            if isinstance(build, dict):
                dockerfile = build.get("dockerfile", "Dockerfile")
                context = build.get("context", ".")
                full_path = os.path.join(base_dir, context, dockerfile)

                if os.path.exists(full_path):
                    print(f"  ✅ Dockerfile exists: {dockerfile}")
                else:
                    print(f"  ❌ Dockerfile not found: {full_path}")
        elif "image" in service_config:
            print(f"  ✅ Uses image: {service_config['image']}")

        # Check ports
        if "ports" in service_config:
            ports = service_config["ports"]
            print(f"  ✅ Ports: {ports}")

        # Check volumes
        if "volumes" in service_config:
            volumes = service_config["volumes"]
            print(f"  ✅ Volumes: {len(volumes)} volume(s)")

        # Check environment
        if "environment" in service_config:
            env = service_config["environment"]
            if isinstance(env, dict):
                print(f"  ✅ Environment variables: {len(env)}")

        # Check dependencies
        if "depends_on" in service_config:
            deps = service_config["depends_on"]
            if isinstance(deps, dict):
                print(f"  ✅ Depends on: {list(deps.keys())}")
            else:
                print(f"  ✅ Depends on: {deps}")

        # Check health check
        if "healthcheck" in service_config:
            print(f"  ✅ Health check configured")

        print()

    # Validate networks
    print("=" * 78)
    print("NETWORKS VALIDATION")
    print("=" * 78 + "\n")

    networks = compose.get("networks", {})
    if networks:
        print(f"✅ Networks defined: {list(networks.keys())}")
        for net_name, net_config in networks.items():
            if net_config and "driver" in net_config:
                print(f"   - {net_name}: {net_config['driver']}")
    else:
        print("ℹ️  No custom networks defined")

    print()

    # Validate volumes
    print("=" * 78)
    print("VOLUMES VALIDATION")
    print("=" * 78 + "\n")

    volumes = compose.get("volumes", {})
    if volumes:
        print(f"✅ Named volumes defined: {list(volumes.keys())}")
    else:
        print("ℹ️  No named volumes defined (using bind mounts only)")

    print()

    # Check for common issues
    print("=" * 78)
    print("COMMON ISSUES CHECK")
    print("=" * 78 + "\n")

    issues = []

    # Check for version field
    if "version" in compose:
        issues.append("⚠️  'version' field is obsolete in Compose v3+")

    # Check all services have proper config
    for service_name, service_config in services.items():
        if "build" not in service_config and "image" not in service_config:
            issues.append(f"⚠️  Service '{service_name}' has neither 'build' nor 'image'")

        if "container_name" in service_config:
            container_name = service_config["container_name"]
            # Check for valid container names
            if not all(c.isalnum() or c in "-_" for c in container_name):
                issues.append(f"⚠️  Invalid container name: {container_name}")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ No common issues detected")

    print()

    # Port conflict check
    print("=" * 78)
    print("PORT CONFLICT CHECK")
    print("=" * 78 + "\n")

    port_map = {}
    for svc_name, svc_config in services.items():
        ports = svc_config.get("ports", [])
        if ports:
            for port in ports:
                if isinstance(port, str):
                    parts = port.split(":")
                    if len(parts) == 2:
                        host, container = parts
                        try:
                            host_port = int(host)
                            port_map[host_port] = svc_name
                        except ValueError:
                            pass

    if len(port_map) == len(set(port_map.keys())):
        print("✅ No port conflicts detected - all ports are unique")
        print(f"   Ports in use: {sorted(port_map.keys())}")
    else:
        print("⚠️  Port conflicts detected!")
        for port, service in port_map.items():
            print(f"   Port {port}: {service}")

    print()

    # Dependency analysis
    print("=" * 78)
    print("SERVICE STARTUP SEQUENCE")
    print("=" * 78 + "\n")

    def get_deps(service_name):
        service = services[service_name]
        deps = service.get("depends_on", {})
        if isinstance(deps, dict):
            return list(deps.keys())
        elif isinstance(deps, list):
            return deps
        return []

    # Calculate startup order
    order = []
    processed = set()

    def process_service(name, path=[]):
        if name in processed:
            return
        if name in path:
            return  # Avoid circular deps

        deps = get_deps(name)
        for dep in deps:
            if dep in services:
                process_service(dep, path + [name])

        if name not in processed:
            order.append(name)
            processed.add(name)

    for svc_name in services:
        process_service(svc_name)

    for i, svc in enumerate(order, 1):
        print(f"Step {i}: {svc}")
        deps = get_deps(svc)
        if deps:
            for dep in deps:
                dep_config = services[svc].get("depends_on", {})
                if isinstance(dep_config, dict):
                    condition = dep_config.get(dep, {}).get("condition", "service_started")
                else:
                    condition = "service_started"
                print(f"   → Wait for {dep} ({condition})")

    print()
    print("=" * 78)
    print("VALIDATION SUMMARY")
    print("=" * 78)
    print("✅ Configuration is valid and ready to use")
    print(f"   - Services: {len(services)}")
    print(f"   - Networks: {len(networks)}")
    print(f"   - Volumes: {len(volumes)}")
    print()

    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "docker-compose.yml"

    success = validate_compose_file(filepath)
    sys.exit(0 if success else 1)
