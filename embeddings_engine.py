import json
import re
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Optional sentence-transformers support for dense semantic embeddings
_ST_MODEL = None
_HAS_ST = False

def _init_sentence_transformer():
    global _ST_MODEL, _HAS_ST
    if _ST_MODEL is None and not _HAS_ST:
        try:
            from sentence_transformers import SentenceTransformer
            # Using ultra-lightweight mini model
            _ST_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
            _HAS_ST = True
        except Exception:
            _HAS_ST = False
    return _ST_MODEL

class StandardsRecommendationEngine:
    """
    Hybrid Recommendation Engine for Indian Standards (BIS).
    Combines TF-IDF semantic vector similarity, dense sentence embeddings (when available),
    and exact domain keyword matching to compute relevance scores.
    """
    def __init__(self, data_path: str = None):
        if data_path is None:
            data_path = Path(__file__).parent / "data" / "indian_standards.json"
        
        self.data_path = Path(data_path)
        self.standards: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 3))
        self.tfidf_matrix = None
        self.corpus_texts: List[str] = []
        self.load_dataset()

    def load_dataset(self):
        """Loads the JSON dataset of Indian Standards and builds the TF-IDF index."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Standards database not found at {self.data_path}")

        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.standards = json.load(f)

        # Construct rich searchable corpus representation for each standard
        self.corpus_texts = []
        for std in self.standards:
            keys_str = " ".join(std.get("key_specifications", []))
            related_str = " ".join(std.get("related_standards", []))
            full_text = f"{std['standard_number']} {std['title']} {std['category']} {std['sub_category']} {std['description']} {keys_str} {related_str}"
            self.corpus_texts.append(full_text)

        # Fit TF-IDF matrix
        if self.corpus_texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_texts)

    def extract_keywords(self, text: str) -> List[str]:
        """Extracts technical terms, numbers, and ratings from query text (e.g. 90W, M30, IP66, 5HP)."""
        # Find numeric specs with units or alphanumeric technical codes
        tokens = re.findall(r'\b\d+\s*(?:w|kw|hp|v|kv|m\d*|ip\d+|mm|kg|kva|bar|p)\b|\b[a-z0-9\-]{2,}\b', text.lower())
        return list(set(tokens))

    def search_standards(self, query: str, top_k: int = 5, min_score_threshold: float = 0.1, category_filter: str = "All") -> List[Dict[str, Any]]:
        """
        Searches and ranks Indian Standards for a user procurement specification query.
        Returns top_k matches sorted by relevance score percentage.
        """
        if not query or not query.strip():
            return []

        # Multilingual Normalization (Hindi/Marathi/English concept mapping)
        from i18n import normalize_multilingual_query
        normalized_query_text = normalize_multilingual_query(query.strip())
        query_clean = normalized_query_text

        # 1. TF-IDF Cosine Similarity
        query_vec = self.vectorizer.transform([query_clean])
        tfidf_scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # 2. Check Dense Embeddings if SentenceTransformer available
        st_scores = None
        try:
            st_model = _init_sentence_transformer()
            if st_model is not None:
                q_emb = st_model.encode([query_clean])
                c_embs = st_model.encode(self.corpus_texts)
                st_scores = cosine_similarity(q_emb, c_embs)[0]
        except Exception:
            st_scores = None

        query_keywords = self.extract_keywords(query_clean)
        
        # Domain detection taxonomy map
        domain_triggers = {
            "Electrical & Lighting": ["led", "light", "luminaire", "street light", "lamp", "bulb", "90w", "100w", "watt", "driver", "ballast", "illumination", "fixture"],
            "Civil & Construction": ["concrete", "rmc", "m20", "m30", "m40", "cement", "tmt", "rebar", "steel bar", "strand", "paver", "paving", "block", "structure", "building"],
            "Civil & Piping": ["pipe", "hdpe", "pvc", "polyethylene", "water supply", "pe100", "pe80", "drainage", "piping"],
            "Electronics & IT": ["ups", "uninterruptible", "computer", "laptop", "server", "data center", "mobile", "phone", "telecom", "it equipment"],
            "Mechanical & Hydraulics": ["pump", "submersible", "pumpset", "borewell", "tubewell", "hydraulics", "impeller", "motor"],
            "Mechanical & Safety": ["cylinder", "lpg", "gas cylinder", "pressure vessel", "cooking gas"],
            "Healthcare & Medical Devices": ["oximeter", "medical", "spo2", "patient", "hospital", "clinical", "pulse", "respirator"],
            "Renewable Energy & Solar": ["solar", "pv", "photovoltaic", "panel", "kusum", "solar pump"],
            "Safety & Personal Protective Equipment": ["gumboots", "boot", "safety shoe", "footwear", "ppe", "protective boot"],
            "Safety & Management Systems": ["safety audit", "occupational health", "hazard audit", "osh"]
        }

        # Detect active domains from query text
        query_lower = query_clean.lower()
        detected_domains = set()
        for dom, keywords in domain_triggers.items():
            for kw in keywords:
                if kw in query_lower:
                    detected_domains.add(dom)

        results = []
        for idx, std in enumerate(self.standards):
            # Category Filtering (if explicit sidebar filter applied)
            if category_filter != "All" and std.get("category") != category_filter:
                continue

            base_tfidf = tfidf_scores[idx]
            
            # Combine TF-IDF and Dense Embedding if available
            if st_scores is not None:
                combined_score = 0.4 * base_tfidf + 0.6 * st_scores[idx]
            else:
                combined_score = base_tfidf

            std_category = std.get("category", "")
            
            # 3. Domain Compatibility & Mismatch Penalty logic
            domain_bonus = 0.0
            domain_penalty = 0.0

            if detected_domains:
                if std_category in detected_domains:
                    domain_bonus = 0.35 # Strong boost for category match
                else:
                    # Check if candidate category is fundamentally incompatible
                    # E.g. Healthcare when searching for LED or Civil Pipes
                    domain_penalty = 0.70 # Severe penalty for cross-domain mismatch

            # 4. Keyword Signal Matching
            boost = 0.0
            std_keys = [k.lower() for k in std.get("key_specifications", [])]
            std_text_lower = self.corpus_texts[idx].lower()

            matched_signal_count = 0
            for kw in query_keywords:
                if kw in std_text_lower:
                    boost += 0.08
                    matched_signal_count += 1
                for key_spec in std_keys:
                    if kw in key_spec or key_spec in query_lower:
                        boost += 0.15
                        matched_signal_count += 1

            # Calculate raw composite score
            raw_score = (combined_score + boost + domain_bonus) - domain_penalty
            
            # Ignore items with negative or near-zero score
            if raw_score <= 0.02:
                continue

            # Normalized presentation percentage
            final_pct = round(min(0.99, max(0.10, (raw_score ** 0.55))) * 100, 1)

            # Assign qualitative confidence level
            if final_pct >= 85.0:
                match_level = "High Match"
            elif final_pct >= 70.0:
                match_level = "Strong Match"
            elif final_pct >= 50.0:
                match_level = "Moderate Match"
            else:
                match_level = "Fair Match"

            # Highlight exact matched terms for UI display
            matched_terms = []
            for term in query_keywords:
                if len(term) >= 2 and term in std_text_lower and term not in matched_terms:
                    matched_terms.append(term)
            for spec in std.get("key_specifications", []):
                if spec.lower() in query_lower and spec not in matched_terms:
                    matched_terms.append(spec)

            if raw_score >= min_score_threshold or matched_terms:
                res_item = dict(std)
                res_item["relevance_score"] = final_pct
                res_item["match_level"] = match_level
                res_item["raw_score"] = float(raw_score)
                res_item["matched_terms"] = matched_terms[:6]
                results.append(res_item)

        # Sort by relevance score descending
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

    def get_categories(self) -> List[str]:
        """Returns list of distinct categories in the database."""
        cats = sorted(list(set(std.get("category", "General") for std in self.standards)))
        return ["All"] + cats
