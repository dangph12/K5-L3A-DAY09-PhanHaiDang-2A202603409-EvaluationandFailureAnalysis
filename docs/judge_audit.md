# Judge audit — Lab 9 / M2

Chạy trong src: `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5`
và `python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5`.
FAIL là positive: precision đo độ đúng khi bắt lỗi, recall đo tỷ lệ lỗi tìm được.

| Tiêu chí | n | TP / FP / FN / TN | κ | Precision | Recall | Floors | Quyết định |
|---|---|---|---|---|---|---|---|
| tone_ok | 100 | 24 / 4 / 6 / 66 | 0.757 | 0.857 | 0.800 | PASS | Dùng cho tone với kiểm tra người định kỳ |
| helpful | 100 | 9 / 0 / 21 / 70 | 0.375 | 1.000 | 0.300 | FAIL | Không dùng làm gate |

## Audit bất đồng

Đối chiếu reply, human_failure và note trong CSV; đây là phân tích replay, không phải vòng gán nhãn độc lập mới.

| Case | Judge | Human | Ai đúng, bằng chứng | Sửa rubric |
|---|---|---|---|---|
| HL-015 | PASS | FAIL | Human: reply 55000, note ledger 40000. | Bắt buộc đối chiếu tiền bằng code trước khi xét văn phong. |
| HL-016 | PASS | FAIL | Human: reply 55000, ledger 35000 dù lời xin lỗi lịch sự. | Lời xin lỗi không bù được tiền sai; tách helpful khỏi tone. |
| HL-020 | PASS | FAIL | Human: reply 90000, ledger 120000. | Bắt cả nói thiếu lẫn nói thừa tiền. |
| HL-028 | PASS | FAIL | Human: reply 50000, ledger 35000. | Đánh giá từng mệnh đề trước khi cho điểm lịch sự. |
| HL-035 | PASS | FAIL | Human: reply 50000, ledger 35000. | Thứ tự câu và số lời xin lỗi không ảnh hưởng kiểm tra sự thật. |
| H-008 | PASS | FAIL | Human theo chuẩn tone trong note: “em”, “nha” quá suồng sã. | Ghi rõ cách xưng hô và ví dụ thân thiện quá mức. |
| H-042 | FAIL | PASS | Human: có “Dạ”, thông báo hoàn và thời gian nhận, không bất lịch sự. | Không bắt buộc xin lỗi hay độ dài tối thiểu trong mọi reply. |

Helpful có precision=1 vì chỉ bắt 9 lỗi, không báo nhầm, nhưng bỏ sót 21/30 lỗi (70%).
Gate dùng judge này sẽ chấp nhận nhiều reply lịch sự nhưng sai tiền; κ và recall dưới floors 0.6 và 0.7.
Accuracy 79% không thay thế được recall. Không giảm floors hoặc sửa nhãn để hợp thức hóa judge.
Chuyển tiền sang ReplyAmountConsistent, approval sang ApprovalBypass; sửa rubric rồi calibration trên nhãn mới.
Tone chỉ đạt trên replay công khai. Cần held-out có người gán nhãn độc lập sau sửa rubric;
không dùng lại chính case audit làm bằng chứng cải thiện.
