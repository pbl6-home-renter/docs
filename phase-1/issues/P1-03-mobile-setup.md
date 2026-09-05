# P1-03 — Mobile Setup

**Status:** 🟡 Open
**Assignee:** Mobile
**Depends on:** P1-01 (feature map — để biết build gì)
**Deliverable:** Proposal file của Mobile (tự nghiên cứu + chọn + giải thích lý do) → `pm/phase-1/discovery/mobile-proposal.md`

---

## Mục đích

Thiết lập repo `pbl6-mobile` (Kotlin/Android): chọn tech stack, library, bộ component UI, coding convention, và agent skill. Mục tiêu là **repo có thể code ngay**, mọi người tuân theo 1 chuẩn thống nhất.

> **Cách làm:** **Tự nghiên cứu** (web/Android 2026), **nêu rõ lựa chọn + lý do** cho từng mục. Không có đáp án đúng tuyệt đối — PM chỉ cần bạn căn cứ nhu cầu dự án này (tenant portal là chính + landlord-lite, demo 13 tuần, 1 dev, cần bản đồ/form/payment/FCM) mà chọn hợp lý và **giải thích được**.
>
> Bối cảnh dự án: Mobile = **tenant portal (chính)** + **landlord-lite (phụ)**: FCM push, duyệt sự cố, xem dashboard/hóa đơn. Cần: tìm phòng bản đồ (2.1/2.2), invoice + payment (2.4/2.5), roommate profile/match (4.1–4.3), issue báo cáo + Property Chat (2.7/6.6), map-based search. D29: mobile là optional, landlord vận hành chính trên web.

---

## Câu hỏi cần quyết định

### A. Scaffold
- A1. **Kotlin DSL** (`build.gradle.kts`) + **version catalog** (`libs.versions.toml`)? 
- A2. **minSdk / targetSdk / compileSdk** bao nhiêu? (gợi ý cân nhắc độ phủ thiết bị)
- A3. Có dùng **library module** tách (core/feature) hay single module?
- A4. Kotlin version + Compose BOM version nào?

### B. UI framework & kiến trúc
- B1. **Jetpack Compose** hay XML Views? (research 2026 để xác nhận — cái nào là chuẩn mới?)
- B2. **Material 3**? Design tokens setup (theme/color/typography).
- B3. Kiến trúc: **MVVM** / **MVI** / **Clean**? Cho thấy pattern ViewModel + StateFlow. (Team 1 dev, 13 tuần — đừng quá nặng boilerplate.)
- B4. Package structure: **feature-based** (auth/search/invoice/payment/...)? Đưa cây thư mục.
- B5. Single-activity + Compose Navigation?

### C. UI component
- C1. Chỉ dùng **Material 3 built-in** (TopAppBar, TextField, Card, BottomSheet...) hay kèm thư viện Compose khác (Accompanist? Vico charts?)? Vì sao?
- C2. Những component nào bạn cần mà M3 chưa có → chọn lib hay tự viết?

### D. Networking
- D1. **Retrofit + OkHttp** / **Ktor client** / khác? Vì sao?
- D2. JSON: **Moshi** / **kotlinx.serialization** / **gson**? (codegen hay runtime?)
- D3. Pattern **JWT interceptor** tự attach token + xử lý 401/refresh?

### E. Dependency Injection
- E1. **Hilt** / **Koin** / khác? Cân nhắc compile-time safety vs đơn giản. Dùng **KSP** hay **KAPT**?

### F. Local storage
- F1. Lưu token: **DataStore** hay gì? (EncryptedSharedPreferences còn được khuyến nghị không?)
- F2. Có cần **Room** cache dữ liệu local (invoice/room offline) cho demo không, hay chỉ API call?

### G. Navigation
- G1. **Compose Navigation** — type-safe route (sealed class / NavType) hay string route?
- G2. **Deep linking** (từ FCM notification → mở màn hình invoice/issue cụ thể)?

### H. Maps (tìm phòng 2.1)
- H1. **Google Maps SDK** (+ maps-compose) / **Mapbox** / OSM-on-Andrid / khác? Xét free-tier + độ chín của lib Compose.
- H2. **Marker clustering** (nhiều phòng zoom-out)?

### I. Image loading
- I1. **Coil** / **Glide** / khác cho Compose (`AsyncImage`)? Vì sao?

### J. Forms & validation
- J1. Pattern validate form trong Compose (TextField `isError` + supportingText?).
- J2. Có cần lib validate riêng hay viết `String.isValidEmail()` extension util? 
- J3. **Multi-step form** (tạo roommate profile, report issue) xử lý thế nào?

### K. Error / Loading / Snackbar
- K1. Pattern **sealed `UiState<T>`** (Loading/Success/Error) cho mỗi screen?
- K2. Snackbar / error message pattern? Pull-to-refresh?

### L. Push notification
- L1. **Firebase Cloud Messaging (FCM)** setup: notification channel, xử lý deep link từ notification (D7 — FCM là kênh chính)?

### M. Payment (2.5)
- M1. **VNPay** flow trên Android: dùng SDK native hay WebView mở URL do backend sinh? Callback deep-link? (MoMo stretch.)
- M2. Fallback: mock payment / QR scan bằng app ngân hàng (D29)?

### N. Build & distribution
- N1. **Signing config** (keystore, từ env) cho release?
- N2. **ProGuard/R8** rules (giữ retrofit/moshi/retrofit model)?
- N3. Output: **APK** (Firebase App Distribution / Google Drive) hay **AAB**?

### O. Code quality
- O1. **ktlint** / **detekt**? Cấu hình.
- O2. Pre-commit hook (giống FE)?

### P. Agent skill (repo `pbl6-mobile`)
- P1. Viết `AGENTS.md` cho repo (trỏ về `pm/phase-1/` + quy ước team).
- P2. (Nếu dùng opencode) config agent/skill `.opencode/` hay `opencode.json`. Trình bày bạn định setup gì.

---

## Yêu cầu output

1. Tạo file `pm/phase-1/discovery/mobile-proposal.md` trả lời **từng câu A1→P2** + lý do ngắn gọn.
2. Bổ sung: **mục "Feature map verify"** — ghi kết quả verify P1-01 từ phía Mobile (đồng ý/sửa/thêm/bớt feature, lý do).
3. Bổ sung: danh sách dependencies (groupId:artifactId:version) cho `libs.versions.toml`.
4. Nêu tradeoff bạn cân nhắc (vd chọn Koin vì...) để PM + FE biết.
5. Đánh dấu mục **ảnh hưởng 2 platform** (màu chủ đạo, validation, format, translation) → đưa sang P1-04/P1-05.

## Định nghĩa "Done"

- [ ] Proposal Mobile đầy đủ A1→P2 + lý do.
- [ ] Feature map verify (P1-01) đã ghi trong proposal.
- [ ] Danh sách dependencies + version (libs.versions.toml).
- [ ] Các quyết định cross-platform được highlight cho PM.
- [ ] Sẵn sàng scaffold project + chạy trống khi PM duyệt tech stack.

---

*Không tạo issue riêng cho Linear/GitHub/Apidog/FCM-project — PM tự nhắc & lo hạ tầng.*
