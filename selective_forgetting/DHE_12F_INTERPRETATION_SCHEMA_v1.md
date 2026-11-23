# DHE_12F_INTERPRETATION_SCHEMA_v1

**类别**：REPORTING / INTERPRETATION STRUCTURE（非结果、非门、非判据）
**授权**：凌翼 §5（`YES — PRODUCE IT`）+ Mion 三条 + 睫 ①②
**作者**：Coder（**只产结构**）
**日期**：2026-09-24
**状态**：DESIGNED — awaiting seal

---

## 0. 本文件的边界（先声明，防误用）

本 schema **只定义报告结构与 claim ceiling**，不含任何当前结果数值，也不指定当前落在哪一格。

| 它是什么 | 它不是什么 |
|---|---|
| 措辞稿的**唯一结构输入** | 一份"在不知道结果情况下重写结果"的练习 |
| 结果填进去之前的**语法** | 一个 statistical qualification criterion |
| 冻结的**强度阶梯**骨架 | 一个新的 gate |
| 具名诊断项的**清单** | 诊断项的当前取值 |

> **The result may fill the report; it may not redesign the grammar of the report.**

### 0.1 具名占位符规则（睫 ①）

凡是被隐去的数值位，**必须留一个具名占位符** —— 一个有名的洞，好过一个没名的洞：

```text
[C_raw : REDACTED UNTIL DRAFT]
[C_signed : REDACTED UNTIL DRAFT]
[Delta_C : REDACTED UNTIL DRAFT]
[fraction_positive_raw : REDACTED UNTIL DRAFT]
[fraction_positive_signed : REDACTED UNTIL DRAFT]
[shore_A_mean : REDACTED UNTIL DRAFT]
[shore_B_mean : REDACTED UNTIL DRAFT]
[shore_max_abs_gap : REDACTED UNTIL DRAFT]
[item_max_abs : REDACTED UNTIL DRAFT]
[lambda_over_mean_delta_norm : REDACTED UNTIL DRAFT]
[lambda_over_perpair_norm : REDACTED UNTIL DRAFT]
```

起草者必须看见"那里原本站着一个数"，而不是看见空白。

---

## A. Registered decisions（预注册判定）

固定结构，**结果填位**：

| 判定位 | 定义（预注册） | 允许取值 |
|---|---|---|
| `H_raw` | `C_raw > 0` | `PASS` / `FAIL` |
| `H_signed` | `C_signed > 0` | `PASS` / `FAIL` |
| `Delta_C` role | `C_signed - C_raw`，SECONDARY comparator | **永不**是 gate / 永不 rescue |
| `result_class` | 由 `H_raw × H_signed` 唯一确定 | `A` / `B` / `C` / `D` |

**两条 primary 必须同等地位申报。** 不报赢的那个，不把 `Delta_C` 塞脚注。

### A.1 四格 → 措辞映射（预冻，不填当前格）

| 类 | `H_raw` | `H_signed` | 预冻措辞 |
|---|---|---|---|
| `A` | PASS | PASS | 两个 estimator package 都展示 held-out 因果效应；`Delta_C` 为描述 |
| `B` | FAIL | PASS | raw 互反平均 null 与方向相消相容；material-aligned estimator 恢复出 held-out 因果效应 ⇒ **"方向设定被证伪"，不是"记忆存在"**；**不作换臂主张** |
| `C` | PASS | FAIL | 已有 primary（raw）成立；signed 未成立；报 `Delta_C` 为描述性 |
| `D` | FAIL | FAIL | 两个线性聚合 estimator 都未展示冻结的因果效应；**仍然不是"没有记忆"** |

> **Freeze the grammar before filling in the values.**

### A.2 C 类的最小完整表述（五句不可拆）

`result_class = C` 时，完整表述**必须同时包含**以下五条。任何省略其余四句、单独引用其中一句的写法，构成**选择性申报**：

1. `H_raw` = PASS，`C_raw` = `[C_raw : REDACTED UNTIL DRAFT]`
2. 该 PASS 是**符号级**，不是量级级：`fraction_positive` = `[fraction_positive_raw : REDACTED UNTIL DRAFT]`
3. 两臂反号，对称化**承重**：`[shore_A_mean : REDACTED]` vs `[shore_B_mean : REDACTED]`
4. `H_signed` = FAIL，`C_signed` = `[C_signed : REDACTED UNTIL DRAFT]`
5. `C_raw` PASS **不是**"记忆存在"的证据；`C_signed` FAIL **不是**"记忆不存在"的证据

---

