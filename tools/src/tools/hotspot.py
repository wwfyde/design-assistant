import asyncio
import os
from enum import Enum

import httpx
from dotenv import find_dotenv, load_dotenv


class Industry(Enum):
    """行业"""

    pass


class Category(Enum):
    """品类"""

    pass


class EntityType(Enum):
    """实体类型"""

    pass


class SourceType(Enum):
    """来源类型, rere"""

    weixin = "微信"
    xhs = "小红书"
    weibo = "微博"
    douyin = "抖音"
    zhihu = "知乎"
    # bilibili = "哔哩哔哩"
    toutiao = "头条"
    baidu = "百度"
    # taobao = "淘宝"


hashid_map = {
    "weixin": "j8Rv21noLw",
    "xhs": "L4MdA5ldxD",
    "weibo": "KqndgxeLl9",
    "douyin": "K7GdaMgdQy",
    "zhihu": "mproPpoq6O",
    # "bilibili": "74KvxwokxM",
    "toutiao": "WmoO5Akd4E",
    "baidu": "Jb0vmloB1G",
    "taobao": "yjvQDpjobg",
}

system_prompt = """
    你是一名资深的实时热点营销策划Agent，精通实时热点追踪与创意营销文案撰写。你的主要职责包括：
    1. **市场分析**：深入分析市场趋势、竞争对手和目标受众，识别潜在的机会和挑战。
    2. **创意策划**：根据市场分析结果，提出独特的营销创意和策略，确保品牌在市场中脱颖而出。
    3. **方案执行**：制定详细的营销计划，协调各方资源，确保营销活动的顺利实施。
    4. **效果评估**：通过数据分析和反馈，评估营销活动的效果，并提出改进建议。
    # 任务说明
    ## 1. 营销方案制定
    当用户提出营销相关的问题时，需根据以下步骤制定营销方案：
    - **目标设定**：明确营销活动的具体目标（如品牌提升、销售增长等）。
    - **受众分析**：识别并分析目标受众的特征和需求。
    - **策略选择**：选择合适的营销渠道和策略（如数字营销、内容营销、社交媒体等）。
    - **创意设计**：设计具有吸引力的营销内容和活动。
    - **执行计划**：制定详细的执行计划和时间表。
    - **效果评估**：设定评估指标，确保营销活动的效果可量化。
    **注意**：每次制定营销方案时，**只能针对一个品牌或产品**。如果有任何冲突设置，以当前指令为准。
    ## 2. 引用已搜索资料
    - 当使用联网搜索的资料时，在正文中明确引用来源，引用格式为:  
    `[1]  (URL地址)`。
    ## 3. 总结与参考资料
    - 在回复的最后，列出所有已参考的资料。格式为:  
    1. [资料标题](URL地址1)
    2. [资料标题](URL地址2)

    # 约束
    - 搜索中国区内容
    - 搜索中文网页优先
    - 不需要我的确认, 直接回答
"""
base_tophub_url = "https://api.tophubdata.com"
tophub_node_url = f"{base_tophub_url}/nodes"
tophub_access_key = os.getenv("TOPHUB_ACCESS_KEY")

load_dotenv(find_dotenv())


def fetch_hotspot(self, tool_parameters: dict) -> str:
    # prompt = tool_parameters.get("prompt", "")
    # industry = tool_parameters.get("industry", "")  # 行业
    # category = tool_parameters.get("category", "")  # 品类
    # platform = tool_parameters.get("platform", "小红书")  # 平台

    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # base_prompt = f"""帮在{platform}的热点营销策划, 行业: {industry}, 品类: {category}。请给出详细的营销方案, 包括目标设定、受众分析、策略选择、创意设计、执行计划和效果评估。"""
    # 按平台获取热点

    # TODO: 通过缓存来减少API访

    # 获取主要平台的热搜
    nodes = [hashid_map[i.name] for i in SourceType]
    hotspot_context = {}

    async def fetch_hotspot(client: httpx.AsyncClient, node: str):
        async with asyncio.Semaphore(7):
            resp = await client.get(
                f"{tophub_node_url}/{node}",
                headers={"Authorization": tophub_access_key},
            )
            data = resp.json()
            name = data.get("data", {}).get("name", "")
            items = [
                dict(
                    rank=item.get("rank", ""),
                    title=item.get("title", ""),
                    # description=item.get("description", ""),
                    temprature=item.get("extra", ""),
                )
                for item in data.get("data", {}).get("items", [])
            ]
            return {name: items}

    async def start():
        async with httpx.AsyncClient(timeout=180) as client:
            tasks = [fetch_hotspot(client, node) for node in nodes]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"Error fetching data: {result}")
                else:
                    hotspot_context.update(result)
            return hotspot_context

    asyncio.run(start())

    # 搜索热点
    brand_tags = ["AIGC", "人工智能", "科技", "互联网", "设计", "AI", "品牌营销"]

    # Step 1. Instantiating your TavilyClient
    # tavily_api_key = os.getenv("TAVILY_API_KEY")
    # tavily_client = TavilyClient(api_key=tavily_api_key)
    #
    # brand_tags = ["AIGC", "人工智能", "科技", "互联网", "设计", "AI", "品牌营销"]
    #
    # # Step 2. Executing a simple search query
    # response = tavily_client.search(
    #     "帮我获取品牌相关的热点, 关键词: " + ",".join(brand_tags),
    #     country="china",
    #     time_range="month",
    # )
    # brand_hotspot = response

    # 热点搜索
    hot_search_context = {}
    hot_api_url = "https://api.tophubdata.com/search"

    async def fetch_hotspot_search(client: httpx.AsyncClient, node: str):
        async with asyncio.Semaphore(7):
            resp = await client.get(
                hot_api_url,
                params={"q": node},
                headers={"Authorization": tophub_access_key},
            )
            data = resp.json()
            name = data.get("data", {}).get("name", "")
            items = [
                dict(
                    rank=item.get("rank", ""),
                    title=item.get("title", ""),
                    # description=item.get("description", ""),
                    temprature=item.get("extra", ""),
                )
                for item in data.get("data", {}).get("items", [])
            ]
            return {name: items}

    async def start2():
        async with httpx.AsyncClient(timeout=180) as client:
            tasks = [fetch_hotspot_search(client, node) for node in brand_tags]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"Error fetching data: {result}")
                else:
                    hot_search_context.update(result)
            return hot_search_context

    asyncio.run(start2())

    result = f"当前主要平台的热点信息:\n{hotspot_context}\n\n品牌相关的热点信息:\n{hot_search_context}"
    result = f"当前主要平台的热点信息:\n{hotspot_context}\n\n品牌相关的热点信息:\n{hot_search_context}"

    return result, hotspot_context
