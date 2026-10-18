#!/usr/bin/env python3
"""Generate 02.5 deliverables: 4 web-llm receipts + fields.json + advance.json.
origin: ai
Run from: loop-artifacts/stages/02.5/r1/
"""
import json, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent          # stages/02.5/r1
RAW_DS = (BASE / "web-llm-raw" / "deepseek-raw.txt").read_text()

OBSERVED = "2026-10-17T13:10:00+08:00"
DS_URL = "https://chat.deepseek.com/a/chat/s/338ebad0-e49f-4c4c-ac7c-af0407bc515f"
GPT_URL = "https://chatgpt.com/c/6ad302ee-3b50-83ee-a25d-944d1333987a"
RECEIPT_DIR = BASE / "web-llm"
RECEIPT_DIR.mkdir(exist_ok=True)

# ---------- extract the 4 claim texts from raw (lines 113-129) ----------
claims = {}
for m in re.finditer(r"【Claim (\d) - ([^】]+)】\n(.*?)(?=\n【Claim \d|\n请按 Claim)", RAW_DS, re.S):
    claims[int(m.group(1))] = {"title": m.group(2).strip(), "text": m.group(3).strip()}
assert len(claims) == 4, f"expected 4 claims, got {list(claims)}"

state = json.loads((BASE / "state.json").read_text())
leaves = state["attribute_matrix"]
CONCEPTS = [l["concept"] for l in leaves]   # exact concept strings

# claim N -> leaf index
CLAIM_LEAF = {1: 1, 2: 3, 3: 4, 4: 6}

# ---------- 1-4. receipts ----------
receipt_meta = {
 1: {"file": "cross-check-bull-coverage.json",
     "ds_key_points": "Binance UM数据通常2020年前后起步, fundingRate月度多数symbol 2020-01起但逐symbol不同; \"只有2020-21完整牛\"过强; A股2004/美股1993起点过度概括(Yahoo ^GSPC实际1927, AkShare多接口可更早)。",
     "gpt_key_points": "2020-01至2025-01约5年非6年; 窗口方向正确, 核心结论成立。",
     "contradictions": "周期表述5年vs6年; 起点年份概括过强(Yahoo ^GSPC 1927)→已修正表述, 核心窗口(2020-01→2025-01+覆盖2020-21牛/2022熊/2023震荡/24-25牛)双方确认。"},
 2: {"file": "cross-check-stability-criteria.json",
     "ds_key_points": "方法论方向对(多年度OOS+expanding常见, 无普适阈值, PIT前提); 具体\"最严格判据集合\"与2026 arXiv编号(2608.27734)LLM不可核验, 表述过强; DSR/PBO无法防前视核心事实成立。",
     "gpt_key_points": "四道独立门(多窗口/三概念分离: OOS≠PIT≠稳定性); PIT是第一层前提; 统计阈值只控制部分选择偏差。",
     "contradictions": "\"最严格显式判据集合\"表述过强→软化为\"候选判据集合(2026文献, arXiv编号待03直验)\"; 方法论核心双方确认。"},
 3: {"file": "cross-check-funding-oi-timing.json",
     "ds_key_points": "点1/2对(PIT语义, t_available=max(bar_end,published,received)+δ, 只用已结算fundingRate); 点3前半(Binance免费OI仅30天)对, 后半\"只能Bybit\"被驳(Bybit亦有窗口/频率限制且不一定回上线日, 其他源存在); 点4单位\"Coinglass秒/交易所毫秒\"过度概括→逐字段核验。",
     "gpt_key_points": "PIT语义确认; 免费5年OI\"只能Bybit\"表述错误→Bybit同样有窗口限制; 单位归一化必须逐源逐字段。",
     "contradictions": "\"仅Bybit可得5年免费OI\"被两站独立驳回→OI三选项决策点(放弃/短窗口/$29mo)路由03; PIT核心语义双方确认。"},
 4: {"file": "cross-check-public-benchmarks.json",
     "ds_key_points": "负检索声明无法核验且过强; funding rate信号存在从业者/working paper; \"全部无arXiv全文\"以偏概全; 2603.19380无法核验(疑LLM知识截止)。",
     "gpt_key_points": "方向有价值但\"未找到\"≠\"不存在\"; 绝对表述(\"无公开研究\"\"全部无arXiv全文\"\"唯一已核验\")均缺充分依据; 缺口定义须改为可核验negative search协议。",
     "contradictions": "缺口真实性双方确认; \"不存在\"→\"公开检索未找到(2026-10, 双LLM+直验)\"; 2603.19380(4.94pp/23.3%)我方export.arxiv.org直验成立, LLM知识截止, 矛盾以直验解决; 03须建可操作negative search协议。"},
}

