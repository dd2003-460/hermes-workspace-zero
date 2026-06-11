{
  "requirement": "对 persona-v3 系统进行一次全面健康检查：验证所有脚本可编译、所有集成测试通过、所有评估基线达标、文档索引与实际情况一致",
  "background": "persona-v3 系统经过 327 次迭代，动态工作流基础设施已部署。需要定期确认系统健康状态，确保长期运行下无回归。",
  "existing_info": [
    "scripts/ 下 20 个活跃脚本",
    "memory/ 下 157 个记忆文件",
    "eval_results/ 下 11 个评估结果文件",
    "integration_test.py 11/11 PASS",
    "动态工作流 4 种方案已部署"
  ],
  "constraints": ["每次健康检查不超过 5 分钟", "自动修复可发现的问题", "报告必须可验证"],
  "priority": "planning"
}
