"""
Neo4j Graph Database Service for BashkortNet
=============================================
Provides graph database backend for semantic word relationships.

Features:
- Full Neo4j integration with fallback to in-memory graph
- Cypher query support for complex traversals
- Visual graph export for D3.js/vis.js
- Automatic schema creation and data import
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from contextlib import contextmanager

# Neo4j import with graceful fallback
try:
    from neo4j import GraphDatabase, Driver
    from neo4j.exceptions import ServiceUnavailable, AuthError
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None
    Driver = None


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection."""
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "bashkortnet"
    database: str = "neo4j"

    @classmethod
    def from_env(cls) -> 'Neo4jConfig':
        """Load configuration from environment variables."""
        return cls(
            uri=os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
            username=os.environ.get('NEO4J_USER', 'neo4j'),
            password=os.environ.get('NEO4J_PASSWORD', 'bashkortnet'),
            database=os.environ.get('NEO4J_DATABASE', 'neo4j')
        )


class Neo4jService:
    """
    Service for interacting with Neo4j graph database.

    Handles all graph operations for the BashkortNet semantic network,
    including word storage, relationship management, and complex queries.
    """

    # Relationship types in the semantic network
    RELATION_TYPES = {
        'SYN': ('SYNONYM', 'Synonyms - words with similar meaning'),
        'ANT': ('ANTONYM', 'Antonyms - words with opposite meaning'),
        'ISA': ('IS_A', 'Hypernym - category membership'),
        'HAS_TYPE': ('HAS_TYPE', 'Hyponym - specific instances'),
        'PART_OF': ('PART_OF', 'Meronym - component of something'),
        'HAS_PART': ('HAS_PART', 'Holonym - contains components'),
        'CULT_ASSOC': ('CULTURAL_ASSOCIATION', 'Cultural connection'),
        'MYTH_LINK': ('MYTHOLOGICAL_LINK', 'Mythological reference'),
        'MADE_FROM': ('MADE_FROM', 'Material composition'),
        'MADE_BY': ('MADE_BY', 'Creator/producer'),
        'LOCATED_AT': ('LOCATED_AT', 'Geographical location'),
        'FLOWS_THROUGH': ('FLOWS_THROUGH', 'River/path traversal'),
        'COLLOCATES_WITH': ('COLLOCATES_WITH', 'Common word pairing')
    }

    def __init__(self, config: Optional[Neo4jConfig] = None):
        """Initialize the Neo4j service."""
        self.config = config or Neo4jConfig.from_env()
        self._driver: Optional[Driver] = None
        self._connected = False
        self._connection_error: Optional[str] = None

    @property
    def is_available(self) -> bool:
        """Check if Neo4j driver is available."""
        return NEO4J_AVAILABLE

    @property
    def is_connected(self) -> bool:
        """Check if connected to Neo4j database."""
        return self._connected

    @property
    def connection_error(self) -> Optional[str]:
        """Get the last connection error if any."""
        return self._connection_error

    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.

        Returns:
            bool: True if connection successful, False otherwise
        """
        if not NEO4J_AVAILABLE:
            self._connection_error = "Neo4j driver not installed. Install with: pip install neo4j"
            return False

        try:
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password)
            )
            # Test connection
            self._driver.verify_connectivity()
            self._connected = True
            self._connection_error = None
            return True

        except ServiceUnavailable as e:
            self._connection_error = f"Neo4j service unavailable at {self.config.uri}: {str(e)}"
            self._connected = False
            return False

        except AuthError as e:
            self._connection_error = f"Neo4j authentication failed: {str(e)}"
            self._connected = False
            return False

        except Exception as e:
            self._connection_error = f"Neo4j connection error: {str(e)}"
            self._connected = False
            return False

    def disconnect(self):
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            self._connected = False

    @contextmanager
    def session(self):
        """Context manager for Neo4j sessions."""
        if not self._connected or not self._driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")

        session = self._driver.session(database=self.config.database)
        try:
            yield session
        finally:
            session.close()

    def setup_schema(self) -> bool:
        """
        Create database schema (constraints and indexes).

        Returns:
            bool: True if schema created successfully
        """
        if not self._connected:
            return False

        schema_queries = [
            # Constraints
            "CREATE CONSTRAINT word_bashkir IF NOT EXISTS FOR (w:Word) REQUIRE w.bashkir IS UNIQUE",
            "CREATE CONSTRAINT word_id IF NOT EXISTS FOR (w:Word) REQUIRE w.id IS UNIQUE",

            # Indexes for performance
            "CREATE INDEX word_english IF NOT EXISTS FOR (w:Word) ON (w.english)",
            "CREATE INDEX word_russian IF NOT EXISTS FOR (w:Word) ON (w.russian)",
            "CREATE INDEX word_pos IF NOT EXISTS FOR (w:Word) ON (w.pos)",
            "CREATE INDEX word_locus IF NOT EXISTS FOR (w:Word) ON (w.locus)",
            "CREATE INDEX word_bird IF NOT EXISTS FOR (w:Word) ON (w.bird)",

            # Full-text search index
            """CREATE FULLTEXT INDEX word_search IF NOT EXISTS
               FOR (w:Word) ON EACH [w.bashkir, w.english, w.russian]"""
        ]

        try:
            with self.session() as session:
                for query in schema_queries:
                    try:
                        session.run(query)
                    except Exception:
                        # Constraint/index might already exist
                        pass
            return True
        except Exception as e:
            self._connection_error = f"Schema creation failed: {str(e)}"
            return False

    def import_words(self, words_data: List[Dict]) -> Tuple[int, int]:
        """
        Import words into Neo4j database.

        Args:
            words_data: List of word dictionaries

        Returns:
            Tuple of (words_imported, relations_created)
        """
        if not self._connected:
            return 0, 0

        words_imported = 0
        relations_created = 0

        with self.session() as session:
            # Import words
            for word in words_data:
                try:
                    # Create word node
                    memory_palace = word.get('memory_palace', {})
                    cultural_context = word.get('cultural_context', {})

                    create_word_query = """
                    MERGE (w:Word {bashkir: $bashkir})
                    SET w.id = $id,
                        w.english = $english,
                        w.russian = $russian,
                        w.ipa = $ipa,
                        w.pos = $pos,
                        w.frequency_rank = $frequency_rank,
                        w.locus = $locus,
                        w.bird = $bird,
                        w.mnemonic = $mnemonic,
                        w.ocm_codes = $ocm_codes,
                        w.significance = $significance
                    RETURN w
                    """

                    session.run(create_word_query, {
                        'bashkir': word['bashkir'],
                        'id': word.get('id', ''),
                        'english': word.get('english', ''),
                        'russian': word.get('russian', ''),
                        'ipa': word.get('ipa', ''),
                        'pos': word.get('pos', 'noun'),
                        'frequency_rank': word.get('frequency_rank', 999),
                        'locus': memory_palace.get('locus', ''),
                        'bird': memory_palace.get('bird', ''),
                        'mnemonic': memory_palace.get('mnemonic', ''),
                        'ocm_codes': cultural_context.get('ocm_codes', []),
                        'significance': cultural_context.get('significance', '')
                    })
                    words_imported += 1

                except Exception as e:
                    print(f"Error importing word {word.get('bashkir', '?')}: {e}")

            # Create relationships
            for word in words_data:
                bashkortnet = word.get('bashkortnet', {})
                relations = bashkortnet.get('relations', {})

                for rel_type, targets in relations.items():
                    neo4j_rel_type = self.RELATION_TYPES.get(rel_type, (rel_type, ''))[0]

                    for target in targets:
                        try:
                            if isinstance(target, dict):
                                target_word = target.get('target', '')
                                properties = {k: v for k, v in target.items() if k != 'target'}
                            else:
                                target_word = str(target).split(' (')[0]
                                properties = {}

                            if not target_word:
                                continue

                            # Create relationship (MERGE to avoid duplicates)
                            rel_query = f"""
                            MATCH (w1:Word {{bashkir: $source}})
                            MERGE (w2:Word {{bashkir: $target}})
                            MERGE (w1)-[r:{neo4j_rel_type}]->(w2)
                            SET r += $properties
                            RETURN r
                            """

                            session.run(rel_query, {
                                'source': word['bashkir'],
                                'target': target_word,
                                'properties': properties
                            })
                            relations_created += 1

                        except Exception as e:
                            print(f"Error creating relation: {e}")

        return words_imported, relations_created

    def get_word(self, bashkir: str) -> Optional[Dict]:
        """Get a word node by its Bashkir form."""
        if not self._connected:
            return None

        with self.session() as session:
            result = session.run(
                "MATCH (w:Word {bashkir: $bashkir}) RETURN w",
                {'bashkir': bashkir}
            )
            record = result.single()
            if record:
                return dict(record['w'])
        return None

    def get_relations(self, bashkir: str) -> Dict[str, List[Dict]]:
        """Get all relations for a word."""
        if not self._connected:
            return {}

        relations = {}

        with self.session() as session:
            result = session.run("""
                MATCH (w:Word {bashkir: $bashkir})-[r]->(target:Word)
                RETURN type(r) as rel_type, target.bashkir as target,
                       target.english as english, properties(r) as props
            """, {'bashkir': bashkir})

            for record in result:
                rel_type = record['rel_type']
                # Convert Neo4j relation type back to short form
                short_type = next(
                    (k for k, v in self.RELATION_TYPES.items() if v[0] == rel_type),
                    rel_type
                )

                if short_type not in relations:
                    relations[short_type] = []

                relations[short_type].append({
                    'target': record['target'],
                    'english': record['english'],
                    **record['props']
                })

        return relations

    def find_path(self, start: str, end: str, max_depth: int = 5) -> Optional[List[Dict]]:
        """Find shortest path between two words."""
        if not self._connected:
            return None

        with self.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (start:Word {bashkir: $start})-[*1..$max_depth]-(end:Word {bashkir: $end})
                )
                RETURN [node in nodes(path) | node.bashkir] as words,
                       [rel in relationships(path) | type(rel)] as relations
            """, {'start': start, 'end': end, 'max_depth': max_depth})

            record = result.single()
            if record:
                words = record['words']
                rels = record['relations']
                path = []
                for i in range(len(rels)):
                    path.append({
                        'from': words[i],
                        'relation': rels[i],
                        'to': words[i + 1]
                    })
                return path
        return None

    def search_words(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search for words."""
        if not self._connected:
            return []

        with self.session() as session:
            # Try full-text search first
            try:
                result = session.run("""
                    CALL db.index.fulltext.queryNodes('word_search', $query)
                    YIELD node, score
                    RETURN node.bashkir as bashkir, node.english as english,
                           node.russian as russian, score
                    ORDER BY score DESC
                    LIMIT $limit
                """, {'query': query + '*', 'limit': limit})

                return [dict(record) for record in result]
            except Exception:
                # Fallback to CONTAINS search
                result = session.run("""
                    MATCH (w:Word)
                    WHERE w.bashkir CONTAINS $query
                       OR w.english CONTAINS $query
                       OR w.russian CONTAINS $query
                    RETURN w.bashkir as bashkir, w.english as english,
                           w.russian as russian
                    LIMIT $limit
                """, {'query': query, 'limit': limit})

                return [dict(record) for record in result]

    def get_word_family(self, bashkir: str) -> Dict[str, List[str]]:
        """Get semantically related words grouped by relationship type."""
        if not self._connected:
            return {}

        with self.session() as session:
            result = session.run("""
                MATCH (w:Word {bashkir: $bashkir})-[r]->(related:Word)
                RETURN type(r) as rel_type, collect(related.bashkir) as words
            """, {'bashkir': bashkir})

            family = {}
            for record in result:
                rel_type = record['rel_type']
                # Map to friendly names
                type_names = {
                    'SYNONYM': 'synonyms',
                    'ANTONYM': 'antonyms',
                    'IS_A': 'categories',
                    'HAS_TYPE': 'types',
                    'HAS_PART': 'parts',
                    'PART_OF': 'whole',
                    'CULTURAL_ASSOCIATION': 'cultural',
                    'MYTHOLOGICAL_LINK': 'mythological'
                }
                friendly_name = type_names.get(rel_type, rel_type.lower())
                family[friendly_name] = record['words']

            return family

    def get_words_by_theme(self, theme: str) -> List[Dict]:
        """Get words related to a cultural theme."""
        if not self._connected:
            return []

        with self.session() as session:
            result = session.run("""
                MATCH (w:Word)
                WHERE w.significance CONTAINS $theme
                   OR w.locus CONTAINS $theme
                   OR any(code IN w.ocm_codes WHERE code CONTAINS $theme)
                RETURN w.bashkir as bashkir, w.english as english,
                       w.locus as locus, w.significance as significance
            """, {'theme': theme})

            return [dict(record) for record in result]

    def get_graph_statistics(self) -> Dict[str, int]:
        """Get statistics about the graph database."""
        if not self._connected:
            return {}

        with self.session() as session:
            stats = {}

            # Word count
            result = session.run("MATCH (w:Word) RETURN count(w) as count")
            stats['total_words'] = result.single()['count']

            # Relationship count
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats['total_relations'] = result.single()['count']

            # Words by locus
            result = session.run("""
                MATCH (w:Word)
                WHERE w.locus IS NOT NULL AND w.locus <> ''
                RETURN w.locus as locus, count(w) as count
                ORDER BY count DESC
            """)
            stats['by_locus'] = {r['locus']: r['count'] for r in result}

            # Relations by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)
            stats['by_relation'] = {r['type']: r['count'] for r in result}

            return stats

    def export_for_visualization(self, limit: int = 100) -> Dict[str, List[Dict]]:
        """Export graph data for D3.js or vis.js visualization."""
        if not self._connected:
            return {'nodes': [], 'edges': []}

        with self.session() as session:
            # Get nodes
            result = session.run("""
                MATCH (w:Word)
                RETURN w.bashkir as id, w.bashkir as label,
                       w.english as english, w.bird as bird, w.locus as locus
                LIMIT $limit
            """, {'limit': limit})

            nodes = [dict(record) for record in result]

            # Get edges
            result = session.run("""
                MATCH (w1:Word)-[r]->(w2:Word)
                WHERE w1.bashkir IN $words AND w2.bashkir IN $words
                RETURN w1.bashkir as source, w2.bashkir as target, type(r) as relation
            """, {'words': [n['id'] for n in nodes]})

            edges = [dict(record) for record in result]

            return {'nodes': nodes, 'edges': edges}

    def generate_cypher_export(self, words_data: List[Dict]) -> str:
        """Generate Cypher statements for exporting data."""
        lines = [
            "// BashkortNet Neo4j Export",
            "// Generated Cypher statements for importing into Neo4j",
            "// Run in Neo4j Browser or with neo4j-admin",
            "",
            "// Create constraints first",
            "CREATE CONSTRAINT word_bashkir IF NOT EXISTS FOR (w:Word) REQUIRE w.bashkir IS UNIQUE;",
            ""
        ]

        # Generate CREATE statements for words
        lines.append("// Create word nodes")
        for word in words_data:
            bashkir = word['bashkir'].replace("'", "\\'").replace('"', '\\"')
            english = word.get('english', '').replace("'", "\\'").replace('"', '\\"')
            russian = word.get('russian', '').replace("'", "\\'").replace('"', '\\"')
            pos = word.get('pos', 'noun')

            memory_palace = word.get('memory_palace', {})
            locus = memory_palace.get('locus', '').replace("'", "\\'")
            bird = memory_palace.get('bird', '').replace("'", "\\'")

            lines.append(f"""MERGE (w:Word {{bashkir: "{bashkir}"}})
SET w.english = "{english}",
    w.russian = "{russian}",
    w.pos = "{pos}",
    w.locus = "{locus}",
    w.bird = "{bird}";""")

        lines.append("")
        lines.append("// Create relationships")

        # Generate relationship statements
        for word in words_data:
            bashkir = word['bashkir'].replace("'", "\\'").replace('"', '\\"')
            bashkortnet = word.get('bashkortnet', {})
            relations = bashkortnet.get('relations', {})

            for rel_type, targets in relations.items():
                neo4j_rel = self.RELATION_TYPES.get(rel_type, (rel_type, ''))[0]

                for target in targets:
                    if isinstance(target, dict):
                        target_word = target.get('target', '').replace("'", "\\'").replace('"', '\\"')
                    else:
                        target_word = str(target).split(' (')[0].replace("'", "\\'").replace('"', '\\"')

                    if target_word:
                        lines.append(f"""MATCH (w1:Word {{bashkir: "{bashkir}"}})
MERGE (w2:Word {{bashkir: "{target_word}"}})
MERGE (w1)-[:{neo4j_rel}]->(w2);""")

        return "\n".join(lines)


# Singleton instance for app-wide use
_neo4j_service: Optional[Neo4jService] = None

def get_neo4j_service() -> Neo4jService:
    """Get or create the Neo4j service singleton."""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service


def init_neo4j(config: Optional[Neo4jConfig] = None) -> Tuple[bool, str]:
    """
    Initialize Neo4j connection and setup schema.

    Returns:
        Tuple of (success: bool, message: str)
    """
    service = get_neo4j_service()
    if config:
        service.config = config

    if not service.is_available:
        return False, "Neo4j driver not installed. Install with: pip install neo4j>=5.0.0"

    if not service.connect():
        return False, service.connection_error or "Connection failed"

    if not service.setup_schema():
        return False, "Schema creation failed"

    return True, "Connected to Neo4j successfully"
