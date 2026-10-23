# Theo dõi thay đổi API contract — Nghiên cứu và POC

> **Ngày kiểm chứng:** 22/10/2026. **Trạng thái:** có POC chạy cục bộ; chờ PM, BE, FE và Mobile review.

## 1. Mục tiêu và khuyến nghị

Web/Mobile cần biết API đổi **endpoint, field hoặc quy tắc nào; khi nào; vì sao; commit/PR nào đưa vào; client phải làm gì** mà không phải tự đọc toàn bộ Git diff.

**Khuyến nghị:** dùng Git/PR lưu lý do và review; CI bundle hai phiên bản nguồn rồi chạy `oasdiff`; công bố báo cáo Markdown/JSON cho FE/Mobile và đặt link changelog trong Apidog.

**Hiện tại:** script đã thực hiện phần bundle, diff, phân loại và tạo report khi chạy bằng lệnh. Chưa triển khai GitHub Actions, PR comment, publication hoặc đồng bộ Apidog tự động. Đây là POC kỹ thuật làm nền cho CI, chưa phải workflow CI đã vận hành.

Phạm vi chỉ gồm lịch sử **contract OpenAPI**. Không sửa contract đang dùng, runtime `AuditLog`, SDK hoặc code client; không rollout sang các service repository trong task này. Report không chứng minh backend đã triển khai thay đổi.

Task gọi hai repository là `api-docs/` và `pm/`; checkout thực tế là `api-doc/` và `docs/`. Deliverable trong workspace:

| Thành phần | Đường dẫn |
|---|---|
| Script và fixture | [contract-change-report.mjs](../../../api-doc/scripts/contract-change-report.mjs), [fixtures/contract-change/](../../../api-doc/scripts/fixtures/contract-change/) |
| Báo cáo POC | [Markdown](../../../api-doc/reports/contract-change-report.md), [JSON](../../../api-doc/reports/contract-change-report.json) |
| Nghiên cứu | Tài liệu này: `docs/phase-4/discovery/api-contract-change-tracking.md` |

Các link sang repository bên cạnh phục vụ workspace cục bộ; khi công bố trên GitHub cần dùng link repository/commit tương ứng.

## 2. So sánh các phương án

Ba phương án dưới đây có thể kết hợp: B là cách tự động chạy kiểm tra; C cung cấp công cụ và cách tích hợp. POC dùng Redocly `2.64.1` và `oasdiff` `1.34.1` chạy cục bộ. Chưa benchmark các engine hoặc kiểm chứng tích hợp bằng tài khoản Apidog dự án.

| Tiêu chí | A — Git/PR, changelog thủ công | B — CI OpenAPI diff | C — Công cụ diff/changelog và tích hợp tài liệu |
|---|---|---|---|
| Cách làm | Tác giả/reviewer đọc diff, viết log | Mỗi PR tự so nguồn trước/sau, xuất report và áp ngưỡng chặn | Chạy CLI local/release hoặc dùng dịch vụ review; nối report với GitHub/Apidog |
| Độ chính xác | Có nguồn gốc rõ; dễ bỏ sót ảnh hưởng schema dùng chung | Tốt với cấu trúc được khai báo trong OpenAPI; không hiểu hết nghiệp vụ | Phụ thuộc engine, snapshot đầu vào và thời điểm chạy |
| Tự động hóa | Thấp; phụ thuộc người viết | Cao khi được gắn vào mọi PR/merge | Thủ công với CLI local; cao hơn khi nối CI/import |
| Breaking/non-breaking | Reviewer tự kết luận | Engine phân loại, có exit code để chặn | Có tùy engine; vẫn cần policy và review |
| Chi phí | Công sức đọc diff và duy trì log | CLI nguồn mở; runner, storage và công bảo trì | CLI nguồn mở hoặc phí dịch vụ; có thể thêm Runner/import |
| Bảo trì | Đơn giản ban đầu, dễ thiếu nhất quán | Pin phiên bản, duy trì fixture, policy và publication | Theo dõi version/format, Java/Docker hoặc dịch vụ tích hợp |
| Polyrepo | Link chéo thủ công | Định danh repo/contract, cùng format để tổng hợp | Hỗ trợ nhiều spec/module tùy cấu hình; vẫn cần owner |
| FE/Mobile khám phá | Phải biết PR cần đọc | PR summary, artifact, changelog sau merge | Link từ Apidog/tài liệu tới report và commit |

