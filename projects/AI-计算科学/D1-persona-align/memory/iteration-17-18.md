# Ralph Loop Iteration 17-18

**日期**: 2026-05-22/23
**迭代**: 17-18
**状态**: 项目结构修正

## 本迭代工作

### 1. goal 修正
- 删除 ralph-loop.global.md 中错误规则："每次迭代都必须加深对领导者的对齐程度"
- 理由：没有用户信息输入时，对齐会被噪声淹没

### 2. 项目结构修正
- 创建 ~/Desktop/workspace/projects/D1-persona-align/ 标准项目结构
- 迁移 persona-evolve/ 到项目目录
- 迁移 persona-manifest.md 到项目目录
- 迁移迭代记录到 memory/ 目录
- 创建 INDEX.md（项目入口）

### 3. 之前迭代记录
- iteration-15.md, iteration-16.md: persona sync 脚本创建
- iteration-11.md, iteration-13.md, iteration-14.md: persona manifest + loader + e2e test

## 收敛状态

- **项目结构**: INDEX.md + memory/ + tasks/ + persona-evolve/
- **goal**: 已修正，移除错误对齐规则
- **persona-evolve**: 5 个组件完整迁移到项目目录

## 约束

- CLAUDE.md EPERM，无法直接修改
- persona 通过 shell aliases + manifest 机制加载
