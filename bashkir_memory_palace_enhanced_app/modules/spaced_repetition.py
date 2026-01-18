"""
Spaced Repetition System: SM-2 Algorithm Implementation
========================================================
Implements the SuperMemo 2 algorithm for optimal review scheduling.

Based on Piotr Wozniak's research on memory and learning curves.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ReviewItem:
    """Represents a word's review state."""
    word_id: str
    bashkir: str
    english: str
    ease_factor: float = 2.5  # Initial ease factor
    interval: int = 0  # Days until next review
    repetitions: int = 0  # Successful repetitions in a row
    next_review: Optional[str] = None  # ISO format date
    last_review: Optional[str] = None
    total_reviews: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReviewItem':
        return cls(**data)


class SpacedRepetitionSystem:
    """
    Implements SM-2 algorithm for optimal learning.
    
    Quality ratings:
    0 - Complete blackout (couldn't remember at all)
    1 - Incorrect, but recognized when shown answer
    2 - Incorrect, but answer seemed easy to remember
    3 - Correct, but with significant difficulty
    4 - Correct, after some hesitation
    5 - Perfect, instant recall
    """
    
    MIN_EASE_FACTOR = 1.3
    QUALITY_THRESHOLD = 3  # Minimum quality for success
    
    def __init__(self, data_file: Optional[str] = None):
        """Initialize the SRS with optional persistence file."""
        self.items: Dict[str, ReviewItem] = {}
        self.data_file = data_file
        
        if data_file and Path(data_file).exists():
            self.load()
    
    def add_word(self, word_id: str, bashkir: str, english: str) -> ReviewItem:
        """Add a new word to the review system."""
        if word_id not in self.items:
            item = ReviewItem(
                word_id=word_id,
                bashkir=bashkir,
                english=english,
                next_review=datetime.now().isoformat()
            )
            self.items[word_id] = item
        return self.items[word_id]
    
    def review(self, word_id: str, quality: int) -> Tuple[int, float, str]:
        """
        Process a review and update scheduling.
        
        Args:
            word_id: The word being reviewed
            quality: Quality of recall (0-5)
        
        Returns:
            Tuple of (new_interval, new_ease_factor, next_review_date)
        """
        if word_id not in self.items:
            raise ValueError(f"Word {word_id} not found in review system")
        
        item = self.items[word_id]
        quality = max(0, min(5, quality))  # Clamp to 0-5
        
        item.total_reviews += 1
        item.last_review = datetime.now().isoformat()
        
        if quality >= self.QUALITY_THRESHOLD:
            # Successful recall
            item.correct_count += 1
            
            if item.repetitions == 0:
                item.interval = 1
            elif item.repetitions == 1:
                item.interval = 6
            else:
                item.interval = round(item.interval * item.ease_factor)
            
            item.repetitions += 1
        else:
            # Failed recall - reset
            item.incorrect_count += 1
            item.repetitions = 0
            item.interval = 1
        
        # Update ease factor
        item.ease_factor = max(
            self.MIN_EASE_FACTOR,
            item.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )
        
        # Calculate next review date
        next_review = datetime.now() + timedelta(days=item.interval)
        item.next_review = next_review.isoformat()
        
        # Auto-save if data file specified
        if self.data_file:
            self.save()
        
        return item.interval, item.ease_factor, item.next_review
    
    def get_due_items(self, limit: Optional[int] = None) -> List[ReviewItem]:
        """Get items due for review, sorted by urgency."""
        now = datetime.now()
        due = []
        
        for item in self.items.values():
            if item.next_review is None:
                due.append((item, now))  # New items are immediately due
            else:
                next_review = datetime.fromisoformat(item.next_review)
                if next_review <= now:
                    due.append((item, next_review))
        
        # Sort by due date (oldest first)
        due.sort(key=lambda x: x[1])
        items = [item for item, _ in due]
        
        if limit:
            return items[:limit]
        return items
    
    def get_new_items(self, words_data: List[Dict], limit: int = 5) -> List[Dict]:
        """Get words that haven't been added to the review system yet."""
        new_words = []
        for word in words_data:
            word_id = word.get('id', word.get('bashkir'))
            if word_id not in self.items:
                new_words.append(word)
                if len(new_words) >= limit:
                    break
        return new_words
    
    def get_statistics(self) -> Dict:
        """Get overall statistics for the review system."""
        if not self.items:
            return {
                'total_words': 0,
                'mastered': 0,
                'learning': 0,
                'new': 0,
                'due_today': 0,
                'average_ease': 0,
                'retention_rate': 0
            }
        
        now = datetime.now()
        mastered = 0  # interval >= 21 days
        learning = 0  # has been reviewed
        due_today = 0
        total_correct = 0
        total_reviews = 0
        ease_sum = 0
        
        for item in self.items.values():
            ease_sum += item.ease_factor
            total_correct += item.correct_count
            total_reviews += item.total_reviews
            
            if item.interval >= 21:
                mastered += 1
            elif item.total_reviews > 0:
                learning += 1
            
            if item.next_review:
                if datetime.fromisoformat(item.next_review) <= now:
                    due_today += 1
        
        return {
            'total_words': len(self.items),
            'mastered': mastered,
            'learning': learning,
            'new': len(self.items) - mastered - learning,
            'due_today': due_today,
            'average_ease': round(ease_sum / len(self.items), 2) if self.items else 0,
            'retention_rate': round(total_correct / total_reviews * 100, 1) if total_reviews > 0 else 0
        }
    
    def get_item_status(self, word_id: str) -> str:
        """Get the learning status of a word."""
        if word_id not in self.items:
            return 'unseen'
        
        item = self.items[word_id]
        
        if item.total_reviews == 0:
            return 'new'
        elif item.interval >= 21:
            return 'mastered'
        elif item.interval >= 7:
            return 'reviewing'
        else:
            return 'learning'
    
    def save(self):
        """Save review data to file."""
        if not self.data_file:
            return
        
        data = {word_id: item.to_dict() for word_id, item in self.items.items()}
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self):
        """Load review data from file."""
        if not self.data_file or not Path(self.data_file).exists():
            return
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.items = {
            word_id: ReviewItem.from_dict(item_data) 
            for word_id, item_data in data.items()
        }


