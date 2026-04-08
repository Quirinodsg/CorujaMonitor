"""
AI: Feedback Loop Tests — Coruja Monitor v3.0
Tests: outcome classification, weight adjustment.
Requirements: 6.4, 6.7
"""
import pytest

from ai_agents.feedback_loop import (
    FeedbackLoop, RemediationAction, ActionResult,
    POSITIVE_OUTCOME_THRESHOLD_SECONDS,
)


@pytest.mark.ai
class TestFeedbackLoop:
    """Req 6.4, 6.7 — feedback loop outcome and weights."""

    def test_positive_outcome_under_300s(self):
        loop = FeedbackLoop()
        action = RemediationAction(agent_name="test", action_type="restart", target_host="h1")
        aid = loop.record_action(action)
        loop.record_result(aid, ActionResult(success=True, resolution_time_seconds=100.0))
        assert loop.get_history()[0]["outcome"] == "positive"

    def test_negative_outcome_over_300s(self):
        loop = FeedbackLoop()
        action = RemediationAction(agent_name="test", action_type="restart", target_host="h1")
        aid = loop.record_action(action)
        loop.record_result(aid, ActionResult(success=True, resolution_time_seconds=500.0))
        assert loop.get_history()[0]["outcome"] == "negative"

    def test_weight_increases_on_positive(self):
        loop = FeedbackLoop()
        action = RemediationAction(agent_name="test", action_type="scale_up", target_host="h1")
        aid = loop.record_action(action)
        loop.record_result(aid, ActionResult(success=True, resolution_time_seconds=60.0))
        assert loop.get_action_weight("scale_up") > 1.0

    def test_weight_decreases_on_negative(self):
        loop = FeedbackLoop()
        action = RemediationAction(agent_name="test", action_type="scale_down", target_host="h1")
        aid = loop.record_action(action)
        loop.record_result(aid, ActionResult(success=True, resolution_time_seconds=600.0))
        assert loop.get_action_weight("scale_down") < 1.0

    def test_metrics_report(self):
        loop = FeedbackLoop()
        action = RemediationAction(agent_name="test", action_type="restart", target_host="h1")
        aid = loop.record_action(action)
        loop.record_result(aid, ActionResult(success=True, resolution_time_seconds=60.0))
        m = loop.get_metrics()
        assert m.actions_total == 1
        assert m.actions_successful == 1
