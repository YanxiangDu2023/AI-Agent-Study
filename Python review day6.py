import json


# %%


def divide(a, b):
    return a / b


result = divide(10, 2)

print(result)
# %%


# | 错误类型 | 含义 | 例子 |
# |---|---|---|
# | `ValueError` | 类型可以，但具体的值不合适 | `int("hello")` |
# | `TypeError` | 数据类型不支持这个操作 | `"3" + 2` |
# | `ZeroDivisionError` | 除数为零 | `10 / 0` |
# | `IndexError` | 列表下标超出范围 | `[10, 20][5]` |
# | `KeyError` | 字典里没有这个键 | `{"name": "小明"}["age"]` |
# | `FileNotFoundError` | 找不到文件 | 打开不存在的文件 |
# | `NameError` | 使用了没有定义的名字 | 使用未定义的变量 |


# %%
import json

llm_output = '{"tool": "calculator", "a": 10, "b": 2}'


def calculator(a, b):
    return a / b


tools = {
    "calculator": calculator
}


try:
    # 1. 把 JSON 字符串转成字典
    data = json.loads(llm_output)

    # 2. 提取工具名称和参数
    tool_name = data["tool"]
    a = data["a"]
    b = data["b"]

    # 3. 检查工具是否存在
    if tool_name not in tools:
        raise ValueError(f"没有这个工具：{tool_name}")
    
    
# 按顺序理解：
# 1. 想找的工具是 "search"。
# 2. tools 里只有 "calculator"，没有 "search"。
# 3. 条件成立，执行 raise。
# 4. 产生一个 ValueError，说明是 "没有这个工具：search"。
# 如果外面有对应的 except，这个错误就会被接住：

# - raise：产生错误，立即中断当前执行流程，寻找能处理它的 except；没有人接住，就报错终止。

    # 4. 取出函数，然后调用
    
    
    tool_function = tools[tool_name]
    result = tool_function(a, b)

except json.JSONDecodeError:
    print("模型输出不是合法的 JSON")

# 模型输出不是合法 JSON

except KeyError as e:
    print(f"缺少必要字段：{e}")
    
# 缺少 "tool"、"a" 或 "b"

except ZeroDivisionError:
    print("计算失败：除数不能为零")
    
# b 是 0   


except TypeError:
    print("数据结构或参数类型不正确")
    
# 用 "hello" 等字符串做除法    


except ValueError as e:
    print(e)

# 工具名称不存在，执行了前面的 raise


else:
    print(f"工具执行成功：{result}")
    
    
    
    
    
# %%
user = {"name": "小明"}

try:
    age = user["age"] # user["age"] 想取出年龄，但字典里没有 "age"。
    print(age) # Python 自动产生 KeyError，跳过 print(age)。
    
except KeyError as e: # except KeyError as e 接住错误，用 e 保存这个错误。
    print(f"缺少字段：{e}") # print(f"缺少字段：{e}") 显示缺的是 'age'。

print("程序继续运行")

# 缺少字段：'age'
# 程序继续运行



#############################
# %%
# import asyncio

# async def main():
#     print("开始")
#     await asyncio.sleep(1)
#     print("结束")

# asyncio.run(main())



# %%

# | 写法 | 作用 |
# |---|---|
# | `async def` | 定义异步函数 |
# | `await` | 等待异步操作的结果 |
# | `asyncio.gather()` | 并发执行多个任务，收集结果 |
# | `asyncio.run()` | 在普通 `.py` 文件中启动异步程序 |


import asyncio

async def boil_water():
    print("开始烧水")
    await asyncio.sleep(3)
    print("水烧好了")

async def toast_bread():
    print("开始烤面包")
    await asyncio.sleep(2)
    print("面包烤好了")

async def main():
    await asyncio.gather( # 安排他们并发进行
        boil_water(),
        toast_bread()
    )
    

await main()



###################################
# %%
import asyncio

# asyncio 是 Python 自带的模块，提供异步相关功能，不需要额外安装。

# 你这段代码用了其中三个名字：
# 名字	用途
# asyncio.sleep()	模拟异步等待
# asyncio.wait_for()	等待一个操作，并设置超时时间
# asyncio.TimeoutError	表示等待超时的错误类型


