from __future__ import annotations

from typing import Dict, List, Tuple


def f1_score(precision: float, recall: float) -> float:
    """Return harmonic F1 score given precision and recall."""
    return (
        2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    )


def compute_board_metrics(
    pred: List[int], gold: List[int]
) -> Tuple[float, float, float, bool, int, int, int]:
    """
    precision, recall, f1, exact,
    tp (pred==gold!=0), p (pred!=0), g (gold!=0)
    """
    correct = sum(1 for p, g in zip(pred, gold) if p == g and g != 0)
    pred_colored = sum(1 for p in pred if p != 0)
    gold_colored = sum(1 for g in gold if g != 0)

    precision = (
        correct / pred_colored if pred_colored else (1.0 if gold_colored == 0 else 0.0)
    )
    recall = (
        correct / gold_colored if gold_colored else (1.0 if pred_colored == 0 else 0.0)
    )
    f1 = f1_score(precision, recall)
    exact = pred == gold
    return precision, recall, f1, exact, correct, pred_colored, gold_colored


def compute_action_metrics(
    prev_pred: List[int], pred: List[int], prev_gold: List[int], gold: List[int]
) -> Tuple[float, float, float, bool, int, int, int]:
    """
    precision, recall, f1, exact,
    tp (#correct changed tiles), p (#pred changed tiles), g (#gold changed tiles)
    """
    pred_diff = {i for i, (a, b) in enumerate(zip(prev_pred, pred)) if a != b}
    gold_diff = {i for i, (a, b) in enumerate(zip(prev_gold, gold)) if a != b}
    correct = {i for i in pred_diff & gold_diff if pred[i] == gold[i]}

    precision = (
        len(correct) / len(pred_diff) if pred_diff else (1.0 if not gold_diff else 0.0)
    )
    recall = (
        len(correct) / len(gold_diff) if gold_diff else (1.0 if not pred_diff else 0.0)
    )
    f1 = f1_score(precision, recall)
    exact = pred_diff == gold_diff and all(pred[i] == gold[i] for i in pred_diff)
    return precision, recall, f1, exact, len(correct), len(pred_diff), len(gold_diff)


def evaluate_prediction(
    prev_pred: List[int], pred: List[int], prev_gold: List[int], gold: List[int]
) -> Dict[str, float | bool | int]:
    b_prec, b_rec, b_f1, b_exact, b_tp, b_p, b_g = compute_board_metrics(pred, gold)
    a_prec, a_rec, a_f1, a_exact, a_tp, a_p, a_g = compute_action_metrics(
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
        "board_tp": b_tp,
        "board_p": b_p,
        "board_g": b_g,
        "action_tp": a_tp,
        "action_p": a_p,
        "action_g": a_g,
    }
