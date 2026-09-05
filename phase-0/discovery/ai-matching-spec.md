# AI Roommate Matching Logic Spec

## 1. Overview

Tài liệu này mô tả tính khả thi và luồng xử lý end-to-end cho tính năng **AI Roommate Matching**.

Mục tiêu của module:

1. Nhận hồ sơ của tenant đã opt-in vào roommate matching.
2. Loại các cặp vi phạm hard constraints bằng rule-based filter.
3. Chỉ gửi các cặp đã pass filter sang LLM.
4. LLM trả về `compatibility_score`, `strengths`, `concerns`, và `advice`.
5. Cache kết quả theo cặp tenant để tránh gọi model lặp lại.

### Feasibility verdict

**KEEP as Stretch.**

Tính năng có thể triển khai bằng rule-filter + LLM scoring. Qua prototype hiện tại, phần prompt, structured output, hard-filter, caching key, no-candidate handling và score stability đều đã được kiểm thử.

Rủi ro cold-start thuộc về quy mô marketplace/data pool hơn là logic AI.

---

## 2. RoommateProfile Schema

### Required fields

- `tenant_id`
- `gender`
- `gender_preference`
- `budget.min_vnd`
- `budget.max_vnd`
- `smoking`
- `smoking_preference`
- `pets.has_pet`
- `pet_preference`
- `sleep_schedule.sleep_time`
- `sleep_schedule.wake_time`

### Optional / soft-scoring fields

- `lifestyle.cleanliness`
- `lifestyle.noise_tolerance`
- `lifestyle.social_level`

### Example

```json
{
  "tenant_id": "uuid",
  "gender": "male",
  "gender_preference": ["male", "female", "any"],
  "budget": {
    "min_vnd": 2500000,
    "max_vnd": 4000000
  },
  "smoking": "no",
  "smoking_preference": "no_smoker",
  "pets": {
    "has_pet": false,
    "pet_types": []
  },
  "pet_preference": "accept",
  "sleep_schedule": {
    "sleep_time": "23:00",
    "wake_time": "07:00"
  },
  "lifestyle": {
    "cleanliness": "high",
    "noise_tolerance": "low",
    "social_level": "medium"
  }
}
```

---

## 3. Matching Pipeline

```text
RoommateProfile pool
        ↓
Hard rule-filter
        ↓
Candidate pairs
        ↓
LLM soft scoring
        ↓
Cache result
        ↓
Sorted result list
        ↓
Mobile explanation card
```

### 3.1 Hard-filter fields

Hard-filter xử lý các điều kiện mang tính loại trừ rõ ràng:

- gender preference;
- budget overlap;
- smoking compatibility;
- pet compatibility.

### 3.2 Soft-scoring fields

LLM chỉ đánh giá:

- sleep schedule;
- cleanliness;
- noise tolerance;
- social level.

LLM không quyết định các hard constraints.

---

## 4. Rule-filter Logic

### Gender

- Nếu requester không chấp nhận gender của candidate → reject.
- Nếu candidate không chấp nhận gender của requester → reject.
- `any` → pass.

### Budget

Hai khoảng budget phải có overlap.

```text
max(A.min, B.min) <= min(A.max, B.max)
```

Nếu không overlap → reject.

### Smoking

Ví dụ:

```text
A.smoking_preference = no_smoker
B.smoking = yes
```

→ reject.

Kiểm tra hai chiều.

### Pets

Nếu một người không chấp nhận pet và người còn lại có pet → reject.

Kiểm tra hai chiều.

---

## 5. LLM Scoring Contract

### Input

Chỉ gửi các soft-scoring fields của hai profile đã pass hard-filter.

```json
{
  "requester": {
    "sleep_schedule": {
      "sleep_time": "23:00",
      "wake_time": "07:00"
    },
    "lifestyle": {
      "cleanliness": "high",
      "noise_tolerance": "low",
      "social_level": "medium"
    }
  },
  "candidate": {
    "sleep_schedule": {
      "sleep_time": "01:00",
      "wake_time": "09:00"
    },
    "lifestyle": {
      "cleanliness": "medium",
      "noise_tolerance": "medium",
      "social_level": "high"
    }
  }
}
```

### Output

```json
{
  "compatibility_score": 55,
  "strengths": [],
  "concerns": [
    "Chênh lệch giờ giấc sinh hoạt...",
    "Khác biệt về mức độ chịu tiếng ồn..."
  ],
  "advice": "Hai bạn nên trao đổi trước về giờ yên tĩnh..."
}
```

### Constraints

- `compatibility_score`: integer, 0–100.
- `strengths`: chỉ chứa điểm tương thích trực tiếp từ input.
- `concerns`: chỉ chứa khác biệt trực tiếp từ input.
- `advice`: 2–3 câu tiếng Việt có dấu.
- Không tự thêm tình huống, hành vi hoặc dữ liệu không có trong input.
- Nếu không có strength thực sự, trả `strengths: []`.

---

## 6. Prompt v2

