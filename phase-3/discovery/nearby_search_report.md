# Báo cáo thử nghiệm chức năng bản đồ và tìm trọ gần nhất

## 1. Tool và Tech Stack

### 1.1. Supabase PostgreSQL + PostGIS
Hệ thống thử nghiệm sử dụng **Supabase PostgreSQL** để lưu trữ dữ liệu và **PostGIS** để hỗ trợ dữ liệu không gian.

Đối với mỗi địa điểm/Building, ngoài địa chỉ dạng text, hệ thống lưu:
- `latitude`
- `longitude`
- `location` kiểu `geography(Point, 4326)`

PostGIS được sử dụng để hỗ trợ các truy vấn vị trí, khoảng cách và tìm các địa điểm nằm trong một phạm vi xác định.

### 1.2. TrackAsia
Sau quá trình thử nghiệm nhiều dịch vụ bản đồ, **TrackAsia được chọn làm công cụ chính cho bản demo** vì:
- Hỗ trợ tốt địa chỉ tại Việt Nam.
- Có API Geocoding.
- Có API Directions/Routing.
- Có thư viện hiển thị bản đồ trên web.
- Tài khoản thử nghiệm hiện có **100.000 credit**, đủ để phát triển và demo chức năng.

> **Lưu ý về chi phí:** Không nên kết luận TrackAsia hoàn toàn miễn phí. Dashboard hiện tại hiển thị 100.000 credit, nhưng website TrackAsia vẫn công bố cơ chế Pay As You Go và các gói trả phí cho Geocoding, Routing và các API khác. Vì vậy trong giai đoạn prototype có thể sử dụng credit hiện có, còn khi triển khai thực tế cần kiểm tra lại chính sách giá và giới hạn tài khoản.

---

## 2. Kết quả các thử nghiệm

### 2.1. Thử nghiệm lưu trữ dữ liệu với Supabase/PostGIS — Thành công

Đã tạo database trên Supabase và bật extension PostGIS.

Dữ liệu Building được lưu với:
- địa chỉ dạng text;
- latitude;
- longitude;
- `location` kiểu `geography(Point, 4326)`.

Đã thử nghiệm thành công các truy vấn khoảng cách với PostGIS, bao gồm:
- `ST_DWithin`: lọc các địa điểm nằm trong một bán kính cho trước;
- `ST_Distance`: tính khoảng cách giữa hai vị trí.

Kết quả cho thấy PostgreSQL + PostGIS phù hợp để lưu trữ và xử lý vị trí của các Building trong hệ thống Rentify.

---

### 2.2. Thử nghiệm Mapbox — Chưa phù hợp với yêu cầu

Mapbox đã được thử nghiệm cho chức năng geocoding địa chỉ.

Đối với các địa chỉ phổ biến, Mapbox có thể trả về tọa độ tương đối tốt. Tuy nhiên với các địa chỉ chi tiết như số nhà trong hẻm/kiệt, kết quả có thể chỉ xác định được tuyến đường hoặc khu vực thay vì đúng chính xác vị trí cần tìm.

Ngoài ra, việc lấy **vị trí hiện tại chính xác của người dùng** không phải do Mapbox trực tiếp cung cấp. Vị trí này thực tế được lấy từ Location Service/GPS/Wi-Fi của thiết bị hoặc Browser Geolocation API.

Do đó Mapbox chưa được chọn làm công cụ chính cho bản demo hiện tại.

---

### 2.3. Thử nghiệm Nominatim và Google Maps API — Không sử dụng

#### Nominatim / OpenStreetMap

Đã thử nghiệm Nominatim để geocode địa chỉ.

API có thể truy cập được trên trình duyệt, nhưng khi gọi bằng Python và `curl` trên máy thử nghiệm thì kết nối liên tục bị reset (`WinError 10054` / `Connection reset`).

Vì vậy Nominatim không được tiếp tục sử dụng trong bản demo.

#### Google Maps API

Google Maps được xem xét do khả năng geocoding và routing tốt.

Tuy nhiên việc sử dụng Google Maps Platform yêu cầu cấu hình billing/thẻ thanh toán. Vì mục tiêu hiện tại chỉ là prototype cho đồ án, nhóm không tiếp tục triển khai theo hướng này.

