from neo4j import GraphDatabase

# Neo4j driver instance
neo4j_driver = None

def init_neo4j(uri, username, password):
    """Initialize Neo4j driver"""
    global neo4j_driver
    neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))
    return neo4j_driver

def get_neo4j_driver():
    """Get Neo4j driver instance"""
    return neo4j_driver

def close_neo4j():
    """Close Neo4j driver"""
    if neo4j_driver:
        neo4j_driver.close()
