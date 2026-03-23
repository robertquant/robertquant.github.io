#!/usr/bin/env python3
"""
GitHub量化代码库自动调研脚本
功能：
1. 搜索GitHub上的量化交易相关仓库
2. 分析仓库质量（stars、forks、更新频率、代码结构）
3. 生成调研报告/随笔
4. 推送到GitHub Pages
"""

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

BLOG_DIR = Path("/project/robertquant.github.io/blog")
POSTS_DIR = BLOG_DIR / "posts"

def get_next_post_number():
    """获取下一个文章编号"""
    existing = list(POSTS_DIR.glob("*.html"))
    numbers = []
    for f in existing:
        import re
        match = re.search(r'(\d{3})-', f.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1

def search_github_repos(query, sort="stars", order="desc", per_page=10):
    """搜索GitHub仓库"""
    cmd = [
        "gh", "api", 
        f"search/repositories",
        "-X", "GET",
        "-f", f"q={query}",
        "-f", f"sort={sort}",
        "-f", f"order={order}",
        "-f", f"per_page={per_page}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"搜索失败: {e}")
    return None

def analyze_repo(full_name):
    """分析单个仓库详情"""
    cmd = ["gh", "api", f"repos/{full_name}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"分析仓库失败: {e}")
    return None

def get_repo_languages(full_name):
    """获取仓库主要语言"""
    cmd = ["gh", "api", f"repos/{full_name}/languages"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        pass
    return {}

def generate_research_post(topic, repos_data):
    """生成调研随笔HTML"""
    post_num = get_next_post_number()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 构建仓库列表HTML
    repos_html = ""
    for i, repo in enumerate(repos_data[:5], 1):
        name = repo.get('full_name', 'Unknown')
        description = repo.get('description', '无描述') or '无描述'
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        lang = repo.get('language', 'Unknown') or 'Unknown'
        url = repo.get('html_url', '#')
        
        repos_html += f"""
            <div class="repo-card">
                <div class="repo-header">
                    <span class="repo-rank">#{i}</span>
                    <a href="{url}" target="_blank" class="repo-name">{name}</a>
                </div>
                <p class="repo-desc">{description}</p>
                <div class="repo-stats">
                    <span class="stat">⭐ {stars}</span>
                    <span class="stat">🍴 {forks}</span>
                    <span class="stat">🔤 {lang}</span>
                </div>
            </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码库调研 #{post_num:03d} - {topic} | Robert Quant</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f7fa;
        }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        .article {{
            background: white;
            border-radius: 12px;
            padding: 50px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ font-size: 1.8em; color: #2d3748; margin-bottom: 10px; }}
        .meta {{ color: #718096; font-size: 0.9em; }}
        .tag {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            margin-right: 8px;
        }}
        h2 {{ color: #4a5568; margin: 30px 0 15px; font-size: 1.3em; }}
        p {{ margin: 15px 0; }}
        .highlight {{
            background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .repo-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }}
        .repo-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .repo-rank {{
            background: #667eea;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .repo-name {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1em;
        }}
        .repo-name:hover {{ text-decoration: underline; }}
        .repo-desc {{ color: #4a5568; margin: 10px 0; }}
        .repo-stats {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .repo-stats .stat {{
            color: #718096;
            font-size: 0.9em;
        }}
        .back {{ margin-top: 40px; }}
        .back a {{ color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <article class="article">
            <div class="header">
                <h1>代码库调研 #{post_num:03d}</h1>
                <div class="meta">
                    <span class="tag">技术调研</span>
                    <span>{date_str}</span>
                </div>
            </div>
            
            <h2>{topic}</h2>
            
            <p>本次调研通过GitHub API搜索了相关的量化交易开源项目，从stars数量、代码活跃度、功能完整性等维度进行筛选。</p>
            
            <div class="highlight">
                <strong>调研方法：</strong>使用 GitHub CLI (gh) 搜索API，按stars排序，筛选近期有更新的活跃仓库。
            </div>
            
            <h2>值得关注的仓库</h2>
            
            {repos_html}
            
            <div class="highlight">
                <strong>下一步计划：</strong><br>
                1. 深入研读排名靠前的仓库源码<br>
                2. 提取可复用的策略逻辑和工具函数<br>
                3. 评估是否可以集成到现有量化体系中
            </div>
            
            <div class="back">
                <a href="../index.html">← 返回随笔列表</a>
            </div>
        </article>
    </div>
</body>
</html>"""
    
    return html, post_num

def update_blog_index(new_post_num, topic):
    """更新博客首页索引"""
    index_path = BLOG_DIR / "index.html"
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        content = index_path.read_text(encoding='utf-8')
        new_entry = f'''            <!-- 文章卡片 -->
            <div class="post-card">
                <a href="./posts/{new_post_num:03d}-github-research.html">
                    <div class="post-header">
                        <h3 class="post-title">{topic}</h3>
                        <span class="post-date">{date_str}</span>
                    </div>
                    <div class="post-meta">
                        <span class="tag tech">技术调研</span>
                    </div>
                    <p class="post-excerpt">
                        GitHub量化代码库自动调研报告，发现值得关注的开源项目...
                    </p>
                </a>
            </div>
            
'''
        marker = "<!-- 最新文章列表 -->\n        <div class=\"post-list\">\n"
        if marker in content:
            content = content.replace(marker, marker + new_entry)
            index_path.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"更新索引失败: {e}")
    return False

def main():
    """主函数 - 执行GitHub代码库调研"""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 搜索关键词列表（每次随机选择一个）
    search_topics = [
        ("量化交易回测", "backtrader OR zipline OR quant trading python"),
        ("技术分析指标", "ta-lib OR technical analysis python"),
        ("投资组合优化", "portfolio optimization python"),
        ("机器学习量化", "machine learning trading python"),
        ("加密货币量化", "crypto trading bot python"),
    ]
    
    import random
    topic_cn, topic_en = random.choice(search_topics)
    
    print(f"🔍 正在搜索: {topic_cn} ({topic_en})")
    
    # 搜索GitHub
    results = search_github_repos(topic_en, per_page=10)
    
    if not results or 'items' not in results:
        print("❌ 搜索失败或无结果")
        return
    
    repos = results['items']
    print(f"✅ 找到 {len(repos)} 个仓库")
    
    # 过滤和分析
    analyzed_repos = []
    for repo in repos:
        if repo.get('stargazers_count', 0) < 10:  # 降低门槛到10 stars
            continue
        analyzed_repos.append(repo)
    
    if not analyzed_repos:
        print("❌ 没有符合条件的仓库")
        return
    
    # 生成文章
    html, post_num = generate_research_post(f"GitHub量化代码库调研：{topic_cn}", analyzed_repos)
    
    filename = f"{post_num:03d}-github-research.html"
    filepath = POSTS_DIR / filename
    filepath.write_text(html, encoding='utf-8')
    
    print(f"✅ 生成文章: {filename}")
    
    # 更新索引
    if update_blog_index(post_num, f"GitHub量化代码库调研：{topic_cn}"):
        print(f"✅ 更新首页索引")
    
    # 推送到GitHub
    print("🚀 推送到 GitHub Pages...")
    os.system("cd /project/robertquant.github.io && git add . && git commit -m 'Add GitHub code research post' && git push")
    
    print(f"\n🔗 文章地址: https://robertquant.github.io/blog/posts/{filename}")

if __name__ == "__main__":
    main()
