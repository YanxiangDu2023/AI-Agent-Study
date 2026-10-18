
# %%

from ast import Dict


messages = [
    {"role": "system", "content": "You are an AI agent."},
    {"role": "user", "content": "What is 10 + 20?"},
    {"role": "assistant", "content": "I will calculate it."}
]

messages.append({
    "role": "tool",
    "content": "30"
})

########### str
user_input = "What is 10 + 20?"
system_prompt = "You are a helpful AI assistant."

print(type(user_input))
# <class 'str'>



###### 字符串的拼接
system_prompt = "You are an AI assistant."
user_input = "What is Python?"

full_prompt = system_prompt + "\n" + user_input

print(full_prompt)



# %%
# 1.2 f-string：动态构建 Prompt

user_input = "What is 10 + 20?"
tool_names = "calculator, web_search"

prompt = f"""
You are an AI Agent.

Available tools:
{tool_names}

User Question:
{user_input}

Think step by step and decide whether to use a tool.
"""

print(prompt)




# %%
###### 字符串索引和切片

action = "calculator"

print(action[0])    # c
print(action[1])    # a
print(action[-1])   # r
print(action[:4])   # calc
print(action[4:])   # ulator




# %%
# 1.4 字符串常用方法：.strip()、.split()、.replace()

# .strip()：去除首尾空白

llm_output = "   Action: calculator   \n"

clean_output = llm_output.strip()

print(clean_output)
# Action: calculator



# %%

### .split()：拆分字符串

action = "calculator:10,20"

parts = action.split(":")

print(parts)
# ['calculator', '10,20']

tool_name = parts[0]
arguments = parts[1].split(",")

print(tool_name)  # calculator
print(arguments)  # ['10', '20']




# %%

## .replace()：替换字符串内容
response = "Action: calculator"

new_response = response.replace("Action:", "")

print(new_response.strip())
# calculator




# %%

# 1.5 字符串检查：.startswith() 与 in

if action_str.startswith("Finish"):
    print("Agent finished")
    
action1 = "Finish(answer='30')"
action2 = "calculator(a=10, b=20)"

print(action1.startswith("Finish"))  # True
print(action2.startswith("Finish"))  # False




# %%

# 2.1 创建列表

messages = [
    "Hello",
    "How are you?",
    "I'm fine."
]

print(messages[0])   # Hello
print(messages[-1])  # I'm fine.



# 2.2 .append()：Agent 如何保存历史消息？

messages = []

messages.append("Hello")
messages.append("How are you?")
messages.append("I'm fine.")

print(messages)

history = []

user_input = "What is 10 + 20?"
history.append(user_input)

llm_response = "The answer is 30."
history.append(llm_response)

result = history.append("New message")

print(result)  # None




# 2.3 .append() 与 .extend() 的区别

history = ["Message 1"]
history.append(["Message 2", "Message 3"])
print(history)


# [
#     "Message 1",
#     ["Message 2", "Message 3"]
# ]


# history = ["Message 1"]
# history.extend(["Message 2", "Message 3"])
# print(history)


# [
#     "Message 1",
#     "Message 2",
#     "Message 3"
# ]




# 2.4 List 的切片：控制 Agent 的上下文窗口

messages = [
    "message_1",
    "message_2",
    "message_3",
    "message_4",
    "message_5"
]

recent = messages[-3:]

print(recent)

# ["message_3", "message_4", "message_5"]





# 2.5 for 循环：遍历对话历史
history = [
    "User: Hello",
    "Assistant: Hi",
    "User: What is Python?"
]

for message in history:
    print(message)


# 你还可以使用 enumerate() 获取索引：
for index, message in enumerate(history):
    print(index, message)
    

# 0 User: Hello
# 1 Assistant: Hi
# 2 User: What is Python?   




# List comprehension：列表推导式
tools = ["search", "calculator", "weather"]

formatted_tools = [tool.upper() for tool in tools]

print(formatted_tools)
# ['SEARCH', 'CALCULATOR', 'WEATHER']




# 过滤数据：
numbers = [10, 20, 30, 40]

filtered = [n for n in numbers if n > 20]

print(filtered)
# [30, 40]






# 3.1 创建 Dictionary

message = {
    "role": "user",
    "content": "What is Python?"
}


print(message["role"])
# user

print(message["content"])
# What is Python?


print(message.get("role"))
# user

print(message.get("name"))
# None


# message["name"]  # KeyError
# message.get("name")  # None
# 当键不存在时，[] 会抛出 KeyError，.get() 默认返回 None。



# 修改和增加字段
# message["content"] = "Hello Agent!"
# message["timestamp"] = "2026-10-17"
# {
#     "role": "user",
#     "content": "Hello Agent!",
#     "timestamp": "2026-10-17"
# }




# 3.2 Agent 最重要的数据结构：List of Dicts

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "What is 10 + 20?"
    },
    {
        "role": "assistant",
        "content": "The answer is 30."
    }
]

print(messages[0])

# {
#     "role": "system",
#     "content": "You are a helpful assistant."
# }



# 循环读取user消息
# for message in messages:
#     if message["role"] == "user":
#         print(message["content"])




# %%
# 3.3 Nested Dict：嵌套字典

tool_call = {
    "tool_name": "calculator",
    "arguments": {
        "a": 10,
        "b": 20
    }
}


print(tool_call["tool_name"])
# calculator

print(tool_call["arguments"])
# {'a': 10, 'b': 20}

print(tool_call["arguments"]["a"])
# 10



# %%
# 3.4 字典 + 函数：工具调用的核心

def calculator(a, b):
    return a + b

def greet(name):
    return f"Hello, {name}!"

tools = {
    "calculator": calculator,
    "greet": greet
}


print(tools["calculator"](10, 20))
# 30

tool_name = "calculator"

arguments = {
    "a": 10,
    "b": 20
}

result = tools[tool_name](**arguments)

print(result)
# 30

tools[tool_name](**arguments)
# %%

# 可以拆解为：
# 1. tools[tool_name]：找到要调用的 Python 函数。
# 2. **arguments：把字典展开为关键字参数。
# 3. (...)：执行函数并返回结果。



# %%

class ConversationManager:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        message = {
            "role": role,
            "content": content
        }
        self.messages.append(message)

    def get_history(self):
        return self.messages.copy()

    def get_recent_messages(self, n=3):
        return self.messages[-n:] if n > 0 else []

    def get_user_messages(self):
        return [
            msg["content"]
            for msg in self.messages
            if msg["role"] == "user"
        ]
        
# 1. 执行 agent_memory = ConversationManager() 时，哪个方法会自动运行？
# 创建对象时 Python 会调用 __init__ 完成初始化。


# Create a conversation manager
agent_memory = ConversationManager()

agent_memory.add_message(
    "system", "You are an AI assistant."
)

agent_memory.add_message(
    "user", "What is Python?"
)

agent_memory.add_message(
    "assistant", "Python is a programming language."
)

agent_memory.add_message(
    "user", "Can it be used for AI Agents?"
)

agent_memory.add_message(
    "assistant", "Yes, Python is widely used for AI Agents."
)

print("Recent messages:")
print(agent_memory.get_recent_messages(2))

print("\nUser questions:")
print(agent_memory.get_user_messages())

# %%
