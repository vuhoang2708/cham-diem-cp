"""
Generate .apx file for AmiBroker COM automation.

Rules learned from Codex retest (2026-05-20):
- FormulaContent must be real multiline text — no \\r\\n escapes, no &#13;&#10; entities
- No raw < in FormulaContent (XML invalid) — use NOT logic instead
- No "\\n" inside AFL string literals — use single-line output with ; separator
- FormulaPath must point to a real .afl file (empty path → AmiBroker modal error)
- Output file: single line, key=value;key=value;ready=1
"""
from __future__ import annotations

from pathlib import Path

# AmiBroker Formulas directory — AFL will be written here so FormulaPath resolves
AMI_FORMULAS_DIR = r"D:\MetakitData\AmibrokerFA\EOD\Formulas"
AFL_SUBDIR = "CodexBridge"
AFL_FILENAME = "ag_bridge.afl"

OUTPUT_FILE = "C:/Users/Public/ag_bridge_out.txt"

# Real multiline AFL — no raw <, no "\n" in strings, no \r\n escapes
# Quadrant logic uses NOT instead of < to avoid raw < in XML
AFL_TEMPLATE = """\
mcdx_Banker   = FA_MCDX(50, 1.5, 50, 20);
mcdx_HotMoney = FA_MCDX(40, 0.7, 30, 20);

bc       = Foreign("VNINDEX", "C");
rs_ratio = FA_RRG(C, bc, 1);
rs_mom   = FA_RRG(C, bc, 0);

bk  = LastValue(mcdx_Banker);
hm  = LastValue(mcdx_HotMoney);
rsr = LastValue(rs_ratio);
rsm = LastValue(rs_mom);

rsr_hi = rsr >= 0;
rsm_hi = rsm >= 0;
quad = IIf(rsr_hi AND rsm_hi, 1, IIf(rsr_hi AND NOT rsm_hi, 2, IIf(NOT rsr_hi AND NOT rsm_hi, 3, 4)));

dx = rs_ratio - Ref(rs_ratio, -1);
dy = rs_mom   - Ref(rs_mom,   -1);
tail5d = LastValue(Sum(sqrt(dx * dx + dy * dy), 5));

outfile = "{output_file}";
fh = fopen(outfile, "w");
fh_ok = 0;

if (fh)
{{
    fh_ok = 1;
    out = "symbol=" + Name();
    out = out + ";banker="   + NumToStr(bk,     1.6);
    out = out + ";hotmoney=" + NumToStr(hm,     1.6);
    out = out + ";rs_ratio=" + NumToStr(rsr,    1.6);
    out = out + ";rs_mom="   + NumToStr(rsm,    1.6);
    out = out + ";quadrant=" + NumToStr(quad,   1.0);
    out = out + ";tail_5d="  + NumToStr(tail5d, 1.6);
    out = out + ";ready=1";
    fputs(out, fh);
    fclose(fh);
}}

Filter = 1;
AddTextColumn(Name(), "symbol", 1.0);
AddColumn(bk,     "banker",   1.6);
AddColumn(hm,     "hotmoney", 1.6);
AddColumn(rsr,    "rs_ratio", 1.6);
AddColumn(rsm,    "rs_mom",   1.6);
AddColumn(quad,   "quadrant", 1.0);
AddColumn(tail5d, "tail_5d",  1.6);
AddColumn(fh_ok,  "fh_ok",   1.0);
"""

# APX template — FormulaContent is real multiline text, FormulaPath points to real AFL
APX_TEMPLATE = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<AmiBroker-Analysis CompactMode="0">
<General>
<FormatVersion>1</FormatVersion>
<Symbol>{symbol}</Symbol>
<FormulaPath>{formula_path}</FormulaPath>
<FormulaContent>{formula_content}</FormulaContent>
<ApplyTo>1</ApplyTo>
<RangeType>1</RangeType>
<RangeAmount>1</RangeAmount>
<FromDate>2020-01-01 00:00:00</FromDate>
<ToDate>2026-12-31</ToDate>
<SyncOnSelect>0</SyncOnSelect>
<RunEvery>0</RunEvery>
<RunEveryInterval>5min</RunEveryInterval>
<IncludeFilter>
<ExcludeMode>0</ExcludeMode>
<OrSelection>0</OrSelection>
<Favourite>0</Favourite>
<Index>0</Index>
<Type0>0</Type0><Category0>-1</Category0>
<Type1>1</Type1><Category1>-1</Category1>
<Type2>2</Type2><Category2>-1</Category2>
<Type3>3</Type3><Category3>-1</Category3>
<Type4>4</Type4><Category4>-1</Category4>
<Type5>5</Type5><Category5>-1</Category5>
<Type6>6</Type6><Category6>-1</Category6>
</IncludeFilter>
<ExcludeFilter>
<ExcludeMode>1</ExcludeMode>
<OrSelection>0</OrSelection>
<Favourite>0</Favourite>
<Index>0</Index>
<Type0>0</Type0><Category0>-1</Category0>
<Type1>1</Type1><Category1>-1</Category1>
<Type2>2</Type2><Category2>-1</Category2>
<Type3>3</Type3><Category3>-1</Category3>
<Type4>4</Type4><Category4>-1</Category4>
<Type5>5</Type5><Category5>-1</Category5>
<Type6>6</Type6><Category6>-1</Category6>
</ExcludeFilter>
</General>
<BacktestSettings>
<InitialEquity>10000</InitialEquity>
<TradeFlags>1</TradeFlags>
<RangeType>1</RangeType>
<RangeLength>1</RangeLength>
<RangeFromDate>2020-01-01 00:00:00</RangeFromDate>
<RangeToDate>2026-12-31</RangeToDate>
<ApplyTo>1</ApplyTo>
</BacktestSettings>
</AmiBroker-Analysis>"""


def ensure_afl(output_file: str = OUTPUT_FILE) -> str:
    """Write the AFL file to AmiBroker Formulas dir. Returns relative path for FormulaPath."""
    afl_dir = Path(AMI_FORMULAS_DIR) / AFL_SUBDIR
    afl_dir.mkdir(parents=True, exist_ok=True)
    afl_path = afl_dir / AFL_FILENAME
    afl_content = AFL_TEMPLATE.format(output_file=output_file)
    afl_path.write_text(afl_content, encoding="utf-8")
    return f"{AFL_SUBDIR}\\{AFL_FILENAME}"


def create_apx(
    symbol: str,
    apx_path: str = r"C:\Users\Public\ag_bridge.apx",
    output_file: str = OUTPUT_FILE,
) -> str:
    """
    Write AFL to AmiBroker Formulas dir, then generate APX pointing to it.
    Returns apx_path.
    """
    formula_rel_path = ensure_afl(output_file)

    # FormulaContent is the same AFL as real multiline text.
    # APX FormulaContent is what AmiBroker imports into Formulas\Imported\ on Open().
    # FormulaPath tells AmiBroker which file to actually run.
    afl_content = AFL_TEMPLATE.format(output_file=output_file)

    content = APX_TEMPLATE.format(
        symbol=symbol,
        formula_path=formula_rel_path,
        formula_content=afl_content,
    )
    Path(apx_path).write_text(content, encoding="iso-8859-1")
    return apx_path


if __name__ == "__main__":
    path = create_apx("VCB")
    print(f"Created APX: {path}")
    afl = Path(AMI_FORMULAS_DIR) / AFL_SUBDIR / AFL_FILENAME
    print(f"AFL written: {afl}")
