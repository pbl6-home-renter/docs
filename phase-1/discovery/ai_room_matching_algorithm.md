# AI Roommate Matching — Thuật toán & Thiết kế chi tiết

> Tài liệu tổng hợp toàn bộ thuật toán matching cho feature **AI Roommate Matching**  
> Kết hợp yêu cầu từ phase-1 (P1-13, business-rules, DB design) + thiết kế/code thực tế (schema, matching engine, embedding, workflow).

---

## 1. Tổng quan Feature

### 1.1 Mục tiêu
Hỗ trợ tenant tìm bạn ở ghép (roommate) một cách thông minh, dựa trên:
- Ràng buộc cứng (hard constraints)
- Thói quen sinh hoạt + mức độ ưu tiên cá nhân
- Ngữ nghĩa bio (semantic embedding)
- Điểm tương thích **hai chiều** (reciprocal)

### 1.2 Hai kịch bản chính
| Kịch bản | Mô tả | Hard filter áp dụng |
|----------|--------|---------------------|
| **NEED_ROOM + NEED_ROOM** | Cả hai đều chưa có phòng → tìm bạn trước, sau đó cùng đi thuê | Giao quận mong muốn + giao khoảng ngân sách |
| **HAVE_ROOM + NEED_ROOM** | Một người đã có phòng, tìm người vào ở ghép | Seeker phải thích quận của phòng + tiền phòng nằm trong ngân sách + tuân thủ rule chủ nhà (pets…) |

> Matching là **P2P giữa tenant**. Landlord chỉ set hard constraints trên Room (nếu có), không duyệt từng cặp.

### 1.3 Phạm vi
- **Stretch feature** (không bắt buộc MVP).
- Chỉ dành cho tenant **có tài khoản và bật chế độ tìm bạn** (`is_active = true`).
- Profile bị ẩn khi tenant đã ký hợp đồng active.

---

## 2. Data Schema (RoommateProfile)

Cấu trúc dữ liệu được thiết kế theo 4 lớp rõ ràng:

### 2.1 HardConstraints (Bộ lọc cứng)
```python
class HardConstraints:
    gender: Gender                    # Giới tính bản thân
    target_genders: List[Gender]      # Giới tính chấp nhận được
    room_status: RoomStatus           # NEED_ROOM | HAVE_ROOM
    move_in_date: Optional[date]

    # Chỉ khi NEED_ROOM
    preferred_districts: List[str]
    budget_min: int
    budget_max: int

    # Chỉ khi HAVE_ROOM
    existing_room: ExistingRoomInfo   # district, rent_per_person, landlord_rule_no_pets...
```

### 2.2 LifestyleSelf (Thói quen bản thân)
| Field | Scale | Ý nghĩa |
|-------|-------|---------|
| `cleanliness` | 1–3 | 1 = bừa bộn, 3 = rất sạch |
| `sleep_schedule` | 0/1 | 0 = ngủ sớm, 1 = cú đêm |
| `smoke` | 0/1 | 0 = không hút, 1 = có hút/vape |
| `pet_friendly` | 0/1 | 0 = không nuôi/dị ứng, 1 = nuôi hoặc thích |
| `guest_frequency` | 1–3 | Tần suất dẫn bạn về |
| `cooking_frequency` | 1–3 | Tần suất nấu nướng |

### 2.3 LifestylePreferences (Kỳ vọng & Trọng số)
- **Deal-breakers**:
  - `require_non_smoking: bool`
  - `require_no_pets: bool`
- **Importance weights** (1–5):
  - `importance_budget`
  - `importance_cleanliness`
  - `importance_schedule`
  - `importance_guest`
  - `importance_cooking`

### 2.4 SemanticProfile
```python
class SemanticProfile:
    bio_text: str                     # Đoạn tự giới thiệu (≤ 500 ký tự)
    bio_embedding: Optional[List[float]]  # Vector 768 chiều (SBERT)
```

### 2.5 Root Model
```python
class RoommateProfile:
    user_id: str
    is_active: bool                   # Bật/tắt chế độ tìm bạn
    hard_constraints: HardConstraints
    lifestyle_self: LifestyleSelf
    lifestyle_preferences: LifestylePreferences
    semantic_profile: SemanticProfile
```

---

## 3. Pipeline Matching (Tổng thể)

```
User A yêu cầu danh sách quẹt
        │
        ▼
┌─────────────────────────────┐
│  1. HARD FILTER             │  ← Loại bỏ ngay các ứng viên không đủ điều kiện
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│  2. FEATURE EXTRACTION      │  ← Budget sim, Lifestyle sim, Semantic sim
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│  3. DIRECTIONAL SCORE       │  ← S(A→B) và S(B→A)
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│  4. RECIPROCAL SCORE        │  ← √(S(A→B) × S(B→A))
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│  5. RANKING & TOP-K         │  ← Sắp xếp giảm dần → Swipe Deck
└─────────────────────────────┘
```

