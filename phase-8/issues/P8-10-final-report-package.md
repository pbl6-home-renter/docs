# P8-10 — Viết báo cáo cuối kỳ theo mẫu và bàn giao DOCX/PDF

**Epic:** Phase 8  
**Trạng thái:** 🟡 Open  
**Người phụ trách:** `ThaiBao11125` (Võ Hoàng Thái Bảo — Lead Report Author)  
**Người review:** `baoduong17` / PM  
**Ước lượng:** 3 points · 12 giờ (**tối đa 3 points và khoảng 15 file mỗi PR**)  
**Phụ thuộc:** P8-09, [P8-10a](P8-10a-report-architecture-infrastructure.md), [P8-10b](P8-10b-report-class-diagrams-database.md), [P8-10c](P8-10c-report-sequence-diagrams-backend.md), [P8-10d](P8-10d-report-use-case-diagrams-mobile.md)  
**Repo / branch:** `docs/` · `docs/p8-10-final-report`  
**Issue:** `docs#TBD`

> **Phạm vi tổ chức:** `ThaiBao11125` là người phụ trách chính báo cáo, chủ trì viết toàn văn nội dung học thuật, tiếp nhận các sơ đồ kỹ thuật từ 4 sub-issue hỗ trợ, tổng hợp và định dạng tệp báo cáo hoàn chỉnh.

## Mục tiêu

Hoàn thiện toàn bộ báo cáo tốt nghiệp đồ án chuyên ngành PBL6 theo mẫu `Report/PBL6Report.docx`, bám sát khung đề cương `Report/khungbaocao.md` và quy chuẩn `Report/AGENTS.md`, tích hợp toàn bộ sơ đồ kỹ thuật và kết quả kiểm thử, bàn giao bản DOCX và PDF chính thức trên Google Drive của nhóm.

## Cấu trúc phân rã sub-issue hỗ trợ kỹ thuật

Để đảm bảo tiến độ và chất lượng chuyên môn sâu cho từng phân hệ, công việc chuẩn bị sơ đồ và thông số kỹ thuật được phân rã thành 4 sub-issue tương ứng với các thành viên phát triển:

| Mã sub-issue | Tên nhiệm vụ | Người phụ trách | Nội dung bàn giao cho Lead Author |
|---|---|---|---|
| [P8-10a](P8-10a-report-architecture-infrastructure.md) | Sơ đồ kiến trúc và hạ tầng triển khai | `baoduong17` | Sơ đồ kiến trúc vi dịch vụ (1.2), các mục 4.1 đến 4.5 của Chương 4, cấu hình biến môi trường (5.2), đóng gói Docker Compose (5.7) |
| [P8-10b](P8-10b-report-class-diagrams-database.md) | Sơ đồ lớp, ERD và cơ sở dữ liệu | `leminhkhai345` | Toàn bộ 3 sơ đồ lớp hệ thống (1.4.1, 1.4.2, 1.4.3), mô hình ERD, hướng dẫn di chuyển cơ sở dữ liệu (5.3) |
| [P8-10c](P8-10c-report-sequence-diagrams-backend.md) | Sơ đồ tuần tự và vận hành backend | `huynhtiennhat0403` | Toàn bộ 7 sơ đồ tuần tự hệ thống (1.5.1 đến 1.5.7), hướng dẫn cài đặt và vận hành dịch vụ máy chủ (5.4) |
| [P8-10d](P8-10d-report-use-case-diagrams-mobile.md) | Sơ đồ use case, thông báo đẩy và vận hành mobile | `tphuongin` | Toàn bộ 5 sơ đồ use case hệ thống (1.3.1 đến 1.3.5), dịch vụ thông báo đẩy Firebase Cloud Messaging (4.6), bộ ảnh chụp màn hình ứng dụng di động Android (2.4), hướng dẫn biên dịch Android (5.6) |

## Nhiệm vụ trực tiếp của người phụ trách chính (`ThaiBao11125`)

- **Chủ trì biên soạn toàn văn học thuật:**
  - Phần mở đầu: Lời cảm ơn (0.2), Thông tin tài liệu (0.5), Lời mở đầu (0.4), Giới thiệu đề tài (0.6, 0.7, 0.8).
  - Chương 1: Phân tích các tác nhân trong hệ thống (1.1) và viết lời dẫn giải chi tiết cho tất cả các sơ đồ kỹ thuật từ 1.2 đến 1.5.
  - Chương 2: Mô tả chi tiết toàn bộ các phân hệ chức năng từ 2.1 đến 2.4, trực tiếp chụp và chèn hình ảnh giao diện web React do mình phát triển, kết hợp bộ ảnh chụp màn hình di động từ `tphuongin`.
  - Chương 3: Trình bày toàn bộ các yêu cầu phi chức năng từ 3.1 đến 3.6 (hiệu năng, bảo mật, tính sẵn sàng, tính toàn vẹn dữ liệu, trải nghiệm người dùng, ràng buộc kỹ thuật).
  - Chương 5: Yêu cầu môi trường phát triển chung (5.1) và cài đặt vận hành giao diện web React (5.5).
  - Chương 6: Mục tiêu, phạm vi, công cụ kiểm thử và bộ kịch bản kiểm thử chi tiết từ 6.1 đến 6.4; tổng kết kết quả kiểm thử (6.5).
  - Chương 7: Kết luận (7.1), Hướng phát triển (7.2) và chuẩn hóa danh mục tài liệu tham khảo (7.3).