```text
Bạn là hệ thống đánh giá mức độ tương thích giữa hai người có nhu cầu ở ghép.

Hai người đã vượt qua hard rule-filter trước đó, vì vậy:
- Không đánh giá lại gender, budget, smoking hoặc pets như điều kiện loại trừ.
- Chỉ tập trung vào mức độ tương thích mềm trong sinh hoạt.

Hãy đánh giá dựa trên:
- sleep_schedule
- cleanliness
- noise_tolerance
- social_level

Yêu cầu:
1. Trả về compatibility_score là số nguyên từ 0 đến 100.
2. Score càng cao khi hai người có thói quen sinh hoạt càng tương đồng hoặc dễ thích nghi với nhau.
3. Không tự bịa thông tin ngoài input.
4. Không đưa ra kết luận tuyệt đối như "chắc chắn hợp" hoặc "không thể ở cùng".
5. strengths chỉ liệt kê các điểm tương thích thực sự có trong input.
6. concerns chỉ liệt kê các điểm khác biệt thực sự có trong input.
7. advice gồm 2–3 câu ngắn bằng tiếng Việt.
8. Output phải là JSON hợp lệ theo đúng schema.
9. Tất cả nội dung text phải được viết bằng tiếng Việt có dấu đầy đủ.
10. strengths CHỈ được chứa những đặc điểm thực sự tương đồng hoặc tương thích trực tiếp giữa hai profile.
11. concerns CHỈ được suy ra trực tiếp từ dữ liệu input.
12. advice chỉ được đưa ra lời khuyên liên quan trực tiếp đến các strengths và concerns đã xác định.
13. Không được tự thêm tình huống, hành vi hoặc giả định không có trong input.
14. Nếu không có strength thực sự, trả về "strengths": [].

Output schema:

{
  "compatibility_score": 0,
  "strengths": [],
  "concerns": [],
  "advice": ""
}
```

---

## 7. Prompt Test Results

Model used: `gemini-3.5-flash`

### Test 1 — High compatibility

Result:

- Score: **95**
- Vietnamese output: PASS
- Strengths relevance: PASS
- Concerns relevance: PASS
- Hallucination check: PASS

### Test 2 — Medium compatibility

Result:

- Score: **55**
- `strengths`: `[]`
- Concerns correctly reflected sleep/noise/cleanliness differences.
- Vietnamese output: PASS
- Hallucination check: PASS

### Test 3 — Low compatibility

Result:

- Score: **15**
- `strengths`: `[]`
- Concerns correctly reflected large differences in sleep schedule, cleanliness, noise tolerance and social level.
- Vietnamese output: PASS
- Hallucination check: PASS

### Prompt conclusion

```text
95 > 55 > 15
```

Prompt v2 preserves the expected compatibility ordering and returns structured explanations without the hallucination issues observed in Prompt v1.

**Prompt v2: PASS**

---

## 8. Caching Strategy

### Goal

Một unique tenant pair chỉ cần tính một lần nếu profile không thay đổi.

### Canonical pair

A → B và B → A phải dùng cùng một cache entry.

Concept:

```text
pair = sort(requester_id, target_id)
```

### Profile version

Cache key cần gắn với version của từng profile.

Ví dụ:

```text
match:tenant_A:v1:tenant_B:v1
```

Nếu A cập nhật profile:

```text
match:tenant_A:v2:tenant_B:v1
```

→ key mới → model được gọi lại.

### Cache policy

- Same pair + same profile versions → reuse cached result.
- A-B và B-A → same cache entry.
- Profile update → old cache không được reuse.

---

## 9. API Contract

### Endpoint

```http
POST /api/v1/ai/matchmaking
```

### Request

```json
{
  "requester": {
    "tenant_id": "tenant_001",
    "sleep_schedule": {
      "sleep_time": "23:00",
      "wake_time": "07:00"
    },
    "lifestyle": {
      "cleanliness": "high",
      "noise_tolerance": "low",
      "social_level": "medium"
    }
  },
  "candidate": {
    "tenant_id": "tenant_005",
    "sleep_schedule": {
      "sleep_time": "01:00",
      "wake_time": "09:00"
    },
    "lifestyle": {
      "cleanliness": "medium",
      "noise_tolerance": "medium",
      "social_level": "high"
    }
  }
}
```

### Success response

```json
{
  "compatibility_score": 55,
  "strengths": [],
  "concerns": [
    "Chênh lệch giờ giấc sinh hoạt...",
    "Khác biệt về mức độ chịu tiếng ồn..."
  ],
  "advice": "Hai bạn nên trao đổi trước về giờ yên tĩnh..."
}
```

### Status codes

| Code | Meaning |
|---:|---|
| 200 | Matching result generated successfully |
| 400 | Invalid input |
| 422 | Schema validation error |
| 500 | AI service internal error |
| 503 | AI provider temporarily unavailable |

### Error response

```json
{
  "error": {
    "code": "AI_MATCHING_FAILED",
    "message": "Unable to generate matching result."
  }
}
```

### Authentication

