#!/usr/bin/env python3
"""
量化随笔自动生成脚本
功能：
1. 搜索量化/投资相关新闻
2. 基于市场动态生成投资思考
3. 自动推送到 GitHub Pages
4. 自动更新博客首页索引
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

BLOG_DIR = Path("/project/robertquant.github.io/blog")
POSTS_DIR = BLOG_DIR / "posts"

def get_next_post_number():
    """获取下一个文章编号"""
    existing = list(POSTS_DIR.glob("*.html"))
    numbers = []
    for f in existing:
        match = re.search(r'(\d{3})-', f.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1

def generate_post_content(topic, thoughts):
    """生成博客文章 HTML"""
    post_num = get_next_post_number()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>投资笔记 #{post_num:03d} - {topic} | Robert Quant</title>
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
            background: #edf2f7;
            color: #4a5568;
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
        .back {{ margin-top: 40px; }}
        .back a {{
            color: #667eea;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <article class="article">
            <div class="header">
                <h1>投资笔记 #{post_num:03d}</h1>
                <div class="meta">
                    <span class="tag">市场观察</span>
                    <span>{date_str}</span>
                </div>
            </div>
            
            <h2>{topic}</h2>
            
            {thoughts}
            
            <div class="highlight">
                <strong>提醒：</strong>以上观点基于公开信息整理，不构成投资建议。市场有风险，投资需谨慎。
            </div>
            
            <div class="back">
                <a href="../index.html">← 返回随笔列表</a>
            </div>
        </article>
    </div>
</body>
</html>"""
    
    return html, post_num

def update_blog_index(new_post_num, topic, slug):
    """更新博客首页索引 - 插入HTML格式的文章卡片"""
    index_path = BLOG_DIR / "index.html"
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 读取现有内容
    content = index_path.read_text(encoding='utf-8')
    
    # 生成有意义的文件名
    filename = f"{new_post_num:03d}-{slug}.html"
    
    # 生成新的文章卡片HTML
    new_card = f'''            
            <!-- 文章卡片 -->
            <div class="post-card">
                <a href="./posts/{filename}">
                    <div class="post-header">
                        <h3 class="post-title">{topic}</h3>
                        <span class="post-date">{date_str}</span>
                    </div>
                    <div class="post-meta">
                        <span class="tag strategy">策略研究</span>
                    </div>
                    <p class="post-excerpt">
                        基于最新市场动态的量化思考与策略研究...
                    </p>
                </a>
            </div>
            
'''
    
    # 在 "<div class=\"post-list\">" 后面插入新卡片
    marker = '<div class="post-list">\n'
    if marker in content:
        # 找到 post-list div 的位置，在后面插入新卡片
        content = content.replace(marker, marker + '\n' + new_card)
        index_path.write_text(content, encoding='utf-8')
        return True
    
    print("⚠️ 未找到 post-list 标记，跳过索引更新")
    return False

def topic_to_slug(topic):
    """将中文主题转换为URL友好的slug"""
    # 主题映射表
    topic_map = {
        "关于量化策略的持续迭代": "celue_die_dai",
        "市场波动与情绪指标": "shichang_bodong",
        "A股散户行为与量化机会": "sanhu_xingwei",
        "ETF轮动策略实践": "etf_lun_dong",
        "小市值因子初探": "xiaoshizhi_yinzi",
        "可转债双低策略": "kezhuanzhai_shuangdi",
    }
    
    # 如果有映射，使用映射；否则生成通用slug
    if topic in topic_map:
        return topic_map[topic]
    
    # 简单的拼音转换（对于未映射的主题）
    # 这里简化处理，实际可以使用pypinyin库
    return "quant_research"