- **Tổng hợp và hoàn thiện tệp báo cáo:**
  - Căn chỉnh định dạng Word (`Report/PBL6Report.docx`): căn lề trang, chuẩn hóa font chữ, heading style, danh mục hình ảnh, danh mục bảng biểu và cập nhật mục lục tự động.
  - Rà soát chính tả, kiểm tra quy tắc viết hoa chuẩn tiếng Việt và quy tắc tuyệt đối không dùng dấu ngoặc đơn trong tên đề mục.
  - Xuất bản PDF và tải bộ tài liệu lên Google Drive của nhóm.

## Tham chiếu tài liệu

- Mẫu chuẩn: `Report/PBL6Report.docx`.
- Khung đề cương chuẩn: `Report/khungbaocao.md`.
- Hướng dẫn và quy chuẩn báo cáo: `Report/AGENTS.md`.
- Kế hoạch phân công chi tiết: `Report/phancong.md`.
- Bằng chứng kiểm thử: `docs/phase-8/issues/P8-09-e2e-smoke.md`.

## Các bước triển khai

### Bước 1 — Tiếp nhận tư liệu từ các sub-issue (P8-10a, P8-10b, P8-10c, P8-10d)
- **Cách làm:** Theo dõi tiến độ nộp sơ đồ và tài liệu của các thành viên; kiểm tra tính đầy đủ, độ sắc nét và tính khớp nối với mã nguồn thực tế.
- **Kiểm tra bước:** Toàn bộ 4 gói tư liệu đã được bàn giao đầy đủ file sơ đồ và thuyết minh.

### Bước 2 — Biên soạn các chương nội dung còn lại
- **Cách làm:** Viết hoàn chỉnh các mục do mình trực tiếp phụ trách vào các file tương ứng trong thư mục `Report/` (`00_modau.md`, `01_chuong1.md`, `02_chuong2.md`, `03_chuong3.md`, `05_chuong5.md`, `06_chuong6.md`, `07_ketluan.md`).
- **Kiểm tra bước:** Mỗi chương có lập luận chặt chẽ, đầy đủ hình ảnh chụp giao diện và bảng biểu minh họa.

### Bước 3 — Ráp toàn văn và định dạng tệp Word
- **Cách làm:** Ráp toàn bộ nội dung văn bản và sơ đồ vào tệp `Report/PBL6Report.docx`. Áp dụng đúng các style `heading`, `demuc`, `demucon`, `tieude`, `stt` và căn chỉnh bảng biểu ngay ngắn.
- **Kiểm tra bước:** Cập nhật trường mục lục tự động, danh mục hình và danh mục bảng chính xác số trang.

### Bước 4 — Xuất PDF và bàn giao
- **Cách làm:** Xuất file PDF từ Word, kiểm tra từng trang để đảm bảo không bị lỗi ngắt trang hay lệch lề; tải cả hai tệp DOCX và PDF lên Google Drive của nhóm.
- **Kiểm tra bước:** File DOCX và PDF mở được bình thường, liên kết Drive hoạt động tốt và cấp quyền đầy đủ cho các thành viên.

## Ngoài phạm vi

- Viết nội dung kỹ thuật chưa được kiểm chứng trong mã nguồn thực tế.
- Làm thay các sơ đồ thuộc phạm vi của các sub-issue P8-10a, P8-10b, P8-10c, P8-10d.

## Blocker

- Chờ kết quả smoke test từ P8-09 để hoàn thiện số liệu đánh giá kiểm thử tại mục 6.5.

## Acceptance

- [ ] Toàn bộ 4 sub-issue (P8-10a, P8-10b, P8-10c, P8-10d) hoàn tất và được nghiệm thu.
- [ ] Mọi đề mục trong `Report/khungbaocao.md` được viết đầy đủ, không bỏ sót mục nào.
- [ ] Sơ đồ và ảnh chụp giao diện rõ ràng, có chú thích bảng hình đầy đủ.
- [ ] Tệp Word và PDF chuẩn định dạng, không vỡ trang, không lỗi font.
- [ ] Đã upload bản hoàn chỉnh lên Google Drive của nhóm.

## Definition of Done

- [ ] PM và các thành viên duyệt thông qua toàn văn báo cáo.
- [ ] Tệp `Report/PBL6Report.docx` và bản PDF lưu trữ an toàn; issue được đóng kèm link Google Drive.
