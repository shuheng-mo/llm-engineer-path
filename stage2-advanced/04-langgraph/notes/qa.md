# LangGraph Q&A 汇总

> 汇总 stage2-advanced/04-langgraph 各模块（图与状态 / 工具与 Middleware / MCP / 持久化 / HITL / 流式 / 多 Agent）的开放性问题。
>
> 选题原则：避开"如何用 LangGraph 实现 X"这类教程八股，聚焦在**真正上生产时会被反复打脸的细节**、**框架抽象泄漏的地方**、以及**面试官常用来区分"会调 API"和"真的理解底层"的问题**。

---

## 一、图执行 / 状态 / Reducer

1. LangGraph 的执行底层是 Pregel-style BSP（bulk synchronous parallel），每个 super-step 内的节点并行执行、step 之间靠 barrier 同步。这种"等齐了才进下一步"的木桶效应在 fan-out 调用多个慢 LLM 时会被严重放大——10 个并行子 Agent 里有 1 个慢 30s，整个 step 就卡 30s。生产里这种"长尾节点"怎么处理？timeout 是粗暴 raise 还是返回降级结果？跟真正的事件驱动 actor 模型（AutoGen v0.4、Akka）比起来，LangGraph 这种 BSP 抽象在什么场景下是硬伤？什么场景下反而是优势？

2. Reducer 的设计哲学是"node 返回片段、框架统一合并"，但是当两个并行节点在同一个 super-step 里都更新同一个字段时，合并顺序到底是怎么决定的？`add_messages` 靠 `id` 去重，那如果两个并行分支生成了**相同 id** 的消息（比如都调用了同一个工具、tool_call_id 撞车）会发生什么？`operator.add` 拼接 list 的顺序是不是依赖节点注册顺序、是非确定的？这种"reducer 的合并不可交换"会不会成为隐藏的并发 bug 源？生产里怎么测出这类 bug？

3. 课程文档反复强调"图节点不要直接更改State，要返回更新的片段"，但这只是约定而非框架强制——TypedDict这个结构本身没有不可变性。如果某个人在节点里写了 `state["messages"].append(msg)` 然后 `return {}`，框架不会报错，但 checkpoint 拿到的"更新片段"和真实 state 就对不上了，时间旅行会拿到错的中间态。这种"静默的状态泄漏"在 code review 里很容易漏过——能不能在编译期或运行期强制State的不可变性？Pydantic `BaseModel` 的 `frozen=True` 配合 LangGraph 有没有副作用？

---

## 二、持久化 / Checkpoint / 短期记忆

1. Checkpointer 的设计是"每个 node 执行后写一次 checkpoint"，意味着一次 10 步的图执行会产生 10 个 checkpoint 行。在长会话场景下（比如客服 Agent 跑了 200 轮对话），同一个 `thread_id` 下会堆积成千上万的 checkpoint。这种写放大对 Postgres 来说是真问题——表会爆炸、`get_state_history` 越来越慢、备份成本飙升。生产里 checkpoint 的 GC 策略一般怎么定？按对话轮数留 N 个？按时间窗口？还是只留"分支点"的 checkpoint？业界有没有标准做法？另外，能不能在某些节点上**显式跳过 checkpoint 写入**（比如纯读、纯日志节点）？

2. State schema 一旦发版上线就和已有的 checkpoint 强绑定了——加一个字段、改一个 reducer、把 `int` 改成 `str`，旧 checkpoint 反序列化就可能挂掉或者拿到错值。LangGraph 在这件事上其实没给出明确的迁移方案。我理解State schema和迁移和数据库的Schema一样重要，生产里怎么做 schema 演进？是必须像数据库迁移一样写迁移脚本去重写所有历史 checkpoint，还是在反序列化层做版本兼容（看到旧版本就补默认值）？如果 reducer 函数本身改了（比如 `add_messages` 升级换了去重规则），重放旧 checkpoint 会不会得到和当年不一样的"未来"？

