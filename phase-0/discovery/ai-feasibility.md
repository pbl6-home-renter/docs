# AI Feature Feasibility — Auto-Description

## 1. Overview

Tài liệu này đánh giá tính khả thi của tính năng **AI Auto-Description** cho hệ thống quản lý bất động sản/phòng trọ cho thuê.

Tính năng nhận dữ liệu có cấu trúc của phòng và sinh ra:

- `title`: tiêu đề tin đăng;
- `description`: nội dung mô tả phòng bằng tiếng Việt.

### Scope note

Issue Linear ban đầu có cả **AI Matchmaking** và **AI Auto-Description**. Trong phạm vi hiện tại, nhóm chỉ tiếp tục đánh giá **AI Auto-Description**; AI Matchmaking không được triển khai trong report này.

> Cần đảm bảo PM/trưởng nhóm đã đồng ý cập nhật scope này trên Linear để Definition of Done khớp với deliverable thực tế.

---

## 2. Proposed Input / Output

### 2.1 Input schema

```json
{
  "room_type": "Phòng trọ",
  "area_m2": 20,
  "location": "Gần Đại học Bách Khoa",
  "price_vnd": 3500000,
  "amenities": [
    "nóng lạnh",
    "điều hòa",
    "gác lửng",
    "bếp",
    "wifi"
  ],
  "furnishing": [
    "tủ lạnh",
    "tủ quần áo",
    "kệ sách",
    "bàn ghế",
    "nồi cơm điện"
  ],
  "utility_costs": {
    "electricity": {
      "price": 3500,
      "unit": "kWh"
    },
    "water": {
      "price": 100000,
      "unit": "person/month"
    }
  },
  "target_tenant": {
    "gender": null,
    "tenant_types": [
      "Sinh viên",
      "Người đi làm",
      "Gia đình"
    ]
  }
}
```

### 2.2 Output schema

```json
{
  "title": "string",
  "description": "string"
}
```

### 2.3 Design decision

Input được chuẩn hóa thành JSON thay vì một chuỗi keyword tự do để:

- dễ validate ở Backend/AI service;
- hạn chế model hiểu sai dữ liệu;
- giữ nguyên các giá trị quan trọng như giá thuê, giá điện/nước và đơn vị;
- dễ tích hợp với API sau này.

---

## 3. Prompt v1

```text
Bạn là trợ lý viết nội dung cho một nền tảng cho thuê phòng trọ.

Nhiệm vụ:
Từ dữ liệu phòng được cung cấp, hãy viết một bài đăng cho thuê phòng bằng tiếng Việt.

Yêu cầu:
- Tạo một tiêu đề ngắn gọn, rõ ràng và hấp dẫn.
- Tạo một đoạn mô tả tự nhiên, khoảng 60–100 từ.
- Ưu tiên làm nổi bật diện tích, vị trí, giá thuê, tiện nghi và nội thất.
- Có thể diễn đạt lại dữ liệu để câu văn tự nhiên hơn.
- Tuyệt đối không tự bịa thêm thông tin không xuất hiện trong input.
- Không tự thêm các thông tin như:
  + khoảng cách cụ thể
  + an ninh
  + chỗ để xe
  + giờ giấc
  + chính sách nuôi thú cưng
  + phí dịch vụ
  + ban công
  + cửa sổ
  + nhà vệ sinh riêng
  nếu input không cung cấp.
- Giá thuê, giá điện và giá nước phải giữ đúng theo input.
- Nếu target_tenant.gender là null thì không đề cập yêu cầu giới tính.
- Chỉ đề cập đối tượng thuê nếu dữ liệu target_tenant có cung cấp.
- Không sử dụng các câu quảng cáo quá mức hoặc thông tin không kiểm chứng được.

Chỉ trả về JSON theo đúng cấu trúc:

{
  "title": "string",
  "description": "string"
}
```

---

## 4. Prompt Testing

### Test setup

- Model: `gemini-3.5-flash`
- Structured output: JSON
- Validation: Pydantic schema
- Số test case: 3