## B. Mandatory contextual decomposition（强制语境分解）

任何 `C_raw` / `C_signed` 的呈报，必须同时呈报以下四项。**缺一即不完整呈报。**

| # | 分解项 | 具名占位符 |
|---|---|---|
| B1 | item-level distribution（mean / median / q05 / q25 / q75 / q95 / min / max / n_positive / N） | `[item_max_abs : REDACTED]` |
| B2 | pair-level distribution（同上一组 + 每 pair 聚合规则） | — |
| B3 | **shore A / shore B decomposition**（各自的 mean 与符号） | `[shore_A_mean : REDACTED]` `[shore_B_mean : REDACTED]` |
| B4 | **reference-state declaration** | 见 `REFERENCE_STATE_SELF_DECLARATION` |

### B.3 shore 分解为何是强制项而非脚注

若 $C_A$ 与 $C_B$ 反号，则净均值是**两个相反效应之差**，**不是**"效应的量级"。

- `net = ½(C_A + C_B)` 可以接近零，同时 `|C_A|`、`|C_B|` 都很大
- 此时 `fraction_positive ≈ 0.5` 是**结构必然**，不是"效应很弱"的证据

$$ \boxed{\textbf{A positive net slope built from opposite constituent slopes is a real net slope} \\ \textbf{— but not a robust common slope.}} $$

### B.4 `REFERENCE_STATE_SELF_DECLARATION`（已立常设规则）

任何 `difference` / `delta` / `contrast` / `causal effect` / `slope` / `shift`，若不声明以下三项，则 scientific provenance 不完整：

```text
relative to what state?
under what conditioning context?
with which sign convention?
```

$$ \boxed{\textbf{A difference without a declared reference state is not yet a scientific quantity.}} $$

**已登记同病历史**：`a0` 缺"坐标系"（这个数属于哪个对象）；`12F-v1` 缺"参考态"（这个差值从哪个参考态减出来）。**同一形状。**

### B.5 `REFERENCE_SCALE_SELF_DECLARATION`（睫 ② 提议，与 B.4 并列）

对数**剂量型**量（如 `lambda`），若不声明"一份是相对于**哪一个自然大小**而言的"，则剂量-反应的解释不完整：

```text
dose = lambda
relative to which natural scale?  (global mean ||delta|| ? per-pair mean ||delta|| ? unit norm ?)
```

$$ \boxed{\textbf{Do not use one ruler to set the divisions of another ruler.}} $$

**与 B.4 的区别**：B.4 问"这个差相对于**哪一岸**"；B.5 问"这个剂量相对于**哪一个大小**才算一份"。

**已知对照**：`PC_CAL` 那次无此病 —— `d_PC` 是单位化的梯度方向，**它没有"自然大小"**，于是 `alpha * S` 是唯一可选的尺。而 `d_M` **有**自然大小。

> ⚠️ 本项状态：**PROPOSED — pending 凌翼 ruling**。`d_M` 的两个候选自然尺分别为 `mean_delta_norm_f64 = 0.32388130550063315`（全局，成对抵消后的残数）与 per-pair mean norm（待定义确认）。Coder 不裁二者谁是有效尺。

---

## C. Claim ceilings（措辞天花板）

### C.1 `H_raw PASS` 许可 / 不许可

| 许可 | 不许可 |
|---|---|
| `PRESPECIFIED AGGREGATE CONTEXT-DERIVED CAUSAL CONTRAST = POSITIVE` | `CAUSAL TRACE DEMONSTRATED` |
| `positive net effect after prespecified symmetric averaging` | `positive effect on each constituent shore` |
| 陈述预注册符号判定成立 | `memory causal effect demonstrated` |
| 陈述在冻结构造下产生了正的净对比 | `raw design worked` |
| — | `the causal effect was robust across episode states` |
| — | `the same direction worked from both shores` |
| — | `the effect generalized across A/B conditioning` |
| — | `most episodes showed a same-direction causal shift` |

$$ \boxed{\textbf{A gate determines the registered decision; it does not automatically license every stronger English sentence.}} $$

### C.2 `H_signed FAIL` 许可 / 不许可

| 许可 | 不许可 |
|---|---|
| `SIGNED ALTERNATIVE = FAIL`（真实结果，不解释掉） | `signed 理论其实仍然是对的` |
| 陈述 derive geometry 与 reciprocal-component 图像**定量相容** | `signed 错了`（作贬义判断） |
| 陈述"几何整齐性没有自动转化为因果有用性" | 把 signed 降级为"非正式试跑"或"探索性" |