---

### 2.4. Thử nghiệm TrackAsia — Thành công

TrackAsia đáp ứng được các chức năng chính cần thiết cho bản demo.

#### a. Geocoding địa chỉ

Sử dụng **TrackAsia Search/Geocoding API** để chuyển địa chỉ dạng text thành tọa độ:

```text
Địa chỉ
→ TrackAsia Geocoding API
→ latitude + longitude
```

Trong demo, có thể đặt `k = 1` để chỉ lấy kết quả đầu tiên mà TrackAsia trả về cho mỗi địa chỉ.

#### b. Khoảng cách đường chim bay

Khoảng cách đường chim bay được tính bằng **công thức Haversine** trong Python.

Công thức chỉ sử dụng latitude và longitude của hai điểm, không xét đến hệ thống đường giao thông.

```text
Vị trí người dùng
──────────────
      ↓
Khoảng cách đường chim bay
      ↓
Địa điểm đích
```

#### c. Khoảng cách thực tế theo đường đi

Sử dụng **TrackAsia Directions API** với chế độ `driving`.

API nhận:
- tọa độ vị trí hiện tại;
- tọa độ địa điểm đích.

Sau đó TrackAsia tìm tuyến đường phù hợp trên mạng lưới giao thông và trả về **distance** của route.

Đây là khoảng cách được dùng cho chức năng **tìm trọ trong phạm vi X km**.

Ví dụ:

```text
Người dùng nhập radius = 2 km

Building A: 1.2 km → giữ lại
Building B: 3.5 km → loại
Building C: 1.8 km → giữ lại
```

#### d. Thời gian di chuyển ước tính

Thời gian được lấy trực tiếp từ kết quả của **TrackAsia Directions API**.

API trả về thời gian của route theo giây, sau đó chương trình chuyển sang phút để hiển thị.

```text
TrackAsia Directions API
→ duration (giây)
→ chuyển sang phút
```

Thời gian có thể chênh lệch so với Google Maps vì mỗi nền tảng sử dụng dữ liệu và mô hình ước tính thời gian khác nhau.

#### e. Hiển thị bản đồ

Website demo sử dụng **TrackAsia GL JS** để hiển thị bản đồ tương tác trên trình duyệt.

Bản đồ demo có:
- marker vị trí hiện tại của người dùng;
- marker các địa điểm phù hợp;
- tuyến đường từ người dùng đến từng địa điểm;
- khoảng cách đường đi;
- thời gian di chuyển dự kiến.

Route được lấy từ **TrackAsia Directions API**, sau đó polyline được giải mã và vẽ lên bản đồ dưới dạng `LineString`.

Luồng demo hiện tại:

```text
Lấy vị trí hiện tại
        ↓
Danh sách địa chỉ Building
        ↓
TrackAsia Geocoding (k = 1)
        ↓
TrackAsia Directions
        ↓
Tính khoảng cách + thời gian
        ↓
Lọc theo radius do người dùng nhập
        ↓
Sắp xếp gần → xa
        ↓
Hiển thị các địa điểm phù hợp trên TrackAsia Map
```

---

## 3. Kết luận

Prototype hiện tại đã kiểm chứng được các phần quan trọng của chức năng **tìm trọ gần vị trí người dùng**:

- Lưu dữ liệu vị trí bằng Supabase PostgreSQL + PostGIS: **Thành công**.
- Lấy vị trí hiện tại của thiết bị bằng Browser Geolocation: **Thành công**.
- Geocode địa chỉ bằng TrackAsia: **Thành công**.
- Tính khoảng cách đường chim bay bằng Haversine: **Thành công**.
- Tính khoảng cách thực tế bằng TrackAsia Directions: **Thành công**.
- Tính thời gian di chuyển dự kiến: **Thành công**.
- Lọc địa điểm theo bán kính người dùng nhập: **Thành công**.
- Hiển thị marker và route trên bản đồ bằng TrackAsia GL JS: **Thành công**.

Với kết quả thử nghiệm hiện tại, **TrackAsia + PostgreSQL/PostGIS** là hướng phù hợp để tiếp tục phát triển prototype của chức năng bản đồ cho Rentify.
