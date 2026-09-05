**Discovery: Mô hình sở hữu (Ownership Model) — v2**
- **Task:** Ownership/Delegation Model
- **Assignee:** BE ·  **Participants:** PM, Mobile/FE
- **Trạng thái:** ✅ Finalized 31/08 — quyết định **D25** đã chốt theo đúng bản này.
- **Input:** requirement.md, feedback buổi 27/08 + làm rõ 30/08 ("tòa 59 phòng, A sở hữu 50, B/C/D mỗi người 3; mỗi phòng chỉ 1 chủ")
- **Output này phục vụ:** business-rules.md §1 (Room/Building), ERD v1 (Phase 2)
- **Quyết định liên quan:** D25 (chốt Accepted 31/08 theo bản này)

**1. Bối cảnh & bài toán**
Bài toán thực tế (làm rõ 30/08):
> Một tòa nhà có **59 phòng**. A sở hữu **50 phòng**, B/C/D mỗi người sở hữu **3 phòng**. Mỗi phòng chỉ có **đúng 1 chủ sở hữu**. Chủ tòa nhà (toàn bộ) có thể không xác định / không liên quan — việc sở hữu được xác định ở **mức phòng**, không phải mức tòa nhà.

Đây không phải ca đặc biệt — đó là dạng tổng quát: **một tòa nhà có thể có nhiều chủ sở hữu khác nhau trên các phòng khác nhau**, và mỗi phòng thuộc về đúng 1 người. Không có khái niệm "giao quản lý / ủy quyền" trong phạm vi này: **ai sở hữu phòng đó thì chính người đó vận hành phòng đó** (ký hợp đồng, thu tiền, xuất hóa đơn).

Nếu model hiện tại của MVP chỉ có 1 field ownerId trên Building thì:
- Không biểu diễn được B/C/D sở hữu một phần phòng của tòa nhà (phòng của họ sẽ bị gán nhầm cho 1 chủ tòa duy nhất).
- Doanh thu/hóa đơn/hợp đồng của từng phòng sẽ bị gán sai chủ thể.
- Khó thống kê theo chủ (mỗi chủ sở hữu bao nhiêu phòng, thu nhập bao nhiêu).

**2. Mục tiêu thiết kế**
1. Mỗi phòng có **đúng 1 chủ sở hữu** (`owner_id` bắt buộc) — đơn giản, gọn, không mơ hồ.
2. Giữ cây tài sản **Building → Floor (tùy chọn) → Room** để: tránh sai sót khi nhập liệu, dễ hiển thị sơ đồ theo tầng (feature 1.3), dễ thống kê theo tầng/building.
3. **Không có Manager ở MVP** — chủ phòng là người vận hành phòng đó. Bỏ toàn bộ khái niệm ủy quyền/manager để giảm độ phức tạp (bài toán này chỉ cần sở hữu, không cần delegation).
4. Không phá vỡ schema MVP hiện có (Building/Room) — thêm field, không đổi cấu trúc gốc.

**3. Mô hình miền (Domain model)**
**3.1 Nguyên tắc: 1 chủ duy nhất, xác định ở mức phòng**
Building (node gốc, chỉ là nhóm phòng)
  └─ Floor (tùy chọn, dùng để nhóm phòng theo tầng — tránh nhập sai, dễ thống kê)
      └─ Room  ← owner_id BẮT BUỘC tại đây (chủ sở hữu pháp lý của phòng)

- `Room.owner_id` (NOT NULL) = chủ sở hữu duy nhất của phòng → người ký hợp đồng, thu tiền, phát hành hóa đơn cho phòng đó.
- `Floor.owner_id` (nullable) = chỉ mang tính **gợi ý / kiểm tra nhất quán** (mọi phòng trong một Floor thường cùng chủ), KHÔNG phải nguồn chân lý. Nếu Floor có `owner_id` mà một phòng trong đó set khác → cảnh báo khi nhập (tránh sai sót), nhưng `Room.owner_id` luôn thắng.

**3.2 Vì sao KHÔNG cần Manager (ủy quyền) ở MVP**
- Bài toán hiện tại chỉ nói về **sở hữu** (ai là chủ phòng) — không có tình huống "chủ thuê người khác quản lý".
- Mỗi phòng 1 chủ → chủ tự vận hành → không cần phân biệt `ownerId` / `managerId`, không cần `on_behalf_of`, không cần `delegation_proof`.
- Nếu sau này (Phase 1+) có nhu cầu ủy quyền quản lý (chủ không tự vận hành), sẽ **bổ sung** field `manager_id` (nullable, mặc định = `owner_id`) hoặc bảng `unit_managers` dạng many-to-many **mà không phá** model hiện tại.

**3.3 Có cần Floor là entity không? — CÓ (giữ)**
| Phương án | Quyết định | Lý do |
|-|-|-|
| A. Thêm entity **Floor** giữa Building và Room | **✅ CHỌN (giữ)** | Tránh người dùng nhập sai thông tin (floor là lớp kiểm tra/gợi ý chủ), dễ thống kê theo tầng, dễ hiển thị sơ đồ (feature 1.3). `Room.floor_id` nullable — case đơn giản (1 chủ 1 dãy) có thể bỏ qua Floor. |