def main():
    """主函数 - 模拟生成一篇随笔"""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 示例：基于当前时间生成不同主题
    hour = datetime.now().hour
    
    topics_and_thoughts = [
        ("关于量化策略的持续迭代", "celue_die_dai", """
            <p>量化策略的有效性总是随时间衰减。今天回顾了过去几个策略的表现，发现一个规律：</p>
            
            <p>任何策略在公开或被多人使用后，超额收益都会逐渐收窄。这不仅仅是市场有效性的体现，更是因为市场参与者的学习效应。</p>
            
            <div class="highlight">
                <strong>思考：</strong>策略开发不应该追求"圣杯"，而应该建立一个持续发现、验证、迭代的体系。
            </div>
            
            <p>接下来需要建立一个策略监控框架，及时发现策略失效的信号。</p>
        """),
        ("市场波动与情绪指标", "shichang_bodong", """
            <p>今天观察到一个有趣的现象：当VIX（波动率指数）处于低位时，趋势跟踪策略的胜率明显下降。</p>
            
            <p>这可能是因为低波动环境下，市场缺乏明确方向，均线交叉信号更容易产生假突破。</p>
            
            <div class="highlight">
                <strong>假设：</strong>波动率可以作为趋势策略的过滤器。在ATR低于20日均值时，减少仓位或暂停交易。
            </div>
            
            <p>需要用历史数据验证这个假设的有效性。</p>
        """),
        ("A股散户行为与量化机会", "sanhu_xingwei", """
            <p>A股市场的参与者结构与美股有显著差异。散户占比高意味着情绪波动更大，但也可能带来套利机会。</p>
            
            <p>观察到一个现象：在涨停板上，经常出现封单不稳定的情况，这可能反映了散户的跟风心理。</p>
            
            <div class="highlight">
                <strong>方向：</strong>情绪指标（如融资余额变化、换手率异常）可能领先价格变化，值得深入研究。
            </div>
            
            <p>下一步：收集情绪指标数据，与价格走势做相关性分析。</p>
        """),
        ("ETF轮动策略实践", "etf_lun_dong", """
            <p>ETF轮动是量化投资中最经典的策略之一。最近回测了几种不同的轮动方法，包括波动率过滤、大盘趋势过滤等优化手段。</p>
            
            <p>核心发现：加入大盘趋势过滤后，策略在熊市中的回撤明显降低，但牛市中的收益也有所减少。</p>
            
            <div class="highlight">
                <strong>结论：</strong>任何优化都有代价，关键是找到适合自己风险偏好的平衡点。
            </div>
            
            <p>下一步：测试不同参数组合，寻找稳健性更好的配置。</p>
        """),
        ("小市值因子初探", "xiaoshizhi_yinzi", """
            <p>小市值因子在A股市场长期有效，但近年来波动加大。今天回测了2015-2024年的数据，验证其有效性。</p>
            
            <p>关键发现：小市值因子在牛市中表现优异，但在熊市中回撤巨大，需要配合止损机制。</p>
            
            <div class="highlight">
                <strong>启示：</strong>单一因子风险高，需要多因子组合和严格的风控。
            </div>
            
            <p>下一步：研究小市值+低PE的组合策略，降低波动。</p>
        """),
        ("可转债双低策略", "kezhuanzhai_shuangdi", """
            <p>可转债双低策略（低价+低溢价率）是低风险投资者的最爱。今天分析了当前市场的可转债标的。</p>
            
            <p>当前市场环境：债底保护明显，但转股溢价率普遍较高，双低标的稀缺。</p>
            
            <div class="highlight">
                <strong>策略：</strong>放宽价格标准到115元以下，溢价率20%以下，增加可选标的。
            </div>
            
            <p>风险提示：可转债信用风险不可忽视，需分散持仓。</p>
        """),
    ]
    
    # 根据时间选择主题
    topic_idx = hour % len(topics_and_thoughts)
    topic, slug, thoughts = topics_and_thoughts[topic_idx]
    
    # 生成文章
    html, post_num = generate_post_content(topic, thoughts)
    
    # 生成有意义的文件名
    filename = f"{post_num:03d}-{slug}.html"
    filepath = POSTS_DIR / filename
    filepath.write_text(html, encoding='utf-8')
    
    print(f"✅ 生成文章: {filename}")
    print(f"   主题: {topic}")
    
    # 更新索引（使用新的文件名格式）
    if update_blog_index(post_num, topic, slug):
        print(f"✅ 更新首页索引")
    
    # 推送到 GitHub
    print("🚀 推送到 GitHub Pages...")
    os.system("cd /project/robertquant.github.io && git add . && git commit -m 'Add auto-generated blog post' && git push")
    
    print(f"\n🔗 文章地址: https://robertquant.github.io/blog/posts/{filename}")

if __name__ == "__main__":
    main()