3. 短期记忆管理三大策略（trim/delete/summary）在文档的示例里看起来都很优雅，但有个细节文档没说清楚：**修剪/删除的消息在 checkpoint 里还在不在？** 如果只是把 State 里的 `messages` 截短但 checkpoint 历史完整保留，那时间旅行回到旧 checkpoint 是不是又能拿到完整消息？这对**合规场景**（用户行使 GDPR 删除权）是个大坑——以为删了，其实历史快照里还在。反过来如果是物理删除 checkpoint 历史，那时间旅行能力就废了。两难怎么破？另外 SummarizationMiddleware 总结后 LLM 看到的是摘要，但下游节点如果直接读 `state["messages"]` 是不是又会看到原始消息，导致"看到的上下文不一致"？

---

## 三、HITL / 中断 / 副作用幂等

1. 文档提了 `interrupt()` 的核心机制——节点会**从函数开头重新执行**，靠"interrupt 调用的顺序索引"把恢复值塞回去。这个设计在玩具示例里没问题，但生产里大多数节点函数在 interrupt 之前已经做了**昂贵且有副作用**的事情：调了 LLM 烧了 token、写了数据库、发了 Slack 通知、扣了用户配额。恢复时整个函数从头跑，岂不是这些副作用全部重放？文档说"中断前的操作应该是幂等的"——但 LLM 调用本身就不是幂等的（temperature>0 每次结果都不一样？我理解）。生产里到底怎么做？是把所有 pre-interrupt 的副作用拆到单独的节点里？还是用 checkpoint 里的中间态做"已执行过就跳过"的判断？有没有比"程序员小心翼翼"更系统的方案？

2. HITL 中断后 Agent 进程其实并不是"挂着等"——真正的长周期审批（运营周一才批）一定是接外部工单/审批系统，Agent 这边在 interrupt 触发的瞬间就该返回 `thread_id` 释放连接，由外部系统在审批完成后回调 `graph.invoke(None, config)` 来恢复。问题就出在这个"回调恢复"的调度框架本身：进程重启 / 实例扩缩容 / 跨节点漂移之后，**谁负责知道还有哪些 thread 卡在 interrupt 状态**？LangGraph 原生有没有"列出所有 pending interrupt"的查询接口，还是必须自己在外部维护一张 `(thread_id, status, resume_url)` 的索引表？多实例部署时，一个回调进来怎么路由到"能恢复这个 thread 的实例"——是任意实例都能恢复（无状态，靠 checkpointer 共享），还是必须粘性路由？这套调度框架在 LangGraph Platform 之外要自己怎么搭？

---

## 四、流式 / Middleware

1. `stream_mode="messages"` 是实现打字机效果的唯一通道，但它只 stream 当前图的 LLM token。一旦进入**多 Agent / 子图**场景就出问题了——子 Agent 的 token 流默认不会冒泡到父图的 stream。要前端看到子 Agent 的 "正在思考..." 怎么办？是父图 stream 嵌套子图 stream 然后手动 forward？还是子 Agent 通过 `custom` 通道自己上报？跟 HITL 配合时更难——正在 token streaming 的过程中触发 interrupt，已经吐到前端的半截 token 怎么处理？回退？保留？前端 UI 怎么表达"这段刚才显示的内容其实未完成、等审批中"？

2. Middleware 的 wrap-style hook 是洋葱模型 `M1.pre → M2.pre → M3.pre → model → M3.post → M2.post → M1.post`，跟 web 框架的中间件几乎一模一样。但实际生产里有个坑：如果 model 调用抛异常，**外层 middleware 的 post 还会执行吗？** 比如 `M2 = RateLimitMiddleware` 在 pre 里 `acquire_quota()`、post 里 `release_quota()`——如果中间 model 调用抛了，quota 没还回去，长期就泄漏。LangGraph 这层有没有提供类似 `finally` 语义的 hook？常见 middleware（trace span 开关、rate limit、budget tracking）在异常路径下都要保证清理，靠开发者自己写 try/finally 是不是太脆弱？有没有从框架层强制约束的方式？

---

## 五、Multi-Agent / Subagents / Handoffs / Skills

1. 文档自己承认了一个尴尬的事实：**Handoff 模式的示例其实没有真的创建多个 Agent**，是单个 Agent 内部根据 `current_step` 切换 prompt + tools 子集来"模拟"多个专家。这暴露了一个更深的问题——LangGraph 教程里讲的"多 Agent" 90% 都是这种**伪多 Agent**（单进程、共享 state、靠 middleware 切换人格）。真正的多 Agent（独立进程、独立状态、靠消息通信）反而很少示范。这两种"多 Agent"的区分边界在哪？什么时候必须上真正的分布式多 Agent（独立部署、独立 scale、独立 fail）？**业界（比如 Anthropic、Cognition）关于 "should you build multi-agent systems" 的争论，对 LangGraph 这种"轻多 Agent"框架而言怎么定位才合理**？

