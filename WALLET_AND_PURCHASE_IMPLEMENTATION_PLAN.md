# 钱包系统和购买功能完整实现方案

## 📋 审计结果总结

### 现有资源：
1. ✅ **UserProfile模型** 已有 `balance` 字段（余额）
2. ✅ **Order模型** 订单基础结构已存在
3. ✅ **OrderPayment模型** 支付记录结构已存在
4. ✅ **用户菜单** 下拉菜单结构已存在（在base.html）
5. ✅ **购买按钮** 车辆详情页已有"立即购买"按钮

### 需要新增：
1. ❌ User模型缺少 `payment_password` (交易密码)字段
2. ❌ 缺少钱包充值记录模型
3. ❌ 缺少钱包页面模板
4. ❌ 缺少订单创建页面模板
5. ❌ 缺少订单列表页面模板
6. ❌ 缺少相关API端点

---

## 🎯 功能模块划分

### 模块1: 钱包系统 (Wallet System)

#### 1.1 数据库层
- **新增字段**: User模型添加 `payment_password` (交易密码，加密存储)
- **新增模型**: `WalletTransaction` (钱包交易记录)
  - 字段：user, amount, type(充值/消费/退款), status, payment_method, created_at

#### 1.2 后端API
- **设置交易密码**: `POST /api/users/set-payment-password/`
- **验证交易密码**: `POST /api/users/verify-payment-password/`
- **获取钱包信息**: `GET /api/users/wallet/`
- **充值**: `POST /api/users/wallet/recharge/`
- **交易记录**: `GET /api/users/wallet/transactions/`

#### 1.3 前端页面
- **我的钱包页面**: `/wallet/`
  - 显示余额
  - 充值按钮
  - 交易记录列表
- **首次访问弹窗**: 设置6位数字交易密码
- **充值弹窗**:
  - 输入金额
  - 选择支付方式（微信/支付宝/银行卡）
  - 输入交易密码

#### 1.4 导航栏修改
- 在用户下拉菜单中添加"我的钱包"选项（在"个人中心"上方）

---

### 模块2: 购买流程 (Purchase Flow)

#### 2.1 订单模型扩展
- **扩展Order模型**:
  - 添加: delivery_address, delivery_time, buyer_phone, vehicle_color, vehicle_model_type

#### 2.2 后端API
- **创建订单**: `POST /api/orders/`
  - 参数：vehicle_id, color, model_type, phone, address, delivery_time, payment_password
  - 逻辑：
    1. 验证交易密码
    2. 检查余额是否足够
    3. 扣除余额
    4. 创建订单
    5. 创建支付记录
    6. 更新车辆状态
- **订单列表**: `GET /api/orders/`
- **订单详情**: `GET /api/orders/{id}/`

#### 2.3 前端页面
- **订单创建页面**: `/orders/create/{vehicle_id}/`
  - 车辆信息展示
  - 表单：颜色、款型、电话、地址、送达时间
  - 确定下单按钮
- **订单列表页面**: `/orders/`
  - 订单卡片列表
  - 订单详情按钮
- **订单详情弹窗**: 显示完整订单信息

#### 2.4 支付密码验证弹窗
- 输入6位数字密码（星号隐藏）
- 确认/取消按钮
- 密码验证逻辑

---

## 📐 数据库设计

### 1. User模型扩展
```python
class User(AbstractUser):
    # 现有字段...
    payment_password = models.CharField(max_length=128, null=True, blank=True, verbose_name='交易密码')
```

### 2. WalletTransaction模型
```python
class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('recharge', '充值'),
        ('purchase', '购买'),
        ('refund', '退款'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('wechat', '微信'),
        ('alipay', '支付宝'),
        ('bank', '银行卡'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('success', '成功'),
        ('failed', '失败'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.CharField(max_length=255)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3. Order模型扩展
```python
class Order(models.Model):
    # 现有字段...
    # 新增字段
    buyer_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    delivery_time = models.DateTimeField()
    vehicle_color = models.CharField(max_length=50, null=True, blank=True)
    vehicle_model_type = models.CharField(max_length=100, null=True, blank=True)
```

---

## 🔐 安全设计

### 交易密码加密
- 使用Django的 `make_password()` 和 `check_password()` 进行加密
- 与登录密码分离存储
- 密码输入时前端用星号隐藏

### 余额操作
- 使用数据库事务确保原子性
- 操作前验证交易密码
- 记录所有交易日志

---

## 🎨 UI设计要点

### 1. 我的钱包页面
- 顶部：余额大卡片（醒目显示）
- 中部：充值按钮
- 底部：交易记录列表（分页）

### 2. 充值弹窗
- 输入金额
- 三选一支付方式（单选按钮）
- 输入交易密码
- 确认/取消按钮

### 3. 订单创建页面
- 左侧：车辆信息卡片
- 右侧：订单表单
  - 颜色选择（下拉或输入）
  - 款型选择（下拉或输入）
  - 联系电话
  - 配送地址
  - 送达时间（日期时间选择器）
- 底部：总价显示 + 确定下单按钮

### 4. 订单列表页面
- 卡片式布局
- 每个订单显示：车辆图片、基本信息、状态、价格
- 详情按钮

---

## 🔄 实现步骤

### 阶段1: 数据库和模型（优先级：高）
1. 修改User模型添加payment_password字段
2. 创建WalletTransaction模型
3. 扩展Order模型
4. 生成并执行数据库迁移

### 阶段2: 钱包后端API（优先级：高）
1. 实现设置交易密码API
2. 实现验证交易密码API
3. 实现钱包信息API
4. 实现充值API
5. 实现交易记录API

### 阶段3: 订单后端API（优先级：高）
1. 实现创建订单API（包含支付逻辑）
2. 实现订单列表API
3. 实现订单详情API

### 阶段4: 前端页面（优先级：中）
1. 创建钱包页面模板
2. 创建订单创建页面模板
3. 创建订单列表页面模板
4. 修改导航栏添加"我的钱包"入口

### 阶段5: 前端交互（优先级：中）
1. 实现设置交易密码弹窗
2. 实现充值弹窗
3. 实现支付密码验证弹窗
4. 实现订单详情弹窗

### 阶段6: 测试和优化（优先级：低）
1. 测试钱包充值流程
2. 测试购买流程
3. 测试余额不足情况
4. 测试密码错误情况
5. 优化用户体验

---

## ⚠️ 注意事项

1. **不影响现有功能**: 所有修改都是新增或扩展，不删除现有代码
2. **数据一致性**: 使用数据库事务处理余额操作
3. **安全性**: 交易密码必须加密存储，验证时使用安全比对
4. **用户体验**: 提供清晰的错误提示和成功反馈
5. **代码规范**: 遵循现有项目的代码风格和结构

---

**方案制定时间**: 2025-11-05
**预计实现时间**: 分阶段实施，每个阶段独立测试
**文档版本**: v1.0