---

## 4. Hard Filtering (Chi tiết)

Hàm `passes_hard_filter(user_a, user_b)` trả về `True` chỉ khi **cả hai chiều** đều thỏa mãn.

### 4.1 Các điều kiện loại trừ bắt buộc

1. **Cùng một người** hoặc `target.is_active = False`
2. **Cả hai đều HAVE_ROOM** → không thể ở ghép với nhau
3. **Giới tính hai chiều**:
   - `B.gender ∈ A.target_genders`
   - `A.gender ∈ B.target_genders`
4. **Deal-breaker Smoking**:
   - Nếu A yêu cầu không hút thuốc mà B hút → loại
   - Ngược lại cũng loại
5. **Deal-breaker Pets**: tương tự smoking

### 4.2 Điều kiện theo kịch bản

**Kịch bản NEED_ROOM + NEED_ROOM:**
- Phải có **ít nhất 1 quận chung** trong `preferred_districts`
- Khoảng ngân sách phải **giao nhau**:
  ```
  overlap_min = max(A.budget_min, B.budget_min)
  overlap_max = min(A.budget_max, B.budget_max)
  overlap_min ≤ overlap_max
  ```

**Kịch bản HAVE_ROOM + NEED_ROOM:**
- Gọi `host` = người có phòng, `seeker` = người cần phòng
- `room.district` phải nằm trong `seeker.preferred_districts`
- `room.rent_per_person` phải nằm trong `[seeker.budget_min, seeker.budget_max]`
- Nếu `room.landlord_rule_no_pets = True` mà seeker nuôi thú cưng → loại

> Hard filter chạy **trước** mọi tính toán điểm → giảm số lần gọi embedding / scoring.

---

## 5. Scoring Algorithm

### 5.1 Directional Score — S(source → target)

Điểm một chiều thể hiện mức độ **source hài lòng với target**.

#### a. Budget Similarity

- **Cả hai NEED_ROOM**: Intersection-over-Union (IoU) của 2 khoảng ngân sách
  ```
  overlap = max(0, min(maxA, maxB) - max(minA, minB))
  union   = max(maxA, maxB) - min(minA, minB)
  score   = overlap / union
  ```

- **Source NEED_ROOM, Target HAVE_ROOM**:
  ```
  center = (budget_min + budget_max) / 2
  radius = (budget_max - budget_min) / 2
  score  = max(0, 1 - |rent - center| / radius)
  ```

- **Source HAVE_ROOM, Target NEED_ROOM**: Vì đã qua hard filter → điểm = 1.0

#### b. Lifestyle Similarity

Tính độ tương đồng từng tiêu chí rồi nhân với trọng số ưu tiên của **source**:

```
sim_clean  = 1 - |clean_s - clean_t| / 2
sim_sleep  = 1 - |sleep_s - sleep_t|
sim_guest  = 1 - |guest_s - guest_t| / 2
sim_cook   = 1 - |cook_s - cook_t| / 2

weights = [imp_clean, imp_schedule, imp_guest, imp_cooking]
normalized_weights = weights / sum(weights)

lifestyle_score = dot(normalized_weights, [sim_clean, sim_sleep, sim_guest, sim_cook])
```

#### c. Semantic Similarity

```
cosine = (emb_s · emb_t) / (||emb_s|| × ||emb_t||)
score  = clip((cosine + 1) / 2, 0, 1)   # map [-1,1] → [0,1]
```

Nếu thiếu embedding → trả về 0.5 (neutral).

#### d. Tổng hợp Directional Score

```
imp_budget     = source.importance_budget          # 1–5
budget_ratio   = (imp_budget / 5.0) * 0.5          # tối đa 50% trong nhóm tabular
lifestyle_ratio = 1.0 - budget_ratio

tabular_score  = budget_ratio * s_budget + lifestyle_ratio * s_lifestyle

final_score    = (1 - γ) * tabular_score + γ * s_semantic
```

Trong đó **γ (gamma) = 0.20** (tỷ trọng semantic).

### 5.2 Reciprocal Score (Điểm hai chiều)

```
Score(A, B) = √( S(A→B) × S(B→A) )
```

**Lý do dùng căn bậc hai (geometric mean):**
- Phạt mạnh trường hợp lệch một chiều (A rất thích B nhưng B không thích A).
- Phù hợp với bài toán “cùng sống chung” — cần sự đồng thuận từ cả hai phía.

### 5.3 Ranking