**4. Khung pháp lý / hợp đồng (legal framing)**
**4.1 Ai là bên đứng tên hợp đồng?**
Bên phát hành hợp đồng (Contract issuer) = **chủ sở hữu phòng** (`Room.owner_id`). Không có khái niệm manager/ủy quyền ở MVP → `issued_by_user_id` (= issuer) luôn là `Room.owner_id`.
- Cơ sở pháp lý: chủ sở hữu có quyền cho thuê tài sản thuộc sở hữu của mình (Điều 562 Bộ luật Dân sự 2015 — hợp đồng thuê tài sản không bắt buộc phải là chủ sở hữu nhưng thực tế thường là chủ hoặc người được chủ ủy quyền; ở MVP ta quy ước issuer = chủ).
- Do không có ủy quyền, **bỏ** nhu cầu các field `on_behalf_of_user_id`, `delegation_proof_url`, `delegation.expiresAt`.

**4.2 Dữ liệu cần lưu**
- `Contract.issued_by_user_id` (NOT NULL) → trỏ tới `Room.owner_id` tại thời điểm ký. (Field mới, NOT NULL.)

**4.3 Quy trách nhiệm (liability)**
- Trách nhiệm vận hành + pháp lý về tài sản cho thuê của phòng đó → thuộc `issued_by_user_id` = chủ phòng.
- Hệ thống **không** tự xử lý nghĩa vụ thuế — chỉ lưu đủ dữ liệu (owner, số tiền) để 2 bên tự đối soát ngoài hệ thống.

**4.4 Lưu ý riêng cho thị trường Việt Nam**
- Mỗi phòng 1 chủ → không có vấn đề tranh chấp "nhiều chủ chung phòng".
- Nếu một phòng thực tế có nhiều người cùng đứng tên (đồng sở hữu) → **ngoài phạm vi MVP** (Phase 1+), cần bảng phụ `ownership_shares`.
- Đây là ghi chú tham khảo, không thay thế tư vấn pháp lý — khuyến nghị PM xác nhận với luật sư nếu cần giá trị pháp lý chính thức.

**5. ERD sketch**
```
users ──1:1── rooms.owner_id (N rooms / 1 user)
buildings 1──n floors 1──n rooms
rooms: owner_id (NOT NULL), floor_id (nullable)
```

**6. Đề xuất schema PostgreSQL (diff so với MVP hiện tại)**
```sql
-- Floor: bảng mới, tùy chọn (giữ để nhóm phòng, tránh nhập sai, dễ thống kê)
CREATE TABLE floors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    building_id UUID NOT NULL REFERENCES buildings(id),
    name VARCHAR(100) NOT NULL,          -- vd. "Tầng 6"
    owner_id UUID REFERENCES users(id),  -- nullable = gợi ý/kiểm tra nhất quán, KHÔNG phải nguồn chân lý
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Room: thêm 2 cột
ALTER TABLE rooms
    ADD COLUMN floor_id UUID REFERENCES floors(id),   -- nullable
    ADD COLUMN owner_id UUID NOT NULL REFERENCES users(id);  -- BẮT BUỘC: chủ sở hữu phòng

-- Contract: thêm 1 cột
ALTER TABLE contracts
    ADD COLUMN issued_by_user_id UUID NOT NULL REFERENCES users(id);

-- Building: KHÔNG đổi (bỏ việc thêm manager_id; owner_id cấp building không bắt buộc)
```

**Tác động migration lên MVP hiện có**
| Entity | Thay đổi | Rủi ro |
|-|-|-|
| User | Không đổi | — |
| Building | Không đổi | — |
| Floor | Bảng mới | Thấp — không bắt buộc dùng |
| Room | +2 cột, `owner_id` NOT NULL | Trung bình — cần backfill `owner_id` cho phòng hiện có trước khi đặt NOT NULL (dùng chủ tòa hiện tại hoặc dữ liệu nhập mới) |
| Contract | +1 cột bắt buộc (`issued_by_user_id`) | Trung bình — backfill `issued_by_user_id` = phòng.owner tương ứng cho hợp đồng cũ |
| Invoice/Payment | Không đổi field, nhưng logic gán chủ nợ (ai nhận tiền) cần đọc `Room.owner_id` thay vì `Building.ownerId` cứng | Trung bình — rà lại code tạo hóa đơn (feature 3.4) |

**7. Việc còn mở (để PM/legal chốt cùng P1-12)**
1. `Building.owner_id` có cần thiết không? → Đề xuất: **không bắt buộc** (nullable / bỏ). Sở hữu xác định ở mức phòng. Nếu cần hiển thị "chủ tòa" trên UI → dùng `owner_id` phổ biến nhất trong các phòng, hoặc để null.
2. Floor có bắt buộc khai báo khi tạo Room không? → Đề xuất: **không bắt buộc** (`floor_id` nullable), nhưng khuyến khích nhập để dễ thống kê. Chặn mâu thuẫn: nếu Floor có `owner_id` khác phòng → cảnh báo (chưa chặn cứng).
3. Đồng sở hữu một phòng (2 người cùng đứng tên sổ đỏ) → nằm trong scope không? → Đề xuất **không** (Phase 1+), cần bảng `ownership_shares`.
4. Ủy quyền quản lý (chủ thuê ngoài vận hành) → nằm trong scope không? → Đề xuất **không** (Phase 1+), bổ sung `manager_id` sau khi có nhu cầu thực.

**Definition of Done — đối chiếu**
- Mô hình sở hữu (mỗi phòng 1 chủ, giữ Floor, bỏ Manager MVP) phủ được case 59 phòng / A-B-C-D và tổng quát hóa (Building → optional Floor → Room).
- Contract issuer được định nghĩa rõ trong data model (§4.1, §4.2) = `Room.owner_id`.
- ERD + field changes đã tài liệu hóa (§5, §6).
- ✅ **D25 đã chốt Accepted 31/08 theo bản này** — P1-12 (BE) chỉ còn triển khai ERD, không mở lại quyết định.