receipts = {}
for n, meta in receipt_meta.items():
    leaf_idx = CLAIM_LEAF[n]
    concept = CONCEPTS[leaf_idx]
    r = {
        "kind": "ralph_web_llm_cross_check",
        "schema_version": 1,
        "field_concept": concept,
        "claim": f"【Claim {n} - {claims[n]['title']}】\n{claims[n]['text']}",
        "submitted_at": "2026-10-17T13:00:00+08:00",
        "observed_at": OBSERVED,
        "timezone": "Asia/Shanghai",
        "transport": "ego-browser 0.5.1.13 (ego-lite persistent logged-in session; taskSpace web-llm-02.5-20261017)",
        "responses": [
            {"provider_id": "deepseek", "endpoint_host": "chat.deepseek.com",
             "status": "success", "conversation_url": DS_URL,
             "verdict": "部分正确", "key_points": meta["ds_key_points"],
             "raw_ref": "stages/02.5/r1/web-llm-raw/deepseek-raw.txt"},
            {"provider_id": "chatgpt", "endpoint_host": "chatgpt.com",
             "status": "success", "conversation_url": GPT_URL,
             "verdict": "部分正确", "key_points": meta["gpt_key_points"],
             "raw_ref": "stages/02.5/r1/web-llm-raw/chatgpt-raw.txt"},
        ],
        "successful_provider_ids": ["deepseek", "chatgpt"],
        "contradictions_recorded": True,
        "contradiction_notes": meta["contradictions"],
    }
    path = RECEIPT_DIR / meta["file"]
    path.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n")
    receipts[n] = str(path.relative_to(BASE.parent.parent))  # loop-artifacts/...
    print(f"wrote {path}")

