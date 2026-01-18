"""
BashkortNet: Semantic Network for Bashkir Language
===================================================
A knowledge graph system connecting words through linguistic and cultural relationships.

Relationship Types:
- SYN: Synonyms
- ANT: Antonyms  
- ISA: Category membership (hypernym)
- HAS_TYPE: Specific instances (hyponym)
- PART_OF: Component relationships
- HAS_PART: Contains components
- CULT_ASSOC: Cultural associations
- MYTH_LINK: Mythological connections
"""

import json
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict


class BashkortNet:
    """Semantic network for Bashkir vocabulary with cultural connections."""
    
    RELATION_TYPES = {
        'SYN': 'Synonym',
        'ANT': 'Antonym',
        'ISA': 'Is a type of',
        'HAS_TYPE': 'Has type',
        'PART_OF': 'Part of',
        'HAS_PART': 'Has part',
        'CULT_ASSOC': 'Cultural association',
        'MYTH_LINK': 'Mythological link',
        'MADE_FROM': 'Made from',
        'MADE_BY': 'Made by',
        'LOCATED_AT': 'Located at',
        'FLOWS_THROUGH': 'Flows through'
    }
    
    def __init__(self, words_data: List[Dict]):
        """Initialize the semantic network from words data."""
        self.words = {w['bashkir']: w for w in words_data}
        self.words_by_id = {w['id']: w for w in words_data}
        self.graph = defaultdict(lambda: defaultdict(list))
        self._build_graph()
    
    def _build_graph(self):
        """Build the relationship graph from word data."""
        for word_data in self.words.values():
            word = word_data['bashkir']
            
            if 'bashkortnet' not in word_data:
                continue
                
            relations = word_data['bashkortnet'].get('relations', {})
            
            for rel_type, targets in relations.items():
                if not targets:
                    continue
                    
                for target in targets:
                    if isinstance(target, str):
                        # Simple string target
                        target_word = target.split(' (')[0]  # Remove gloss if present
                        self.graph[word][rel_type].append({
                            'target': target_word,
                            'gloss': target
                        })
                    elif isinstance(target, dict):
                        # Rich target with metadata
                        self.graph[word][rel_type].append(target)
    
    def get_relations(self, word: str) -> Dict[str, List[Dict]]:
        """Get all relations for a word."""
        return dict(self.graph.get(word, {}))
    
    def get_related_words(self, word: str, relation_type: Optional[str] = None) -> List[str]:
        """Get words related to the given word."""
        relations = self.graph.get(word, {})
        
        if relation_type:
            targets = relations.get(relation_type, [])
            return [t.get('target', t) if isinstance(t, dict) else t for t in targets]
        
        # All relations
        all_related = []
        for rel_type, targets in relations.items():
            for t in targets:
                target = t.get('target', t) if isinstance(t, dict) else t
                if target not in all_related:
                    all_related.append(target)
        return all_related
    
    def find_path(self, start: str, end: str, max_depth: int = 5) -> Optional[List[Tuple[str, str, str]]]:
        """Find a path between two words through the network."""
        if start not in self.words or end not in self.words:
            return None
            
        visited = {start}
        queue = [(start, [])]
        
        while queue and len(queue[0][1]) < max_depth:
            current, path = queue.pop(0)
            
            for rel_type, targets in self.graph.get(current, {}).items():
                for target_data in targets:
                    target = target_data.get('target', target_data) if isinstance(target_data, dict) else target_data
                    
                    if target == end:
                        return path + [(current, rel_type, target)]
                    
                    if target not in visited and target in self.words:
                        visited.add(target)
                        queue.append((target, path + [(current, rel_type, target)]))
        
        return None
    
    def get_word_family(self, word: str) -> Dict[str, List[str]]:
        """Get semantically related word family."""
        family = {
            'synonyms': self.get_related_words(word, 'SYN'),
            'antonyms': self.get_related_words(word, 'ANT'),
            'categories': self.get_related_words(word, 'ISA'),
            'types': self.get_related_words(word, 'HAS_TYPE'),
            'parts': self.get_related_words(word, 'HAS_PART'),
            'whole': self.get_related_words(word, 'PART_OF'),
            'cultural': self.get_related_words(word, 'CULT_ASSOC'),
            'mythological': self.get_related_words(word, 'MYTH_LINK')
        }
        return {k: v for k, v in family.items() if v}
    
    def get_cultural_connections(self, word: str) -> List[Dict]:
        """Get cultural and mythological connections for a word."""
        connections = []
        
        cultural = self.graph.get(word, {}).get('CULT_ASSOC', [])
        for c in cultural:
            connections.append({
                'type': 'cultural',
                'target': c.get('target', c) if isinstance(c, dict) else c,
                'relation': c.get('relation', 'associated with') if isinstance(c, dict) else 'associated with',
                'note': c.get('note', '') if isinstance(c, dict) else ''
            })
        
        mythological = self.graph.get(word, {}).get('MYTH_LINK', [])
        for m in mythological:
            connections.append({
                'type': 'mythological',
                'target': m.get('target', m) if isinstance(m, dict) else m,
                'relation': m.get('relation', 'connected to') if isinstance(m, dict) else 'connected to',
                'note': m.get('note', '') if isinstance(m, dict) else ''
            })
        
        return connections
    
    def search_by_theme(self, theme: str) -> List[str]:
        """Search for words by cultural theme."""
        results = []
        theme_lower = theme.lower()
        
        for word, data in self.words.items():
            # Check cultural context
            cultural = data.get('cultural_context', {})
            significance = cultural.get('significance', '').lower()
            
            if theme_lower in significance:
                results.append(word)
                continue
            
            # Check relations
            connections = self.get_cultural_connections(word)
            for conn in connections:
                if theme_lower in conn.get('note', '').lower():
                    results.append(word)
                    break
        
        return results
    
    def get_etymology(self, word: str) -> Optional[Dict]:
        """Get etymology information for a word."""
        word_data = self.words.get(word)
        if not word_data:
            return None
        
        bashkortnet = word_data.get('bashkortnet', {})
        return bashkortnet.get('etymology')
    
    def get_collocations(self, word: str) -> List[Dict]:
        """Get common collocations for a word."""
        word_data = self.words.get(word)
        if not word_data:
            return []
        
        bashkortnet = word_data.get('bashkortnet', {})
        return bashkortnet.get('collocations', [])
    
    def export_for_visualization(self) -> Dict:
        """Export network data for D3.js or vis.js visualization."""
        nodes = []
        edges = []
        
        for word, data in self.words.items():
            nodes.append({
                'id': word,
                'label': word,
                'english': data.get('english', ''),
                'bird': data.get('memory_palace', {}).get('bird', 'Unknown'),
                'locus': data.get('memory_palace', {}).get('locus', 'Unknown')
            })
        
        edge_id = 0
        for source, relations in self.graph.items():
            for rel_type, targets in relations.items():
                for target_data in targets:
                    target = target_data.get('target', target_data) if isinstance(target_data, dict) else target_data
                    edges.append({
                        'id': edge_id,
                        'source': source,
                        'target': target,
                        'relation': rel_type,
                        'label': self.RELATION_TYPES.get(rel_type, rel_type)
                    })
                    edge_id += 1
        
        return {'nodes': nodes, 'edges': edges}


def load_bashkortnet(words_file: str) -> BashkortNet:
    """Load BashkortNet from a words JSON file."""
    with open(words_file, 'r', encoding='utf-8') as f:
        words_data = json.load(f)
    return BashkortNet(words_data)


if __name__ == "__main__":
    # Test the module
    import os
    
    words_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'words.json')
    
    if os.path.exists(words_file):
        net = load_bashkortnet(words_file)
        
        # Test: Get relations for 'бал' (honey)
        print("Relations for 'бал' (honey):")
        relations = net.get_relations('бал')
        for rel_type, targets in relations.items():
            print(f"  {rel_type}: {targets}")
        
        # Test: Find word family
        print("\nWord family for 'ат' (horse):")
        family = net.get_word_family('ат')
        for category, words in family.items():
            print(f"  {category}: {words}")
        
        # Test: Cultural connections
        print("\nCultural connections for 'бал':")
        connections = net.get_cultural_connections('бал')
        for conn in connections:
            print(f"  {conn}")
