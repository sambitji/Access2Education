"""
Spaced Repetition Engine — SM-2 Algorithm with Learning Style Adaptation
Integrates with EduPlatform's ML clustering model.

SM-2 Algorithm: https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-super-memo-method
Enhanced with learning-style-aware review content selection.
"""

import math
from datetime import datetime, timedelta
from typing import Optional
from enum import IntEnum


class Quality(IntEnum):
    """Response quality ratings for SM-2 algorithm (0-5 scale)"""
    BLACKOUT = 0       # Complete blackout, no recollection
    WRONG_FAMILIAR = 1 # Wrong answer, but recognized correct one
    WRONG_EASY = 2     # Wrong answer, correct one seemed easy
    HARD = 3           # Correct answer with serious difficulty
    HESITANT = 4       # Correct answer after hesitation
    PERFECT = 5        # Perfect response


LEARNING_STYLE_REVIEW_FORMAT = {
    0: {  # Visual Learner
        "primary": "video_clip",
        "secondary": "infographic",
        "description": "Short video recap + visual summary",
        "review_prompt": "Watch this 2-min visual recap, then answer:",
        "color": "#6366f1"
    },
    1: {  # Conceptual Thinker
        "primary": "article_excerpt",
        "secondary": "concept_map",
        "description": "Key concept summary + theory links",
        "review_prompt": "Read this conceptual overview, then answer:",
        "color": "#0ea5e9"
    },
    2: {  # Practice-Based
        "primary": "mini_exercise",
        "secondary": "worked_example",
        "description": "Quick practice problem + solution walkthrough",
        "review_prompt": "Solve this quick problem to test recall:",
        "color": "#10b981"
    },
    3: {  # Step-by-Step
        "primary": "step_tutorial",
        "secondary": "checklist",
        "description": "Step-by-step refresher notes",
        "review_prompt": "Review these steps, then answer:",
        "color": "#f59e0b"
    }
}