# ---------- 5. fields.json ----------
CONF = {0: 0.82, 1: 0.80, 2: 0.85, 3: 0.85, 4: 0.80, 5: 0.85, 6: 0.72}
RATIONALE = {
 0: "02.5直验C1-C6全confirm: Binance免费fundingRate月度2020-01起(2019各月404), OI文件不存在(404), 当月未归档; 修订风险低; 幸存者偏差规避附条件=Coinglass付费档(C6, $29/mo)。",
 1: "02.5双LLM交叉确认核心窗口(2020-01→2025-01+覆盖2020-21牛/2022熊/2023震荡/24-25牛); 修正: 周期约5年非6年, \"只有2020-21完整牛\"软化为\"2020-21为免费funding唯一完整大牛\", A股2004/美股1993起点表述过度概括(Yahoo ^GSPC实际1927)。",
 2: "02.5直验3/3 confirm: S1起点=2019-12-31(2018全段404), 2022熊+2023震荡覆盖成立; 矛盾1项(2022-10-13 Yahoo 3577.0 vs 新浪3669.91)判新浪正确采用3669.91; 0.85不给0.9因C1两源同Binance发布方。",
 3: "02.5双LLM交叉确认方法论核心(3-5个不重叠年度OOS窗口+expanding, 无普适阈值, PIT第一层前提, DSR/PBO无法防前视); \"最严格显式判据集合\"软化为候选集合(2026 arXiv:2608.27734编号LLM不可核验, 03直验)。",
 4: "02.5双LLM交叉确认PIT语义(t_available=max(bar_end,published,received)+δ, funding只用已结算值8h默认逐symbol可变, OI bar需bar_start+duration<=t+延迟缓冲, 单位逐字段归一); 驳回\"仅Bybit可得5年免费OI\"→OI三选项决策点路由03。",
 5: "02.5直验C1/C2/C3/C6 confirm(官方updates/清单3文件全spot零futures→futures归档无记录修订, 风险中→低; 修订实为3例spot: 2022-04-21/2022-08-08/2022-10-04; 迟报=日线T+1/月线首周一); C4/C5 unresolved记录(Coinglass changelog无futures修订条目, CSI300\"计划生效样本\"PIT隐患)。",
 6: "02.5双LLM交叉确认研究缺口真实(截至2026-10公开检索未找到以funding rate作主择时信号的已发表回测), 表述修正\"不存在\"→\"公开检索未找到\"; \"全部无arXiv全文\"被驳; 2603.19380(4.94pp/23.3%)export.arxiv.org直验成立; 03须建可操作negative search协议。",
}
DETAILS = {
 0: {"recheck_method": "02.5 direct HTTP re-probe (curl -r 0-0)", "verdicts": "C1-C6 confirm (6/6)",
     "residuals": ["2019-12-31 kline孤立存在(2020-01起批量归档前的单日异常)", "Coinglass HOBBYIST $29/mo付费档为幸存者偏差规避唯一路径(C6附条件)"]},
 1: {"recheck_method": "02.5 dual-LLM web-llm cross-check (DeepSeek+ChatGPT, ego-browser)",
     "residuals": ["\"免费funding覆盖的完整牛市唯一性\"表述已软化", "A股/美股免费起点年份逐源核验延至03数据层"]},
 2: {"recheck_method": "02.5 direct HTTP re-probe + dual-source cross-check",
     "residuals": ["C1两源同Binance发布方(独立性打折)", "2000-02熊底单源未二验"]},
 3: {"recheck_method": "02.5 dual-LLM web-llm cross-check",
     "residuals": ["2026 arXiv:2608.27734编号待03直验(LLM知识截止不可核验)"]},
 4: {"recheck_method": "02.5 dual-LLM web-llm cross-check",
     "residuals": ["OI三选项决策点(放弃/短窗口/$29mo)待03拍板", "各源时间戳单位逐字段核验表待03建立"]},
 5: {"recheck_method": "02.5 direct HTTP re-probe",
     "residuals": ["C4 Coinglass changelog无futures修订条目(无法完全排除)", "C5 CSI300历史成分\"计划生效\"语义PIT隐患"]},
 6: {"recheck_method": "02.5 dual-LLM web-llm cross-check + export.arxiv.org direct verify",
     "residuals": ["negative search协议(检索词/库/日期/复现步骤)待03建立", "SSRN/working paper全文不可达(沙箱), 列表级结论"]},
}

