from asyncio import tools
import json
import re


# Python for AI Agent — 第三阶段：正则表达式与 JSON

# 今天我们学习 AI Agent 开发中非常实用的两个知识点：
# - 正则表达式（Regular Expressions / Regex）：从 LLM 生成的文本中提取指定信息。
# - JSON（JavaScript Object Notation）：把 LLM 返回的结构化数据转换成 Python 可以使用的字典。
# 你之前已经学习过 def、return、**kwargs、函数对象和 Tool Registry。今天我们要把这些知识串联起来，完成一个真正的 Action Parser（行动解析器）。


# 一、先理解为什么 Agent 需要解析 Action
# 假设你向 LLM 提问：
# What is 15 multiplied by 8?

# 在传统的文本式 ReAct Agent 中，我们可能要求 LLM 按照下面的格式回答：
# Thought: I need to calculate 15 multiplied by 8.
# Action: calculator(a=15, b=8, operation="multiply")


# 但是对于 Python 来说，上面只是一个普通字符串。
# llm_output = '''Thought: I need to calculate 15 multiplied by 8.Action: calculator(a=15, b=8, operation="multiply")'''



# 我们真正希望得到：
# tool_name = "calculator"kwargs = {    "a": 15,    "b": 8,    "operation": "multiply"}



# 这样才能调用：
# result = tools[tool_name](**kwargs)

# 第一课：re.search() 是什么？
# 1.1 为什么不用普通字符串操作？
# 假设：
# llm_output = "Thought: I need a tool. Action: calculator(10, 20)"



# 我们希望提取：
# calculator(10, 20)


# 当然可以使用 .split()，但如果输出格式变得复杂，例如：
# Thought: I need to calculate.
# Action: calculator(10, 20)
# Observation: 30


# 就需要更灵活的文本匹配方式。

# 这时候可以使用 Python 内置的 re 模块。
# import re


# re 是 Regular Expressions（正则表达式）的缩写。


# %%
# 1.2 第一个 re.search() 案例

import re

text = "The result is 120."

match = re.search(r"\d+", text)

print(match.group())





# %%


# re.search(r"\d+", text)


# - re.search()：在字符串中寻找第一个匹配正则规则的位置。
# - r"..."：原始字符串（raw string）。
# - \d：匹配数字字符。
# - +：表示前面的模式出现一次或多次。
# - text：要搜索的字符串。

text = "Hello World"

match = re.search(r"\d+", text)

print(match)
# None

if match:
    print(match.group())
else:
    print("No match found")
    
    
#  %%
# 1.3 .group() 的作用

text = "Action: calculator"

match = re.search(r"Action: \w+", text)

print(match.group())
# Action: calculator

# .group() 默认等价于 .group(0)，获取整个匹配结果。

# 我们等一下会学习 .group(1)，它可以提取括号里面的部分。


###########################################################
# 第二课：正则表达式最重要的语法
# 你不需要一开始就记住所有 Regex 语法。

# 对于 AI Agent，先掌握下面这些就够用了。
# 正则符号	含义	示例
# \d	数字字符	1、9
# \w	单词字符	a、B、9、_
# \s	空白字符	空格、换行
# .	任意字符（默认不包括换行）	a、8、?
# *	前面的模式出现 0 次或多次	a*
# +	前面的模式出现 1 次或多次	\d+
# ?	前面的模式出现 0 次或 1 次	a?
# ()	分组和捕获	(\w+)
# ^	匹配字符串开头	^Action
# $	匹配字符串末尾	Finish$


# %%
# 2.1 \w+ 是什么意思？

text = "Action: calculator"

match = re.search(r"\w+", text)

print(match.group())
# Action
# 为什么不是 calculator？
# 因为 re.search() 默认寻找第一个符合要求的部分。
# 字符串中的 Action 已经符合 \w+。
# 如果想匹配 calculator



match = re.search(r"Action: (\w+)", text)

print(match.group(1))
# calculator



# 2.2 捕获组（Capturing Groups）

text = "Action: calculator"

match = re.search(r"Action: (\w+)", text)

print(match.group(0))
print(match.group(1))

# Action: calculator
# calculator

