from __future__ import annotations

from typing import Dict, List, Tuple

from runner_utils import f1_score


def compute_board_metrics(
    pred: List[int], gold: List[int]
) -> Tuple[float, float, float, bool]:
    """Return precision, recall, F1 and exact match for two board states."""
    correct = sum(1 for p, g in zip(pred, gold) if p == g and g != 0)
    pred_colored = sum(1 for p in pred if p != 0)
    gold_colored = sum(1 for g in gold if g != 0)
    if pred_colored:
        precision = correct / pred_colored
    else:
        precision = 1.0 if gold_colored == 0 else 0.0
    if gold_colored:
        recall = correct / gold_colored
    else:
        recall = 1.0 if pred_colored == 0 else 0.0
    f1 = f1_score(precision, recall)
    exact = pred == gold
    return precision, recall, f1, exact


def compute_action_metrics(
    prev_pred: List[int], pred: List[int], prev_gold: List[int], gold: List[int]
) -> Tuple[float, float, float, bool]:
    """Metrics for changed tiles only (action-based)."""
    pred_diff = {i for i, (a, b) in enumerate(zip(prev_pred, pred)) if a != b}
    gold_diff = {i for i, (a, b) in enumerate(zip(prev_gold, gold)) if a != b}
    correct = {i for i in pred_diff if i in gold_diff and pred[i] == gold[i]}
    if pred_diff:
        precision = len(correct) / len(pred_diff)
    else:
        precision = 1.0 if not gold_diff else 0.0
    if gold_diff:
        recall = len(correct) / len(gold_diff)
    else:
        recall = 1.0 if not pred_diff else 0.0
    f1 = f1_score(precision, recall)
    exact = pred_diff == gold_diff and all(pred[i] == gold[i] for i in pred_diff)
    return precision, recall, f1, exact


def evaluate_prediction(
    prev_pred: List[int], pred: List[int], prev_gold: List[int], gold: List[int]
) -> Dict[str, float | bool]:
    """Return a dictionary with board and action metrics."""
    b_prec, b_rec, b_f1, b_exact = compute_board_metrics(pred, gold)
    a_prec, a_rec, a_f1, a_exact = compute_action_metrics(
        prev_pred, pred, prev_gold, gold
    )
    return {
        "correct": b_exact,
        "precision_board": b_prec,
        "recall_board": b_rec,
        "f1_board": b_f1,
        "exact_board": b_exact,
        "precision_action": a_prec,
        "recall_action": a_rec,
        "f1_action": a_f1,
        "exact_action": a_exact,
    }