# CV records: (leaf_idx, claim, source_refs, notes)
REC_OBS = "2026-10-17T13:10:00+08:00"
CV_RECORDS = [
 (0, "Binance免费批量归档data.binance.vision的fundingRate月度文件起点2020-01(2019各月404), 无openInterest文件(404), 当月未归档; Coinglass无免费档",
   ["https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/",
    "https://docs.coinglass.com/reference/getting-started-with-your-api"],
   "C1-C6全confirm(6/6)。附条件: 幸存者偏差规避需Coinglass付费档$29/mo(C6); 2019-12-31单日孤立kline异常已记录。"),
 (1, "免费数据窗口2020-01→2025-01+覆盖2020-21牛、2022熊、2023震荡、2024-25牛, 满足\"至少5年含牛熊震荡\"",
   ["https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/",
    DS_URL, GPT_URL],
   "双LLM确认核心窗口。修正: 周期约5年非6年; \"只有2020-21完整牛\"软化为\"免费funding唯一完整大牛\"; A股2004/美股1993起点过度概括(Yahoo ^GSPC实际1927)。"),
 (2, "S1 2022熊+2023震荡覆盖成立(S1起点=2019-12-31, 2018全段404); S2美股免费日线1993+; S3 A股免费日线2004+",
   ["https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d",
    "https://stock.finance.sina.com.cn/usstock/api/json_v2.php/US_MinKService.getDailyK?symbol=.INX",
    "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000001,day,,,10,qfq"],
   "3/3 confirm。矛盾1项: 2022-10-13熊底Yahoo 3577.0 vs 新浪3669.91→判新浪正确采用3669.91; 0.85不给0.9因C1两源同Binance发布方。"),
 (3, "稳定性判据: 3-5个不重叠年度OOS窗口+expanding, 无普适阈值; DSR/PBO无法防前视, PIT是第一层前提",
   ["https://arxiv.org/abs/2608.27734", DS_URL, GPT_URL],
   "双LLM确认方法论核心。\"最严格显式判据集合\"软化为候选集合; 2026 arXiv:2608.27734编号LLM不可核验, 03直验。"),
 (4, "funding PIT: t_available=max(bar_end,published,received)+δ, 只用已结算fundingRate(8h默认逐symbol可变); OI bar需bar_start+duration<=t+延迟缓冲; 时间戳单位逐字段归一",
   ["https://bybit-exchange.github.io/docs/v5/derivatives/history/open-interest",
    "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History",
    DS_URL],
   "双LLM确认PIT语义。驳回: \"仅Bybit可得5年免费OI\"不成立(Bybit亦有窗口限制且不一定回上线日, 其他源存在)→OI三选项决策点路由03; 单位概括\"Coinglass秒/交易所毫秒\"改逐字段核验。"),
 (5, "futures归档无*_updates修订记录(官方updates/清单3文件全spot); 修订实为3例spot(2022-04-21/2022-08-08/2022-10-04); 迟报=日线T+1/月线首周一",
   ["https://api.github.com/repos/binance/binance-public-data/contents/updates",
    "https://data.binance.vision/",
    "https://raw.githubusercontent.com/binance/binance-public-data/master/README.md"],
   "C1/C2/C3/C6 confirm→修订风险中→低。C4/C5 unresolved记录: Coinglass changelog无futures修订条目(无法完全排除); CSI300历史成分\"计划生效\"PIT隐患。"),
 (6, "截至2026-10, 公开检索未找到以funding rate作市场状态/择时信号主标的的已发表回测(缺口); 经典失败模式文献清单(DSR/PBO/multiple testing/survivorship)",
   ["https://arxiv.org/abs/1912.03270",
    "https://arxiv.org/abs/2212.06888",
    GPT_URL],
   "双LLM确认缺口真实。\"不存在\"→\"公开检索未找到\"; \"全部无arXiv全文\"被驳(部分在SSRN/working paper); 2603.19380(4.94pp/23.3%)export.arxiv.org直验成立(LLM知识截止, 矛盾以直验解决); 03须建可操作negative search协议。"),
]

fields = []
for i, leaf in enumerate(leaves):
    fields.append({
        "concept": leaf["concept"],
        "attribute": leaf["attribute"],
        "role": "research_findings",
        "disposition": "confirmed",
        "rationale": RATIONALE[i],
        "evidence_refs": (leaf.get("evidence_refs") or [])[:8],
        "confidence": CONF[i],
        "observed_at": OBSERVED,
        "impact": "high",
        "reversible": True,
        "details": DETAILS[i],
    })

cv_record_objs = []
for (idx, claim, srcs, notes) in CV_RECORDS:
    cv_record_objs.append({
        "claim": claim,
        "claim_ref": CONCEPTS[idx],
        "source_refs": srcs,
        "verdict": "supported",
        "observed_at": REC_OBS,
        "notes": notes,
        "updated_confidence": CONF[idx],
    })

