pip install requests tavily-python openai

import re
import requests
from tavily import TavilyClient
from openai import OpenAI


# ==================================================
# 1. 配置：告诉程序使用哪个模型和搜索服务
# ==================================================

# 这里填写你的实际配置。
# 填写密钥后的代码不要公开或上传到 GitHub。
API_KEY = "YOUR_API_KEY"
BASE_URL = "YOUR_BASE_URL"
MODEL_ID = "YOUR_MODEL_ID"
TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"


# ==================================================
# 2. 给模型的说明书
# ==================================================

# 这是一个普通的多行字符串。
# 它告诉模型：有哪些工具、怎样请求调用工具、怎样结束任务。
#
# 注意：
# 把工具名字写在提示词里，并不会自动执行工具。
# 后面的 Python 主循环才负责真正调用函数。

AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。
请根据用户请求，使用可用工具获取信息，然后给出答案。

可用工具：
1. get_weather(city: str)
   查询指定城市的当前天气。

2. get_attraction(city: str, weather: str)
   根据城市和天气，搜索合适的旅游景点。

每次回复必须使用下面的格式：

Thought: 简短说明下一步行动的目的。
Action: 具体行动

Action 只能使用以下两种格式之一：

调用工具：
Action: get_weather(city="北京")
Action: get_attraction(city="北京", weather="晴天")

结束任务：
Action: Finish[给用户的最终答案]