```http
Authorization: Bearer <AI_SERVICE_KEY>
```

---

## 10. Empirical Edge-case Tests

Edge cases trong mục này chỉ ghi các behavior đã được test trực tiếp.

### 10.1 Hard-filter conflicts

Đã test các case:

- control pair;
- gender conflict;
- budget conflict;
- smoking conflict;
- pet conflict.

Kết quả:

```text
control_pass      → PASS
gender_conflict   → correctly rejected
budget_conflict   → correctly rejected
smoking_conflict  → correctly rejected
pet_conflict      → correctly rejected
```

**Conclusion:** hard-filter logic xử lý đúng các conflict đã kiểm thử.

---

### 10.2 No candidates after hard-filter

Experiment:

```text
candidate_count = 5
survivor_count = 0
```

Kết quả:

```text
LLM should be called = false
```

**Conclusion:** nếu không còn candidate sau hard-filter thì pipeline phải trả empty result và không gọi LLM.

---

### 10.3 Cache invalidation

Experiment:

1. Tính A(v1)-B(v1).
2. Gọi lại A(v1)-B(v1).
3. Update A lên profile version 2.
4. Gọi A(v2)-B(v1).

Observed:

```text
same_pair_cache_hit = true
stale_cache_reused_after_profile_change = false
llm_call_count = 2
```

**Conclusion:** cache key theo profile version tránh reuse stale matching result.

---

### 10.4 Score stability

Cùng một profile pair được gọi LLM 5 lần.

Scores:

```text
96, 98, 98, 96, 98
```

Statistics:

```text
mean  = 97.2
min   = 96
max   = 98
spread = 2
```

Ngưỡng thử nghiệm:

```text
spread <= 10
```

Observed spread:

```text
2
```

**Conclusion:** với test pair hiện tại, score đủ ổn định để dùng caching. Không ghi score instability là observed risk trong report này.

---

## 11. Observed Risks / Behaviors

Dựa trên các thực nghiệm đã chạy:

### 11.1 Empty candidate pool after hard-filter

Observed:

- pool có thể về 0 candidate sau hard-filter;
- LLM không nên được gọi trong trường hợp này.

Mitigation:

```text
survivor_count == 0
→ return empty result
→ skip LLM
```

### 11.2 Stale cached score after profile update

Risk tồn tại nếu cache key không phản ánh profile version.

Mitigation:

- version profile;
- cache key chứa version của cả hai profile;
- profile đổi → cache miss → tính lại.

### 11.3 Hard-rule conflicts

Gender, budget, smoking và pet conflicts đã được xác nhận là các trường hợp cần reject trước LLM.

Mitigation:

- deterministic rule-filter;
- không tiêu tốn LLM call cho cặp đã vi phạm hard rules.

### Score instability

Không được ghi là observed risk ở thời điểm hiện tại.

Trong 5 lần gọi cùng một pair, score spread chỉ là **2 điểm**, thấp hơn ngưỡng thử nghiệm 10 điểm.

---

## 12. D29 / Passive Tenant Behavior

Roommate matching chỉ áp dụng cho tenant:

- có account;
- tạo `RoommateProfile`;
- opt-in vào matching pool.

Tenant không login / passive tenant:

```text
→ không xuất hiện trong pool
→ không tạo MatchRequest
→ không ảnh hưởng flow của những tenant đã opt-in
```

Do đó landlord-solo mode không block AI matching.

---

## 13. Moderation

LLM chỉ nhận các lifestyle fields đã định nghĩa.

Không gửi free-form private conversation hoặc nội dung chat.

Output chỉ gồm:

- score;
- strengths;
- concerns;
- short advice.

Không build chat trong module này.

---

## 14. Final Feasibility Verdict

### Verdict: KEEP AS STRETCH

Prototype hiện tại đã xác nhận:

- RoommateProfile schema đủ để tạo pipeline;
- hard-filter hoạt động với các conflict đã test;
- Prompt v2 phân biệt tốt high / medium / low compatibility;
- structured JSON output ổn định;
- same pair có thể cache;
- profile update không reuse stale cache nếu dùng profile version;
- no-candidate flow có thể skip LLM hoàn toàn;
- score ổn định trong test lặp 5 lần.

### Remaining product risk

Cold-start vẫn là risk thuộc marketplace/data pool và chưa được kiểm chứng bằng prototype AI hiện tại.

Đây không phải blocker cho implementation của AI module.

---

## 15. Definition of Done Status

- [x] `RoommateProfile` fields enumerated
- [x] Hard rule-filter logic defined
- [x] LLM scoring contract defined
- [x] Prompt v2 written
- [x] Prompt tested on high / medium / low compatibility cases
- [x] Caching strategy defined and experimentally checked
- [x] API `/api/v1/ai/matchmaking` drafted
- [x] No-candidate behavior tested
- [x] Hard-rule conflict behavior tested
- [x] Score stability tested
- [x] D29 passive-tenant behavior documented
- [x] Feasibility verdict recorded as Stretch
- [ ] API contract reviewed / handed to BE