# r"Action: (\w+)"

# Action: ：需要匹配的固定文字。
# (\w+)：第一个捕获组。
# .group(0)：返回整个正则表达式匹配到的内容，不管有没有括号。
# .group(1)：只返回第一对 () 捕获到的内容。

# %%
text = "Action: calculator(a=15, b=8)"

match = re.search(r"Action: (\w+)", text)

# Action: (\w+)
# │       │   │
# │       └───┘
# │       第一个捕获组
# │
# └── 固定匹配的文字

print(match.group(0))
# Action: calculator

print(match.group(1))
# calculator




# %%


action = "calculator(a=15, b=8)"

match = re.search(r"(\w+)\(", action)

tool_name = match.group(1)

print(tool_name)
# calculator

print(match.group(0))
# calculator( 这是因为正则表达式中有一个 \(，表示匹配左括号 (，所以 .group(0) 返回了整个匹配结果 calculator(。

print(match.group(1))
# calculator 这是



# # 注意
# 1. r"Action: (\w+)"
# 意思是：
# - 先找到 Action: 。
# - (\w+) 捕获后面连续的字母、数字或下划线。
# - 不会捕获后面的所有内容。
# 例如：

# text = "Action: calculator(a=15, b=8)"

# match = re.search(r"Action: (\w+)", text)

# print(match.group(0))  # Action: calculator
# print(match.group(1))  # calculator


# 2. r"Action: (\w+)\("
# 意思是：
# - 先找到 Action: 。
# - (\w+) 捕获 calculator。
# - \( 要求后面紧跟一个真正的左括号 (。
# - 左括号必须存在才能匹配成功，但不会进入 group(1)。

# text = "Action: calculator(a=15, b=8)"

# match = re.search(r"Action: (\w+)\(", text)

# print(match.group(0))  # Action: calculator(
# print(match.group(1))  # calculator

# 第二种写法里的 \( 就是要求找到真正的左括号，并不要求把它捕获下来。




# 第二部分：re.findall()
# 1. re.search() 和 re.findall() 有什么区别？
# 先看一个例子。

# 假设 AI Agent 收到了 LLM 返回的内容：


# text = """
# Thought: I need to calculate two numbers.
# Action: calculator
# Parameter: a=15
# Parameter: b=8
# """



result = re.search(r"Parameter: (\w+)=(\d+)", text)

print(result.group(0))
print(result.group(1))
print(result.group(2))


# Parameter: a=15
# a
# 15


# 为什么只有 a=15？
# 因为 re.search() 只返回第一个匹配结果。
# 即使后面还有 b=8，它也不会继续寻找。


# %%

# 1.2 使用 re.findall()

result = re.findall(r"Parameter: (\w+)=(\d+)", text)


# [('a', '15'), ('b', '8')]

# 区别总结：
# 方法	            用途	                返回值
# re.search()	找到第一个匹配	Match 对象，找不到返回 None
# re.findall()	找到所有匹配	列表 list




# 2. 为什么 findall 返回的是 tuple？
# 我们拆开看：
# r"Parameter: (\w+)=(\d+)"



# 这里有两个捕获组。

# - (\w+)：匹配连续的字母、数字或下划线，例如 a、b。
# - (\d+)：匹配连续的数字，例如 15、8。
# 每找到一个匹配项，Python 就将两个捕获组组合成一个 tuple：

# ("a", "15")
# ("b", "8")

# 最终把所有 tuple 放进一个列表：

# [
#     ("a", "15"),
#     ("b", "8")
# ]



# 3. 为什么 Agent 代码经常使用 dict(re.findall())？
# 之前你看到过：

# %%
kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))


args_str = 'city="Stockholm", country="Sweden"'

result = re.findall(r'(\w+)="([^"]*)"', args_str)

print(result)

# [
#     ("city", "Stockholm"),
#     ("country", "Sweden")
# ]

# kwargs = dict(result)

# print(kwargs)


# 输出：
# {    "city": "Stockholm",    "country": "Sweden"}

# 为什么可以直接使用 dict()？

# 因为 Python 支持把一组由两个元素组成的 tuple 转换成字典：


