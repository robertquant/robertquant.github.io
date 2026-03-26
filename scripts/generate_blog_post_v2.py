#!/usr/bin/env python3
"""
量化随笔生成脚本 v2.0 - 基于实质发现
核心逻辑：
1. 收集市场数据和研究发现
2. 判断是否有值得记录的新内容
3. 有实质内容时生成随笔，无则跳过

信息来源：
- 自选股价格异动
- 策略回测新结果
- 市场技术指标信号
- GitHub新发现
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# 添加项目路径
sys.path.insert(0, '/project/quant-research')
sys.path.insert(0, '/root/.openclaw/workspace/skills/tencent-finance-stock-price')

BLOG_DIR = Path("/project/robertquant.github.io/blog")
POSTS_DIR = BLOG_DIR / "posts"
DATA_DIR = Path("/project/quant-research/data")
NOTES_DIR = Path("/project/quant-research/notes")

class BlogPostGenerator:
    """基于实质发现的随笔生成器"""
    
    def __init__(self):
        self.today = datetime.now()
        self.date_str = self.today.strftime("%Y-%m-%d")
        self.has_content = False
        self.content_sections = []
        self.post_topic = None
        self.post_tags = []
        
    def collect_market_data(self):
        """收集市场数据"""
        print("📊 收集市场数据...")
        
        # 1. 获取自选股价格
        try:
            from get_stock_price import get_realtime_quotes
            stocks = ['600519', '000001', '002594', '300750']
            quotes = get_realtime_quotes(stocks)
            
            # 检查是否有异常波动（涨跌幅>5%）
            abnormal_moves = []
            for code, data in quotes.items():
                change_pct = data.get('涨跌幅', 0)
                if abs(change_pct) > 5:
                    abnormal_moves.append({
                        'code': code,
                        'name': data.get('名称', code),
                        'price': data.get('最新价', 0),
                        'change': change_pct
                    })
            
            if abnormal_moves:
                self.has_content = True
                self.content_sections.append({
                    'type': 'market_move',
                    'title': '今日异动观察',
                    'data': abnormal_moves
                })
                print(f"   ✅ 发现 {len(abnormal_moves)} 只异动股票")
            else:
                print("   ℹ️ 自选股无显著异动")
                
        except Exception as e:
            print(f"   ⚠️ 获取股价失败: {e}")
    
    def collect_backtest_results(self):
        """收集策略回测结果"""
        print("📈 检查策略回测结果...")
        
        # 检查是否有新的回测报告
        reports_dir = Path("/project/quant-research/reports")
        if reports_dir.exists():
            # 查找今天生成的报告
            today_str = self.today.strftime("%Y%m%d")
            new_reports = list(reports_dir.glob(f"*{today_str}*.json"))
            
            if new_reports:
                self.has_content = True
                for report_file in new_reports[:1]:  # 最多取一个
                    try:
                        data = json.loads(report_file.read_text())
                        self.content_sections.append({
                            'type': 'backtest',
                            'title': f"策略回测：{data.get('strategy_name', '未知策略')}",
                            'data': data
                        })
                        print(f"   ✅ 发现新回测报告: {report_file.name}")
                    except:
                        pass
            else:
                print("   ℹ️ 今日无新回测报告")
    
    def collect_strategy_signals(self):
        """收集策略信号"""
        print("🔔 扫描策略信号...")
        
        # 检查今日信号文件
        signal_file = NOTES_DIR / f"signals_{self.today.strftime('%Y%m%d')}.json"
        if signal_file.exists():
            try:
                signals = json.loads(signal_file.read_text())
                if signals:
                    self.has_content = True
                    self.content_sections.append({
                        'type': 'signals',
                        'title': '今日策略信号',
                        'data': signals
                    })
                    print(f"   ✅ 发现 {len(signals)} 个交易信号")
            except:
                pass
        else:
            print("   ℹ️ 今日无策略信号")
    
    def collect_research_notes(self):
        """收集研究笔记"""
        print("📝 检查研究笔记...")
        
        # 检查今天的手动笔记
        note_file = NOTES_DIR / f"{self.today.strftime('%Y-%m-%d')}.md"
        if note_file.exists():
            content = note_file.read_text()
            if len(content) > 100:  # 有实质内容
                self.has_content = True
                self.content_sections.append({
                    'type': 'research',
                    'title': '研究笔记',
                    'content': content[:500]  # 取前500字
                })
                print("   ✅ 发现今日研究笔记")
        else:
            print("   ℹ️ 今日无研究笔记")
    
    def decide_topic(self):
        """根据收集的内容决定文章主题"""
        if not self.has_content:
            return None
        
        # 优先级：回测结果 > 交易信号 > 异动观察 > 研究笔记
        priority_types = ['backtest', 'signals', 'market_move', 'research']
        
        for ptype in priority_types:
            for section in self.content_sections:
                if section['type'] == ptype:
                    self.post_topic = section['title']
                    self.post_tags = self._get_tags_for_type(ptype)
                    return self.post_topic
        
        return None
    
    def _get_tags_for_type(self, content_type):
        """根据内容类型返回标签"""
        tag_map = {
            'backtest': ['策略研究', '回测分析'],
            'signals': ['交易信号', '实盘跟踪'],
            'market_move': ['市场观察', '异动分析'],
            'research': ['深度研究', '因子挖掘']
        }
        return tag_map.get(content_type, ['量化随笔'])
    
    def generate_content(self):
        """基于收集的数据生成文章正文"""
        sections_html = []
        
        for section in self.content_sections:
            if section['type'] == 'market_move':
                html = self._render_market_move(section)
            elif section['type'] == 'backtest':
                html = self._render_backtest(section)
            elif section['type'] == 'signals':
                html = self._render_signals(section)
            elif section['type'] == 'research':
                html = self._render_research(section)
            else:
                continue
            sections_html.append(html)
        
        return '\n'.join(sections_html)
    
    def _render_market_move(self, section):
        """渲染异动观察部分"""
        stocks_html = ""
        for stock in section['data']:
            direction = "📈" if stock['change'] > 0 else "📉"
            stocks_html += f"<li>{direction} <strong>{stock['name']}</strong> ({stock['code']}): {stock['change']:+.2f}% @ ¥{stock['price']:.2f}</li>\n"
        
        return f"""
            <h2>{section['title']}</h2>
            <p>今日自选股中出现以下显著波动，值得跟踪分析：</p>
            <ul style="margin-left: 20px; color: #4a5568; line-height: 2;">
                {stocks_html}
            </ul>
            <div class="highlight">
                <strong>💡 初步观察：</strong><br>
                异动可能是消息驱动或技术性突破。需要结合成交量、资金流向进一步确认持续性。
            </div>
        """
    
    def _render_backtest(self, section):
        """渲染回测结果部分"""
        data = section['data']
        metrics = data.get('metrics', {})
        
        return f"""
            <h2>{section['title']}</h2>
            <p>今日完成对该策略的系统性回测验证，关键指标如下：</p>
            <div class="data-box">
                <strong>回测区间：</strong>{data.get('start_date', 'N/A')} ~ {data.get('end_date', 'N/A')}<br>
                <strong>年化收益：</strong>{metrics.get('annual_return', 0):.2f}%<br>
                <strong>最大回撤：</strong>{metrics.get('max_drawdown', 0):.2f}%<br>
                <strong>夏普比率：</strong>{metrics.get('sharpe_ratio', 0):.2f}<br>
                <strong>交易次数：</strong>{metrics.get('trade_count', 0)}次
            </div>
            <p>{data.get('summary', '策略回测完成，结果待进一步分析。')}</p>
        """
    
    def _render_signals(self, section):
        """渲染交易信号部分"""
        signals = section['data']
        signals_html = ""
        for sig in signals[:5]:  # 最多显示5个
            direction = "买入" if sig.get('direction') == 'buy' else "卖出"
            signals_html += f"<li><strong>{sig.get('code')}</strong> - {direction} @ {sig.get('price', 'N/A')} ({sig.get('reason', '')})</li>\n"
        
        return f"""
            <h2>{section['title']}</h2>
            <p>根据今日收盘数据，以下标的触发交易信号：</p>
            <ul style="margin-left: 20px; color: #4a5568; line-height: 2;">
                {signals_html}
            </ul>
            <div class="highlight">
                <strong>⚠️ 风险提示：</strong><br>
                以上信号基于历史数据回测生成，不构成投资建议。请结合自身风险承受能力谨慎决策。
            </div>
        """
    
    def _render_research(self, section):
        """渲染研究笔记部分"""
        # 将Markdown转为简单HTML
        content = section['content'].replace('\n\n', '</p><p>').replace('\n', '<br>')
        return f"""
            <h2>{section['title']}</h2>
            <p>{content}</p>
        """
    
    def create_post(self):
        """创建博客文章"""
        if not self.has_content:
            print("\n⚠️ 今日无实质内容，跳过随笔生成")
            return False
        
        topic = self.decide_topic()
        if not topic:
            print("\n⚠️ 无法确定文章主题，跳过")
            return False
        
        print(f"\n✅ 确定文章主题: {topic}")
        
        # 生成内容
        content_html = self.generate_content()
        
        # 获取文章编号
        post_num = self._get_next_post_number()
        
        # 生成HTML
        html = self._generate_html(post_num, topic, content_html)
        
        # 保存文件
        slug = self._generate_slug(topic)
        filename = f"{post_num:03d}-{slug}.html"
        filepath = POSTS_DIR / filename
        filepath.write_text(html, encoding='utf-8')
        print(f"   ✅ 生成文章: {filename}")
        
        # 更新索引
        self._update_index(post_num, topic, slug)
        
        # 推送到GitHub
        self._push_to_github()
        
        return True
    
    def _get_next_post_number(self):
        """获取下一个文章编号"""
        existing = list(POSTS_DIR.glob("*.html"))
        numbers = []
        for f in existing:
            match = re.search(r'(\d{3})-', f.name)
            if match:
                numbers.append(int(match.group(1)))
        return max(numbers, default=0) + 1
    
    def _generate_slug(self, topic):
        """生成URL友好的slug"""
        # 简单拼音映射
        pinyin_map = {
            '今日异动观察': 'jinri_yidong',
            '策略回测': 'celue_huice',
            '交易信号': 'jiaoyi_xinhao',
            '研究笔记': 'yanjiu_biji',
        }
        for key, value in pinyin_map.items():
            if key in topic:
                return value
        return 'quant_notes'
    
    def _generate_html(self, post_num, topic, content):
        """生成完整HTML"""
        tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in self.post_tags])
        
        return f"""<!DOCTYPE html>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            margin-right: 8px;
        }}
        h2 {{ color: #4a5568; margin: 30px 0 15px; font-size: 1.3em; border-left: 4px solid #667eea; padding-left: 15px; }}
        p {{ margin: 15px 0; color: #4a5568; }}
        .highlight {{
            background: linear-gradient(120deg, #f6f9fc 0%, #e9f2f9 100%);
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
        }}
        .data-box {{
            background: #f7fafc;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 15px 0;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.9em;
            line-height: 1.8;
        }}
        .back {{ margin-top: 40px; }}
        .back a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .timestamp {{
            color: #a0aec0;
            font-size: 0.85em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <article class="article">
            <div class="header">
                <h1>投资笔记 #{post_num:03d}</h1>
                <div class="meta">
                    {tags_html}
                    <span>{self.date_str}</span>
                </div>
            </div>
            
            {content}
            
            <div class="timestamp">
                ⚠️ 风险提示：以上观点基于公开信息整理，不构成投资建议。市场有风险，投资需谨慎。<br>
                <span style="color: #a0aec0;">本文数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            </div>
            
            <div class="back">
                <a href="../index.html">← 返回随笔列表</a>
            </div>
        </article>
    </div>
</body>
</html>"""
    
    def _update_index(self, post_num, topic, slug):
        """更新博客首页索引"""
        index_path = BLOG_DIR / "index.html"
        content = index_path.read_text(encoding='utf-8')
        
        filename = f"{post_num:03d}-{slug}.html"
        excerpt = f"基于{self.date_str}市场数据和研究发现的量化分析..."
        
        new_card = f'''            
            <!-- 文章卡片 {post_num:03d} - {topic} -->
            <div class="post-card">
                <a href="./posts/{filename}">
                    <div class="post-header">
                        <h3 class="post-title">{topic}</h3>
                        <span class="post-date">{self.date_str}</span>
                    </div>
                    <div class="post-meta">
                        {''.join([f'<span class="tag strategy">{tag}</span>' for tag in self.post_tags[:2]])}
                    </div>
                    <p class="post-excerpt">{excerpt}</p>
                </a>
            </div>
            
'''
        
        marker = '<div class="post-list">\n'
        if marker in content:
            content = content.replace(marker, marker + '\n' + new_card)
            index_path.write_text(content, encoding='utf-8')
            print("   ✅ 索引更新成功")
    
    def _push_to_github(self):
        """推送到GitHub"""
        print("\n🚀 推送到 GitHub Pages...")
        result = os.system("cd /project/robertquant.github.io && git add . && git commit -m 'Add research note' && git push")
        if result == 0:
            print("   ✅ 推送成功")
        else:
            print("   ⚠️ 推送可能失败，请手动检查")


def main():
    """主函数"""
    print("=" * 60)
    print(f"📊 量化随笔生成 v2.0 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    
    generator = BlogPostGenerator()
    
    # 收集各类信息
    generator.collect_market_data()
    generator.collect_backtest_results()
    generator.collect_strategy_signals()
    generator.collect_research_notes()
    
    # 创建文章（有内容时才创建）
    success = generator.create_post()
    
    if success:
        print("\n✅ 随笔生成完成")
    else:
        print("\nℹ️ 今日无新发现，随笔生成已跳过")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
