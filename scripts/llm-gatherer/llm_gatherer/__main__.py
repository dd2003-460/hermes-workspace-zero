#!/usr/bin/env python3
"""
LLM Gatherer CLI

用法:
    # 1. 登录（首次使用）
    $ python3 -m llm_gatherer login <service>

    # 2. 提问
    $ python3 -m llm_gatherer ask <service> "你的问题"

    # 3. 带文件提问（上传文件给 LLM）
    $ python3 -m llm_gatherer ask <service> "请审查此文件" --file path/to/file

    # 4. 通过 Google 搜索辅助
    $ python3 -m llm_gatherer search "关键词"
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright
from llm_gatherer import browser, config
from llm_gatherer.llm_interface import get_llm_api, SERVICE_MAP
from llm_gatherer import cdp_client


def cmd_login(args):
    """登录流程"""
    service_name = args.service
    if service_name not in config.SERVICES:
        print(f"不支持的服务: {service_name}")
        print(f"支持的: {list(config.SERVICES.keys())}")
        sys.exit(1)

    service_cfg = config.SERVICES[service_name]
    print(f"[llm-gatherer] 正在启动 {service_cfg['name']} ...")

    ctx, browser_obj, pw = browser.create_context()
    try:
        success = browser.handle_login(ctx, service_cfg)
        if success:
            browser.save_auth_state(ctx, service_name)
            print(f"[llm-gatherer] 登录成功！认证状态已保存。")
        else:
            print("[llm-gatherer] 登录超时，请手动重试。")
    finally:
        browser_obj.close()
        pw.stop()


async def cmd_ask_cdp(args):
    """提问 — CDP mode: control the user's already-running Chrome window."""
    service_name = args.service
    question = args.question

    if service_name not in SERVICE_MAP:
        print(f"不支持的服务: {service_name}")
        sys.exit(1)

    service_cfg = config.SERVICES[service_name]
    print(f"[llm-gatherer] 正在通过 CDP 连接 {service_cfg['name']} ...")

    client = await cdp_client.create_cdp_client()
    if not client:
        print("[llm-gatherer] 无法连接到 Chrome，请确保 Chrome 正在运行。")
        sys.exit(1)

    page_info = cdp_client.find_chatgpt_page(client)
    if not page_info:
        print("[llm-gatherer] 无法找到 ChatGPT 页面。")
        print("[llm-gatherer] 请先打开 ChatGPT 页面后再试。")
        sys.exit(1)

    # Check login status
    if not await cdp_client.check_logged_in(page_info):
        print("[llm-gatherer] 未检测到登录状态，请手动登录 ChatGPT。")
        sys.exit(1)

    result = await cdp_client.ask_chatgpt_cdp(page_info, question, timeout=60)

    print("\n" + "=" * 60)
    print("[llm-gatherer] 回复:")
    print("=" * 60)
    print(result)

    output_file = Path("llm_response.txt")
    output_file.write_text(f"服务: {service_cfg['name']}\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n问题:\n{question}\n\n回复:\n{result}")
    print(f"\n[llm-gatherer] 结果已保存到 {output_file}")


def cmd_ask(args):
    """提问"""
    service_name = args.service
    question = args.question
    file_path = args.file

    if service_name not in config.SERVICES:
        print(f"不支持的服务: {service_name}")
        sys.exit(1)

    service_cfg = config.SERVICES[service_name]
    print(f"[llm-gatherer] 正在连接 {service_cfg['name']} ...")

    ctx, browser_obj, pw = browser.create_context()
    try:
        api = get_llm_api(service_name, ctx, service_cfg)

        # 确保登录
        if not browser.check_logged_in(ctx, service_cfg):
            print("[llm-gatherer] 未检测到登录状态，尝试登录...")
            if not browser.handle_login(ctx, service_cfg):
                print("[llm-gatherer] 登录失败，请手动登录。")
                sys.exit(1)
            browser.save_auth_state(ctx, service_name)

        # 执行提问
        if file_path:
            print(f"[llm-gatherer] 发送问题（含文件: {file_path}）...")
            result = api.ask_with_file(question, file_path)
        else:
            print(f"[llm-gatherer] 发送问题...")
            result = api.ask(question)

        print("\n" + "=" * 60)
        print("[llm-gatherer] 回复:")
        print("=" * 60)
        print(result)

        # 保存结果到文件
        output_file = Path("llm_response.txt")
        output_file.write_text(f"服务: {service_cfg['name']}\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n问题:\n{question}\n\n回复:\n{result}")
        print(f"\n[llm-gatherer] 结果已保存到 {output_file}")

    finally:
        browser_obj.close()
        pw.stop()


def cmd_search(args):
    """通过 Gemini 搜索"""
    query = args.query

    print(f"[llm-gatherer] 正在通过 Gemini 搜索: {query}")

    ctx, browser_obj, pw = browser.create_context()
    try:
        api = get_llm_api("gemini", ctx, config.SERVICES["gemini"])

        # 确保登录
        if not browser.check_logged_in(ctx, config.SERVICES["gemini"]):
            print("[llm-gatherer] 未检测到 Gemini 登录状态，尝试登录...")
            if not browser.handle_login(ctx, config.SERVICES["gemini"]):
                print("[llm-gatherer] 登录失败。")
                sys.exit(1)
            browser.save_auth_state(ctx, "gemini")

        search_query = f"请搜索并总结关于 \"{query}\" 的最新信息"
        print(f"[llm-gatherer] 发送搜索请求...")
        result = api.ask(search_query, timeout=90)

        print("\n" + "=" * 60)
        print("[llm-gatherer] 搜索结果:")
        print("=" * 60)
        print(result)

    finally:
        browser_obj.close()
        pw.stop()


def main():
    parser = argparse.ArgumentParser(description="LLM Gatherer — RALPH 信息搜集工具")
    subparsers = parser.add_subparsers(dest="command")

    # login
    login_parser = subparsers.add_parser("login", help="登录 LLM 服务（首次使用）")
    login_parser.add_argument("service", choices=list(config.SERVICES.keys()), help="要登录的服务")

    # ask
    ask_parser = subparsers.add_parser("ask", help="向 LLM 提问")
    ask_parser.add_argument("service", choices=list(config.SERVICES.keys()), help="目标服务")
    ask_parser.add_argument("question", help="你的问题")
    ask_parser.add_argument("--file", help="附加文件路径（上传给 LLM）")

    # search
    search_parser = subparsers.add_parser("search", help="通过 Gemini 搜索")
    search_parser.add_argument("query", help="搜索关键词")

    # ask --cdp
    ask_cdp_parser = subparsers.add_parser("ask-cdp", help="向 LLM 提问（通过 CDP 控制已登录的 Chrome）")
    ask_cdp_parser.add_argument("service", choices=list(config.SERVICES.keys()), help="目标服务")
    ask_cdp_parser.add_argument("question", help="你的问题")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "login": cmd_login,
        "ask": cmd_ask,
        "search": cmd_search,
        "ask-cdp": lambda args: asyncio.run(cmd_ask_cdp(args)),
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