### 4.1 Test Case 1 — Phòng đầy đủ tiện nghi và nội thất

**Kết quả:**

```json
{
  "title": "Cho thuê phòng trọ gác lửng 20m2 gần Đại học Bách Khoa",
  "description": "Cho thuê phòng trọ diện tích 20m2 có gác lửng, vị trí gần Đại học Bách Khoa. Phòng được trang bị tiện nghi gồm điều hòa, nóng lạnh, bếp và wifi. Nội thất có sẵn tủ lạnh, tủ quần áo, kệ sách, bàn ghế và nồi cơm điện. Giá thuê phòng là 3.500.000 VND/tháng. Chi phí điện là 3.500 VND/kWh và nước là 100.000 VND/người/tháng. Phòng phù hợp cho đối tượng thuê là nam (sinh viên, người đi làm hoặc gia đình)."
}
```

**Đánh giá:** PASS.

Model giữ đúng các thông tin chính trong input và không tự thêm tiện ích ngoài dữ liệu được cung cấp.

### 4.2 Test Case 2 — Phòng tối giản, không có furnishing

**Kết quả:**

```json
{
  "title": "Cho thuê phòng trọ 14m2 tại Quận Thanh Xuân, Hà Nội",
  "description": "Cho thuê phòng trọ diện tích 14m2 tại Quận Thanh Xuân, Hà Nội với giá thuê 2.500.000 VND/tháng. Phòng thích hợp cho đối tượng là sinh viên và người đi làm. Về tiện nghi, phòng đã được trang bị sẵn wifi và máy nóng lạnh. Chi phí điện nước được tính rõ ràng với giá điện là 4.000 VND/kWh và giá nước là 80.000 VND/người/tháng."
}
```

**Đánh giá:** PASS.

Model không tự sinh thêm furnishing khi danh sách nội thất rỗng.

### 4.3 Test Case 3 — Căn hộ mini, nước tính theo m³

**Kết quả:**

```json
{
  "title": "Cho thuê căn hộ mini rộng 42m2 tại Quận 7, TP.HCM",
  "description": "Cho thuê căn hộ mini diện tích 42m2 tọa lạc tại Quận 7, TP.HCM với giá thuê 7.800.000 VND/tháng. Căn hộ được trang bị đầy đủ nội thất gồm giường, tủ quần áo, bàn ăn, sofa và tủ lạnh. Tiện nghi sẵn có bao gồm điều hòa, bếp, wifi và máy giặt. Chi phí điện là 3.800 VND/kWh và nước là 18.000 VND/m3. Đây là lựa chọn phù hợp dành cho đối tượng người đi làm hoặc gia đình đang tìm kiếm nơi ở tiện nghi."
}
```

**Đánh giá:** PASS.

Model giữ đúng đơn vị nước `m3` thay vì tự đổi sang `person/month`.

### 4.4 Testing conclusion

Cả 3 test case đều trả về đúng JSON schema và giữ đúng dữ liệu quan trọng của phòng.

Prompt v1 đạt mức đủ khả thi cho prototype/integration.

---

## 5. Cost Estimate

### 5.1 Measured token usage

Kết quả đo thực tế bằng `usage_metadata` từ Gemini API:

| Test case | Input tokens | Output tokens | Thinking tokens | Total tokens | Estimated paid cost/call |
|---|---:|---:|---:|---:|---:|
| 1 | 602 | 182 | 2,425 | 3,209 | $0.024366 |
| 2 | 530 | 162 | 3,305 | 3,997 | $0.031998 |
| 3 | 582 | 168 | 1,498 | 2,248 | $0.015867 |
| **Average** | **571.33** | **170.67** | **2,409.33** | **3,151.33** | **$0.024077** |

### 5.2 Monthly estimate

Dựa trên average cost khoảng **$0.024077/call**:

| Calls/month | Estimated paid-tier cost |
|---:|---:|
| 1,000 | $24.08 |
| 5,000 | $120.39 |
| 10,000 | $240.77 |
| 50,000 | $1,203.85 |

### 5.3 Cost observation

