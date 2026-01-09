from life_chart_api.temporal.chinese_luck_pillars import build_chinese_luck_pillar_cycles


def test_chinese_luck_pillar_builder_unit():
    chinese_output = {
        "input": {"birth": {"date": "1999-02-26"}},
        "luckCycles": {
            "pillars": [
                {
                    "index": 0,
                    "startAge": 7,
                    "endAge": 17,
                    "pillar": {
                        "stem": "xin",
                        "branch": "mao",
                        "stemElement": "metal",
                        "stemYinYang": "yin",
                        "branchAnimal": "rabbit",
                        "hiddenStems": [],
                        "notes": "",
                    },
                    "themes": ["Example"],
                    "notes": "",
                }
            ]
        },
        "elements": {"favourable": ["metal"], "unfavourable": ["fire"]},
        "dayMaster": {"strength": "strong"},
    }

    cycles = build_chinese_luck_pillar_cycles(
        chinese_system_output=chinese_output,
        range_from="2006-01",
        range_to="2020-12",
        as_of=None,
    )

    assert len(cycles) == 1
    cycle = cycles[0]
    assert cycle["system"] == "chinese"
    assert cycle["kind"] == "luck_pillar"
    assert "pillar:xin-mao" in cycle["themes"]
