"""
Property-Based Tests — Matriz de Notificação Inteligente
Feature: notification-matrix
Properties 1-6 (resolve_channels)
"""

import sys
import os
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# Adicionar worker ao path para importar o módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "worker"))

from notification_dispatcher import (
    resolve_channels,
    VALID_CHANNELS,
    VALID_SENSOR_TYPES,
    DEFAULT_MATRIX,
)

settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")


# ─── Strategies ─────────────────────────────────────────────────────────────

# Sensor types válidos (mapeados na DEFAULT_MATRIX)
valid_sensor_types_st = st.sampled_from(sorted(DEFAULT_MATRIX.keys()))

# Sensor types arbitrários (incluindo desconhecidos)
any_sensor_type_st = st.text(min_size=1, max_size=50)

# Canal válido
valid_channel_st = st.sampled_from(sorted(VALID_CHANNELS))

# Canal arbitrário (incluindo inválidos)
any_channel_st = st.text(min_size=1, max_size=30)

# Custom matrix: None ou dicionário com canais arbitrários
custom_matrix_st = st.one_of(
    st.none(),
    st.dictionaries(
        keys=st.text(min_size=1, max_size=30),
        values=st.lists(any_channel_st, min_size=0, max_size=6),
        min_size=0,
        max_size=15,
    ),
)

# Custom matrix com canais válidos apenas
valid_custom_matrix_st = st.one_of(
    st.none(),
    st.dictionaries(
        keys=st.text(min_size=1, max_size=30),
        values=st.lists(valid_channel_st, min_size=1, max_size=6),
        min_size=0,
        max_size=15,
    ),
)


# ─── Property 1: Determinismo da resolução de canais ─────────────────────────
# Feature: notification-matrix, Property 1: Determinismo da resolução de canais
# **Validates: Requirements 10.1, 10.2**


class TestResolveChannelsDeterministic:
    """Propriedade 1: Para qualquer sensor_type e qualquer custom_matrix,
    chamar resolve_channels duas vezes com os mesmos argumentos deve retornar
    exatamente o mesmo conjunto de canais."""

    @settings(max_examples=100)
    @given(sensor_type=any_sensor_type_st, custom_matrix=custom_matrix_st)
    def test_same_inputs_same_output(self, sensor_type, custom_matrix):
        """resolve_channels(s, m) == resolve_channels(s, m) para quaisquer s, m."""
        result1 = resolve_channels(sensor_type, custom_matrix)
        result2 = resolve_channels(sensor_type, custom_matrix)
        assert result1 == result2

    @settings(max_examples=100)
    @given(sensor_type=valid_sensor_types_st)
    def test_default_matrix_deterministic(self, sensor_type):
        """resolve_channels com DEFAULT_MATRIX é determinístico."""
        result1 = resolve_channels(sensor_type)
        result2 = resolve_channels(sensor_type)
        assert result1 == result2


# ─── Property 2: Email sempre presente ───────────────────────────────────────
# Feature: notification-matrix, Property 2: Email sempre presente
# **Validates: Requirements 8.1**


class TestResolveChannelsEmailAlwaysPresent:
    """Propriedade 2: Para qualquer sensor_type válido (exceto network_in e
    network_out que são metric_only) e qualquer custom_matrix válida,
    o conjunto retornado deve sempre conter 'email'."""

    @settings(max_examples=100)
    @given(sensor_type=valid_sensor_types_st, custom_matrix=valid_custom_matrix_st)
    def test_email_in_result_for_valid_sensors(self, sensor_type, custom_matrix):
        """'email' está sempre presente no resultado para sensor_types válidos."""
        result = resolve_channels(sensor_type, custom_matrix)
        assert "email" in result

    @settings(max_examples=100)
    @given(sensor_type=valid_sensor_types_st)
    def test_email_in_default_matrix(self, sensor_type):
        """'email' está presente no resultado usando DEFAULT_MATRIX."""
        result = resolve_channels(sensor_type)
        assert "email" in result


# ─── Property 3: Resultado não-vazio ─────────────────────────────────────────
# Feature: notification-matrix, Property 3: Resultado não-vazio
# **Validates: Requirements 10.3**


class TestResolveChannelsNonEmpty:
    """Propriedade 3: Para qualquer sensor_type (incluindo tipos desconhecidos)
    e qualquer custom_matrix, resolve_channels deve retornar um conjunto com
    pelo menos um canal."""

    @settings(max_examples=100)
    @given(sensor_type=any_sensor_type_st, custom_matrix=custom_matrix_st)
    def test_result_never_empty(self, sensor_type, custom_matrix):
        """O resultado nunca é um conjunto vazio."""
        result = resolve_channels(sensor_type, custom_matrix)
        assert len(result) >= 1

    @settings(max_examples=100)
    @given(sensor_type=any_sensor_type_st)
    def test_result_never_empty_default(self, sensor_type):
        """O resultado nunca é vazio mesmo sem custom_matrix."""
        result = resolve_channels(sensor_type)
        assert len(result) >= 1