```python
def rank_roommates_for_user(current_user, candidate_pool, top_k=20):
    results = []
    for candidate in candidate_pool:
        if not passes_hard_filter(current_user, candidate):
            continue
        score = compute_reciprocal_score(current_user, candidate)
        results.append((candidate, score))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
```

Kết quả được đẩy vào **Swipe Deck** (giao diện quẹt kiểu Tinder).

---

## 6. Semantic Embedding

### 6.1 Model sử dụng
```
sentence-transformers/paraphrase-multilingual-mpnet-base-v2
```

- Hỗ trợ đa ngôn ngữ (tiếng Việt khá tốt trong nhóm SBERT công khai).
- `normalize_embeddings=True` → cosine similarity = dot product.
- Vector 768 chiều.

### 6.2 Cách dùng
- Encode bio khi user tạo/sửa profile → lưu `bio_embedding` vào DB.
- Khi matching chỉ cần lấy vector đã lưu (không encode lại real-time).
- Cache embedding là bắt buộc để đảm bảo hiệu năng.

### 6.3 Lưu ý
- Bio quá ngắn hoặc generic → embedding kém chất lượng → nên có validation tối thiểu (ví dụ ≥ 40 từ) hoặc fallback score = 0.5.
- Model chưa fine-tune trên domain roommate Việt Nam → hiệu quả thực tế cần đo bằng A/B test sau này.

---

## 7. Cold-start vs Learning từ hành vi (XGBoost)

### 7.1 Giai đoạn đầu (Cold-start)
Dùng hoàn toàn **heuristic** như mô tả ở mục 5:
- Hard filter + Directional + Reciprocal
- Không phụ thuộc vào dữ liệu lịch sử.

### 7.2 Giai đoạn nâng cao (khi có đủ log)
Khi có đủ swipe logs (khuyến nghị ≥ 500–1000 mẫu chất lượng):

1. **Thu thập log**:
   ```
   Swipe_Logs(user_id, target_id, action=0|1, timestamp, features_snapshot)
   ```
   Lưu snapshot feature lúc quẹt (vì profile có thể thay đổi sau này).

2. **Train supervised model** (XGBoost / LightGBM):
   - Input: feature vector (budget_sim, lifestyle_sim, semantic_sim, importance weights, …)
   - Output: `P(A sẽ quẹt phải B)`

3. **Sử dụng**:
   - Vẫn giữ hard filter ở tầng đầu.
   - Model dùng để **re-rank** hoặc thay thế directional score.
   - Có thể kết hợp learning-to-rank.

### 7.3 Vòng lặp phản hồi
```
Swipe → Log → (định kỳ) Retrain model → Cập nhật Scoring Engine
```

Đây là hướng đi chuẩn của các hệ thống matching hiện đại (Tinder, Hinge…).

---

## 8. Edge Cases & Design Decisions

| Edge case | Cách xử lý |
|-----------|------------|
| Không còn ứng viên sau hard filter | Hiển thị empty state + gợi ý nới lỏng constraint |
| Bio trống / quá ngắn | Semantic score = 0.5 (neutral) |
| Cả hai đều HAVE_ROOM | Hard filter loại ngay |
| Profile đã ký HĐ active | `is_active = false` hoặc ẩn khỏi pool |
| User mới (cold-start) | Dùng heuristic, chưa cần model |
| Importance weights = 0 hết | Fallback về trọng số đều |
| Budget min = max | Radius = 0 → xử lý riêng (trả 1.0 nếu khớp) |

### Quyết định thiết kế quan trọng
- Matching **không** bắt buộc phải gắn với một Room cụ thể ngay từ đầu (hỗ trợ cả 2 kịch bản).
- Landlord **không** veto từng cặp (PDPD-safe).
- Hard filter của Room (maxOccupancy, genderPolicy…) được áp dụng khi matching gắn với phòng cụ thể.
- Profile chỉ bị ẩn sau khi **ký hợp đồng active**, không phải sau khi accept match.

---

## 9. Workflow tổng thể (tóm tắt)

```
[User A mở App] 
    → Hard Constraint Filter (giới tính, ngân sách, quận, smoking, pets…)
    → Rút gọn pool ứng viên
    → Trích xuất đặc trưng cặp (Budget IoU / Lifestyle weighted / Cosine Bio)
    → Tính S(A→B) và S(B→A)
    → Reciprocal Score = √(S(A→B)*S(B→A))
    → Rank & đưa vào Swipe Deck
    → User quẹt Trái/Phải
    → Lưu Swipe_Logs
    → (Nếu cả hai quẹt phải) → Mở chat + Explainable AI
    → (Định kỳ) Train lại model từ logs
```
