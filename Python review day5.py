# 第一课：HTTP 到底是什么？

# 1. 先理解一个真实场景
# 假设你打开浏览器，访问：

# https://api.github.com/users/octocat

# 浏览器会向 GitHub 的服务器发送一个请求。

# GitHub 收到请求后，会返回用户资料。

# 这里有三个核心概念：
# - Client（客户端）：发送请求的一方，可以是浏览器，也可以是 Python 程序。
# - Server（服务器）：接收请求并处理它的系统。
# - HTTP（Hypertext Transfer Protocol）：规定客户端和服务器如何交换请求与响应的协议。
# 你可以把 HTTP 理解成一套通信规则。

# 它规定了：客户端如何描述自己想要什么，以及服务器如何说明处理结果。


from email.policy import HTTP
from gettext import install


# 4. HTTP 方法：GET 和 POST
# 这是 AI Agent 开发中最常用的两种 HTTP 方法。
# GET

# 获取资源

# 例如，让天气 API 返回 Stockholm 的天气，或者从 GitHub API 获取用户资料。

# POST

# 提交数据供服务器处理

# 例如，把一段 Prompt 发送给 LLM API，并获取模型生成的回答。

# 来看两个 Python 示例。现在不要求你记住 requests 的所有语法，只需要看懂它们的作用。



# GET 请求：
import pip
import requests

response = requests.get(
    "https://api.github.com/users/octocat"
)


# POST 请求（示意）：
import requests

response = requests.post(
    "https://example.com/api/chat",
    json={
        "message": "Hello, AI Agent!"
    }
)


# 5. HTTP Status Code（状态码）
# 当 Agent 调用外部 API 时，不是每一次都能成功。

# 因此，我们必须学会判断 HTTP 状态码。
# 状态码	含义	Agent 应该怎么处理
# 200	OK，请求成功	处理返回数据
# 201	Created，资源创建成功	确认创建结果
# 400	Bad Request，请求有问题	检查请求参数
# 401	Unauthorized，认证失败	检查 API Key
# 403	Forbidden，禁止访问	检查访问权限
# 404	Not Found，资源不存在	检查 URL 或资源
# 429	Too Many Requests，请求过多	根据限流信息等待重试
# 500	Internal Server Error	记录错误，必要时重试
# 503	Service Unavailable，服务不可用	稍后重试
# 你可以先记住这个规律：
# - 2xx：通常代表成功。
# - 4xx：通常代表客户端请求存在问题或不被允许。
# - 5xx：通常代表服务器处理失败。



# %%
###################### 第二课：REST API 与 Endpoint

# requests 是 Python 中常用的第三方 HTTP 客户端库。

import requests

url = "https://api.github.com/users/octocat"

response = requests.get(url, timeout=10)

print(response.status_code)


# 2. 把 JSON 转换成 Python 字典
# 继续：

import requests

url = "https://api.github.com/users/octocat"

response = requests.get(url, timeout=10)

response.raise_for_status()

data = response.json()

print(data["login"])
print(data["id"])

# 这里出现两个新方法。

# response.raise_for_status()

# 检查 HTTP 状态码。如果是 4xx 或 5xx，会抛出 HTTPError 异常。

# response.json()

# 尝试把响应体中的 JSON 解析为 Python 对象。

# 比如返回：
# {
#   "login": "octocat",
#   "id": 583231,
#   "type": "User"
# }


# 经过：
# data = response.json()

# data 就是 Python 字典。

# 你可以使用之前学过的字典知识：
# data["login"]data.get("login")data.get("company", "Unknown")

# 不过要注意：response.json() 不一定返回字典，也可能返回列表、字符串或其他合法 JSON 类型，取决于 API 的响应。



# %%
##############################################################

# 3. GET 参数的完整示例
# 我们用一个不要求 API Key 的 Open-Meteo 天气 API。

import requests

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 59.33,
    "longitude": 18.06,
    "current": "temperature_2m"
}

response = requests.get(
    url,
    params=params,
    timeout=10
)

response.raise_for_status()

data = response.json()

temperature = data["current"]["temperature_2m"]

print(f"Stockholm: {temperature}°C")

# 最重要的是这部分：
# data["current"]["temperature_2m"]

# 它为什么有两个方括号？

# 因为返回的 JSON 中存在嵌套结构：
# {
#   "current": {
#     "temperature_2m": 8.5
#   }
# }

# 第一次：
# data["current"]

# 得到：
# {"temperature_2m": 8.5}

# 第二次：
# data["current"]["temperature_2m"]

# 得到：
# 8.5

# 这里的 8.5 只是示例数据，不代表 Stockholm 当前的真实气温。
















####### 第六课：装饰器 Decorator #############################

# %%
def hello():
    print("Hello")

func = hello

func()

# 没有括号，因此没有执行 hello()。
# 而是让 func 引用这个函数。



# %%
##### 2. 函数可以作为参数传给另一个函数

def hello():
    print("Hello")

def execute(func):
    func()

execute(hello)


# 注意：
# execute(hello)

# 把 hello 函数本身传进去。

# 如果写：
# execute(hello())

# 就会先执行 hello()，再把其返回值传给 execute。这是不同的行为。


# %%
# 3. 函数内部还可以定义函数
def outer():

    def inner():
        print("Inside inner")

    return inner

func = outer()

func()

# return inner


# %%

# 4. 装饰器的核心原理
# 假设我们想要在执行某个函数前后，自动打印日志。


def decorator(func):

    def wrapper():
        print("Before function")

        func()

        print("After function")

    return wrapper


def say_hello():
    print("Hello")

say_hello = decorator(say_hello)

say_hello()

# 第一步：把原来的 say_hello 函数传给 decorator。
# 第二步：decorator 创建并返回 wrapper 函数。
# 第三步：把 wrapper 赋给变量 say_hello。


#################### 解释
def say_hello():
    print("Hello")


# 现在，我想让它在说 Hello 之前，先说一句 Before。
# 所以我写了另一个函数：

def wrapper():
    print("Before")
    say_hello()

wrapper()


# 如果我想让 wrapper 不仅可以包住 say_hello，还可以包住其他函数，怎么办？
# 我们就写：

def decorator(func):

    def wrapper():
        print("Before")
        func()

    return wrapper

# func：你想包装的函数。
# wrapper：在这个函数执行之前，增加一个 print("Before")。
# return wrapper：把包装好的函数返回。


new_func = decorator(say_hello)

new_func()


# Before
# Hello


# 而 @decorator 只是下面这行代码的简写：
# say_hello = decorator(say_hello)
# 所以：

@decorator
def say_hello():
    print("Hello")

# 就是让 say_hello 自动获得打印 Before 的功能。

# new_func = decorator(say_hello) 等于把 say_hello 这个函数本身传进去，暂时不执行



##### 对！完全正确！ 你现在写的就是一个标准的 Python 装饰器。

# def decorator(func):

#     def wrapper():
#         print("Before")
#         func()

#     return wrapper


# @decorator
# def say_hello():
#     print("Hello")
# @decorator 就相当于自动帮你写了这一句：say_hello = decorator(say_hello)