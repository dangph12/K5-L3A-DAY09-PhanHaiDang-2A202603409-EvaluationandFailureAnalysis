# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Case đã replay: C-002@11, FM-03

| Trường | Nội dung |
|---|---|
| Trial | seeded_regression C-002@11; report `E-seeded_regression-20261117-582d`, `src/reports/eval_seeded_regression.json` |
| Triệu chứng | Lab 8 grader: `status resolved != denied`; ledger=20000, refund_count=1 trong khi label=0/0; reply cũng nói hoàn 20.000đ. |
| Bước sai đầu tiên | Event **3**, `model_override`, payload `{"delay_days": 5}`. |
| Vì sao là bước *đầu tiên* | Event 1 handoff chỉ chứa allowlist; event 2 investigator đọc dữ kiện DB hợp lệ (delay_days=2); event 3 mới ghi đè bằng lời ticket; quote 20000 tại event 4 là hậu quả. |
| Failure mode | FM-03 ticket_trust, layer model/prompt. |
| Đối chứng | fixed C-002@11 không có model_override; giữ DB, quote=0, status=denied, ledger=0 và Lab 8 grader PASS. |
| Regression test | `tests/test_lab9_trace_case.py::test_c002_ticket_override_regression`: cùng input/seed, DbFactKept=False trên variant lỗi, True trên fixed; assert ledger lỗi=20000, fixed=0 và Lab 8 verdict tương ứng. |
| Chưa chắc chắn | Trace không chứng minh suy nghĩ nội bộ của model; ca này không kiểm tra mọi cách override kín không phát event, cũng không đại diện model thật. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
