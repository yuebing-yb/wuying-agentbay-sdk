"""
User-facing prompt scenarios for official skills demo.

These prompts are written from an end-user perspective:
- They describe the user's need and the required deliverable.
- They do NOT mention skills, tool names, or how to use any skill.

Selection:
- Scenarios are selected by the cookbook script (see main.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping


@dataclass(frozen=True)
class OfficialSkillScenario:
    key: str
    user_prompt: str
    default_report_path: str


def _scenario(key: str, user_prompt: str, default_report_path: str) -> OfficialSkillScenario:
    return OfficialSkillScenario(
        key=key,
        user_prompt=(user_prompt or "").strip() + "\n",
        default_report_path=default_report_path,
    )


def _build_scenarios() -> Dict[str, OfficialSkillScenario]:
    scenarios: Dict[str, OfficialSkillScenario] = {}

    # Marketing / Growth
    scenarios["seo-audit"] = _scenario(
        key="seo-audit",
        user_prompt=(
            "你好。我想对 `https://www.hanslaser.com/` 做一次快速 SEO 审计（不需要登录任何后台）。\n"
            "\n"
            "要求：\n"
            "- 只基于公开可访问信息做判断（不依赖 Search Console / Analytics）\n"
            "- 你需要实际抓取页面并分析 HTML 源码，检查以下 SEO 要素是否存在：\n"
            "  title、meta description、meta keywords、canonical link、robots meta、viewport、\n"
            "  Open Graph 标签、H1 标签、结构化数据等\n"
            "- 分析原则：如果某个标准 SEO 要素在页面中不存在，这本身就是一个重要的 SEO 问题，\n"
            "  应该作为 Issue 明确报告（例如「缺少 canonical link」「缺少 viewport meta」），\n"
            "  而不是认为「信息不足」或跳过分析\n"
            "- 证据（Evidence）必须基于你实际获取到的页面内容：\n"
            "  - 对于存在的元素：引用其具体内容（如 title 的文本、description 的内容）\n"
            "  - 对于缺失的元素：明确说明「在 HTML 源码中未找到该标签」\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告结构必须包含：\n"
            "  - `## 执行摘要`\n"
            "  - `## Top 5 问题与建议`\n"
            "  - `## 下一步行动计划`\n"
            "- 注意：以上小标题必须原样使用，不要翻译成英文（例如不要用 Executive Summary / References 等替代）\n"
            "- 在 `Top 5` 部分，每条必须用以下字段（英文标签）描述：\n"
            "  - **Issue** / **Impact** / **Evidence** / **Fix** / **Priority**\n"
            "- 报告必须包含 `## References Used`：列出你参考过的资料（含文件路径或 URL），并各引用一句原文\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/seo_audit_report.md",
    )

    scenarios["copywriting"] = _scenario(
        key="copywriting",
        user_prompt=(
            "你好。我需要你为一个 B2B SaaS 的落地页写一版高转化的营销文案（中文），并且要能落地成页面结构。\n"
            "\n"
            "产品背景（虚构，用于演示）：\n"
            "- 产品名：NimbusNote\n"
            "- 目标用户：50-500 人的产品与运营团队\n"
            "- 价值主张：把“调研/工单/文档/任务”的信息散落问题，变成一个可搜索的工作流，减少沟通成本\n"
            "- 主要功能：统一收集输入、自动归类标签、跨文档引用、权限管理、AI 总结（不夸大）\n"
            "- 主要竞争：Notion、Confluence\n"
            "- 主要 CTA：预约 Demo\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含：\n"
            "  - Above the Fold：Headline / Subheadline / Primary CTA\n"
            "  - Core Sections（至少 5 个 section，含 Social Proof / How It Works / FAQ）\n"
            "  - Annotations（解释关键选择）\n"
            "  - Alternatives（Headline 与 CTA 各 2-3 个备选）\n"
            "  - Meta Content（page title + meta description）\n"
            "- 报告必须包含 `## References Used`：列出你参考过的资料（含文件路径或 URL），并各引用一句原文\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/copywriting_report.md",
    )

    scenarios["page-cro"] = _scenario(
        key="page-cro",
        user_prompt=(
            "你好。我想对一个营销落地页做一次 CRO 诊断并给出可执行的优化方案（中文）。\n"
            "\n"
            "页面素材（虚构，用于演示）：\n"
            "【Hero】\n"
            "Headline: \"All-in-one workflow platform\"\n"
            "Subheadline: \"Improve team efficiency with automation\"\n"
            "CTA: \"Get Started\"\n"
            "Below: 3 个功能点（无数据/无案例），一个长表单（8 个字段），无 FAQ、无定价信息。\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含：\n"
            "  - Quick Wins\n"
            "  - High-Impact Changes\n"
            "  - Test Ideas（至少 5 条，写成假设 + 预期影响）\n"
            "  - Copy Alternatives（Headline 与 CTA 各 2-3 个）\n"
            "- 报告必须包含 `## References Used`：列出你参考过的资料（含文件路径或 URL），并各引用一句原文\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/page_cro_report.md",
    )

    scenarios["pricing-strategy"] = _scenario(
        key="pricing-strategy",
        user_prompt=(
            "你好。我需要你为一个 SaaS 设计定价与打包策略（中文），用于内部评审。\n"
            "\n"
            "产品背景（虚构，用于演示）：\n"
            "- 产品名：NimbusNote（团队知识与工作流）\n"
            "- 目标市场：SMB → Mid-market\n"
            "- GTM：自助为主，少量销售辅助\n"
            "- 当前：只有 $12/seat/mo 单一计划，转化一般\n"
            "- 目标：提升 ARPU，同时保持自助转化不崩\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含：\n"
            "  - Value Metric（推荐并解释）\n"
            "  - 3-tier 分层（含每档包含内容与定价区间），并且必须用以下英文小标题标注三档（不要翻译）：\n"
            "    - `### Good`\n"
            "    - `### Better`\n"
            "    - `### Best`\n"
            "  - Packaging rationale（对应 persona/价值）\n"
            "  - Research plan（至少包含 Van Westendorp + MaxDiff 的执行步骤）\n"
            "  - Risks & mitigations\n"
            "  - Next steps（2 周内可执行）\n"
            "- 报告必须包含 `## References Used`：列出你参考过的资料（含文件路径或 URL），并各引用一句原文\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/pricing_strategy_report.md",
    )

    scenarios["content-strategy"] = _scenario(
        key="content-strategy",
        user_prompt=(
            "你好。我需要一份 30 天可执行的内容策略（中文），用于启动内容增长。\n"
            "\n"
            "业务背景（虚构，用于演示）：\n"
            "- 产品：NimbusNote（团队知识与工作流）\n"
            "- 目标：获取高意向试用（self-serve）\n"
            "- 现状：只有 5 篇博客，主题零散\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含（按固定小标题）：\n"
            "  - `### 1. Content Pillars`\n"
            "  - `### 2. Priority Topics`\n"
            "  - `### 3. Topic Cluster Map`\n"
            "  - `### 4. 30-day execution plan`\n"
            "  - Content Pillars：3-5 个 + rationale\n"
            "  - Priority Topics：至少 12 个条目，注明 searchable/shareable/both、buyer stage\n"
            "  - Topic Cluster Map：结构化表示\n"
            "  - 30-day execution plan：按周\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/content_strategy_report.md",
    )

    scenarios["email-sequence"] = _scenario(
        key="email-sequence",
        user_prompt=(
            "你好。我需要一个 5 封的 Welcome/onboarding 邮件序列（中文），用于新注册用户。\n"
            "\n"
            "产品背景（虚构，用于演示）：\n"
            "- 产品：NimbusNote\n"
            "- 触发：用户完成邮箱注册并创建第一个 workspace\n"
            "- 目标：在 14 天内到达 Aha（创建并分享一个知识库页面），并引导预约 Demo\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含（按固定小标题，英文原样）：\n"
            "  - `## Sequence Overview`\n"
            "  - `## Email 1`\n"
            "  - `## Email 2`\n"
            "  - `## Email 3`\n"
            "  - `## Email 4`\n"
            "  - `## Email 5`\n"
            "  - `## Metrics Plan`\n"
            "- 每封邮件部分必须包含以下字段（英文标签原样）：`Subject` / `Preview` / `Body` / `CTA` / `Send timing`\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/email_sequence_report.md",
    )

    scenarios["analytics-tracking"] = _scenario(
        key="analytics-tracking",
        user_prompt=(
            "你好。我需要一份营销站点 + 产品的 Tracking Plan（中文），用于研发落地。\n"
            "\n"
            "产品背景（虚构，用于演示）：\n"
            "- 产品：NimbusNote\n"
            "- 关键转化：预约 Demo、完成注册、到达 Aha（创建并分享页面）\n"
            "- 技术栈：Next.js + GTM + GA4\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含：Overview（Tools: GA4, GTM）/ Events 表格（至少 12 条）/ Custom Dimensions 表格（至少 6 条）/ Conversions 表格（至少 3 条）/ UTM 命名约定\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/analytics_tracking_report.md",
    )

    # Product / Strategy
    scenarios["zero-to-launch"] = _scenario(
        key="zero-to-launch",
        user_prompt=(
            "你好。我有一个新功能想从 0 到 1 推进到可交付的原型方案。\n"
            "\n"
            "功能想法（虚构，用于演示）：\n"
            "- 产品：NimbusNote\n"
            "- 想法：在文档里输入“目标”，系统自动生成一个可执行的周计划（任务拆解 + 日程建议）并支持持续迭代\n"
            "- 约束：两周内要交付一个可演示的 MVP\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 方案，落盘到指定报告路径\n"
            "- 报告必须包含：The ONE Job / MVP Scope（Must/Should/Nice-to-have）/ Complete Experience / AI-first Considerations / Risks & mitigations / 2-week plan\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/zero_to_launch_report.md",
    )

    scenarios["ai-product-strategy"] = _scenario(
        key="ai-product-strategy",
        user_prompt=(
            "你好。我需要一份 AI 产品策略建议（中文），用于内部立项评审。\n"
            "\n"
            "背景（虚构，用于演示）：\n"
            "- 产品：NimbusNote（团队知识与工作流）\n"
            "- 目标：在现有产品中引入 AI 助手，提升信息检索、总结与任务流转效率\n"
            "- 约束：必须可控、可解释，不能“偶尔一拳打脸”\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含（按固定小标题，英文原样）：\n"
            "  - `## Problem framing`\n"
            "  - `## Human-AI boundary`\n"
            "  - `## Build vs Buy`\n"
            "  - `## Architecture options`\n"
            "  - `## Failure modes & UX`\n"
            "  - `## Evals & observability`\n"
            "  - `## Data flywheel`\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/ai_product_strategy_report.md",
    )

    # Legacy alias: keep for backwards compatibility with older scenario keys.
    scenarios["product-strategy"] = _scenario(
        key="product-strategy",
        user_prompt=(
            "你好。我需要一份 AI 产品策略建议（中文），用于内部立项评审。\n"
            "\n"
            "背景（虚构，用于演示）：\n"
            "- 产品：NimbusNote（团队知识与工作流）\n"
            "- 目标：在现有产品中引入 AI 助手，提升信息检索、总结与任务流转效率\n"
            "- 约束：必须可控、可解释，不能“偶尔一拳打脸”\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含：Problem framing / Human-AI boundary / Build vs Buy / Architecture options / Failure modes & UX / Evals & observability / Data flywheel\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/product_strategy_report.md",
    )

    # Software Engineering
    scenarios["test-driven-development"] = _scenario(
        key="test-driven-development",
        user_prompt=(
            "你好。我想为团队制定一份“写代码前必须先写测试”的工程规范（中文），用于团队内推广。\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 文档，落盘到指定报告路径\n"
            "- 文档必须包含：Red-Green-Refactor 的操作步骤 / The Iron Law（用原文引用）/ 什么时候例外、例外如何审批 / 常见借口与反驳（至少 6 条）/ 一个最小示例 / Verification checklist\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/tdd_sop.md",
    )

    scenarios["using-git-worktrees"] = _scenario(
        key="using-git-worktrees",
        user_prompt=(
            "你好。我需要一份 Git worktrees 的使用指南（中文），用于新同事快速上手并避免踩坑。\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 文档，落盘到指定报告路径\n"
            "- 文档必须包含：典型场景 / 目录选择规则 / 安全校验步骤 / 创建-进入-验证-清理 的命令序列 / 常见错误与排查\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/git_worktrees_guide.md",
    )

    scenarios["software-architecture"] = _scenario(
        key="software-architecture",
        user_prompt=(
            "你好。我们在做一个“技能在云端沙箱中运行”的方案评审。\n"
            "请你给出一份面向工程落地的架构建议（中文），要求兼顾可演进性与代码质量。\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 报告必须包含：边界与分层（domain/application/infrastructure）/ 模块命名建议 / 关键用例（至少 3 个）/ 依赖方向与接口 / 反模式清单（至少 6 条）/ “Library-first”评估步骤\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/software_architecture_review.md",
    )

    # Generic default
    scenarios["generic"] = _scenario(
        key="generic",
        user_prompt=(
            "你好。我希望你帮我完成一个可以清晰展示你能力的任务（中文）。\n"
            "\n"
            "要求：\n"
            "- 你可以自行做必要的假设，但必须显式写在报告里\n"
            "- 输出必须结构化、可复用\n"
            "\n"
            "交付物：\n"
            "- 生成一份 Markdown 报告，落盘到指定报告路径\n"
            "- 最后请给出中文摘要：至少引用报告原文两处，并给出报告文件的绝对路径\n"
        ),
        default_report_path="/tmp/official_skill_report.md",
    )

    return scenarios


SCENARIOS: Mapping[str, OfficialSkillScenario] = _build_scenarios()


def list_scenarios() -> Iterable[str]:
    return SCENARIOS.keys()


def get_scenario(key: str) -> OfficialSkillScenario:
    k = (key or "").strip()
    if not k:
        return SCENARIOS["generic"]
    if k not in SCENARIOS:
        raise KeyError(f"Unknown scenario key: {k}")
    return SCENARIOS[k]

