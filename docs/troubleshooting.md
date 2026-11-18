# Gỡ lỗi theo từng lớp

- Pod Pending: `kubectl -n sandbox-lab describe pod kata`; kiểm tra label node,
  taint/toleration, request tài nguyên và RuntimeClass có tồn tại.
- FailedCreatePodSandBox: đối chiếu handler `kata-qemu` trong RuntimeClass với
  containerd trên đúng node; kiểm tra log kata-deploy, kubelet và containerd.
  RuntimeClass chỉ chọn handler, không cài runtime. Không sửa containerd theo cấu
  hình của version khác rồi restart mù quáng.
- Không có KVM: kiểm tra `/dev/kvm`, VT-x/AMD-V, nested virtualization của máy host.
  kind/Docker Desktop không tự cung cấp KVM cho Kubernetes worker.
- Kata Ready nhưng chưa chắc VM: xem các chỉ dấu của A và process hypervisor trên
  node. Phiên bản kernel giống nhau không phải lỗi.
- OpenShell Pending: xem PVC và default StorageClass, `kubectl -n openshell get pvc`.
- OpenShell + Kata lỗi namespace/network: guest kernel cần các tính năng OpenShell
  sử dụng, gồm network namespace, veth, seccomp và Landlock nếu muốn filesystem
  enforcement. Sửa guest kernel/image phù hợp với bản Kata, không sửa host rồi
  giả định guest đã đổi. PoC có MachineConfig riêng cho OpenShift, không áp dụng
  trực tiếp lên Kubernetes thường.
- Curl timeout: kiểm tra DNS, proxy, CNI và log policy; timeout không đồng nghĩa deny.
- CLI không nhận `--driver-config-json`: kiểm tra đang dùng v0.0.116. Không trộn
  chart cũ với CLI mới; xem `openshell sandbox create --help` trước khi đổi version.

[DZone](https://dzone.com/articles/deploying-validating-kata-containers) là tài liệu
bổ sung khi cài lỗi; URL trả 403 trong phiên chuẩn bị này nên chưa đối chiếu nội dung.