class ReviewSession:
    """Manages a review session with multiple words."""
    
    def __init__(self, srs: SpacedRepetitionSystem, words_data: List[Dict]):
        """Initialize a review session."""
        self.srs = srs
        self.words_data = {w.get('id', w.get('bashkir')): w for w in words_data}
        self.session_items: List[ReviewItem] = []
        self.current_index = 0
        self.session_stats = {
            'total': 0,
            'correct': 0,
            'incorrect': 0
        }
    
    def start_session(self, new_words: int = 5, review_words: int = 20) -> bool:
        """
        Start a new review session.
        
        Args:
            new_words: Number of new words to introduce
            review_words: Number of words to review
        
        Returns:
            True if session has items to review
        """
        # Get due items
        due_items = self.srs.get_due_items(limit=review_words)
        
        # Get new words
        new_word_data = self.srs.get_new_items(list(self.words_data.values()), limit=new_words)
        
        # Add new words to SRS
        for word in new_word_data:
            word_id = word.get('id', word.get('bashkir'))
            self.srs.add_word(word_id, word['bashkir'], word['english'])
            due_items.append(self.srs.items[word_id])
        
        self.session_items = due_items
        self.current_index = 0
        self.session_stats = {'total': len(due_items), 'correct': 0, 'incorrect': 0}
        
        return len(self.session_items) > 0
    
    def get_current_item(self) -> Optional[Tuple[ReviewItem, Dict]]:
        """Get the current item to review."""
        if self.current_index >= len(self.session_items):
            return None
        
        item = self.session_items[self.current_index]
        word_data = self.words_data.get(item.word_id, {
            'bashkir': item.bashkir,
            'english': item.english
        })
        
        return item, word_data
    
    def submit_answer(self, quality: int) -> Dict:
        """
        Submit answer for current item and move to next.
        
        Returns:
            Dict with result info
        """
        if self.current_index >= len(self.session_items):
            return {'error': 'No more items'}
        
        item = self.session_items[self.current_index]
        interval, ease, next_review = self.srs.review(item.word_id, quality)
        
        if quality >= SpacedRepetitionSystem.QUALITY_THRESHOLD:
            self.session_stats['correct'] += 1
            result = 'correct'
        else:
            self.session_stats['incorrect'] += 1
            result = 'incorrect'
        
        self.current_index += 1
        
        return {
            'result': result,
            'new_interval': interval,
            'new_ease': ease,
            'next_review': next_review,
            'progress': f"{self.current_index}/{len(self.session_items)}"
        }
    
    def get_session_summary(self) -> Dict:
        """Get summary of the current session."""
        return {
            'completed': self.current_index,
            'remaining': len(self.session_items) - self.current_index,
            'correct': self.session_stats['correct'],
            'incorrect': self.session_stats['incorrect'],
            'accuracy': round(
                self.session_stats['correct'] / self.current_index * 100, 1
            ) if self.current_index > 0 else 0
        }


# Convenience functions
def calculate_next_review(quality: int, current_ease: float = 2.5, 
                          current_interval: int = 0, repetitions: int = 0) -> Tuple[int, float]:
    """
    Calculate next review interval using SM-2.
    
    Args:
        quality: Quality of recall (0-5)
        current_ease: Current ease factor
        current_interval: Current interval in days
        repetitions: Number of successful repetitions
    
    Returns:
        Tuple of (new_interval, new_ease_factor)
    """
    if quality < 3:
        # Failed - reset
        return 1, max(1.3, current_ease - 0.2)
    
    # Success
    if repetitions == 0:
        new_interval = 1
    elif repetitions == 1:
        new_interval = 6
    else:
        new_interval = round(current_interval * current_ease)
    
    new_ease = max(1.3, current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    
    return new_interval, new_ease


if __name__ == "__main__":
    # Test the module
    srs = SpacedRepetitionSystem()
    
    # Add some test words
    srs.add_word('word_001', 'бал', 'honey')
    srs.add_word('word_002', 'тау', 'mountain')
    srs.add_word('word_003', 'ат', 'horse')
    
    # Simulate reviews
    print("Simulating reviews...")
    
    # Perfect recall
    interval, ease, next_date = srs.review('word_001', 5)
    print(f"бал (quality 5): next in {interval} days, ease {ease:.2f}")
    
    # Good recall
    interval, ease, next_date = srs.review('word_002', 4)
    print(f"тау (quality 4): next in {interval} days, ease {ease:.2f}")
    
    # Failed recall
    interval, ease, next_date = srs.review('word_003', 2)
    print(f"ат (quality 2): next in {interval} days, ease {ease:.2f}")
    
    # Get statistics
    stats = srs.get_statistics()
    print(f"\nStatistics: {stats}")