2. Subagents 项目模板里把子 Agent 用 `Command + InjectedToolCallId + ToolMessage` 包成工具——这看似漂亮，但子 Agent 自己也是一个有 state、有循环、可能有 HITL、可能有 streaming 的完整 graph。这种"图嵌套图"会带来一堆边界问题：父图的 `thread_id` 和子 Agent 的会话怎么区分？子 Agent 内部的 checkpoint 是写在父 checkpointer 里还是独立的（文档说"父图 checkpointer 自动传导"，但子 Agent 通过 tool 调用又是另一回事）？子 Agent 触发 interrupt 时，整个父图怎么响应？子 Agent内部的LLM token 流怎么冒泡？这套机制在示例代码里都被简化掉了，但生产里只要你跑两层嵌套就全部冒出来——LangGraph 在这件事上的最佳实践应该是什么样？

3. Skills 模式的核心卖点是渐进式加载，目录常驻 ~200 token、技能按需 load。但有个评估问题没人回答：对于Skill这种软注入的方式，**当目录里有 50 个、100 个 skill 时，LLM 在目录里挑对的概率会不会反而下降？** 一个写得不好的 description 就能让 LLM 误调，命中率怎么测？跟全量加载（虽然贵但 LLM 看完整 schema）相比，Skills 模式在 token 上是省的，但在准确率上未必赢——什么场景下省 token 的收益盖不过命中率下降的损失？另外，加载过的 skill schema 留在上下文里、下一轮用户切换话题，是不是要主动"卸载"？怎么知道该卸载——靠用户表态、靠 LLM 自己判断、还是定期清理？这块 Anthropic 的 Agent Skills 文档其实也含糊，有没有什么共识或者实践可以参考？

---

## 六、MCP / 工具系统

1. MCP 协议下的多租户上下文注入靠**客户端拦截器**给每次 `tools/call` 附带 `user_id` / `api_key`。但有个根本性的安全问题：LLM 自己是知道自己是哪个 user 在跟它聊天的（system prompt 或者历史消息里都有），它能不能在生成 tool_call 参数时**自己捏一个 user_id** 塞进 args 里，然后绕过拦截器去访问别人的数据？拦截器层能不能保证"用户身份只能从 host 注入、LLM 输出的 args 里这个字段直接被剔除"？另外 MCP server 是独立进程，stdio 传输下 host 进程崩溃了 server 是孤儿吗？server 自己崩了 host 怎么感知？health check 是 LangGraph 这层做还是 MCP自己有什么机制？

2. `langchain.tools.@tool` 装饰器的本地工具 vs MCP 工具，在 Agent 看来是统一的——都是 `tools=[...]` 里的一项。但是它们的可观测性、错误处理、版本管理路径完全不同：本地 tool 改了代码重新部署就生效，MCP server 升级了 schema 可能要重启所有客户端、re-list tools。生产里大规模使用 MCP（比如 50+ 个 server）会带来一类新问题——**tool catalog 漂移**：模型上次看到的 tool schema 已经过期了。LangGraph 这层有没有"schema 版本指纹 + 失效检测"的机制？还是只能靠运维手动协调？另一个相关问题：`MultiServerMCPClient` 的 `get_tools()` 是启动时拉一次还是每次 invoke 都拉？如果是启动时拉，热加载 server 新增的 tool 就要重启进程？

---

> 以下是写到一半的备选，可以一起聊：
>
> - LangGraph 的"时间旅行"卖点很响，但实际生产里真的有人用它做什么？除了 debug 复盘，业务场景里"回到上一个 checkpoint 重新决策"的用例究竟有多刚需？还是说这是个"听着很酷、实际很少用"的功能？
> - LangSmith 是官方观测方案，但锁定厂商 + 数据上云对很多企业是个红线。换成 OpenTelemetry 给 LangGraph 做 tracing，整个图的 span 层级应该怎么组织？node 是 span 还是 super-step 是 span？子图嵌套时 parent span 怎么传？
