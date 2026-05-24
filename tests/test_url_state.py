import pytest
import defaults
from url_state import encode_state, decode_state, PARAM_MAP, INT_PARAMS, URL_MAX_QUERY_LENGTH


def _miami_defaults():
    """Build a full slider_values dict from Miami defaults."""
    return {const_name: getattr(defaults, const_name) for const_name in PARAM_MAP.values()}


# ── encode_state ──────────────────────────────────────────────────────────────

def test_encode_returns_abbreviated_keys():
    params = encode_state(_miami_defaults())
    assert 'hp' in params
    assert 'HOME_PRICE' not in params


def test_encode_covers_all_params():
    params = encode_state(_miami_defaults())
    assert set(params.keys()) == set(PARAM_MAP.keys())


def test_encode_home_price_as_string():
    params = encode_state(_miami_defaults())
    assert params['hp'] == str(defaults.HOME_PRICE)


def test_encode_query_string_within_budget():
    params = encode_state(_miami_defaults())
    query = '&'.join(f'{k}={v}' for k, v in params.items())
    assert len(query) <= URL_MAX_QUERY_LENGTH


def test_encode_raises_on_budget_overflow():
    # Fabricate a value long enough to overflow 2000 chars
    oversize = {const: 'x' * 200 for const in PARAM_MAP.values()}
    with pytest.raises(ValueError, match="exceeds"):
        encode_state(oversize)


def test_encode_ignores_unknown_keys():
    # Extra keys not in PARAM_MAP are silently dropped
    values = _miami_defaults()
    values['UNKNOWN_KEY'] = 99999
    params = encode_state(values)
    assert set(params.keys()) == set(PARAM_MAP.keys())


def test_encode_partial_dict_only_encodes_present_keys():
    params = encode_state({'HOME_PRICE': 350_000.0})
    assert 'hp' in params
    assert len(params) == 1


# ── decode_state ──────────────────────────────────────────────────────────────

def test_decode_home_price_as_float():
    result = decode_state({'hp': '350000.0'})
    assert result['HOME_PRICE'] == 350_000.0
    assert isinstance(result['HOME_PRICE'], float)


def test_decode_special_assessment_month_as_int():
    result = decode_state({'sam': '12'})
    assert result['SPECIAL_ASSESSMENT_MONTH'] == 12
    assert isinstance(result['SPECIAL_ASSESSMENT_MONTH'], int)


def test_decode_all_non_int_params_are_floats():
    result = decode_state({k: '1.0' for k in PARAM_MAP.keys()})
    for short_key, const_name in PARAM_MAP.items():
        if short_key not in INT_PARAMS:
            assert isinstance(result[const_name], float), f"{const_name} should be float"


def test_decode_empty_params_falls_back_to_all_defaults():
    result = decode_state({})
    for const_name in PARAM_MAP.values():
        assert result[const_name] == getattr(defaults, const_name)


def test_decode_missing_single_key_falls_back_to_default():
    result = decode_state({'hp': '400000.0'})  # only home price provided
    assert result['HOME_PRICE'] == 400_000.0
    assert result['MORTGAGE_RATE'] == defaults.MORTGAGE_RATE  # fallback


def test_decode_invalid_value_falls_back_to_default():
    result = decode_state({'hp': 'not-a-number'})
    assert result['HOME_PRICE'] == defaults.HOME_PRICE


def test_decode_empty_string_falls_back_to_default():
    result = decode_state({'mr': ''})
    assert result['MORTGAGE_RATE'] == defaults.MORTGAGE_RATE


def test_decode_unrecognized_key_is_ignored():
    # Should still return all defaults without error
    result = decode_state({'unknown_key': '999'})
    assert result['HOME_PRICE'] == defaults.HOME_PRICE


def test_decode_inf_falls_back_to_default():
    result = decode_state({'hp': 'inf'})
    assert result['HOME_PRICE'] == defaults.HOME_PRICE


def test_decode_nan_falls_back_to_default():
    result = decode_state({'mr': 'nan'})
    assert result['MORTGAGE_RATE'] == defaults.MORTGAGE_RATE


# ── Round-trip ────────────────────────────────────────────────────────────────

def test_roundtrip_miami_defaults():
    original = _miami_defaults()
    decoded = decode_state(encode_state(original))
    for const_name, val in original.items():
        assert abs(decoded[const_name] - val) < 0.001, \
            f"Round-trip mismatch for {const_name}: {val} -> {decoded[const_name]}"


def test_roundtrip_non_default_values():
    values = _miami_defaults()
    values['HOME_PRICE'] = 450_000.0
    values['MORTGAGE_RATE'] = 7.25
    values['SPECIAL_ASSESSMENT_MONTH'] = 36
    decoded = decode_state(encode_state(values))
    assert abs(decoded['HOME_PRICE'] - 450_000.0) < 0.001
    assert abs(decoded['MORTGAGE_RATE'] - 7.25) < 0.001
    assert decoded['SPECIAL_ASSESSMENT_MONTH'] == 36


def test_roundtrip_zero_special_assessment():
    values = _miami_defaults()
    values['SPECIAL_ASSESSMENT_AMOUNT'] = 0.0
    decoded = decode_state(encode_state(values))
    assert decoded['SPECIAL_ASSESSMENT_AMOUNT'] == 0.0


# ── NFR3: Performance < 100ms ─────────────────────────────────────────────────

def test_encode_is_fast_nfr3():
    import time
    values = _miami_defaults()
    start = time.perf_counter()
    for _ in range(1000):
        encode_state(values)
    elapsed_ms = (time.perf_counter() - start) * 1000 / 1000
    assert elapsed_ms < 100, f"encode_state took {elapsed_ms:.2f}ms avg (NFR3 limit: 100ms)"


def test_decode_is_fast_nfr3():
    import time
    params = encode_state(_miami_defaults())
    start = time.perf_counter()
    for _ in range(1000):
        decode_state(params)
    elapsed_ms = (time.perf_counter() - start) * 1000 / 1000
    assert elapsed_ms < 100, f"decode_state took {elapsed_ms:.2f}ms avg (NFR3 limit: 100ms)"
