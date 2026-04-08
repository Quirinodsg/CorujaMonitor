"""
Chaos: Packet Loss Tests — Coruja Monitor v3.0
Tests: simulated packet loss 10-50%.
Requirements: 14.3
"""
import pytest


@pytest.mark.chaos
class TestPacketLoss:
    """Req 14.3 — packet loss 10-50% simulation."""

    def test_packet_loss_drops_some(self, chaos_engine):
        """With 50% loss, some packets are dropped."""
        with chaos_engine.simulate_packet_loss(loss_pct=50.0) as ctx:
            for _ in range(100):
                ctx["maybe_drop"]()
            stats = ctx["stats"]
            assert stats["total"] == 100
            assert stats["dropped"] > 0
            assert stats["delivered"] > 0

    def test_zero_loss_delivers_all(self, chaos_engine):
        """With 0% loss, all packets are delivered."""
        with chaos_engine.simulate_packet_loss(loss_pct=0.0) as ctx:
            for _ in range(50):
                ctx["maybe_drop"]()
            assert ctx["stats"]["dropped"] == 0
            assert ctx["stats"]["delivered"] == 50

    def test_send_with_loss_function(self, chaos_engine):
        """send_with_loss delivers or drops based on probability."""
        with chaos_engine.simulate_packet_loss(loss_pct=50.0) as ctx:
            delivered = []
            for i in range(100):
                result = ctx["send_with_loss"](f"data_{i}", lambda d: delivered.append(d))
            assert len(delivered) > 0
            assert len(delivered) < 100
