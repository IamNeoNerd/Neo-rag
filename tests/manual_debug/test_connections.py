"""Test script for Neo4j and Neon connections"""
import os
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

print("=" * 50)
print("Testing Database Connections")
print("=" * 50)

# Test Neo4j
print("\n1. Testing Neo4j Connection...")
print(f"   URI: {os.getenv('NEO4J_URI')}")

try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    driver.verify_connectivity()
    print("   ✓ Neo4j connected successfully!")
    
    # Test a simple query
    with driver.session() as session:
        result = session.run("RETURN 1 as num")
        record = result.single()
        print(f"   ✓ Query test passed: {record['num']}")
    
    driver.close()
except Exception as e:
    print(f"   ✗ Neo4j connection failed: {e}")

# Test Neon
print("\n2. Testing Neon PostgreSQL Connection...")
print(f"   URL: {os.getenv('NEON_DATABASE_URL')[:60]}...")

try:
    import psycopg2
    conn = psycopg2.connect(os.getenv('NEON_DATABASE_URL'))
    print("   ✓ Neon connected successfully!")
    
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"   ✓ PostgreSQL: {version[:50]}...")
    
    conn.close()
except Exception as e:
    print(f"   ✗ Neon connection failed: {e}")

print("\n" + "=" * 50)
print("Connection tests complete!")
print("=" * 50)
