# P4-09 — Chuẩn bị thẻ Credit, đăng ký AWS ($200 Credits), cấu hình Billing Alert & khởi tạo EC2

**Status:** 🟡 Open  
**Assignee:** DevOps / BE Dev (hoặc Thành viên phụ trách Hạ tầng)  
**Stakeholders / Reviewers:** PM, BE Lead  
**Created:** 2026-10-11  
**Due date:** 2026-10-14  
**Priority:** 🔴 High / Blocker (Hạ tầng Staging cho toàn bộ hệ thống Web, Mobile & Backend)  

**Input:**
- Quyết định hạ tầng: `pm/phase-3/discovery/decisions.md` ([D56](file:///D:/DUT/Ki%207/PBL6/pm/phase-3/discovery/decisions.md#L95-L108): Single-EC2 deployment với Docker Compose)
- Phân tích rủi ro & tài nguyên: `pm/phase-3/discovery/free-tier-db-storage.md`
- Các chương trình ưu đãi, nhiệm vụ trải nghiệm / thử thách trên AWS hoặc sự kiện cộng đồng để kiếm AWS Credits.

**Deliverables:**
- 01 Tài khoản AWS mới (hoặc tài khoản cá nhân sạch) đã add thẻ thanh toán quốc tế và xác minh danh tính thành công.
- Nhận và áp mã **$100 – $200 AWS Credits** thành công vào mục Billing.
- Cấu hình **AWS Budgets / CloudWatch Billing Alert** gửi email cảnh báo chi phí (tránh bị trừ tiền ngoài ý muốn).
- 01 Máy ảo **AWS EC2 Ubuntu** đang chạy (giai đoạn đầu tạo `t2.micro` kèm Swap RAM, sẵn sàng nâng lên `t3.small`/`t3.medium` khi có credits).
- Cấu hình Security Group (Inbound Rules port 22, 80, 443), tạo Elastic IP (hoặc Public IP cố định) và lưu trữ Key Pair SSH (`.pem`) an toàn cho team.
- Cài đặt sẵn Docker & Docker Compose v2 trên máy ảo EC2.

---

## 1. Hướng dẫn chi tiết từng bước (Step-by-step Guide)

### Bước 1: Chuẩn bị thẻ thanh toán & Đăng ký tài khoản AWS
1. **Chuẩn bị thẻ:**
   - Cần 01 thẻ Visa hoặc Mastercard (Debit hoặc Credit) đã mở chức năng thanh toán quốc tế.
   - Trong tài khoản thẻ cần có tối thiểu **~25.000đ – 50.000đ (khoảng $1 - $2)** để AWS trừ thử nhằm xác minh thẻ (khoản tiền này AWS sẽ hoàn lại sau vài ngày).
2. **Đăng ký tài khoản AWS:**
   - Truy cập [aws.amazon.com](https://aws.amazon.com/) chọn **Create an AWS Account** (chọn loại tài khoản *Personal*).
   - Điền email, mật khẩu và thông tin thẻ thanh toán.
   - Xác minh số điện thoại qua SMS OTP.
   - Chọn gói hỗ trợ: **Basic Support (Free)**.

---

### Bước 2: Săn ~$100 – $200 AWS Promotional Credits (Tự chủ động Research)
> 💡 *Ghi chú cho Member phụ trách:* Có rất nhiều phương thức hợp lệ để kiếm credit từ AWS (thường dao động từ $100 – $200). Nội dung này không gò bó phương thức cố định, bạn hãy chủ động tìm hiểu và lựa chọn cách nhanh/tiện nhất:

- **Một số hướng gợi ý để research:**
  - **Làm nhiệm vụ / Thử thách trên AWS:** AWS thường có các chương trình trải nghiệm, onboarding, nhiệm vụ học tập (như hoàn thành một số lab/challenge/quiz trên AWS Educate, Cloud Quest, AWS Builder ID, hoặc các khảo sát tính năng) có thưởng promo credit.
  - **Chương trình ưu đãi sinh viên / Developer:** Tận dụng email sinh viên trường hoặc các gói hỗ trợ công nghệ (GitHub Student Pack, AWS Activate, các chương trình tài trợ sinh viên làm đồ án).
  - **Sự kiện / Workshop cộng đồng:** Các buổi online seminar, AWS Community Day thường xuyên tặng voucher credit cho người tham dự.
- **Thực hiện áp mã vào tài khoản:**
  - Sau khi nhận được mã credit: Đăng nhập AWS Console $\to$ Tìm mục **Billing and Cost Management**.
  - Chọn mục **Credits** ở menu bên trái $\to$ Nhấn **Redeem credit** $\to$ Nhập Promo Code.
  - Xác nhận số dư credit đã được cộng vào tài khoản và kiểm tra thời hạn sử dụng.

---

### Bước 3: Cấu hình Cảnh báo chi phí (Billing Alert / AWS Budgets)
> ⚠️ **BẮT BUỘC THỰC HIỆN NGAY:** Bước này đảm bảo dù có cấu hình nhầm hoặc bị tấn công thì tài khoản cũng không bị phát sinh hóa đơn trừ vào thẻ ngân hàng mà không hay biết.

1. **Bật tính năng theo dõi chi phí:**
   - Vào **Billing and Cost Management** $\to$ **Billing Preferences**.
   - Tích chọn: **Receive Free Tier Usage Alerts** và **Receive CloudWatch Billing Alerts** $\to$ Điền email nhận cảnh báo $\to$ Nhấn *Save preferences*.
2. **Tạo AWS Budget (Khuyên dùng):**
   - Vào mục **Budgets** $\to$ Nhấn **Create budget**.
   - Chọn template **Zero spend budget** (báo động ngay khi tài khoản phát sinh dù chỉ $0.01 vượt quá mức Free Tier).
   - Hoặc tạo **Cost budget** đặt ngưỡng chi tiêu: ví dụ cảnh báo ở mốc **$5**, **$10** hoặc cảnh báo khi đã tiêu hết **80% số credit** được tặng.
   - Nhập danh sách email của PM và DevOps để nhận cảnh báo tức thời.

---

### Bước 4: Khởi tạo máy ảo AWS EC2 & Xử lý RAM

#### ⚠️ Lưu ý kỹ thuật về cấu hình instance (`t2.micro` vs `t3.small`/`t3.medium`):
* Người dùng hỏi: *"Tạo AWS EC2 t2.micro nhỉ?"*
* **Thực tế:** Gói Free Tier miễn phí 750 giờ/tháng cho `t2.micro` (1 vCPU, 1 GB RAM). Tuy nhiên, kiến trúc hệ thống PBL6 gồm Docker, Postgres, RabbitMQ, Redis và 4 service Node.js. Với chỉ **1 GB RAM**, máy ảo sẽ bị **tràn RAM (Out-Of-Memory - OOM)** làm crash server ngay khi chạy `docker compose up`.
* **Chiến lược tối ưu:**
  1. **Nếu chưa có Credit (dùng tạm gói Free):** Bắt buộc tạo **Swap RAM ảo (2GB - 4GB)** từ ổ đĩa SSD để bù đắp cho 1GB RAM vật lý của `t2.micro`.
  2. **Khi đã áp được $100 - $200 Credit:** Nâng cấp instance lên **`t3.small` (2 GB RAM, ~$15/tháng)** hoặc **`t3.medium` (4 GB RAM, ~$30/tháng)**. Số credit này dư sức chi trả trong 3-4 tháng làm đồ án đến ngày bảo vệ mà chạy cực kỳ mượt mà.

#### Các bước khởi tạo EC2:
1. **Launch Instance:**
   - Region: Chọn **ap-southeast-1 (Singapore)** để độ trễ về Việt Nam thấp nhất (ping ~30-40ms).
   - Name: `pbl6-staging-server`
   - OS Image: **Ubuntu Server 24.04 LTS (HVM)** hoặc **Ubuntu 22.04 LTS**, Architecture 64-bit (x86).
   - Instance type:
     - Tạm thời: `t2.micro` (Free tier eligible).
     - Khi có credit: `t3.small` hoặc `t3.medium`.
2. **Key Pair (Đăng nhập SSH):**
   - Nhấn *Create new key pair* $\to$ Tên: `pbl6-ec2-key` $\to$ Loại: `RSA` $\to$ Định dạng: `.pem`.
   - Tải file `pbl6-ec2-key.pem` về máy và lưu vào nơi an toàn (tuyệt đối không commit lên Git public).
3. **Network Settings (Security Group):**
   - Tạo Security Group mới: `pbl6-sg-web-backend`
   - Cấu hình Inbound Rules:
     - **SSH (Port 22):** Source: *My IP* (hoặc mở rộng cho IP của nhóm).
     - **HTTP (Port 80):** Source: *Anywhere (0.0.0.0/0)*.
     - **HTTPS (Port 443):** Source: *Anywhere (0.0.0.0/0)*.
     - *(Tùy chọn debug ban đầu):* Custom TCP Port 3000, 3001 nếu cần gọi trực tiếp khi chưa gắn domain.
4. **Storage (Ổ cứng):**
   - Đặt dung lượng: **25 GB – 30 GB** loại `gp3` (AWS Free Tier cho phép tối đa 30 GB EBS).
5. **Khởi tạo:** Nhấn **Launch instance**.

---

### Bước 5: Cấu hình ban đầu trên Server (Swap RAM + Docker)

Sau khi instance ở trạng thái *Running*, SSH vào server:
```bash
ssh -i "pbl6-ec2-key.pem" ubuntu@<PUBLIC_IP_EC2>
```

1. **Tạo 4GB Swap RAM (Cực kỳ quan trọng nếu dùng `t2.micro`):**
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   free -h # Kiểm tra thấy Swap 4.0Gi là thành công
   ```

2. **Cài đặt Docker & Docker Compose v2:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   sudo apt-get install -y ca-certificates curl gnupg git
   
   # Cài Docker chính thức
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   sudo chmod a+r /etc/apt/keyrings/docker.gpg
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
     $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   
   # Thêm quyền cho user ubuntu chạy docker không cần sudo
   sudo usermod -aG docker ubuntu
   ```

---

## 2. Tiêu chí nghiệm thu (Definition of Done)

1. Tài khoản AWS hoạt động bình thường, không bị trạng thái Suspended/Verification Pending.
2. Mục Credits trong Billing hiển thị số dư promotional credit đã nạp thành công (hoặc có bằng chứng đang làm các nhiệm vụ/chờ duyệt gói credit).
3. Đã kích hoạt ít nhất 01 AWS Budget cảnh báo chi phí qua email.
4. Máy ảo EC2 đang chạy (Status: 2/2 checks passed), có IP Public truy cập được.
5. SSH vào máy ảo bằng key pair thành công.
6. Lệnh `docker --version` và `docker compose version` chạy thành công trên máy ảo.
7. Lệnh `free -h` hiển thị Swap RAM $\ge$ 2GB (nếu dùng `t2.micro`).