规则：
- 每次只输出一个 Thought 和一个 Action。
- Action 必须写在同一行。
- 工具参数使用双引号。
- 不要自行编造工具返回结果。
- 工具结果会由程序通过 Observation 提供。
- 如果工具失败，应说明限制，不要编造天气或搜索结果。
- 信息足够时，使用 Finish[...] 结束任务。
"""


# ==================================================
# 3. 工具一：查询天气
# ==================================================

# city: str 表示 city 预期是字符串。
# -> str 表示这个函数预期返回字符串。
# 类型提示不会自动检查或转换数据。

def get_weather(city: str) -> str:
    """向天气服务发送请求，返回天气描述。"""

    url = f"https://wttr.in/{city}"

    try:
        # 向天气服务发起 HTTP 请求。
        #
        # params={"format": "j1"}：要求返回 JSON 格式。
        # timeout=10：设置网络等待超时，避免一直等待。
        # 注意：这个超时不是整个请求总耗时的严格上限。
        response = requests.get(
            url,
            params={"format": "j1"},
            timeout=10
        )

        # 如果服务器返回 HTTP 错误，例如 404、500，
        # 这一行会产生异常，跳到下面对应的 except。
        response.raise_for_status()

        # 将响应中的 JSON 转换成 Python 数据结构。
        data = response.json()

        # current_condition 是一个列表。
        # [0] 表示取出列表中的第一项。
        current = data["current_condition"][0]

        # 从当前天气数据中取出描述和温度。
        description = current["weatherDesc"][0]["value"]
        temperature = current["temp_C"]

        # return 把结果交回调用这个函数的地方。
        return (
            f"{city}当前天气：{description}，"
            f"气温 {temperature} 摄氏度"
        )

    except requests.exceptions.Timeout:
        return "错误：查询天气超时。"

    except requests.exceptions.RequestException as e:
        return f"错误：天气请求失败：{e}"

    except (ValueError, KeyError, IndexError, TypeError) as e:
        return f"错误：无法解析天气数据：{e}"


# ==================================================
# 4. 工具二：根据天气搜索景点
# ==================================================

def get_attraction(city: str, weather: str) -> str:
    """调用 Tavily，搜索适合当前天气的景点。"""

    try:
        # 创建搜索服务的客户端。
        tavily = TavilyClient(api_key=TAVILY_API_KEY)

        # 将城市和天气组合成搜索词。
        query = f"{city}，天气为{weather}，推荐适合游览的景点及理由"

        # 调用搜索 API。
        # include_answer=True：请求返回搜索结果的综合回答。
        response = tavily.search(
            query=query,
            search_depth="basic",
            include_answer=True
        )

        # .get("answer")：读取 answer 字段。
        # 字段不存在时返回 None，不会产生 KeyError。
        answer = response.get("answer")

        if answer:
            return answer

        # 如果没有综合回答，就整理每一条搜索结果。
        formatted_results = []

        # 如果 results 字段不存在，使用空列表 []。
        for item in response.get("results", []):
            title = item.get("title", "无标题")
            content = item.get("content", "")

            formatted_results.append(f"- {title}：{content}")

        if not formatted_results:
            return "没有找到相关的景点推荐。"

        # 用换行符把多条结果拼成一个字符串。
        return "\n".join(formatted_results)

    except Exception as e:
        return f"错误：搜索景点失败：{e}"


# ==================================================
# 5. 工具字典：把名字和函数对应起来
# ==================================================

# 左边是字符串，右边是函数本身。
# 右边没有 ()，所以这里不会执行函数。

available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}


# ==================================================
# 6. 模型客户端：负责发送消息并获取模型回复
# ==================================================

class OpenAICompatibleClient:

    def __init__(self, model: str, api_key: str, base_url: str):
        # 创建对象时，把模型名称保存到对象中。
        self.model = model

        # 创建并保存 API 客户端。
        # 服务需要支持这里使用的 Chat Completions 接口。
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def generate(self, prompt: str, system_prompt: str) -> str:
        """把提示词发给模型，返回模型生成的文字。"""

        messages = [
            # system：角色、工具说明和输出规则。
            {"role": "system", "content": system_prompt},

            # user：用户请求，以及之前的执行记录。
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )

        # choices[0]：第一条候选回复。
        # message.content：这条回复的文字内容。
        answer = response.choices[0].message.content

        if not answer:
            raise ValueError("模型没有返回文字内容")

        return answer


# ==================================================
# 7. 创建模型客户端，准备用户请求
# ==================================================

llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

user_prompt = "请查询北京当前的天气，再根据天气推荐一个合适的旅游景点。"

# 用列表保存任务记录。
# 最开始只有用户请求，之后会加入模型回复和工具结果。
prompt_history = [
    f"用户请求：{user_prompt}"
]

print(f"用户请求：{user_prompt}")


# ==================================================
# 8. 主循环：问模型 → 执行工具 → 记录结果
# ==================================================

# 最多执行 5 轮，避免一直循环。
for i in range(5):

    print(f"\n========== 第 {i + 1} 轮 ==========")

    # ----------------------------------------------
    # 8.1 把已有记录合并成字符串，发送给模型
    # ----------------------------------------------

    full_prompt = "\n".join(prompt_history)

    try:
        llm_output = llm.generate(
            prompt=full_prompt,
            system_prompt=AGENT_SYSTEM_PROMPT
            # 对，你理解的方向对：模型根据 AGENT_SYSTEM_PROMPT 里的工具说明，决定要不要查天气、调用哪个工具。
            # 所以，提示词让模型知道“有哪些工具、该选哪个”；Python 函数里写好的代码负责“具体怎么调用 API”。 模型不需要知道天气 API 的网址，只需要输出正确的工具名称和参数。
        )
    except Exception as e:
        print(f"调用模型失败：{e}")
        break

    print(f"\n模型回复：\n{llm_output}")

    # 把模型回复加入历史记录。
    prompt_history.append(llm_output)

    # ----------------------------------------------
    # 8.2 提取 Action 这一行
    # ----------------------------------------------

    # re.MULTILINE 让 ^ 可以匹配每一行的开头。
    # (.*) 捕获 Action: 后面这一行的内容。
    action_match = re.search(
        r"^Action:[ \t]*(.*)$",
        llm_output,
        re.MULTILINE
    )

    if not action_match:
        # 没找到 Action，就记录错误，让模型下一轮重新尝试。
        prompt_history.append(
            "Observation: 没有找到 Action，请按规定格式回复。"
        )
        continue

    action_str = action_match.group(1).strip()

    # 例如，现在 action_str 是：
    # get_weather(city="北京")

    # ----------------------------------------------
    # 8.3 如果是 Finish，输出答案并结束
    # ----------------------------------------------

    finish_match = re.fullmatch(
        r"Finish\[(.*)\]",
        action_str
    )

    if finish_match:
        final_answer = finish_match.group(1)

        print(f"\n最终答案：{final_answer}")

        # break：结束整个 for 循环。
        break

    # ----------------------------------------------
    # 8.4 否则，提取工具名称和参数文字
    # ----------------------------------------------

    tool_match = re.fullmatch(
        r"(\w+)\((.*)\)",
        action_str
    )

    if not tool_match:
        prompt_history.append(
            "Observation: 工具调用格式错误，请使用函数名(参数名=\"参数值\")。"
        )
        continue

    # 第一个括号捕获工具名称。
    tool_name = tool_match.group(1)

    # 第二个括号捕获参数部分。
    args_str = tool_match.group(2)

    # 例如：
    # tool_name = "get_weather"
    # args_str = 'city="北京"'

    # ----------------------------------------------
    # 8.5 把参数文字转换成字典
    # ----------------------------------------------

    # findall 返回匹配到的参数名和参数值：
    # [('city', '北京')]
    #
    # dict 再把它转换成：
    # {'city': '北京'}
    #
    # 这是教学用的简化解析，只适合这里约定的简单双引号参数。
    kwargs = dict(
        re.findall(r'(\w+)\s*=\s*"([^"]*)"', args_str)
    )

    # ----------------------------------------------
    # 8.6 真正执行工具
    # ----------------------------------------------

    if tool_name not in available_tools:
        observation = f"错误：不存在工具 {tool_name}"

    else:
        try:
            # 先从字典中取出函数。
            tool_function = available_tools[tool_name]

            # **kwargs 将字典展开成关键字参数。
            #
            # 如果 kwargs = {"city": "北京"}
            # 下面相当于 get_weather(city="北京")
            observation = tool_function(**kwargs)

        except Exception as e:
            observation = f"错误：工具执行失败：{e}"

    # ----------------------------------------------
    # 8.7 保存工具结果，供下一轮模型参考
    # ----------------------------------------------

    observation_str = f"Observation: {observation}"

    print(f"\n{observation_str}")

    prompt_history.append(observation_str)

else:
    # 这个 else 属于 for。
    # 只有 5 轮全部执行完、没有通过 break 退出时才执行。
    print("\n已达到最大循环次数，任务尚未完成。")
    
    
    
    
# kwargs = {"city": "北京"}                  # 输入参数
# observation = get_weather(**kwargs)       # 调用工具，保存返回结果
# print(observation)                       # 输出：北京晴天，26摄氏度