# 第 7–8 天：Python 面向对象编程（OOP）
# 一、学习目标
# 知识点	   主要内容	            AI Agent 中的用途
# class	定义类	创建 Agent、Tool 等组件
# __init__	初始化方法	设置 Agent 名称、工具、对话历史
# self	引用当前对象	访问 Agent 自己的数据和方法
# 实例属性	self.name、self.memory	保存 Agent 的状态
# 实例方法	类中的函数	让 Agent 执行操作
# 继承	class SearchTool(BaseTool)	扩展不同类型的工具

name = "MyAgent"
memory = []

def add_message(message):
    memory.append(message)
    
    
    
# 这当然可以运行。

# 但是如果你需要创建两个 Agent：
# - 一个负责搜索信息
# - 一个负责数学计算
# 那么它们应该有各自的名字、记忆和工具。

# 如果一直使用全局变量，就容易把两个 Agent 的数据混在一起。

# 这时候就需要 class。

# 1. 定义一个简单的类
# class Agent:    pass


# class 用来定义一个类。

# 这里：
# - Agent 是类的名称。
# - pass 表示暂时不做任何事情。
# 我们可以基于这个类创建对象：
# agent1 = Agent()agent2 = Agent()print(type(agent1))



# 输出：
# <class '__main__.Agent'>


# agent1 和 agent2 都是 Agent 类的实例，但它们是两个不同的对象。

# 你可以把 class 理解成设计图纸，object 理解成按照图纸创建出来的具体产品。


# %%
# 三、什么是 __init__？

class Agent:

    def __init__(self, name):
    # __init__ 是初始化方法。创建实例时，Python 会自动调用它来初始化对象。
    # Python 会创建 Agent 实例，然后调用它的初始化方法，把 "SearchAgent" 传递给参数 name。
        self.name = name
        

agent1 = Agent("SearchAgent")
agent2 = Agent("CalculatorAgent")

print(agent1.name)
print(agent2.name)



# %%

class Agent:

    def __init__(self, name):
        self.name = name
        self.memory = []

    def add_message(self, message):
        self.memory.append(message)

    def get_history(self):
        return self.memory.copy()
    
agent = Agent("MyAgent")

agent.add_message("Hello")
agent.add_message("What is Python?")

print(agent.get_history())



# 为什么 add_message() 定义了两个参数：
# def add_message(self, message):

# 调用时却只传递了一个 "Hello"？

# 因为 Python 会自动把调用方法的实例传给 self。

# 所以：
# agent.add_message("Hello")

# 大致相当于：
# Agent.add_message(agent, "Hello")

# 这是 Python 面向对象编程的核心机制之一。





# %%
import json
from re import search

class SimpleAgent:

    def __init__(self, name):
        self.name = name
        self.memory = []
        self.tools = {}

    def register_tool(self, name, function):
        self.tools[name] = function
        
    

    def add_message(self, role, content):
        message = {
            "role": role,
            "content": content
        }
        self.memory.append(message)

    def execute_action(self, action_json):
        action = json.loads(action_json)

        tool_name = action["tool"]
        arguments = action["arguments"]

        tool_function = self.tools[tool_name]

        result = tool_function(**arguments)

        return result
    

def calculator(a, b):
    return a + b


def search(query):
    return f"Searching for {query}"


agent = SimpleAgent("MathAgent")

agent.register_tool("calculator", calculator)

# self.tools[name] = function
# self.tools["calculator"] = calculator


# 现在 Agent 的工具字典变成：
# {
#     "calculator": calculator
# }

agent.register_tool("search", search)


print(agent.tools)



# {'calculator': <function calculator at 0x...>} 为什么运行出来是这个
# 因为 你保存到字典里的不是函数的执行结果，而是函数本身（Function Object，函数对象）。
# 正是因为我们之前用 def 定义了 calculator 和 search 两个函数，所以 Python 知道它们是函数对象。


llm_action = """
{
    "tool": "calculator",
    "arguments": {
        "a": 15,
        "b": 8
    }
}
"""






result = agent.execute_action(llm_action)

print(result)
# %%


# %%
# 继承 inheritance

class Agent:

    def __init__(self, name):
        self.name = name

    def introduce(self):
        print(f"I am {self.name}")


class SearchAgent(Agent):
    # 括号里的 Agent 表示：SearchAgent 继承 Agent 类。
    # 因为 Python 会沿着继承关系寻找 __init__()。
    # 它发现子类没有定义，就使用父类的：
    # 因此，创建对象后：
    # print(agent.name)
    # 
    # 输出
    # GoogleAgent
    
    


    def search(self, query):
        return f"Searching for {query}"
    

agent = SearchAgent("GoogleAgent")

agent.introduce()


# 三、为什么 agent.introduce() 可以运行？
# agent.introduce()


# Python 会按照下面的顺序查找：
# 1. 先看 SearchAgent 有没有 introduce()。
# 2. 没有，就去父类 Agent 中寻找。
# 3. 找到后执行父类定义的 introduce()。
# 所以输出：
# I am GoogleAgent



print(agent.search("Python AI Agent"))





# 四、如果子类也定义了 introduce() 呢？
# 这就是继承中另一个重要概念：方法重写（Method Overriding）。
# 因为 Python 会优先使用子类自己定义的方法。

# 即使父类也有同名的 introduce()，子类的方法也会覆盖继承来的实现。



# %%



##########################################################

# %%
# 第一步：只有一个类
class Agent:
    def __init__(self, name):
        self.name = name
        

agent = Agent("Alice")
print(agent.name)      


# %%

# 第二步：现在加一个子类
class Agent:
    def __init__(self, name):
        self.name = name


class SearchAgent(Agent): # inherit from Agent
    pass

agent = SearchAgent("Alice")
print(agent.name)

# 为什么？

# 因为 SearchAgent 没有自己的 __init__()，所以直接继承了父类的 __init__()。
# 到这里，完全不需要 super()。


# %%

#### 第三步：子类想增加一个属性
# 现在我们不仅想保存 name，还想保存 engine。

class Agent:
    def __init__(self, name):
        self.name = name


class SearchAgent(Agent): # inherit from Agent
    def __init__(self, name, engine):
        self.engine = engine

agent = SearchAgent("Alice", "Google")

print(agent.engine)  # Google
print(agent.name)    # 报错！


# 为什么 name 没了？

# 因为我们在 SearchAgent 里面重新定义了 __init__()。

# Python 现在执行子类的初始化方法，不会自动再运行父类的初始化方法。

# 所以没有执行：
# self.name = name



# 第四步：super() 出场了

# %%

class Agent:
    def __init__(self, name):
        self.name = name


class SearchAgent(Agent):
    def __init__(self, name, engine):
        super().__init__(name)
        
# 它的意思是：
# 去执行父类的 __init__()，把 name 也初始化好。
        self.engine = engine
        

# 所以：
# agent = SearchAgent("Alice", "Google")

# 实际上会依次执行：
# ① 先执行父类的代码

# super().__init__(name)

# 也就是执行：
# self.name = "Alice"


# ② 再执行子类的代码

# self.engine = "Google"

# ③ 最终 agent 有两个属性

# agent.name = "Alice"
# agent.engine = "Google"