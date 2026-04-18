"""Semantic batching for Stage 1 discovery.

Uses sentence-transformers embeddings + KMeans clustering to group
semantically similar instructions into batches, replacing random chunking.
"""

from __future__ import annotations

import math
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from collections import defaultdict

import numpy as np


def create_semantic_batches(
    instructions: List[Any],
    batch_size: int,
    embedding_model: str = "BAAI/bge-m3",
    output_dir: Optional[Path] = None,
    cache_key: Optional[str] = None,
) -> List[List[Any]]:
    """Cluster instructions by semantic similarity and return as batches.

    Args:
        instructions: All instruction strings to batch.
        batch_size: Target number of instructions per batch.
        embedding_model: Name of the sentence-transformers model.
        output_dir: If provided, save cluster assignments for analysis.

    Returns:
        List of batches (each batch is a list of instruction strings).
    """
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import KMeans

    n_clusters = max(1, math.ceil(len(instructions) / batch_size))

    # If only one cluster needed, return all instructions as one batch
    if n_clusters == 1:
        return [instructions]

    if cache_key:
        cache_dir = Path(".cache/semantic_batches")
        cache_dir.mkdir(parents=True, exist_ok=True)
        safe_model_name = embedding_model.replace("/", "_")
        cache_file = cache_dir / f"{cache_key}_{batch_size}_{safe_model_name}.json"
        
        if cache_file.exists():
            print(f"Loading cached semantic batches from {cache_file}...")
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_indices = json.load(f)
                
                # Reconstruct batches using indices
                batches = [[instructions[idx] for idx in batch_indices] for batch_indices in cached_indices]
                return batches
            except Exception as e:
                print(f"Failed to load cache: {e}. Recomputing...")

    print(f"Loading embedding model '{embedding_model}'...")
    model = SentenceTransformer(embedding_model)

    instruction_texts = []
    for item in instructions:
        if isinstance(item, dict):
            instruction_texts.append(item.get("instruction", str(item)))
        else:
            instruction_texts.append(str(item))

    print(f"Encoding {len(instruction_texts)} instructions...")
    embeddings = model.encode(instruction_texts, show_progress_bar=True, batch_size=256)

    print(f"Clustering into {n_clusters} clusters (target batch_size={batch_size})...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    # Group instruction indices by cluster
    clusters: Dict[int, List[int]] = defaultdict(list)
    for idx, label in enumerate(labels):
        clusters[label].append(idx)

    batch_indices = [clusters[i] for i in sorted(clusters.keys())]
    batches = [[instructions[idx] for idx in current_indices] for current_indices in batch_indices]

    if cache_key:
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(batch_indices, f)
            print(f"Saved semantic batch clusters to {cache_file}")
        except Exception as e:
            print(f"Failed to save cache: {e}")

    # Print cluster size distribution
    sizes = [len(b) for b in batches]
    print(
        f"Cluster sizes: min={min(sizes)}, max={max(sizes)}, "
        f"mean={sum(sizes)/len(sizes):.0f}, median={sorted(sizes)[len(sizes)//2]}"
    )

    # Save cluster assignments for analysis
    if output_dir is not None:
        cluster_info = {
            "embedding_model": embedding_model,
            "n_clusters": n_clusters,
            "target_batch_size": batch_size,
            "total_instructions": len(instructions),
            "cluster_sizes": {str(i): len(batches[i]) for i in range(len(batches))},
        }
        info_file = output_dir / "semantic_batching_info.json"
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(cluster_info, f, indent=2)
        print(f"Saved clustering info to {info_file}")

    return batches
