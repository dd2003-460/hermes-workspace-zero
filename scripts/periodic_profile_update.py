#!/usr/bin/env python3
"""
周期性用户画像与偏好系统更新脚本
- 扫描 memory/raw/ 识别新/变更文件
- 提取用户偏好、思维模式、行为特征
- 输出到 memory/processed/
- 聚合更新到 memory/profile/
- 维护 checkpoint 记录处理状态
"""
import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
import re

class ProfileUpdater:
    """周期性用户画像与偏好系统更新器"""
    
    ROOT_DIR = Path("/Users/a1-6/Desktop/workspace-zero/memory")
    RAW_DIR = ROOT_DIR / "raw"
    PROCESSED_DIR = ROOT_DIR / "processed"
    PROFILE_DIR = ROOT_DIR / "profile"
    TRACKED_DIR = ROOT_DIR / ".tracked"
    CHECKPOINT_FILE = PROFILE_DIR / "update_checkpoint.json"
    METADATA_FILE = PROCESSED_DIR / "_metadata.json"
    
    # 提取路径映射
    EXTRACTION_PATHS = {
        "用户偏好": PROCESSED_DIR / "preferences",
        "思维模式": PROCESSED_DIR / "thinking_patterns", 
        "行为特征": PROCESSED_DIR / "behavior_traits",
    }
    
    def __init__(self):
        self.last_processed_ts = datetime.fromtimestamp(
            os.path.getmtime(self.CHECKPOINT_FILE) if self.CHECKPOINT_FILE.exists() else 0
        )
        self.processed_hashes = {}
        
    def file_hash(self, filepath: Path) -> str:
        """计算文件 SHA256 hash (分块以处理大文件)"""
        content = b''
        chunk_size = 8192
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                content += chunk
        return hashlib.sha256(content).hexdigest()
    
    def is_file_processed(self, rel_path: Path) -> tuple[bool, str]:
        """检查文件是否已处理 (基于 hash 或 timestamp)"""
        tracked_file = self.TRACKED_DIR / rel_path
        
        if not tracked_file.exists():
            return False, ""
        
        data = json.loads(tracked_file.read_text())
        current_hash = self.file_hash(self.RAW_DIR / rel_path)
        
        if data.get("hash") != current_hash:
            return False, "ch"
            
        last_ts = data.get("processed_ts")
        is_modified = last_ts < self.last_processed_ts
        
        return True, "" if not is_modified else "m"
    
    def register_file(self, rel_path: Path, status: str = ""):
        """注册文件追踪状态 (仅追加，不覆盖)"""
        tracked_file = self.TRACKED_DIR / rel_path
        
        if not tracked_file.exists():
            tracked_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "hash": self.file_hash(self.RAW_DIR / rel_path),
            "processed_ts": datetime.now().isoformat(),
            "status": status if status else ""
        }
        tracked_file.write_text(json.dumps(data, ensure_ascii=False))
    
    def load_checkpoint(self) -> dict:
        """加载 checkpoint 信息"""
        if not self.CHECKPOINT_FILE.exists():
            return {"last_processed_ts": "0", "processed_hashes": {}}
        
        data = json.loads(self.CHECKPOINT_FILE.read_text())
        return {
            "last_processed_ts": data.get("last_processed_ts", "0"),
            "processed_hashes": data.get("processed_hashes", {})
        }
    
    def save_checkpoint(self):
        """保存 checkpoint 信息"""
        self.CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        checkpoint_data = {
            "last_processed_ts": self.last_processed_ts.isoformat(),
            "processed_hashes": self.processed_hashes
        }
        
        with open(self.CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
    
    def extract_preferences(self, content: str) -> dict:
        """从内容中提取用户偏好信息"""
        prefs = {
            "表达风格": None,
            "信息密度": None,
            "语言习惯": [],
            "输出格式": []
        }
        
        # 表达风格关键词
        style_indicators = {
            "简洁": ["直接", "简明", "精炼", "言简意赅", "点到为止"],
            "详尽": ["详细", "完整", "详尽", "全面", "深入分析"],
            "结构化": ["列表", "编号", "分点", "层次清晰", "模块"],
            "叙事性": ["故事化", "叙述", "背景说明", "上下文"],
            "技术导向": ["代码", "命令", "technical", "实现"],
            "创意导向": ["创新", "构思", "idea", "探索"]
        }
        
        for style, indicators in style_indicators.items():
            count = sum(1 for ind in indicators if ind.lower() in content.lower())
            if count > 0:
                prefs["表达风格"] = style
                break
        
        # 信息密度估算 (基于分段长度分布)
        paragraphs = re.split(r'\n[ \t]*\n', content.strip())
        avg_len = sum(len(p) for p in paragraphs if len(p) > 10) / max(1, sum(1 for p in paragraphs if len(p) > 10))
        
        if avg_len > 50:
            prefs["信息密度"] = "高"
        elif avg_len > 20:
            prefs["信息密度"] = "中"
        else:
            prefs["信息密度"] = "低"
        
        # 语言习惯
        if re.search(r'\d+ 例子', content):
            prefs["语言习惯"].append("使用示例说明")
        if re.search(r'^[-*#]\d+\.', content):
            prefs["语言习惯"].append("使用列表标记")
        if '\`' in content:
            prefs["语言习惯"].append("代码块标注")
        
        return prefs
    
    def extract_thinking_patterns(self, content: str) -> dict:
        """从内容中提取思维模式信息"""
        patterns = {
            "分析方式": [],
            "决策倾向": None,
            "推理风格": []
        }
        
        # 分析方式
        analysis_indicators = {
            "系统性": ["步骤", "流程", "框架", "systematic", "structured approach"],
            "批判性": ["质疑", "反思", "critique", "审视", "挑战假设"],
            "实验性": ["尝试", "测试", "experiment", "探索"],
            "归纳式": ["总结", "规律", "generalize", "从案例到理论"],
            "演绎式": ["推导", "证明", "deduce", "从理论到验证"]
        }
        
        for pattern, indicators in analysis_indicators.items():
            count = sum(1 for ind in indicators if any(ind.lower() in word for word in content.split()))
            if count >= 2:
                patterns["分析方式"].append(pattern)
        
        # 决策倾向
        decision_verbs = ["总是", "从不", "倾向于", "优先", "更偏好"]
        for verb in decision_verbs:
            if f"{verb} " in content or f"{verb}" in content:
                patterns["决策倾向"] = verb
                break
        
        # 推理风格
        if "因为...所以" in content or "reasoning:" in content:
            patterns["推理风格"].append("因果链")
        if "however/then:" in content:
            patterns["推理风格"].append("转折递进")
        if "首先/其次/最后:" in content:
            patterns["推理风格"].append("分步推导")
        
        return patterns
    
    def extract_behavior_traits(self, content: str) -> dict:
        """从内容中提取稳定行为特征"""
        traits = {
            "关注领域": [],
            "工具偏好": [],
            "内容类型": []
        }
        
        # 领域关键词
        domain_keywords = {
            "数学": ["定理", "证明", "math", "numerical", "formula"],
            "编程": ["代码", "function", "debug", "implement"],
            "数据分析": ["数据", "analysis", "metric", "statistic", "pandas"]
        }
        
        for domain, keywords in domain_keywords.items():
            hits = [kw for kw in keywords if any(kw.lower() in word.lower() for word in content.split())]
            if hits:
                traits["关注领域"].append(domain)
        
        # 工具偏好 (从命令/术语提取)
        tools = re.findall(r'(?:使用|采用|用)[:\s]*(\w+(?:/\w+)*)', content)
        if tools:
            traits["工具偏好"] = list(set(tools))[:5]
        
        # 内容类型
        content_types = re.findall(r'[\w-]+\.md$', content)
        if content_types:
            traits["内容类型"] = list(set(content_types))
        
        return traits
    
    def extract_profile(self, filepath: Path) -> dict:
        """从单个文件提取完整的用户画像信息"""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return {"error": "read_failed"}
        
        profile = {
            "file_origin": str(filepath.relative_to(self.RAW_DIR)),
            "timestamp": datetime.now().isoformat(),
            "preferences": self.extract_preferences(content),
            "thinking_patterns": self.extract_thinking_patterns(content),
            "behavior_traits": self.extract_behavior_traits(content)
        }
        
        return profile
    
    def create_processed_file(self, filepath: Path, profile_data: dict) -> str:
        """创建 processed 文件输出路径和 content (append-only)"""
        if profile_data.get("error"):
            output_path = self.PROCESSED_DIR / filepath.name
        else:
            category = "general"
            
            # 根据内容特征路由到特定子目录
            if profile_data.get("preferences", {}).get("表达风格") in ["简洁", "技术导向"]:
                category = "preferences"
            elif profile_data.get("thinking_patterns", {}).get("分析方式") in ["批判性"]:
                category = "thinking_patterns"
            
            output_path = self.EXTRACTION_PATHS.get(category, PROCESSED_DIR) / filepath.name
            
        # Append-only mode: write to new file with timestamp suffix if exists
        base_path = output_path.parent / Path(filepath.name).stem
        ts_suffix = f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if base_path.exists():
            output_path = base_path / f"{Path(filepath.name).suffix}{ts_suffix}"
        else:
            output_path = base_path / (Path(filepath.name).suffix or "_profile.json")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return str(output_path), profile_data
    
    def run(self, dry_run: bool = False) -> dict:
        """执行完整的更新流程"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "new_files": [],
            "modified_files": [],
            "skipped": [],
            "errors": []
        }
        
        # Load checkpoint state
        checkpoint = self.load_checkpoint()
        self.last_processed_ts = datetime.fromisoformat(checkpoint["last_processed_ts"]) if checkpoint.get("last_processed_ts", "0") != "0" else datetime.min
        self.processed_hashes = checkpoint.get("processed_hashes", {})
        
        # Scan raw directory
        print(f"[*] Scanning {self.RAW_DIR} for files to process...")
        
        raw_files = []
        if self.RAW_DIR.exists():
            for root, dirs, files in os.walk(self.RAW_DIR):
                for f in files:
                    if f.endswith('.md') or f.endswith('.txt') or f.endswith('.json'):
                        rel_path = Path(root).relative_to(self.RAW_DIR)
                        raw_files.append((rel_path, self.file_hash(Path(root) / f)))
        
        print(f"[*] Found {len(raw_files)} files to check")
        
        # Process each file
        for rel_path, current_hash in raw_files:
            is_processed, status = self.is_file_processed(rel_path)
            
            if dry_run:
                if status == "ch":
                    results["modified_files"].append(str(rel_path))
                elif status == "":
                    results["new_files"].append(str(rel_path))
                continue
            
            if is_processed and status == "":
                results["skipped"].append(str(rel_path))
                continue
            
            # Register this file as processed now (mark it being handled)
            self.register_file(rel_path, status if status else "p")
            
            try:
                output_path, profile_data = self.create_processed_file(
                    Path(rel_path) / rel_path.suffix,
                    profile_data
                )
                
                # Write output (append-only)
                with open(output_path, 'a', encoding='utf-8') as f:
                    if not os.path.exists(output_path):
                        f.write('---\n')  # Markdown separator
                    f.write(f"## Profile Update: {rel_path}\n\n")
                    f.write(json.dumps(profile_data, ensure_ascii=False, indent=2))
                
                results["files_processed"] += 1
                self.processed_hashes[f"{rel_path}"] = current_hash
            
            except Exception as e:
                results["errors"].append((str(rel_path), str(e)))
        
        # Save checkpoint
        self.save_checkpoint()
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Periodic Profile Updater")
    parser.add_argument("--dry-run", action="store_true", help="Only report what would be processed")
    args = parser.parse_args()
    
    updater = ProfileUpdater()
    results = updater.run(dry_run=args.dry_run)
    
    print("\n" + "="*60)
    print(f"Profile Update Results ({datetime.now().strftime('%H:%M')})")
    print("="*60)
    print(f"Files processed:  {results['files_processed']}")
    print(f"New files found:  {len(results['new_files'])}")
    print(f"Modified files:   {len(results['modified_files'])}")
    print(f"Skipped (up-to-date): {len(results['skipped'])}")
    print(f"Errors occurred:   {len(results['errors'])}")
    
    if results["modified_files"]:
        print(f"\nModified: {results['modified_files']}")
    if results["new_files"]:
        print(f"New:     {results['new_files']}")
    if results["errors"]:
        print(f"\nErrors: {results['errors']}")
    
    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    exit(main())