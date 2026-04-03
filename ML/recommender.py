# =============================================================
# ml/recommender.py
# Edu-Platform — Content Recommendation Engine
# =============================================================

import json
import os
import pickle
from typing import Optional

LEARNING_STYLE_RULES: dict = {
    "visual_learner": {
        "preferred_types": ["video", "infographic"],
        "secondary_types": ["tutorial", "notes"],
        "tags_boost":      ["visual", "animation", "diagram"],
        "description":     "Diagrams, animations aur visual content se best seekhte ho tum.",
        "study_tip":       "Mind maps banao, notes mein colours use karo!",
    },
    "conceptual_thinker": {
        "preferred_types": ["article", "video"],
        "secondary_types": ["tutorial", "project"],
        "tags_boost":      ["conceptual", "theory", "case-study", "detailed"],
        "description":     "Deep theory aur 'why' samajhne pe focus karte ho tum.",
        "study_tip":       "Pehle poora concept samjho, tab practice karo!",
    },
    "practice_based": {
        "preferred_types": ["exercise", "project"],
        "secondary_types": ["tutorial", "video"],
        "tags_boost":      ["practice", "hands-on", "coding", "build"],
        "description":     "Kar ke seekhte ho tum — theory baad mein.",
        "study_tip":       "Pehle problem try karo, phir solution dekho!",
    },
    "step_by_step": {
        "preferred_types": ["notes", "tutorial"],
        "secondary_types": ["article", "video"],
        "tags_boost":      ["structured", "step-by-step", "guided", "reference", "memory"],
        "description":     "Structured, sequential content se best seekhte ho tum.",
        "study_tip":       "Ek concept complete karo, tab agla shuru karo!",
    },
}

ML_FEATURES = ["logical", "verbal", "numerical", "memory", "attention"]