**冻结句**：

> The derive geometry was quantitatively compatible with the reciprocal-component picture, but the resulting signed estimator did not produce the prespecified positive held-out causal contrast.

> **geometric coherence does not automatically imply causal usefulness.**

### C.3 强度阶梯（`STRENGTH LADDER`，睫 ⑤ —— 本窗未冻，下一轮开门前必冻）

本窗暴露的结构性缺陷：**"一扇通过的门究竟许可多强的一句话"，这次的答案是事后给的。**

下一轮开门前必须预冻：

```text
[门结果] x [稳健性诊断]  ->  [预先命名的强度档位]
```

其中"稳健性诊断"至少包含：item-sign support、shore 同号性、量级/均值比。

> 否则每一次通过，都要临时开会决定"能说多大"。

---

## D. Forbidden upgrades（禁止升级项）

以下措辞在任何结果格下都**不得**出现，除非另有独立授权实验：

```text
persistent memory
memory persistence
memory retained across delay
interference resistance
transplantation
digital hippocampus
cross-shore robustness
role-invariant memory direction
layer-23 specificity
no memory
memory absent
digital hippocampus absent
```

**特别**：`layer-23 specificity` 禁用理由 —— `l* = 23` 是在归一化响应近乎相等（span ~4.8%）下选出的；任何行为效应**不得**读成"第 23 层特殊"。

**特别**：`no memory` / `memory absent` / `digital hippocampus absent` 禁用理由 —— `C_raw <= 0` 无法区分"因果缺席"与"estimator 方向设定失配"。

### D.1 Retention-family 分离（不可跨）

```text
retention        = NOT ENTERED
delay            = NOT ENTERED
interference     = NOT ENTERED
transplantation  = NOT ENTERED
```

`E ‖ F` 是**零延迟的 in-context 结构** ⇒ Persist 这一节 **v0.1 从未检验**。

> **不许让"舵被推动了"静默跨成"记忆留存了"。**

`12F` 只碰了 **in-context 因果**；`Persist` 是另一个问题、另一条线、另一次授权。

---

## E. Interpretation branches（预写结构，不填当前格）

```text
E1  raw+ / signed+   -> class A
E2  raw+ / signed-   -> class C
E3  raw- / signed+   -> class B
E4  raw- / signed-   -> class D
```

**当前落在哪一格：`[result_class : REDACTED UNTIL DRAFT]`**

每格必须伴随 A.2 式的"最小完整表述"清单；本 schema 不预先填入任何一格的当前适用性。

---

## F. Mechanism questions（机制问题，MECHANISM IDENTIFICATION = OPEN）

下一轮**不是**先问"memory 到底有没有"，而是：

$$ \boxed{\textbf{为什么相同 frozen direction / operator 在两个 reference shores 上得到反号 causal slopes？}} $$

### F.1 三个并列候选（均为候选，本窗不裁）

| id | 假设 | 内容 |
|---|---|---|
| `M1` | Context/state-dependent causal geometry | 同一个 `d_M` 在 `E_A` 与 `E_B` 附近对应**不同局部 Jacobian**，因此同一 intervention direction 产生相反 output derivative |
| `M2` | Finite-dose nonlinearity / overshoot | 冻结的 `lambda` 可能已超出两个 shores 中至少一个的局部线性区，出现回弹/符号翻转 |
| `M3` | Material-design consequence（Mion 补充） | `12E` 的 `R_g = 24/24 negative` 不是偶然，是 `MATERIAL_PAIR_RECIPROCITY = CONFIRMED`；材料本身设计成两两反向 ⇒ 行为层面的两岸反号可能是其**下游表现** |

**当前数据不能区分 M1 / M2 / M3。**

> 下一轮的题不是"134 倍怎么了"，而是：**"这个材料本身就是设计成两两反向的，那么把它注入行为，两臂反号是设计的结果，还是记忆的属性？"**

### F.2 机制问题的登记项（DESCRIPTIVE / POST-HOC，不设门）

| id | 诊断 | 说明 |
|---|---|---|
| `F.2a` | shore dependence | 两臂均值与符号、单项最大臂间差 |
| `F.2b` | dose nonlinearity / overshoot | 需要 `REFERENCE_SCALE_SELF_DECLARATION` 先声明尺 |
| `F.2c` | state-dependent Jacobian | 需局部导数估计 |
| `F.2d` | reciprocal geometry | `R_g` 分布（`DESCRIPTIVE ONLY`，无阈值） |
| `F.2e` | reference-state asymmetry | 两 shore 作为参考态的不对称性 |

