
# Python for AI Agent — 第二阶段：函数、参数与工具调用
# Day 3–4
# Python 基础 → Agent 实战
# 这一阶段非常重要，因为你即将学习 AI Agent 是如何调用 Python 工具（Tool Calling）的。

# 你之前学过的 str、list、dict 主要负责存储和组织数据，而这一阶段要学习的是：如何让 Agent 根据 LLM 的决策，选择并执行不同的 Python 函数。



# 第二课：函数参数（Parameters & Arguments）
# 先理解两个英文术语：
# - Parameter（形参）：定义函数时写的变量。
# - Argument（实参）：真正调用函数时传入的数据。
# def calculator(a, b):  # a, b 是 Parameters    return a + bcalculator(10, 20)      # 10, 20 是 Arguments



# 2.1 Positional Arguments：位置参数
# def subtract(a, b):    
#   return a - b

# print(subtract(10, 3))  # 7
# print(subtract(3, 10))  # -7



# 位置参数的顺序很重要。
# subtract(10, 3) 意思是：
# a = 10. b = 3



# 2.2 Keyword Arguments：关键字参数
# 你也可以明确指定参数名称：
# print(subtract(a=10, b=3))# 7
# print(subtract(b=3, a=10))# 7



# 使用关键字参数时，参数的排列顺序通常不会影响结果。
# 这对 AI Agent 非常重要，因为 LLM 的结构化工具调用结果通常会提供参数名称和参数值。
# 例如：
# arguments = {    "a": 10,    "b": 3}



# Agent 可以根据这些键名把参数传给工具。

# 2.3 Default Parameters：默认参数
# def search(query, max_results=5):   
#    return f"Searching for {query}, limit: {max_results}"

# print(search("AI Agents"))
# # Searching for AI Agents, limit: 5

# print(search("AI Agents", 10))
# # Searching for AI Agents, limit: 10



# max_results=5 表示这个参数是可选的，不传时使用默认值 5。
# 未来定义搜索工具时，你经常会见到：
# def web_search(query: str, max_results: int = 5):    ...



# 这里的 : str、: int 是类型注解，后面会详细学习。


# %%

# 假设一个计算工具不只是要计算两个数，而是可以计算任意数量的数字。
# 例如：
# calculator(10, 20, 30, 40)



# 我们可以使用 *args。



def add(*args):
    print(args)
    return sum(args)

result = add(10, 20, 30)

print(result)


# (10, 20, 30)
# 60
# 为什么输出是 (10, 20, 30) 而不是 [10, 20, 30]？
# 因为在函数定义中，*args 会将接收到的位置参数收集成 Tuple（元组）。
# Tuple 和 List 有些相似，但是 Tuple 通常不能直接修改其中的元素。




# 3.2 *args 中的星号是什么？

# 关键其实是 *，而不是 args 这个名字。
# def add(*numbers):    
#     return sum(numbers)

# 同样可以正常运行：
# print(add(1, 2, 3, 4))# 10

# 但 Python 社区习惯使用 *args。



# 3.3 * 也可以用来解包
numbers = [10, 20, 30]

print(add(*numbers))
# 60

# print(add(10, 20, 30))


# 两种情况需要区分：
# 写法	           含义
# def add(*args)	收集多个位置参数
# add(*numbers)	解包 List 或 Tuple 并传递参数



# 第四课：**kwargs — 任意数量的关键字参数
# 这是你学习 AI Agent 工具调用时最应该掌握的内容。
# 4.1 基本语法

# %%
def show_info(**kwargs):
    print(kwargs)

show_info(
    name="Alice",
    age=25,
    city="Stockholm"
)


# {
#     "name": "Alice",
#     "age": 25,
#     "city": "Stockholm"
# }

# 你会发现，**kwargs 会把传入的关键字参数收集成一个 Dict。
# 记住：
# - *args 收集成 Tuple。
# - **kwargs 收集成 Dict。



# %%
# 4.2 为什么 Agent 需要 **kwargs？
# 假设你有一个 calculator 工具：

def calculator(a, b):
    return a + b


# LLM 决定调用这个工具，并提供了参数：

tool_name = "calculator"

arguments = {
    "a": 10,
    "b": 20
}


result = calculator(**arguments)

print(result)
# 30


# 4.3 **kwargs 的两种用法
# 第一种：在函数定义时收集关键字参数。
# def example(**kwargs):    
#.  print(kwargs)
# example(a=10, b=20)



# 第二种：在函数调用时解包字典。
# def add(a, b):    
#   return a + b
# 
# params = {"a": 10, "b": 20}
# add(**params)



# 这两个场景中的 ** 方向相反：一个是收集，一个是展开。
# 特别注意：被调用的函数不一定要定义 **kwargs。
# 只要字典中的键与函数参数相匹配，就可以使用字典解包。



# 4.4 参数不匹配会怎样？
# def calculator(a, b):    
#   return a + b
# 
# kwargs = { "a": 10,  
#    "c": 20}
# 
# calculator(**kwargs)



# 这会产生 TypeError，因为 calculator() 没有名为 c 的参数，而且缺少必需参数 b。
# 这也是为什么真实 Agent 需要验证 LLM 生成的工具参数。



# 第五课：函数对象（Function Objects）
# 这一课是理解 Agent Tool Registry 的关键。

# 5.1 Python 中，函数也是对象
# 看这个代码：
# def calculator(a, b):    return a + b