class SM2Card:
    """
    Single flashcard/concept card with SM-2 spaced repetition state.
    
    Fields match MongoDB document structure in backend.
    """
    
    def __init__(
        self,
        concept_id: str,
        user_id: str,
        subject: str,
        concept_title: str,
        learning_style: int = 0,
        # SM-2 state fields
        repetition: int = 0,
        easiness: float = 2.5,
        interval: int = 1,
        next_review: Optional[datetime] = None,
        last_reviewed: Optional[datetime] = None,
        total_reviews: int = 0,
        streak: int = 0,
        retention_score: float = 1.0
    ):
        self.concept_id = concept_id
        self.user_id = user_id
        self.subject = subject
        self.concept_title = concept_title
        self.learning_style = learning_style
        
        # SM-2 algorithm state
        self.repetition = repetition
        self.easiness = max(1.3, easiness)  # EF never below 1.3
        self.interval = interval
        self.next_review = next_review or datetime.utcnow()
        self.last_reviewed = last_reviewed
        self.total_reviews = total_reviews
        self.streak = streak
        self.retention_score = retention_score

    def review(self, quality: int) -> dict:
        """
        Process a review with given quality rating.
        Updates SM-2 state and returns next review schedule.
        
        Returns dict with updated card state.
        """
        q = max(0, min(5, quality))
        self.total_reviews += 1
        self.last_reviewed = datetime.utcnow()
        
        # Update easiness factor
        self.easiness = max(
            1.3,
            self.easiness + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
        )
        
        if q < 3:
            # Failed recall — reset repetition but keep easiness
            self.repetition = 0
            self.interval = 1
            self.streak = 0
        else:
            # Successful recall
            self.streak += 1
            if self.repetition == 0:
                self.interval = 1
            elif self.repetition == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.easiness)
            self.repetition += 1
        
        # Calculate retention score (exponential decay model)
        # R = e^(-t/S) where S is stability (related to interval)
        stability = max(1, self.interval * 0.7)
        self.retention_score = math.exp(-1 / stability) if self.repetition > 0 else 0.5
        
        # Schedule next review
        self.next_review = datetime.utcnow() + timedelta(days=self.interval)
        
        return self.to_dict()

    def predict_retention(self, days_from_now: int = 0) -> float:
        """
        Predict retention percentage at a given future point.
        Uses Ebbinghaus forgetting curve: R = e^(-t/S)
        """
        if self.last_reviewed is None:
            return 0.5
        
        days_since_review = (datetime.utcnow() - self.last_reviewed).days + days_from_now
        stability = max(1, self.interval * 0.7)
        return round(math.exp(-days_since_review / stability), 4)

    def is_due(self) -> bool:
        """Check if this card is due for review."""
        return datetime.utcnow() >= self.next_review

    def days_until_due(self) -> int:
        """Days until next review (negative = overdue)."""
        delta = self.next_review - datetime.utcnow()
        return delta.days

    def get_review_format(self) -> dict:
        """Get learning-style-aware review format for this card."""
        return LEARNING_STYLE_REVIEW_FORMAT.get(
            self.learning_style,
            LEARNING_STYLE_REVIEW_FORMAT[0]
        )

    def urgency_score(self) -> float:
        """
        Calculate urgency score for review prioritization.
        Higher = more urgent to review.
        
        Formula considers: overdueness, current retention, easiness factor
        """
        days_overdue = max(0, -self.days_until_due())
        retention = self.predict_retention()
        
        # Penalize low retention heavily
        retention_penalty = (1 - retention) * 2
        
        # Reward overdue cards
        overdue_bonus = math.log1p(days_overdue) * 0.5
        
        # Low easiness cards need more attention
        difficulty_factor = max(0, (2.5 - self.easiness) * 0.3)
        
        return round(retention_penalty + overdue_bonus + difficulty_factor, 4)

    def to_dict(self) -> dict:
        """Serialize to MongoDB-compatible dict."""
        return {
            "concept_id": self.concept_id,
            "user_id": self.user_id,
            "subject": self.subject,
            "concept_title": self.concept_title,
            "learning_style": self.learning_style,
            "repetition": self.repetition,
            "easiness": round(self.easiness, 4),
            "interval": self.interval,
            "next_review": self.next_review.isoformat(),
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "total_reviews": self.total_reviews,
            "streak": self.streak,
            "retention_score": round(self.retention_score, 4),
            "urgency_score": self.urgency_score(),
            "is_due": self.is_due(),
            "days_until_due": self.days_until_due(),
            "review_format": self.get_review_format()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SM2Card":
        """Deserialize from MongoDB document."""
        card = cls(
            concept_id=data["concept_id"],
            user_id=data["user_id"],
            subject=data["subject"],
            concept_title=data["concept_title"],
            learning_style=data.get("learning_style", 0),
            repetition=data.get("repetition", 0),
            easiness=data.get("easiness", 2.5),
            interval=data.get("interval", 1),
            total_reviews=data.get("total_reviews", 0),
            streak=data.get("streak", 0),
            retention_score=data.get("retention_score", 1.0)
        )
        if data.get("next_review"):
            card.next_review = datetime.fromisoformat(data["next_review"])
        if data.get("last_reviewed"):
            card.last_reviewed = datetime.fromisoformat(data["last_reviewed"])
        return card


class SpacedRepetitionEngine:
    """
    High-level engine that manages a user's full card deck.
    """

    def __init__(self, cards: list[SM2Card]):
        self.cards = cards

    def get_due_cards(self, limit: int = 20) -> list[SM2Card]:
        """Get cards due for review, sorted by urgency."""
        due = [c for c in self.cards if c.is_due()]
        due.sort(key=lambda c: c.urgency_score(), reverse=True)
        return due[:limit]

    def get_upcoming_schedule(self, days: int = 7) -> dict:
        """
        Returns review schedule for next N days.
        Useful for the frontend calendar/heatmap.
        """
        schedule = {}
        today = datetime.utcnow().date()
        
        for i in range(days):
            day = today + timedelta(days=i)
            schedule[day.isoformat()] = []

        for card in self.cards:
            review_date = card.next_review.date()
            key = review_date.isoformat()
            if key in schedule:
                schedule[key].append({
                    "concept_id": card.concept_id,
                    "concept_title": card.concept_title,
                    "subject": card.subject,
                    "predicted_retention": card.predict_retention(
                        (review_date - today).days
                    )
                })
        return schedule

    def get_retention_heatmap(self) -> list[dict]:
        """
        Returns per-subject retention stats for dashboard heatmap.
        """
        subjects = {}
        for card in self.cards:
            s = card.subject
            if s not in subjects:
                subjects[s] = {"total_retention": 0, "count": 0, "due_count": 0}
            subjects[s]["total_retention"] += card.predict_retention()
            subjects[s]["count"] += 1
            if card.is_due():
                subjects[s]["due_count"] += 1

        result = []
        for subject, stats in subjects.items():
            avg_retention = stats["total_retention"] / stats["count"] if stats["count"] > 0 else 0
            result.append({
                "subject": subject,
                "avg_retention": round(avg_retention * 100, 1),
                "card_count": stats["count"],
                "due_count": stats["due_count"],
                "health": "good" if avg_retention > 0.7 else "warning" if avg_retention > 0.4 else "critical"
            })
        return sorted(result, key=lambda x: x["avg_retention"])

    def get_streak_stats(self) -> dict:
        """Returns gamification stats for the Learning DNA card."""
        if not self.cards:
            return {"max_streak": 0, "avg_streak": 0, "total_reviews": 0}
        
        streaks = [c.streak for c in self.cards]
        return {
            "max_streak": max(streaks),
            "avg_streak": round(sum(streaks) / len(streaks), 1),
            "total_reviews": sum(c.total_reviews for c in self.cards),
            "mastered_cards": sum(1 for c in self.cards if c.repetition >= 5),
            "total_cards": len(self.cards),
            "mastery_percent": round(
                sum(1 for c in self.cards if c.repetition >= 5) / len(self.cards) * 100, 1
            ) if self.cards else 0
        }