# ─── Property 4: Fallback seguro para tipos desconhecidos ────────────────────
# Feature: notification-matrix, Property 4: Fallback seguro para tipos desconhecidos
# **Validates: Requirements 10.4**


class TestResolveChannelsFallbackUnknown:
    """Propriedade 4: Para qualquer string sensor_type que não esteja mapeada
    nem na custom_matrix nem na DEFAULT_MATRIX, resolve_channels deve retornar
    um conjunto contendo pelo menos 'email'."""

    @settings(max_examples=100)
    @given(sensor_type=any_sensor_type_st, custom_matrix=custom_matrix_st)
    def test_unknown_type_gets_email_fallback(self, sensor_type, custom_matrix):
        """Tipos desconhecidos recebem pelo menos 'email'."""
        # Filtrar para sensor_types que não estão em nenhuma matriz
        in_custom = custom_matrix is not None and sensor_type in custom_matrix
        in_default = sensor_type in DEFAULT_MATRIX
        assume(not in_custom and not in_default)

        result = resolve_channels(sensor_type, custom_matrix)
        assert "email" in result


# ─── Property 5: Custom matrix sobrescreve default com fallback ──────────────
# Feature: notification-matrix, Property 5: Custom matrix sobrescreve default
# **Validates: Requirements 11.6, 11.7**


class TestResolveChannelsCustomOverride:
    """Propriedade 5: Para qualquer sensor_type e qualquer custom_matrix não-nula
    que contenha esse sensor_type, resolve_channels deve retornar os canais
    definidos na custom_matrix (não os da DEFAULT_MATRIX). Se a custom_matrix
    for None ou não contiver o sensor_type, deve retornar os canais da
    DEFAULT_MATRIX."""

    @settings(max_examples=100)
    @given(
        sensor_type=valid_sensor_types_st,
        custom_channels=st.lists(valid_channel_st, min_size=1, max_size=6),
    )
    def test_custom_matrix_overrides_default(self, sensor_type, custom_channels):
        """Quando custom_matrix contém o sensor_type, usa canais do custom."""
        custom = {sensor_type: custom_channels}
        result = resolve_channels(sensor_type, custom)
        expected = set(custom_channels) & VALID_CHANNELS
        if not expected:
            expected = {"email"}
        assert result == expected

    @settings(max_examples=100)
    @given(sensor_type=valid_sensor_types_st)
    def test_none_matrix_uses_default(self, sensor_type):
        """Quando custom_matrix é None, usa DEFAULT_MATRIX."""
        result = resolve_channels(sensor_type, None)
        expected = set(DEFAULT_MATRIX[sensor_type]) & VALID_CHANNELS
        if not expected:
            expected = {"email"}
        assert result == expected

    @settings(max_examples=100)
    @given(
        sensor_type=valid_sensor_types_st,
        other_type=st.text(min_size=1, max_size=30),
    )
    def test_missing_in_custom_falls_back_to_default(self, sensor_type, other_type):
        """Quando sensor_type não está na custom_matrix, usa DEFAULT_MATRIX."""
        assume(other_type != sensor_type)
        custom = {other_type: ["sms"]}
        result = resolve_channels(sensor_type, custom)
        expected = set(DEFAULT_MATRIX[sensor_type]) & VALID_CHANNELS
        if not expected:
            expected = {"email"}
        assert result == expected


# ─── Property 6: Somente canais válidos ──────────────────────────────────────
# Feature: notification-matrix, Property 6: Somente canais válidos
# **Validates: Requirements 10.1, 10.5**


class TestResolveChannelsValidOnly:
    """Propriedade 6: Para qualquer sensor_type e qualquer custom_matrix
    (incluindo matrizes com canais inválidos), resolve_channels deve retornar
    apenas canais pertencentes ao conjunto VALID_CHANNELS."""

    @settings(max_examples=100)
    @given(sensor_type=any_sensor_type_st, custom_matrix=custom_matrix_st)
    def test_result_subset_of_valid_channels(self, sensor_type, custom_matrix):
        """Todos os canais retornados pertencem a VALID_CHANNELS."""
        result = resolve_channels(sensor_type, custom_matrix)
        assert result.issubset(VALID_CHANNELS)

    @settings(max_examples=100)
    @given(
        sensor_type=valid_sensor_types_st,
        invalid_channels=st.lists(
            st.text(min_size=1, max_size=30).filter(lambda c: c not in VALID_CHANNELS),
            min_size=1,
            max_size=5,
        ),
    )
    def test_invalid_channels_filtered_out(self, sensor_type, invalid_channels):
        """Canais inválidos na custom_matrix são filtrados."""
        custom = {sensor_type: invalid_channels}
        result = resolve_channels(sensor_type, custom)
        # Nenhum canal inválido deve estar no resultado
        for ch in invalid_channels:
            if ch not in VALID_CHANNELS:
                assert ch not in result
        # Resultado deve ter pelo menos email (fallback)
        assert len(result) >= 1
