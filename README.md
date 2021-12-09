# Vuanem Ecommerce Service

[![CI/CD](https://github.com/vuanembi/vuanem-ecommerce-service/actions/workflows/main.yaml/badge.svg)](https://github.com/vuanembi/vuanem-ecommerce-service/actions/workflows/main.yaml) [![Hits-of-Code](https://hitsofcode.com/github/vuanembi/vuanem-ecommerce-service)](https://hitsofcode.com/github/vuanembi/vuanem-ecommerce-service/view) ![Lines of code](https://img.shields.io/tokei/lines/github/vuanembi/vuanem-ecommerce-service)

- [Vuanem Ecommerce Service](#vuanem-ecommerce-service)
  - [Architect](#architect)
    - [SuiteScript](#suitescript)
    - [Event Handler App](#event-handler-app)
    - [Firestore](#firestore)
    - [Tiki](#tiki)
  - [Sử dụng](#sử-dụng)
    - [Telegram](#telegram)
    - [Tiki](#tiki-1)

---

## Architect

### SuiteScript

NetSuite Records are integrated using REST API specs. Details can be found on **Postman**.

- Methods:
  - `GET`: Get a Record
  - `POST`: Create a Record
  - `DELETE`: Soft delete a Record
- Response Statuses:
  - `200`: **Success**
  - `400`: **Not Found**
  - `>400`: **Failure**

### Event Handler App

NetSuite Event Handler App is built upon MVC architecture, using **Cloud Function/Functions Framework** as runtime.

The app follows semi-Functional Programming Paradigm.

### Firestore

Stateful data (Tiki ack_ids, etc) are stored in **Firestore** NoSQL.

### Tiki

Tiki utilises `Event Queue API`, polling data at a specified frequency. Upon receving events, the App will call `Resources API` to get details.

---

## Sử dụng

### Telegram

Telegram đc vận hành bằng Bot để gửi tin nhắn và nhận yêu cầu từ ng dùng. Có 2 loại tin nhắn

- **Thông tin**: Chỉ cung cấp thông tin, ko yêu cầu ng dùng input
- **Yêu cầu**: Cung cấp các lựa chọn sẵn cho chính đối tượng tin nhắn đang nói đến, gắn vào với **chính tin nhắn đó** sẽ ko tạo ra thay đổi gì nếu ko có input của ng dùng

Với mỗi tin nhắn **thông tin**, Telegram sẽ hiển thị thêm 2 nút quick reply:

![Telegram Reply](docs/tele-reply.png)

Ng dùng có thể sử dụng để trả lời nhanh + reply vào tin nhắn vừa, đánh dấu tình trạng. Dựa trên các tình huống trên sàn, Telegram sẽ gửi tin nhắn:

- Đã có đơn hàng đc tạo trên sàn
  - Bot sẽ hiển thị thêm 1 nút **Tạo đơn** ![Telegram Keyboard New](docs/tele-kb-new.png).
- Đơn hàng trên đã đc tạo thành công trên NetSuite
  - Bot sẽ hiển thị thêm nút **Đóng đơn** ![Telegram Keyboard Created](docs/tele-kb-created.png).

### Tiki

App sẽ check đơn hàng của Tiki **15p/lần**.

Tính năng hiện tại:

- Tạo đơn trên Tiki
  1. Thông báo tạo đơn: Thông tin về đơn hàng:
     - Mã đơn
     - SĐT
     - Địa chỉ
       - Địa chỉ
       - Phường
       - Quận
       - Thành phố
     - Sản phẩm
       - Tên
       - SKU
  2. Thông báo tạo đơn trên NetSuite: Thông tin về đơn hàng đã tạo:
     - **Cần thêm thông tin về Giao hàng**
     - Đường link mở đơn hàng để check
