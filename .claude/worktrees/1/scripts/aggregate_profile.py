#!/usr/bin/env python3
"""
聚合更新脚本：将 memory/processed/ 中的内容合并到 profile/
- 按类别聚合（preferences, thinking_patterns, behavior_traits）
- 新信息追加到对应字段，不覆盖已有内容
- 维护聚合时间戳和版本
"""
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ProfileAggregator:
    """用户画像聚合器 - 将 processed 输出合并为统一 profile"""
    
    ROOT_DIR = Path("/Users/a1-6/Desktop/workspace-zero/memory")
    PROCESSED_DIR = ROOT_DIR / "processed"
    PROFILE_FILE = ROOT_DIR / "profile" / "user_profile.json"
    
    # 类别映射（processed -> profile 字段）
    CATEGORY_MAPPING = {
        "preferences": ["表达风格", "信息密度", "语言习惯", "输出格式"],
        "thinking_patterns": ["分析方式", "决策倾向", "推理风格"],
        "behavior_traits": ["关注领域", "工具偏好", "内容类型"]
    }
    
    def __init__(self):
        self.profile = self._load_existing_profile()
        
    def _load_existing_profile(self) -> dict:
        """加载现有的 profile 数据（如果存在）"""
        if not self.PROFILE_FILE.exists():
            return {
                "version": 1,
                "last_updated": None,
                "metadata": {
                    "total_sources": 0,
                    "category_counts": {}
                },
                "preferences": self._init_category([]),
                "thinking_patterns": self._init_category([]),
                "behavior_traits": self._init_category([])
            }
        
        return json.loads(self.PROFILE_FILE.read_text())
    
    def _init_category(self, default): {
        "version": 1,
        "last_updated": None,
        **default
    }
    
    def _resolve_path(self, check_dir: str) -> Path:
        """解析处理目录路径（支持动态挂载点）"""
        base = self.PROCESSED_DIR / check_dir
        
        # 处理悬空目录（如 _analysis_mounts/xxx）
        if "_mount" in check_dir:
            mount_point = Path(check_dir).parent / f"{check_dir.split('_')[0]}_mounts"
            mount_key = f"_{check_dir}"
            
            # 尝试读取挂载目录
            raw_path = self.PROCESSED_DIR / mount_point / check_dir.lstrip("_")
            if raw_path.exists():
                base = raw_path
            else:
                # 创建临时目录以保持持久性
                base.mkdir(parents=True, exist_ok=True)
        
        return base
    
    def aggregate_processed_files(self, files: list) -> dict:
        """
        聚合指定文件列表的处理结果
        
        Args:
            files: List of (rel_path, content) tuples
        """
        updated = False
        
        for rel_path, content in files:
            try:
                # 解析类别（从路径推断）
                category = "general"
                for cat_dir in self.CATEGORY_MAPPING.keys():
                    if f"/{cat_dir}/" in rel_path:
                        category = cat_dir
                        break
                
                # 解析具体字段（从内容推断）
                fields_to_update = []
                if category == "preferences":
                    has_prefs = any(kw in content.lower() for kw in [
                        "表达风格", "信息密度", "/preferences/"
                    ])
                    if has_prefs:
                        fields_to_update = ["表达风格", "信息密度"]
                elif category == "thinking_patterns":
                    has_thinking = any(kw in content.lower() for kw in [
                        "分析方式", "决策倾向", "/thinking/"
                    ])
                    if has_thinking:
                        fields_to_update = ["分析方式", "决策倾向"]
                elif category == "behavior_traits":
                    has_traits = any(kw in content.lower() for kw in [
                        "关注领域", "工具偏好", "/behavior/"
                    ])
                    if has_traits:
                        fields_to_update = ["关注领域", "工具偏好"]
                
                # 更新对应的类别容器
                if category in self.CATEGORY_MAPPING:
                    cat_container = self.profile[self.CATEGORY_MAPPING[category]]
                    
                    for field in fields_to_update:
                        if field not in cat_container.get("fields", []):
                            continue
                        
                        # 查找该字段的最新条目
                        field_entries = [(k, v) for k, v in cat_container.items() if isinstance(v, dict) and "field" in v and v["field"] == field]
                        target_entry = max(field_entries, key=lambda x: datetime.fromisoformat(x[1]["updated_at"] if ".meta.json" in k else "0"), default=(None, None))
                        
                        if target_entry[0] is None:
                            # 新增条目
                            cat_container[field] = {
                                "field": field,
                                "updated_at": datetime.now().isoformat(),
                                "version": 1,
                                "sources": [] if not target_entry else list(target_entry[1].get("sources", [])),
                                **target_entry[1] if target_entry[0] else {}
                            }
                        else:
                            # 追加更新
                            new_sources = []
                            for src_match in re.findall(r'(?s)##\s*Profile Update:.*?^$', content, flags=re.MULTILINE):
                                src_match = src_match.strip()
                                if not src_match:
                                    continue
                                new_sources.append(src_match)
                            
                            existing_entry = target_entry[1]
                            existing_sources = existing_entry.get("sources", [])
                            
                            # 避免重复
                            combined_sources = []
                            for s in existing_sources:
                                if s not in new_sources and s not in combined_sources:
                                    combined_sources.append(s)
                            for s in new_sources:
                                if s not in existing_sources and s not in combined_sources:
                                    combined_sources.append(s)
                            
                            cat_container[target_entry[0]] = {
                                **existing_entry,
                                "updated_at": datetime.now().isoformat(),
                                "sources": combined_sources,
                                "version": existing_entry.get("version", 1) + 1
                            }
                        
                        updated = True
            
            except Exception as e:
                print(f"  ⚠ Error processing {rel_path}: {e}")
        
        # 保存更新后的 profile
        if updated:
            self.save_profile()
    
    def _save_profile(self):
        """保存 profile 到文件（覆盖模式）"""
        self.PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        save_data = {
            "version": self.profile["version"],
            "last_updated": datetime.now().isoformat(),
            "metadata": self.profile["metadata"]
        }
        
        save_data.update(self.profile.get("preferences", {}))
        save_data.update(self.profile.get("thinking_patterns", {})) 
        save_data.update(self.profile.get("behavior_traits", {}))
        
        with open(self.PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    def report(self) -> dict:
        """生成聚合报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "profile_updated": True,
            "latest_metadata": json.loads(self.PROFILE_FILE.read_text()) if self.PROFILE_FILE.exists() else None
        }


def main():
    # 这个脚本通过 cronjob 的 subagent 调用执行
    import sys
    
    aggregator = ProfileAggregator()
    files_to_process = []  # Will be populated by cronjob context
    
    if files_to_process:
        aggregator.aggregate_processed_files(files_to_process)
        report = aggregator.report()
    else:
        # No files to process, just ensure profile exists
        if not aggregator.PROFILE_FILE.exists():
            aggregator.save_profile()
    
    print("\n[✓] Profile aggregation complete")
    print(f"  Profile location: {aggregator.PROFILE_FILE}")
    
    # Output the profile for downstream consumption
    if aggregator.PROFILE_FILE.exists():
        print(f"\n\n--- Profile Content ---")
        profile_data = aggregator.report()
        print(json.dumps(profile_data["latest_metadata"], ensure_ascii=False, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())