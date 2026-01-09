from life_chart_api.synthesis.overlay_chinese import compute_chinese_tier1, compute_chinese_tier2


def test_chinese_tier2_deterministic():
    tier1 = compute_chinese_tier1("1999-02-26", "14:00:00", "UTC")
    tier2_a = compute_chinese_tier2("1999-02-26", "14:00:00", "UTC", tier1=tier1)
    tier2_b = compute_chinese_tier2("1999-02-26", "14:00:00", "UTC", tier1=tier1)
    assert tier2_a == tier2_b