Thinking tokens chiếm phần lớn token usage trong cả 3 lần test.

Với bài toán chỉ sinh tiêu đề và đoạn mô tả ngắn, đây là phần cần tiếp tục theo dõi nếu hệ thống chuyển sang paid tier hoặc có lượng request lớn.

---

## 6. Fallback Strategy

### 6.1 Primary flow

```text
Request
  ↓
Gemini API
  ↓
Success → return title + description
```

### 6.2 Failure flow

```text
Gemini API
  ↓
503 / timeout / temporary server failure
  ↓
Retry with exponential backoff
  ↓
Still failed
  ↓
Rule-based description generator
```

### 6.3 Rule-based fallback

Rule-based generator sử dụng trực tiếp dữ liệu có cấu trúc để ghép:

- loại phòng;
- diện tích;
- vị trí;
- giá thuê;
- tiện nghi;
- nội thất;
- giá điện/nước;
- đối tượng thuê.

Ưu điểm:

- không cần external AI API;
- không phát sinh token cost;
- output deterministic;
- không phụ thuộc availability của Gemini;
- đủ dùng để hệ thống vẫn hoạt động khi AI không khả dụng.

---

## 7. Proposed Service API Contract

### Endpoint

```http
POST /api/v1/ai/room-description
```

### Request

Backend gửi full room object sang AI service.

```json
{
  "room_type": "Phòng trọ",
  "area_m2": 20,
  "location": "Gần Đại học Bách Khoa",
  "price_vnd": 3500000,
  "amenities": ["điều hòa", "wifi"],
  "furnishing": ["tủ lạnh", "bàn ghế"],
  "utility_costs": {
    "electricity": {
      "price": 3500,
      "unit": "kWh"
    },
    "water": {
      "price": 100000,
      "unit": "person/month"
    }
  },
  "target_tenant": {
    "gender": null,
    "tenant_types": [
      "Sinh viên",
      "Người đi làm"
    ]
  }
}
```

### Success response

```json
{
  "title": "Phòng trọ 20m² gần Đại học Bách Khoa",
  "description": "..."
}
```

### Error response

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "area_m2 must be greater than 0"
  }
}
```

### Status codes

| Code | Meaning |
|---:|---|
| 200 | Description generated successfully, including fallback result |
| 400 | Invalid request/input |
| 500 | AI service and fallback both failed |
| 503 | Service temporarily unavailable |

### Authentication

Internal service-to-service authentication:

```http
Authorization: Bearer <AI_SERVICE_KEY>
```

`AI_SERVICE_KEY` được lưu trong environment variables.

### Timeout

Đề xuất timeout phía Backend: khoảng **10 giây**.

Fallback được xử lý bên trong AI service và không làm thay đổi response contract với Backend.

---

## 8. Observed Risks & Mitigations

Chỉ các vấn đề đã xuất hiện hoặc được quan sát trực tiếp trong quá trình code/test được ghi ở đây.

### 8.1 Gemini API unavailable / high demand

**Observed issue**

Trong quá trình test, Gemini API từng trả:

```text
503 UNAVAILABLE
This model is currently experiencing high demand.
```

**Mitigation**

- retry với exponential backoff;
- nếu retry vẫn thất bại, chuyển sang rule-based description.

---

### 8.2 High thinking-token usage / cost

**Observed issue**

Kết quả cost test cho thấy thinking tokens cao hơn đáng kể so với output tokens.

Average:

- output tokens: ~171;
- thinking tokens: ~2,409.

**Mitigation**

- theo dõi token usage thực tế;
- tối ưu prompt/input;
- cân nhắc model nhẹ hơn nếu chi phí vượt budget;
- rule-based fallback có thể sử dụng khi external AI không còn phù hợp về chi phí.

---

### 8.3 Output schema validation

**Observed technical requirement**

AI output cần được parse và validate trước khi sử dụng trong hệ thống.

**Mitigation**

- yêu cầu `application/json`;
- sử dụng structured output;
- validate bằng Pydantic schema;
- nếu output invalid thì retry hoặc fallback.