# 通常这样调用：
# calculator(10, 20)


# 但是你也可以把函数赋值给变量：
# my_tool = calculatorprint(my_tool(10, 20))# 30


# 为什么可以这样？
# 因为 Python 的函数是 First-Class Objects（一等对象）。
# 它们可以像其他对象一样：
# - 被赋值给变量。
# - 存入 List 或 Dict。
# - 作为参数传给其他函数。
# - 从其他函数中返回。



# 5.2 calculator 与 calculator() 的区别
# 这是一个非常重要的知识点。
# calculator


# 代表函数对象本身。
# 而：
# calculator(10, 20)


# 意味着执行该函数，并获得返回值。
# 比如：
# tools = {    "calculator": calculator}


# 字典保存的是一个函数对象。
# 而：
# tools = {    "calculator": calculator(10, 20)}

# 字典保存的是函数执行后的结果 30。
# 我们希望 Agent 需要计算时才执行工具，因此通常应该保存函数对象，而不是提前调用函数。



# 5.3 函数可以作为参数


def execute_tool(tool, a, b):
    return tool(a, b)

def add(a, b):
    return a + b

result = execute_tool(add, 10, 20)

print(result)
# 30



# %%
# 第六课：字典映射（Tool Registry）
# 现在开始进入真正的 AI Agent 开发逻辑。
# 假设我们有三个工具：

def calculator(a, b):
    return a + b

def search(query):
    return f"Search results for: {query}"

def get_weather(city):
    return f"Weather in {city}: Sunny"




# 暂时不用连接真实 API，这三个函数都是模拟工具。
# 6.1 最原始的 Tool Calling
# 如果 Agent 只有三个工具，我们可以使用：

tool_name = "search"

if tool_name == "calculator":
    result = calculator(10, 20)

elif tool_name == "search":
    result = search("AI Agent")

elif tool_name == "get_weather":
    result = get_weather("Stockholm")



# 但这样存在两个问题：
# 第一，每增加一个工具，就要增加新的 if/elif。
# 第二，每个工具的参数不同，容易出现大量重复代码。
# 因此我们可以使用 Dict 映射工具名称和函数。




# 6.2 创建 Tool Registry


tools = {
    "calculator": calculator,
    "search": search,
    "get_weather": get_weather
}



# 这个字典就是一个简单的 Tool Registry（工具注册表）。
# Key	Value
# "calculator"	calculator 函数对象
# "search"	search 函数对象
# "get_weather"	get_weather 函数对象
# 使用：
# tool_name = "search"tool_function = tools[tool_name]result = tool_function("AI Agent")print(result)


tool_name = "search"

tool_function = tools[tool_name]

result = tool_function("AI Agent")


# def calculator(a, b):
#     return a + b

# def search(query):
#     return f"Search results for: {query}"

# def get_weather(city):
#     return f"Weather in {city}: Sunny"


print(result)


# 输出：
# Search results for: AI Agent


# 这里的关键是：
# tools[tool_name]
# 会根据工具名称，从字典中获取对应的函数对象。



 # %%
# 6.3 将 Tool Registry 和 **kwargs 结合
tools = {
    "calculator": calculator,
    "search": search,
    "get_weather": get_weather
}


tool_call = {
    "tool": "calculator",
    "arguments": {
        "a": 10,
        "b": 20
    }
}


tool_name = tool_call["tool"]
kwargs = tool_call["arguments"]


tool_function = tools[tool_name]

result = tool_function(**kwargs)

print(result)
# 30


# 进一步简化 result = tools[tool_name](**kwargs)


# %%
# 1. Define tools

def calculator(a, b, operation="add"):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero"
        return a / b
    else:
        return "Error: Unknown operation"


def search(query):
    knowledge_base = {
        "python": "Python is a programming language.",
        "agent": "AI Agents can use tools to complete tasks.",
        "llm": "LLM stands for Large Language Model."
    }

    return knowledge_base.get(
        query.lower(),
        "No matching results found."
    )


def get_weather(city):
    fake_weather = {
        "stockholm": "Cloudy, 12°C",
        "london": "Rainy, 15°C",
        "paris": "Sunny, 20°C"
    }

    return fake_weather.get(
        city.lower(),
        "Weather data unavailable."
    )


# 2. Tool Registry

tools = {
    "calculator": calculator,
    "search": search,
    "get_weather": get_weather
}


# 3. Tool Executor

def execute_tool(tool_name, **kwargs):
    if tool_name not in tools:
        return f"Error: Unknown tool '{tool_name}'"

    tool_function = tools[tool_name]

    try:
        result = tool_function(**kwargs)
        return result
    except (TypeError, ValueError, ZeroDivisionError) as e:
        return f"Tool execution error: {e}"


# 4. Simulated LLM Tool Calls

tool_calls = [
    {
        "tool": "calculator",
        "arguments": {
            "a": 10,
            "b": 20,
            "operation": "add"
        }
    },
    {
        "tool": "search",
        "arguments": {
            "query": "agent"
        }
    },
    {
        "tool": "get_weather",
        "arguments": {
            "city": "Stockholm"
        }
    }
]


# 5. Execute

for call in tool_calls:
    tool_name = call["tool"]
    arguments = call["arguments"]

    result = execute_tool(
        tool_name,
        **arguments
    )

    print(f"Tool: {tool_name}")
    print(f"Observation: {result}")
    print("-" * 30)
