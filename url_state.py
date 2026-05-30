"""
URL state encoding and decoding for shareable scenario links.
Pure Python — no Streamlit imports (ARCH-3).
"""
import math
import defaults

PARAM_MAP = {
    'hp':   'HOME_PRICE',
    'mr':   'MORTGAGE_RATE',
    'hoa':  'HOA_MONTHLY',
    'ins':  'HO6_INSURANCE_ANNUAL',
    'tr':   'PROPERTY_TAX_RATE',
    'rent': 'MARKET_RENT',
    'ir':   'INVESTMENT_RETURN_RATE',
    'apr':  'APPRECIATION_RATE',
    'cc':   'CLOSING_COST_PCT',
    'fur':  'FURNITURE_BUDGET',
    'sa':   'SPECIAL_ASSESSMENT_AMOUNT',
    'sam':  'SPECIAL_ASSESSMENT_MONTH',
    'ri':   'RENTAL_INCOME_MONTHLY',
    'vac':  'VACANCY_RATE',
    'mgmt': 'PROPERTY_MGMT_FEE_PCT',
    'rc':   'REALTOR_COMMISSION_PCT',
    'dp':   'DOWN_PCT',
    'yr':   'HORIZON_YEARS',
}

INT_PARAMS = {'sam', 'yr'}

URL_MAX_QUERY_LENGTH = 2000


def encode_state(slider_values: dict) -> dict:
    """Encode slider values to abbreviated URL query params."""
    params = {}
    for short_key, const_name in PARAM_MAP.items():
        if const_name in slider_values:
            params[short_key] = str(slider_values[const_name])
    query_string = '&'.join(f'{k}={v}' for k, v in params.items())
    if len(query_string) > URL_MAX_QUERY_LENGTH:
        raise ValueError(
            f"Encoded URL query string ({len(query_string)} chars) exceeds "
            f"{URL_MAX_QUERY_LENGTH}-character limit (NFR4)"
        )
    return params


def decode_state(query_params: dict) -> dict:
    """Decode URL query params to slider values, falling back to defaults."""
    result = {}
    for short_key, const_name in PARAM_MAP.items():
        default_val = getattr(defaults, const_name)
        raw = query_params.get(short_key)
        if raw is None or raw == '':
            result[const_name] = default_val
        else:
            try:
                parsed = int(raw) if short_key in INT_PARAMS else float(raw)
                if not isinstance(parsed, int) and not math.isfinite(parsed):
                    raise ValueError
                result[const_name] = parsed
            except (ValueError, TypeError):
                result[const_name] = default_val
    return result
