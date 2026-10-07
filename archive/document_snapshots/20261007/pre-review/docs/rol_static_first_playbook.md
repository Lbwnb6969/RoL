# RoL 静态优先开发手册

本项目的真源固定为 `C:\CK3Mods\RoL`。每次改动先完成静态闭环，再选择性启动 CK3；完整活动点击流程只在静态检查已经通过且需要确认 UI 接线时执行。

## 每轮最小闭环

```powershell
python tools/ck3_mcp/rol_static_audit.py
python tools/ck3_mcp/rol_dds_audit.py
python tools/ck3_mcp/server.py  # 通过 MCP 调用 ck3_validate_mod
python "C:\Users\Administrator\.codex\skills\rol-ck3-modder\scripts\check_bom_utf8.py" "C:\CK3Mods\RoL"
python "C:\Users\Administrator\.codex\skills\rol-ck3-modder\scripts\check_rol_prefix.py" "C:\CK3Mods\RoL"
python "C:\Users\Administrator\.codex\skills\rol-ck3-modder\scripts\rol_smoke_checks.py" "C:\CK3Mods\RoL"
git diff --check
```

其中 `ck3_static_audit` 不启动游戏，专门验证：

- 五条活动都保留 discovery、activity entry、阶段、结算和 completion flag 的链路；
- 活动共有字段（显示、可开始、有效性、地点、phase、host/guest intents、背景、window characters）齐全；
- `header_background`、活动 `background.texture` 和 RoL 自有 `gfx/` 引用都能解析到真源文件；
- 960 个当前英中 RoL 本地化键一一对应且没有重复键，包含 `key:0` 和 `key:` 两种 CK3 写法；
- 旧的 effect / trigger / event ID 引用不被误判为资源或本地化键。
- 新增事件背景必须通过尺寸和压缩检查；当前生成批次锁定为 `1592x848 / BC1(DXT1)`。

## 参考模组中可复用的结构

本机 Workshop 目录 `D:\SteamLibrary\steamapps\workshop\content\1158310` 中，RICE（`2273832430`）与 VIET（`2227658180`）的活动定义反复采用同一骨架：`is_shown` → `can_start` / `can_start_showing_failures_only` → `is_valid` → `on_invalidated` / `on_host_death` → `province_filter` → `phases` → `is_location_valid`。阶段事件通过 `on_phase_active` 触发，地点和背景单独接线。

RoL 在此基础上增加了自己的统一约束：活动必须有 `header_background`、双语本地化、`rol_relic_hunt_intent`、活动进度条和 Tier4 终局检查。引用 Workshop 代码时只复制结构和验证方法，不复制其 ID、命名空间或资源路径。

## 何时才进游戏

静态审计失败时不要启动游戏。静态通过后，优先使用 MCP 的 `ck3_run_console_action` 做一次加载探针；只有要确认活动窗口背景、header 或点击顺序时，才使用 `ck3_launch`、`ck3_send_console`、`ck3_capture_screen` 和 `ck3_click`。窗口工具会先验证 CK3 HWND 是前景窗口，失败时拒绝输入，截图也只复制到 `tools/ck3_mcp/artifacts/`，不删除原始日志。

## 资源替换顺序

先保持现有 DDS 占位图和文件名不变，确认脚本接线、分辨率和 alpha 规范，再调用生图 API。事件背景默认只生成环境和道具，不生成人物、动物、尸体、雕像或人形轮廓；人物由事件代码的肖像和 `window_characters` 叠加。生成图按地点、时代、光源与镜头构图写入提示词；筛选后用 `tools/ck3_mcp/png_to_dds_bc1.py` 裁切到 `1592x848` 并转换为 BC1，同名替换 DDS，清理 gfx 缓存并做一次最小窗口验证。重要旧图先复制到专门废弃目录并保留 Git 记录，禁止直接删除。
