# Step 02：修复中断的 R 环境（T1 收尾）—— TwoSampleMR/MVMR 装完

## 目标
把中断的 R 包安装补完，使阶段2 分析所需 R 环境可用：TwoSampleMR（GitHub MRCIEU，记 commit）+ MVMR（GitHub）+ MendelianRandomization + MRPRESSO + ieugwasr 全部 requireNamespace=TRUE。

## 现状（2026-10-28 一手核实）
- R 4.6.1 已装（/opt/homebrew/bin/R）。
- T1 后台进程中断：日志 `projects/健康长寿/D1-longevity-orthogonal/tasks/t1-r-env-install.log`（170 行）停在 `remotes::install_github("MRCIEU/TwoSampleMR")` 依赖安装中。
- 实测：TwoSampleMR/MVMR/MendelianRandomization/ieugwasr = FALSE；MRPRESSO = TRUE。

## 涉及文件
- 写（追加）：`tasks/t1-r-env-install.log`（续装日志）；新 log `tasks/t1b-r-env-finish.log`
- 产出验证：R 包版本表（记入本步骤执行记录，供 Step 05 session_info.txt 用）

## 做法
2-loop：
1. **备份**：log 文件只追加不覆盖（cp 一份 .bak）。
2. **执行**：用 `setsid` 后台承载（acp-rules 硬规则：禁止裸 nohup，沙箱清理会杀裸后台进程）跑：
   ```bash
   setsid bash -c 'Rscript -e "remotes::install_github(\"MRCIEU/TwoSampleMR\")" && \
     Rscript -e "remotes::install_github(\"MRCIEU/MVMR\")" && \
     Rscript -e "install.packages(c(\"MendelianRandomization\",\"ieugwasr\"), repos=\"https://cloud.r-project.org\")"' >> tasks/t1b-r-env-finish.log 2>&1
   ```
   注意：续装前先 `Rscript -e 'renv::dependencies'` 式检查已装依赖，避免重复装 60+ 依赖包（中断前已装完大部分）。
3. **review/verify**：
   ```bash
   Rscript -e 'for (p in c("TwoSampleMR","MVMR","MendelianRandomization","MRPRESSO","ieugwasr")) cat(p, requireNamespace(p,quietly=TRUE), as.character(packageVersion(p)), "\n")'
   ```
   5/5 TRUE 且版本非 NA；另记 `git ls-remote https://github.com/MRCIEU/TwoSampleMR HEAD` 的 commit hash 备用。
4. **提交**：更新 decomposition.md 任务表 T1 状态 = 完成（含版本表）；本步骤属 workspace 内可逆操作，repo 内留痕随 Step 05 session_info 一起 commit。

## 验收标准
- 5 个包 requireNamespace 全部 TRUE，版本号可打印；TwoSampleMR GitHub commit hash 已记录。
- 降级预案（预注册）：brew/CRAN 失败 → miniforge 单 R 环境替代并记 session_info，不阻塞后续步骤。