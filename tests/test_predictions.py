from types import SimpleNamespace

import pytest

from analytics.predictions import calculate_brier_score, predict_match


def test_brier_score_is_zero_for_perfect_home_prediction():
    assert calculate_brier_score(1.0, 0.0, 0.0, 2, 0) == 0.0


def test_brier_score_penalizes_wrong_result():
    score = calculate_brier_score(0.8, 0.1, 0.1, 0, 1)
    assert score == pytest.approx(1.46)


def test_prediction_probabilities_sum_to_one():
    teams = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    result = predict_match(1, 2, teams, [])
    probabilities = result["probabilities"]
    assert all(0.0 <= value <= 1.0 for value in probabilities.values())
    assert sum(probabilities.values()) == pytest.approx(1.0)
    assert result["expected_home_goals"] > 0
    assert result["expected_away_goals"] > 0


def test_prediction_rejects_same_team():
    teams = [SimpleNamespace(id=1)]
    with pytest.raises(ValueError):
        predict_match(1, 1, teams, [])