pairs = [
    ("name", "Alice"),
    ("age", "25")
]

person = dict(pairs)

print(person)


# result

# {
#     "name": "Alice",
#     "age": "25"
# }



# 这在 AI Agent 中特别有用，因为我们经常需要把 LLM 生成的参数文本变成可以传递给 Python 函数的字典。

# 不过，这种正则表达式只适合简单的双引号字符串参数。如果参数包含嵌套 JSON、复杂转义字符或其他数据类型，就需要更可靠的解析方式。


# 第二部分：JSON 基础
# JSON 是 AI Agent 开发中非常重要的数据格式。

# 假设我们让 LLM 调用一个工具：


# {
#     "tool": "calculator",
#     "arguments": {
#         "a": 15,
#         "b": 8
#     }
# }


# 你会发现，它的结构非常像 Python 的字典。
# 但是 JSON 和 Python dict 并不是一回事。


# 4. 什么是 JSON？
# JSON 的全称是 JavaScript Object Notation，是一种用于数据交换的文本格式。

# 例如，LLM 可能返回：
# llm_output = '{"tool": "calculator", "arguments": {"a": 15, "b": 8}}'


# 注意最外层的引号。

# 此时 llm_output 是一个 Python 字符串。
# print(type(llm_output))


# 结果：
# <class 'str'>

# 虽然字符串里面看起来像字典，但你不能直接这样写：
# llm_output["tool"]  # TypeError


# 因为字符串不能用 "tool" 作为索引。

# 那怎样把 JSON 字符串变成 Python 字典？

# 这就是 json.loads() 的作用。


# 5. json.loads()：JSON 字符串转换成 Python 对象


# %%

llm_output = '{"tool": "calculator", "arguments": {"a": 15, "b": 8}}'

data = json.loads(llm_output)

print(data)
print(type(data))



# {
#     'tool': 'calculator',
#     'arguments': {'a': 15, 'b': 8}
# }

# <class 'dict'>

tool_name = data["tool"]

arguments = data["arguments"]

print(tool_name)
print(arguments)


# calculator
# {'a': 15, 'b': 8}


a = arguments["a"]
b = arguments["b"]

print(a + b)


# %%

# 6. json.dumps()：Python 对象转换成 JSON 字符串

import json

result = {
    "tool": "calculator",
    "result": 23,
    "success": True
}


json_str = json.dumps(result)

print(json_str)
print(type(json_str))
# %%


# json.dumps() 会帮我们完成这些转换。

# 这对于 AI Agent 非常重要，因为工具执行完之后，我们经常需要把 Python 结果序列化，再传给 LLM 或发送给 API。
# 7. loads 和 dumps 对照
# 函数	转换方向	常见用途
# json.loads()	JSON 字符串 → Python 对象	解析 LLM 返回的工具参数
# json.dumps()	Python 对象 → JSON 字符串	将工具结果发送给 LLM/API
# 需要注意：loads() 不一定返回字典，如果 JSON 顶层是数组，就会得到 Python 列表。


###############################
# practice

# %%
# 假设 LLM 返回：
llm_output = """
Thought: I need to calculate the sum.
Action: {"tool": "calculator", "arguments": {"a": 15, "b": 8}}
"""

# 我们的目标是让 Python 自动识别工具、解析参数并执行计算。

import re
import json

match = re.search(r"Action: (.*)", llm_output)

# 这里 .* 会匹配同一行中 Action:  后面的内容。

action_str = match.group(1)

print(action_str)
# %%


# 第二步：把 JSON 字符串变成字典

action = json.loads(action_str)

tool_name = action["tool"]
arguments = action["arguments"]


# tool_name = "calculator"

# arguments = {
#     "a": 15,
#     "b": 8
# }



# 第三步：真正调用 Python 工具

def calculator(a, b):
    return a + b

tools = {
    "calculator": calculator
}

tool_function = tools[tool_name]

result = tool_function(**arguments)

print(result)



# 还记得我们之前学过的 **kwargs 吗？
# 这里：
# tool_function(**arguments)

# 就相当于：
# calculator(a=15, b=8)

# 这就是一个最简单的 AI Agent 工具调用过程。