**Chọn A + B, dùng công cụ và kênh công bố của C.** Git/PR giải thích lý do; engine phát hiện thay đổi; FE/Mobile xác nhận tác động thực tế.

Về công cụ, chọn `oasdiff` vì có binary độc lập và JSON thuận tiện cho script Node.js. OpenAPITools `openapi-diff` là phương án dự phòng, hỗ trợ OpenAPI 3.0, báo cáo và `--fail-on-incompatible`, nhưng cần Java/Docker. Apidog tiếp tục là nơi đọc/thử API và đồng bộ bản đã duyệt, không phải nguồn thứ hai để ghi log.

Không mặc định toàn bộ giải pháp miễn phí: GitHub private repository có quota phút/storage; dịch vụ review thương mại và khả năng Apidog phụ thuộc gói/quyền sử dụng. Chưa có số liệu CI thực tế để ước tính hóa đơn.

Nguồn: [oasdiff](https://github.com/oasdiff/oasdiff), [breaking/changelog](https://github.com/oasdiff/oasdiff/blob/v1.34.1/docs/BREAKING-CHANGES.md), [openapi-diff](https://github.com/OpenAPITools/openapi-diff), [GitHub billing](https://docs.github.com/en/actions/concepts/billing-and-usage), [giá dịch vụ oasdiff](https://www.oasdiff.com/pricing).

## 3. Nhóm thay đổi và tác động client

Đây là hướng dẫn review, không phải khẳng định mọi trường hợp đã được fixture kiểm chứng. Request và response phải xét theo hướng truyền dữ liệu.

| Nhóm | Ví dụ và tác động thường gặp | FE/Mobile cần kiểm tra |
|---|---|---|
| Endpoint, HTTP method | Xóa/đổi path hoặc method làm hỏng lời gọi cũ; thêm endpoint độc lập thường tương thích | Caller, URL, method và thao tác UI |
| Parameter | Thêm query/header bắt buộc; đổi tên, vị trí, kiểu hoặc cách encode có thể breaking | Request builder, query/header và validation |
| Request schema/body | Body optional → required, đổi wrapper hoặc content type có thể breaking | Payload, DTO và upload/form |
| Response schema/status | Xóa status/media type hoặc đổi cấu trúc có thể phá parser/success handler | DTO, wrapper, status và error mapping |
| Field/type | Xóa/đổi tên field response, string → object thường breaking | Parser và nơi sử dụng field |
| Required request | Field optional → required làm request cũ thiếu field không còn hợp lệ | Bổ sung payload/form/validation; phối hợp hỗ trợ app cũ |
| Required response | Field luôn có → optional có thể phá giả định non-null | Nullable/default và xử lý missing |
| Optional field | Thêm field response optional thường tương thích nếu parser bỏ qua field lạ | Decoder nghiêm ngặt; default/null khi thêm DTO |
| Enum | Bỏ giá trị request có thể chặn request cũ; thêm giá trị response có thể phá enum decoder | Validation, switch/when và unknown fallback |
| Constraint/schema dùng chung | Đổi nullability, min/max, pattern, array items, `$ref`, `allOf` hoặc discriminator có thể ảnh hưởng nhiều endpoint | Dữ liệu biên và toàn bộ operation sử dụng schema |
| Security | Đổi scheme/header/scope hoặc anonymous → token có thể breaking | Credential, token, scope và luồng đăng nhập |
| Quyền trong mô tả | Đổi role/ownership bằng văn bản có thể chỉ hiện thành metadata diff | BE xác nhận rule, FE/Mobile xác nhận màn hình/quyền |

Với security, cần xét kế thừa từ toàn cục và override ở operation: các scheme trong cùng requirement là AND, các requirement trong danh sách là OR; `security: []` ở operation bỏ yêu cầu security kế thừa. [OpenAPI 3.0.3](https://spec.openapis.org/oas/v3.0.3.html).

Script áp nhãn theo finding nghiêm trọng nhất:

| Nhãn | Ý nghĩa | Khi bật `--fail-on-breaking` |
|---|---|---|
| `BREAKING` | Engine trả ERR; client đúng contract cũ có thể hỏng | Exit 1, vẫn ghi report |
| `NON_BREAKING` | Engine chỉ trả INFO | Exit 0 |
| `NEEDS_REVIEW` | Engine trả WARN hoặc có diff nhưng không có finding được phân loại | Exit 1, cần người xác nhận |
| `NO_CHANGE` | Không có semantic diff/changelog | Exit 0, không thêm entry |

Nếu không bật cờ chặn, chạy report thành công trả 0 kể cả có breaking. Lỗi công cụ/input trả 2. Nhãn tương thích không thay thế kiểm thử client hoặc xác nhận hành vi backend ngoài OpenAPI.

## 4. Nguồn canonical, generated artifact và report

### 4.1. Quy tắc nguồn

- Nguồn hiện tại là `src/openapi.yaml` và các file được `$ref` sử dụng. Git mode lấy snapshot đầy đủ của từng commit, không trộn root cũ với schema mới.
- Redocly bundle mỗi nguồn vào thư mục tạm riêng trước khi diff, dùng chiến lược tên component `title`. `oasdiff` bật flatten `allOf` và path-level parameters. [Redocly bundle](https://redocly.com/docs/cli/commands/bundle).
- `reference/rentify.json` là output của `npm run bundle` cho Apidog. Script từ chối dùng file này hoặc file trong `reference/` làm đầu vào so sánh.
- Nguồn + generated bundle cùng sửa chỉ tạo entry theo cặp nguồn. Chỉ sửa bundle hoặc YAML chưa được entrypoint sử dụng thì không thêm entry nếu contract hiệu lực không đổi.
- Kiểm tra bundle có được generate đúng hay không là check riêng. Retry bundle/import không phải một thay đổi contract mới.

### 4.2. Nội dung và cách lưu report

| Thông tin | Nội dung |
|---|---|
| Vị trí, thay đổi | Endpoint/method, rule ID, JSON Pointer của schema/field và giá trị trước/sau |
| Tác động | Phân loại và hành động FE/Mobile theo mẫu của từng rule |
| Truy vết | Repository, contract ID, base/head commit, link commit/PR, reason |
| Thời gian | `detectedAt`: lúc phát hiện; `committedAt`: thời gian commit, không phải thời điểm deploy |
| Evidence JSON | Finding gốc, semantic diff, version công cụ, hash và ID entry |

**Report hiện lưu lịch sử tích lũy:** script đọc JSON cũ, thêm entry mới rồi dựng lại Markdown. Cùng `--out` dùng chung lịch sử; khác `--out` có kho riêng. `NO_CHANGE` không xóa entry cũ và exit code chỉ phản ánh lần chạy hiện tại. Vì vậy report có thể còn BREAKING cũ dù lần chạy mới trả 0.

Trong Git mode, khóa chống trùng gồm repository, contract ID, baseline commit và hash hai nguồn đã bundle. Với cùng baseline, head có thêm commit chỉ sửa generated bundle vẫn dùng entry cũ; commit được ghi là head của lần đầu phát hiện thay đổi. So commit liền trước/liền sau một lần chỉ đổi bundle trả NO_CHANGE. Revert rồi áp lại với baseline mới được ghi riêng. File mode dùng HEAD làm metadata bối cảnh. JSON là kho dữ liệu; xóa riêng Markdown không xóa lịch sử.

Trong fixture/file mode, SHA là bối cảnh chạy, không chứng minh thay đổi đã commit. PR `example.invalid` trong report mẫu là giả lập. Git mode dùng SHA thực tế; PR URL có thể truyền bằng `--pr` hoặc đọc từ `GITHUB_EVENT_PATH`. Lý do phải do tác giả cung cấp qua `--reason`.

## 5. Chạy và kiểm tra POC

### 5.1. Chuẩn bị

Chạy tại repository API. Cần Node.js ≥ 22.12, npm/npx, Git, `tar` và oasdiff `1.34.1`. Đã kiểm chứng với Node `24.18.0`, npm `11.16.0`. Redocly được gọi bằng `npx --yes @redocly/cli@2.64.1`, cần mạng nếu chưa có cache.

Nếu chưa có oasdiff, ví dụ cài tạm trên Linux x86_64:

```bash
# Subshell dừng nếu tải hoặc kiểm tra checksum thất bại.
tool_dir=$(mktemp -d)
(
  set -e
  curl -fsSL https://github.com/oasdiff/oasdiff/releases/download/v1.34.1/oasdiff_1.34.1_linux_amd64.tar.gz -o "$tool_dir/oasdiff_1.34.1_linux_amd64.tar.gz"
  curl -fsSL https://github.com/oasdiff/oasdiff/releases/download/v1.34.1/checksums.txt -o "$tool_dir/checksums.txt"
  (cd "$tool_dir" && rg '  oasdiff_1\.34\.1_linux_amd64\.tar\.gz$' checksums.txt | sha256sum -c -)
  tar -xzf "$tool_dir/oasdiff_1.34.1_linux_amd64.tar.gz" -C "$tool_dir" oasdiff
)
export OASDIFF_BIN="$tool_dir/oasdiff"
"$OASDIFF_BIN" --version
```

Máy khác kiến trúc chọn asset tại [release v1.34.1](https://github.com/oasdiff/oasdiff/releases/tag/v1.34.1). `/tmp` có thể bị dọn; biến `OASDIFF_BIN` phải trỏ tới binary còn tồn tại.

### 5.2. Hai fixture và kết quả cần thấy

`base/` là bản gốc; `breaking/` và `non-breaking/` lưu sẵn hai phiên bản thay đổi để người khác chạy lại. Mỗi phiên bản có `openapi.yaml` tham chiếu `schemas.yaml`, giúp kiểm tra bundle nhiều file. Ba thư mục chỉ là dữ liệu thử; dự án thật giữ một bộ `src/` và dùng Git lưu các phiên bản.

| So sánh với `base/` | Thay đổi tại `POST /rooms` | Kỳ vọng và hành động |
|---|---|---|
| `breaking/` | `RoomCreate.required`: `[name]` → `[name, buildingId]` | BREAKING: FE thêm payload/validation; Mobile sửa request DTO; BE chuẩn bị tương thích cho app cũ |
| `non-breaking/` | Thêm `Room.displayName` optional ở response 201 | NON_BREAKING: có thể bỏ qua; khi thêm DTO dùng default/null và kiểm tra decoder |

```bash
poc_out=$(mktemp -d)
node scripts/contract-change-report.mjs \
  --base scripts/fixtures/contract-change/base/openapi.yaml \
  --head scripts/fixtures/contract-change/breaking/openapi.yaml \
  --out "$poc_out/breaking.md" --fail-on-breaking
echo "Exit code: $?"  # Kỳ vọng 1; report vẫn được tạo.

node scripts/contract-change-report.mjs \
  --base scripts/fixtures/contract-change/base/openapi.yaml \
  --head scripts/fixtures/contract-change/non-breaking/openapi.yaml \
  --out "$poc_out/non-breaking.md" --fail-on-breaking
echo "Exit code: $?"  # Kỳ vọng 0.
```

Mở đường dẫn `.md` terminal in ra; `.json` cùng tên chứa evidence. `--out /tmp/...` lưu ngoài repository trong thư mục tạm; dùng `--out reports/...` để lưu trong repo. Bỏ `--out` thì ghi mặc định vào `reports/contract-change-report.{md,json}`. Chạy lại cùng lệnh/HEAD phải giữ số entry; muốn gom hai kết quả thì dùng cùng `--out`.

Để chạy cả hai và tự kiểm tra đúng nhãn kỳ vọng:

```bash
node scripts/contract-change-report.mjs --demo \
  --pr https://example.invalid/rentify/pull/123 \
  --out "$poc_out/demo.md"
```

Với fixture gốc, demo trả 0 và tạo hai entry. Nếu sửa fixture khiến nhãn không còn đúng, kể cả trở thành NO_CHANGE, demo trả lỗi 2. Muốn tự sửa fixture để khám phá kết quả khác, dùng `--base`/`--head` thay vì `--demo`. Script so hai đầu vào của lệnh, không so với lần chạy trước.

### 5.3. So hai commit

```bash
node scripts/contract-change-report.mjs \
  --base-ref BASE_SHA --head-ref HEAD_SHA \
  --pr https://github.com/OWNER/REPO/pull/NUMBER \
  --reason 'Lý do nghiệp vụ do tác giả PR cung cấp' \
  --out /tmp/rentify-contract-pr.md --fail-on-breaking
```

Thay placeholder bằng dữ liệu thật. `--entrypoint` mặc định `src/openapi.yaml`; `--contract-id` mặc định `rentify-public`. Git mode chỉ đọc commit; thay đổi chưa lưu/commit không ảnh hưởng snapshot đó. File mode đọc file trên đĩa nên cần lưu editor trước khi chạy. Xem đầy đủ tùy chọn bằng `--help`.

## 6. Workflow CI/PR đề xuất

**Phần này chưa được triển khai.** Sau review, áp dụng trước trong repository API:

1. **PR:** tác giả sửa YAML, ghi reason, client liên quan, link PR service và kế hoạch chuyển đổi. CI chạy lint/bundle; so nguồn tại merge-base với PR head SHA thật. Trước merge kiểm tra lại với base mới/merge candidate nếu cần.
2. **Report:** chạy script với `--fail-on-breaking`; luôn xuất summary/artifact khi report được tạo, kể cả gate đỏ. Lỗi công cụ không được diễn giải thành NO_CHANGE. PR chỉ sửa generated bundle vẫn cần có kết quả check.
3. **Review:** BREAKING/NEEDS_REVIEW cần BE và client xác nhận. Khi bật gate bắt buộc, thay đổi cố ý phải có cơ chế exception theo rule/path/SHA, reviewer và kế hoạch tương thích; POC chưa có override.
4. **Sau merge:** so snapshot nhánh đích trước/sau merge, gắn introduction commit và PR, công bố changelog chính thức một lần. Report PR là preview, không append mỗi lần push vào lịch sử chính thức.
5. **Khám phá/thông báo:** PR summary có endpoint/field, tác động và link report; artifact chứa Markdown/JSON; changelog merge lưu lâu dài trong Git. Gắn link changelog vào Apidog và gửi review request/mention FE/Mobile khi có tác động.
6. **Apidog:** giữ chiều `YAML Git → bundle → Apidog`, đồng bộ bản đã duyệt và ghi nhận source revision. Lỗi/retry import được theo dõi riêng, không thêm entry contract. Scheduled Import dùng Local Client hoặc Runner, cần xác minh cấu hình P4-15.

Job PR dùng quyền đọc; không cấp secret Apidog khi chạy code PR chưa tin cậy. Upload report chỉ dùng kết quả của lần chạy hiện tại, tránh xuất lại file cũ khi công cụ lỗi. Khi publish lịch sử, cần một writer hoặc file bất biến theo merge SHA để tránh ghi đè giữa nhiều job; POC chưa xử lý đồng thời. Artifact PR có thể hết hạn nên không dùng làm lịch sử duy nhất.

Nguồn: [GitHub SHA](https://docs.github.com/en/actions/reference/workflows-and-actions/variables), [workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts), [quyền chạy PR](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target), [Apidog Scheduled Import](https://docs.apidog.com/scheduled-import-bind-data-sources-633932m0).

## 7. Ownership, polyrepo và dependency

| Vai trò | Trách nhiệm đề xuất |
|---|---|
| BE/tác giả | Canonical YAML, reason, tính đúng contract/security, phương án tương thích; duy trì engine/policy và cấu hình CI/Apidog theo phân công |
| FE | API adapter, form, validation, parser/enum và web release |
| Mobile | Kotlin DTO, nullable/default, decoder/enum và các phiên bản app đang phát hành |
| PM | Scope, ownership, dependency và kế hoạch chuyển đổi ảnh hưởng tiến độ |

Hiện giữ một entrypoint. Nếu sau này chia service/gateway, mỗi contract cần `contractId`, repo nguồn, entrypoint, owner và client consumers rõ ràng; dùng cùng report format để tổng hợp. Service PR ảnh hưởng API phải liên kết contract PR; không import shared code giữa service. Event/AMQP diff nằm ngoài POC này.

Các điểm cần xác nhận trước triển khai:

- **D58** trong [decision log Phase 3](../../phase-3/discovery/decisions.md) vẫn Proposed; chưa coi chia repo/spec là quyết định đã duyệt.
- **P4-15** chưa có trong [issue index Phase 4](../issues/README.md) đang checkout; cần xác minh environment/auth, quyền repository, module/branch và cách kiểm tra revision sau import.
- **D59 về contract/event ownership** chưa tìm thấy. [Nghiên cứu free-tier](../../phase-3/discovery/free-tier-db-storage.md) có bản nháp cùng ID về Neon/R2, khác nội dung; không coi đó là quyết định ownership.
- `PROJECT_PLAN.md` còn ghi canonical spec ở backend, còn README repo API và task này dùng `src/openapi.yaml` trong repo API; PM cần xác nhận nguồn chính thức.

## 8. Kiểm chứng, giới hạn và rollout

| Kiểm chứng cục bộ ngày 22/10/2026 | Kết quả |
|---|---|
| Canonical `npm run lint` / `npm run bundle` | Exit 0; lint có 13 cảnh báo sẵn có; giữ nguyên nguồn/artifact hiện tại |
| Hai fixture gốc | Đúng BREAKING và NON_BREAKING; đúng `POST /rooms`, schema/field và hành động client |
| Metadata | Có timestamp, SHA, PR/reason; fixture ghi rõ metadata minh họa |
| Rerun cùng đầu vào | Không thêm entry trùng |
| So HEAD với HEAD | NO_CHANGE, không tạo entry |
| Git sandbox: sửa nguồn rồi commit; commit sau chỉ sửa generated bundle | Nguồn tạo 1 entry; generated-only không tăng entry, JSON lịch sử giữ nguyên |
| Git sandbox: giữ nguyên baseline, head thêm commit chỉ sửa generated bundle | Không thêm entry; gate vẫn trả 1 vì toàn PR còn thay đổi breaking |
| Gate và input | Breaking exit 1, optional field exit 0; từ chối generated bundle làm input, exit 2 |
| Chỉ đổi description | NEEDS_REVIEW khi chỉ có diff chưa được phân loại |
| Demo khi một trong hai fixture trở thành giống baseline | Đã sửa và kiểm chứng: exit 2, không báo thành công khi thiếu fixture kỳ vọng |

Git sandbox được tạo độc lập trong thư mục tạm, không thay lịch sử repository dự án. Bằng chứng này xác nhận POC cục bộ, chưa xác nhận CI/Apidog thực tế hoặc độ đúng của mọi nhóm thay đổi ở mục 3.

Các giới hạn còn lại: vị trí là JSON Pointer trên bundle, chưa ánh xạ dòng YAML; hành động client là mẫu theo rule, chưa phân tích code client; một diff vừa có finding vừa có metadata vẫn cần người đọc bảng trước/sau vì POC chưa phân loại riêng từng metadata change. Một số thông điệp engine còn tiếng Anh. Role/ownership hoặc hành vi backend ngoài OpenAPI cần review thủ công.

**Rollout đề xuất:** review nghiên cứu và POC → tạo task follow-up cho CI xuất report trong repo API → quan sát thay đổi thực tế rồi bật gate → hoàn thiện changelog/Apidog → mở rộng polyrepo sau khi ownership được duyệt. Chưa tạo task triển khai tiếp theo.

| Review bắt buộc trước follow-up | Người / ngày / kết luận |
|---|---|
| PM: scope, canonical source, dependency và rollout | Chờ review |
| BE: phân loại, security, generated rules và ownership | Chờ review |
| FE: từ report xác định được caller/UI và hành động cần làm | Chờ review |
| Mobile: từ report xác định được DTO/parser và ảnh hưởng app cũ | Chờ review |

**Nghiệm thu:** phần nghiên cứu và POC đã được kiểm chứng cục bộ; còn review đủ bốn vai trò và xác nhận FE/Mobile hiểu hành động từ report. Chưa đánh dấu task hoàn tất nghiệm thu.
