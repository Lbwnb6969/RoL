# RoL 静态优先开发手册

真源固定为 `C:\CK3Mods\RoL`。当前用户要求由维护者手测，代理不启动/停止CK3、不执行console action、不发送窗口输入。先读 `PROJECT.md`；历史游戏记录不算本次修改的引擎验证。

## 每轮最低充分闭环

脚本/文案变更先运行相关源码契约或 `rol_static_audit.py`。涉及整体加载或MCP交接时，用一次组合验证即可，不重复逐项扫描：

```powershell
python tools/ck3_mcp/rol_stdio_probe.py
git diff --check
```

stdio探针验证真实MCP协议、15项工具、只读环境与启动器path、组合静态验证。组合涵盖：5条活动/生命周期、4碎片、成长/同行、10用途、2跨链/7继承资料，原版同路径与全局key兼容门槛、双语键、概率提示、资源接线、DDS、UTF-8 BOM/严格解码、前缀和smoke。当前英中各1214键、84张DDS；统计以当前脚本输出为准。

独立入口按改动选择：`rol_quest_lifecycle_contracts.py`、`rol_compatibility_contracts.py`、`rol_dds_audit.py`、`check_bom_utf8.py`等。已通过后只因新改动、失败或明确新风险再扩大验证。仓库工具优先于旧skill备用脚本。

## 原版与模组兼容

不交付整份原版GUI或全局 `ARTIFACT_RARITY_AND_TYPE` / slot key覆盖，不用fallback说明全局覆盖安全。原版/第三方品质与类型由它们各自的界面处理；RoL传奇徽记只挂自有阶位modifier名称。自有GUI插件、texticon、背景、图标保留 `rol_` 名称/路径，on_action只追加自有回调，不替换原逻辑。不恢复 `archive/retired_ui/20261007` 退役文件。

新增检查扫描定义、重复、自有effect/trigger/value、事件、回调、背景、显式/隐式图标及加载文件。扫描与有限源码模型不能证明动态作用域、加载顺序或其他模组组合。

## 活动与延迟状态

活动/事件先检验原host、活动类型、地区和关闭状态；弹窗后的按钮效果再验资格。完整/部分/失败只能结算一次，闭合阶段及清状态；已结算活动允许一天收尾，不被自己新加的完成flag/冷却取消。死亡不奖个人XP，原同行记录留给档案快照。

本机原版 `_activity_type.info` 明确：活动级on_start/is_valid/on_invalidated/on_host_death的ROOT是activity，on_complete的ROOT是当前参与者；切到scope:host不会改ROOT。主办者资格与人物toast用当前人物this，活动日志用scope:host，不能默认ROOT永远是主办者。

延迟成果保存原对象和项目编号，消费一次资格，恢复只重开原记录。旧对象、死亡、转手、取消、缺钱与旧存档缺变量都需要明确边界。数值以当前源码为准，不把文档假定的关数当成整链通过率。

## 游戏交接

维护者先按 `docs/rol_console_test_guide.md` 第16节检查品质/类型与日常模组组合，再按6、7、12–15节检查真实活动、装备、定时、保存/读档与继承。直接 `event` 不自动提供host/activity上下文，无上下文终局不发奖属于正确负例。

只有用户明确恢复代理侧游戏测试后，才选择与未确定行为对应的最小真实操作。MCP默认保留错误日志；日志只复制不删除，窗口工具验证前景。不要把旧日志或存在进程当成本次验证。

## 资源维护

先追踪加载路径→显式/隐式接线→缓存→DDS，不为可用旧图重复生图。事件环境图不生成人物，人物由脚本叠加；背景目标1592×848/BC1，header1100×440，图标按资源家族。需要替换时先归档重要旧图并保留Git记录；缓存排查由维护者关闭游戏后移动到日期备份目录，不直接删除。