### F.3 四条件格重排（睫 ④）

```text
(A, +lambda) (A, -lambda) (B, +lambda) (B, -lambda)   四格均值
```

用途：若 `f(x)` 在两 shore 之间有一个 **interior maximum**，它会直接现形（`f` 在 `x=0` 上升、在 `x=1` 下降）。

**标注**：`DESCRIPTIVE` + `POST-HOC`；**不设门**、**不改** `result_class`、**零新 forward**（数据已在）。

---

## G. 角色与职权（凌翼 §6）

```text
Coder      -> 只产结构清单（本文件）
睫          -> 审 scientific claim boundaries
钳星        -> 审 provenance / operational definitions
凌翼        -> 最终合并 scientific interpretation
Mion       -> 对语言是否偷渡强结论做独立检查（不赋予新 scientific authority）
```

$$ \boxed{\textbf{Authority belongs to definitions and frozen roles, not personalities.}} $$

### G.1 措辞稿来源（睫 ⑤ —— 悖论及其出路）

**悖论**：Mion 的规则是"先看结构、再看符号"；但我们四人现在**全看过符号了**，严格说谁都不"干净"。

**出路（真实存在）**：`C` 类的措辞在 `12F` 开门**之前**就已经冻死（"已有 primary 成立，signed 未成立；`Delta_C` 作描述性"）。那份文本是**预注册**，不是看着符号写出来的。

```text
措辞稿 = [誊写已冻 C 类文本] + [单独标明"新增收紧项为事后"]
```

**必须标注为"事后"的收紧项**：

```text
暂缓 CAUSAL TRACE DEMONSTRATED
禁止表述清单（robust across shores / generalized across A/B / ...）
引用单元规则
```

**风险方向判定**：以上均为**向下收紧**，不是向上加码 ⇒ 风险方向安全。

---

## H. 工程记录（凌翼 §4 —— 不作 merit field）

| id | 记录 | cause | scope | correction | regression guard | 科学结果是否被暴露 |
|---|---|---|---|---|---|---|
| `FORWARD-AXIS REASONING ERROR` | 12F-v1 预算推理 | 把 proposal 维误认为缺失轴 | 协议预算 + 理由陈述 | 重推科学对象，补 `episode_arm` 轴 | ⚠️ **无 fixture**（纯推理态，无代码路径） | **NO** |
| `SYMMETRIZATION IMPLEMENTATION DEVIATION` | runner 初稿 | 自创跨臂相减，偏离 §5 冻结式 | 单文件、启动前拦截 | 按冻结式重写 | ⚠️ **待补 fixture**：`F_SYMMETRIZATION_MUST_BE_WITHIN_ARM_NOT_CROSS_ARM` | **NO** |
| `REPORTING-SEMANTICS ERROR` | 报告 provenance 字段 | 合并"是否消费"与"是否作未注册行为读" | 报告 + artifact guards 字段 | 拆 5 字段，supersede 引用 | ✅ 已有 `DHE_12F_REPORTING_SEMANTICS_CORRECTION.json` | **NO** |

> **自报错误不是美德，是职责；防止同类错误再发生，才是进步。**

> **SEMANTIC-IDENTITY-DEFECT 第 6 次**（Mion）：`U_{0,artifact} != U_{0,spec}` / `MistralDecoderLayer` / `s(x)` 两种读法 / 签字人身份 / `Earlier` / `logits_consumed`。同一个形状：名字看起来对，形状看起来对，但**对象还没被确定**。

---

## I. Frozen sentences（本格新增）

> The result may fill the report; it may not redesign the grammar of the report.

> Reference state is part of the quantity, not metadata attached afterward.

> A positive net slope built from opposite constituent slopes is a real net slope — but not a robust common slope.

> A failed gate does not become a pass because we later discover why the count was larger.

> The raw gate passed; the raw effect is not robust across shores.

> A cleaner geometric direction failed its causal test.

> Do not confuse a positive average with uniformly positive constituents.

> Symmetrization saved us from choosing which shore's sign to believe.

> Do not use one ruler to set the divisions of another ruler.

> A difference without a declared reference state is not yet a scientific quantity.

> **我们终于碰到了过去留下的东西，未来的净平均确实动了一点；但更重要的是 —— 站在两岸，同一根舵把船推向了相反的方向。**

---

*本 schema 不含任何当前结果数值。所有数值位以具名占位符 `[X : REDACTED UNTIL DRAFT]` 标记。措辞稿必须由此结构 + 已封存 artifact 结构产生，不得由符号产生。*