class Recommender:
    def __init__(self, content_file_path: Optional[str] = None):
        if content_file_path is None:
            # ml/recommender.py ke relative data folder
            base = os.path.dirname(os.path.abspath(__file__))
            content_file_path = os.path.join(base, "..", "data", "content_metadata.json")

        self.content_library: list[dict] = self._load_content(content_file_path)
        self.rules = LEARNING_STYLE_RULES
        print(f"Recommender ready! {len(self.content_library)} items loaded.")

    def _load_content(self, path: str) -> list[dict]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: content_metadata.json nahi mili: {path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Warning: JSON parse error: {e}")
            return []

    def _score_item(
        self,
        item:            dict,
        learning_style:  str,
        completed_ids:   list,
        completed_count: int,
    ) -> float:
        if item.get("content_id") in completed_ids:
            return 0.0

        rules = self.rules.get(learning_style, {})
        score = 0.0

        # Type match
        if item.get("type", "") in rules.get("preferred_types", []):
            score += 50
        elif item.get("type", "") in rules.get("secondary_types", []):
            score += 25

        # Tag boost
        boosted_tags = set(rules.get("tags_boost", []))
        item_tags    = set(t.lower() for t in item.get("tags", []))
        score       += min(30, len(boosted_tags & item_tags) * 10)

        # Difficulty progression
        difficulty = item.get("difficulty", 1)
        if completed_count == 0:
            if difficulty == 1: score += 20
            elif difficulty == 2: score += 10
        elif completed_count < 3:
            if difficulty == 1: score += 20
            elif difficulty == 2: score += 15
        elif completed_count < 8:
            if difficulty == 2: score += 20
            elif difficulty == 3: score += 15
            elif difficulty == 1: score += 5
        else:
            if difficulty >= 3: score += 20
            elif difficulty == 2: score += 10

        return round(score, 2)

    def _prerequisites_met(self, item: dict, completed_ids: list) -> bool:
        prereqs = item.get("prerequisites", [])
        if not prereqs:
            return True
        return all(pid in completed_ids for pid in prereqs)

    def get_recommendations(
        self,
        learning_style:  str,
        completed_ids:   list,
        completed_count: int,
        subject:         Optional[str]  = None,
        content_type:    Optional[str]  = None,
        difficulty:      Optional[int]  = None,
        top_n:           int            = 6,
        exclude_ids:     Optional[list] = None,
    ) -> dict:
        if learning_style not in self.rules:
            raise ValueError(f"Invalid learning_style: '{learning_style}'")

        all_excluded = set(completed_ids)
        if exclude_ids:
            all_excluded.update(exclude_ids)

        pool = self.content_library.copy()
        if subject:
            pool = [c for c in pool if c.get("subject","").lower() == subject.lower()]
        if content_type:
            pool = [c for c in pool if c.get("type","").lower() == content_type.lower()]
        if difficulty:
            pool = [c for c in pool if c.get("difficulty") == difficulty]

        scored = []
        for item in pool:
            s = self._score_item(item, learning_style, list(all_excluded), completed_count)
            if s > 0:
                scored.append({
                    **item,
                    "recommendation_score": s,
                    "prerequisites_met":    self._prerequisites_met(item, completed_ids),
                })

        scored.sort(
            key=lambda x: (x["prerequisites_met"], x["recommendation_score"]),
            reverse=True,
        )

        top        = scored[:top_n]
        style_info = self.rules.get(learning_style, {})

        return {
            "learning_style":    learning_style,
            "description":       style_info.get("description", ""),
            "study_tip":         style_info.get("study_tip", ""),
            "completed_count":   completed_count,
            "total_recommended": len(top),
            "recommendations":   top,
            "style_info":        style_info,
        }

    def get_content_by_id(self, content_id: str) -> Optional[dict]:
        return next(
            (c for c in self.content_library if c["content_id"] == content_id), None
        )

    def get_all_subjects(self) -> list:
        subject_map: dict = {}
        for item in self.content_library:
            s = item.get("subject", "")
            if s not in subject_map:
                subject_map[s] = {"subject": s, "total_content": 0, "types": set()}
            subject_map[s]["total_content"] += 1
            subject_map[s]["types"].add(item.get("type", ""))
        return [
            {"subject": s, "total_content": v["total_content"], "types": sorted(v["types"])}
            for s, v in sorted(subject_map.items())
        ]

    def search(self, query: str) -> list:
        q = query.lower().strip()
        if len(q) < 2:
            return []
        return [
            item for item in self.content_library
            if (
                q in item.get("title",        "").lower()
                or q in item.get("subject",    "").lower()
                or q in item.get("description","").lower()
                or any(q in tag.lower() for tag in item.get("tags", []))
            )
        ]

    def get_stats(self) -> dict:
        types = {}; subjects = {}; difficulty = {}
        for item in self.content_library:
            t = item.get("type",       "unknown")
            s = item.get("subject",    "unknown")
            d = item.get("difficulty", 0)
            types[t]      = types.get(t,0) + 1
            subjects[s]   = subjects.get(s,0) + 1
            difficulty[d] = difficulty.get(d,0) + 1
        return {
            "total_content": len(self.content_library),
            "by_type":       types,
            "by_subject":    subjects,
            "by_difficulty": difficulty,
        }

    def get_score_matrix(self) -> dict:
        styles = list(self.rules.keys())
        matrix = []
        for item in self.content_library:
            row = [self._score_item(item, style, [], 0) for style in styles]
            matrix.append(row)
        return {
            "content_ids": [c["content_id"] for c in self.content_library],
            "styles":      styles,
            "matrix":      matrix,
        }


# Singleton
_recommender_instance: Optional[Recommender] = None

def get_recommender() -> Recommender:
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = Recommender()
    return _recommender_instance


if __name__ == "__main__":
    rec   = get_recommender()
    stats = rec.get_stats()
    print(f"Total content: {stats['total_content']}")

    result = rec.get_recommendations("visual_learner", [], 0, subject="Python", top_n=3)
    print(f"\nVisual Learner — Python — Top 3:")
    for i, item in enumerate(result["recommendations"], 1):
        print(f"  {i}. {item['title']} (Score: {item['recommendation_score']})")
    print("\n✅ Test complete!")