# 模拟搜索，需要等待 5 秒
async def search():
    print("开始搜索")
    await asyncio.sleep(5)
    
    # asyncio.sleep(5)	使用 asyncio 工具箱里的功能，异步等待 5 秒
    # await	等这个操作完成，再执行当前函数的下一行
    return "搜索结果：AI Agent 的相关资料"

# 等待期间，当前任务暂停，其他已安排的异步任务可以运行。


async def main():
    try:
        # 最多等待 2 秒
        result = await asyncio.wait_for(search(), timeout=2)
        # 运行搜索，设置 2 秒的超时限制，等待结果；如果成功，就把结果保存到 result。
        
# 这里等待的已经不只是搜索本身，而是：
# 搜索完成，或者等待超时。

# 当前 main() 会停在这一行，直到拿到结果或收到错误。



# # 直接等待搜索结果，不设置超时
# result = await search()

# # 等待搜索结果，但设置 6 秒超时
# result = await asyncio.wait_for(search(), timeout=6)

    except asyncio.TimeoutError:
        print("搜索超时了")

    else:
        print(result)


await main()


# %%
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s | %(message)s",
    force=True
)

# | 配置 | 在这里的意思 |
# |---|---|
# | `level=logging.DEBUG` | 显示 DEBUG 以及更高级别的日志，所以例子中的 DEBUG、INFO 都会显示 |
# | `format="%(levelname)s \| %(message)s"` | 按“级别 \| 消息”的格式显示 |
# | `force=True` | 替换之前的日志配置，方便你在交互窗口重复运行 |


def calculator(a, b):
    logging.info("开始计算")
    logging.debug(f"收到参数：a={a!r}, b={b!r}")

    result = a / b

    logging.info(f"计算完成，结果是 {result}")
    return result


# a!r 是什么？先不用它也可以
# 这一行：
# logging.debug(f"收到参数：a={a!r}, b={b!r}")

# 你可以先简化成：
# logging.debug(f"收到参数：a={a}, b={b}")

# !r 的作用只是让值显示得更明确。例如，b 是字符串 "2" 时：
# b = "2"print(f"b={b}")    # b=2print(f"b={b!r}")  # b='2'

# 有了引号，更容易看出这是字符串。它不是日志必须使用的语法。


calculator(10, 2)
# %%



# **用 `logging` 也是一样：在每一步前记录一条消息，出错时记录具体位置。**

# 下面可以直接运行：

# ```python
# import json
# import logging

# # 日志配置，先当作固定模板
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)s | %(message)s",
#     force=True
# )

# text = '{"a": 10, "b": 0}'

# try:
#     logging.info("第1步：解析 JSON")
#     data = json.loads(text)

#     logging.info("第2步：读取参数")
#     a = data["a"]
#     b = data["b"]

#     logging.info(f"第3步：执行计算，a={a}，b={b}")
#     result = a / b

#     logging.info(f"第4步：计算完成，结果是 {result}")

# except Exception:
#     logging.exception("程序执行失败")
# ```

# 输出类似：

# ```text
# INFO | 第1步：解析 JSON
# INFO | 第2步：读取参数
# INFO | 第3步：执行计算，a=10，b=0
# ERROR | 程序执行失败
# Traceback (most recent call last):
#     ...
#     result = a / b
# ZeroDivisionError: division by zero
# ```

# **怎么看？**

# 1. 最后一条正常日志是“第3步”，没有“第4步”——说明第3步开始了，但没有完成。
# 2. 错误记录指向 `result = a / b`——这就是出错的代码。
# 3. 日志显示 `b=0`，错误说明是除零——原因找到了。

# 这里先记住两个用法：

# ```python
# logging.info("执行到哪一步了")
# ```

# **记录过程。**

# ```python
# logging.exception("程序执行失败")
# ```

# **放在 `except` 里面，记录错误和它发生的位置。**

# `logging` 不会自己猜“第几步”；步骤名称是你写的，具体报错位置则由 `logging.exception()` 自动记录。