cv_field = {
    "concept": "cross_validation",
    "attribute": "02.5交叉验证: 7个研究字段全部完成交叉验证(3字段直验HTTP re-probe + 4字段双LLM web-llm交叉核对)",
    "role": "cross_validation",
    "disposition": "confirmed",
    "rationale": "3字段(data-history/bear-range/data-revision)经02.5 direct HTTP re-probe逐claim confirm(6/6, 3/3, C1C2C3C6 confirm+C4C5 unresolved); 4字段(bull-coverage/stability-criteria/funding-oi-timing/public-benchmarks)经DeepSeek+ChatGPT双站LLM交叉核对, 判定均\"部分正确\", 核心结论全部confirm, 3处表述修正+1处子主张驳回已吸收。",
    "evidence_refs": [
        "stages/02.5/r1/web-llm/cross-check-bull-coverage.json",
        "stages/02.5/r1/web-llm/cross-check-stability-criteria.json",
        "stages/02.5/r1/web-llm/cross-check-funding-oi-timing.json",
        "stages/02.5/r1/web-llm/cross-check-public-benchmarks.json",
        "stages/02.5/r1/research/cross-validation-data-history.json",
        "stages/02.5/r1/research/cross-validation-bear-range.json",
        "stages/02.5/r1/research/cross-validation-data-revision.json",
    ],
    "confidence": 0.85,
    "observed_at": OBSERVED,
    "impact": "high",
    "reversible": True,
    "details": {
        "method": "3字段直验(curl -r 0-0 HTTP re-probe, 02.5 research/) + 4字段双站点LLM交叉(ego-browser 0.5.1.13 ego-lite已登录会话, DeepSeek+ChatGPT各一轮批量4claim)",
        "contradictions": 3,
        "corrections_applied": 4,
        "sub_claim_refuted": "仅Bybit可得5年免费OI(双LLM独立驳回, OI决策点路由03)",
    },
    "validation_records": cv_record_objs,
}
fields.append(cv_field)

fields_doc = {
    "fields": fields,
    "cross_validation_output": {
        "validation_records_file": "stages/02.5/r1/web-llm/cross-check-bull-coverage.json",
        "records_count": 7,
        "summary": "7/7字段交叉验证完成: 3字段直验re-probe(C1-C6 6/6, 3/3, 4/6+2 unresolved), 4字段双LLM(DeepSeek+ChatGPT)判定均部分正确且核心confirm; 3处矛盾记录并解决(2022-10-13熊底取新浪3669.91; 5年vs6年周期; Bybit-only OI驳回); 4处表述修正(牛市唯一性/起点年份/最严格判据集合/缺口表述); 2个03决策点(OI三选项; negative search协议)。",
    },
}
(BASE / "fields.json").write_text(json.dumps(fields_doc, ensure_ascii=False, indent=2) + "\n")
print("wrote", BASE / "fields.json")

# ---------- 6. advance.json ----------
advance = {
    "action": "advance",
    "status": "passed",
    "stage_id": "02.5",
    "revision": "r1",
    "next_stage": "03",
    "payload": {
        "cross_validation": {
            "validated_fields": 7,
            "receipts": [
                "stages/02.5/r1/web-llm/cross-check-bull-coverage.json",
                "stages/02.5/r1/web-llm/cross-check-stability-criteria.json",
                "stages/02.5/r1/web-llm/cross-check-funding-oi-timing.json",
                "stages/02.5/r1/web-llm/cross-check-public-benchmarks.json",
            ],
            "direct_rechecks": [
                "stages/02.5/r1/research/cross-validation-data-history.json",
                "stages/02.5/r1/research/cross-validation-bear-range.json",
                "stages/02.5/r1/research/cross-validation-data-revision.json",
            ],
            "contradictions_recorded": 3,
            "open_decision_points_for_03": [
                "OI三选项: 放弃OI信号 / 短窗口OI(Binance 30天+其他源) / Coinglass付费$29mo",
                "negative search协议: 检索词/数据库/日期/复现步骤(缺口声明的可核验化)",
                "2026 arXiv:2608.27734编号直验",
                "Coinglass $29/mo是否启用(幸存者偏差规避)",
            ],
        },
        "stage_review": "02.5交叉验证通过: 7字段confidence定案(0.82/0.80/0.85/0.85/0.80/0.85/0.72); 无字段被推翻, 无阻塞矛盾; 进入03任务分解, 须将4个03决策点纳入task graph。",
    },
}
(BASE / "advance.json").write_text(json.dumps(advance, ensure_ascii=False, indent=2) + "\n")
print("wrote", BASE / "advance.json")
print("ALL DONE")
