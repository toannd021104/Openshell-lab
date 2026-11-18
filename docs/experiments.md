# Thí nghiệm A–D

Chưa có thí nghiệm nào được chạy trong lần tạo repo này. Các dòng dưới là thao tác
cho người học thực hiện sau; kết quả mong đợi không phải kết quả đo.

## A — Xác nhận kernel riêng

```bash
kubectl -n sandbox-lab wait --for=condition=Ready pod/baseline pod/kata --timeout=180s
bash scripts/observe-kernels.sh | tee evidence/kernels.txt
```

Hai pod phải ở cùng node đã chọn. Đối chiếu `boot_id`, `/proc/uptime`,
`/proc/cmdline`, `uname -r`, `nproc`. Baseline dùng kernel node; Kata có kernel guest.
`uname -r` giống nhau vẫn có thể là hai kernel khác nhau. Uptime có thể được runtime
ảo hóa; số CPU phụ thuộc cgroup. Dùng nhiều tín hiệu, thêm kiểm tra process QEMU
và `crictl inspectp` trên node nếu cần, thay vì kết luận chỉ từ một giá trị.

## B — Chi phí khởi động

```bash
python3 scripts/benchmark-startup.py --node "$LAB_NODE" --runs 5
```

Script tạo từng pod trên cùng node rồi xóa đúng pod đó, đổi thứ tự giữa các vòng,
ghi CSV thời gian từ gửi create đến Ready. Lần đầu bao gồm pull image; tách cold/warm
khi phân tích, ghi phiên bản node/Kata/containerd, cấu hình vCPU/RAM guest, tải node.
Tính median và min/max của mẫu thành công cho từng runtime. Đây là benchmark startup,
không phải benchmark CPU, RAM thực dùng hay chứng minh chống kernel exploit.
Sau B mới đọc [Red Hat phần 2](https://developers.redhat.com/articles/2026/07/23/why-your-ai-agent-needs-two-sandboxes-benchmark-data).
Nếu bài đo tiêu chí khác, không so trực tiếp con số.

## C — OpenShell policy (không Kata)

Sau bước 5 của README, ở terminal riêng:

```bash
bash scripts/create-sandbox.sh openshell-only
# Terminal khác:
openshell sandbox connect opencode-openshell-only
```

Trong shell do OpenShell cung cấp (không dùng `kubectl exec` để kiểm tra policy):

```bash
/usr/bin/curl --fail --max-time 15 https://api.github.com/zen
/usr/bin/curl --fail --max-time 15 https://example.com/
printf 'LAB_FAKE_TOKEN=not-a-real-secret\n' > /sandbox/fake-token.txt
/usr/bin/curl --fail --max-time 15 -X POST https://api.github.com/zen \
  --data-binary @/sandbox/fake-token.txt
```

Mong đợi: GET GitHub được phép; example.com bị chặn; POST GitHub bị policy read-only
chặn. Lưu cả stdout, stderr, exit code và log supervisor. DNS lỗi, timeout hoặc 4xx
của server không đủ chứng minh policy đã chặn. Xác nhận có bản ghi policy deny;
Nếu không có, đánh dấu INCONCLUSIVE. Đối chiếu đường dẫn `command -v curl` với policy.
`best_effort` không bảo đảm Landlock hoạt động: kiểm tra log về kernel/ABI trước khi
kết luận filesystem được bảo vệ.

## D — OpenShell + Kata

```bash
bash scripts/create-sandbox.sh dual
# Terminal khác:
openshell sandbox connect opencode-dual
```

Lặp lại ba lệnh curl của C. Từ máy quản trị:

```bash
kubectl -n openshell get pods -o custom-columns=NAME:.metadata.name,RUNTIME:.spec.runtimeClassName,NODE:.spec.nodeName
```

Xác định pod của sandbox từ `openshell sandbox list` và metadata; không giả định tên
pod Kubernetes luôn trùng tên sandbox. Pod dual phải có `runtimeClassName: kata-qemu`.
Trong shell OpenShell, đọc lại các chỉ dấu kernel ở A. Cần đồng thời có bằng chứng
policy deny và kernel guest; chỉ một trong hai chưa đủ.

| Quan sát | Baseline | Kata | OpenShell | Dual |
|---|---|---|---|---|
| Kernel riêng | Không | Mong đợi | Không nếu default=runc | Mong đợi |
| Egress theo policy OpenShell | Không | Không | Mong đợi | Mong đợi |
| Kết quả thực đo | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |

Lab không tái hiện CVE trong PoC; kiểm tra kernel và egress không chứng minh khả
năng chống mọi container escape. Không có LLM cần chạy: lệnh giả lập hành động mà
agent có thể thực hiện sau prompt injection.
