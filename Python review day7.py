# 异步编程`async`、`await`、`gather()`、超时处理

import asyncio

async def boil_water():
    print("开始烧水")
    await asyncio.sleep(3)
    print("水烧好了")

async def make_tea():
    print("开始泡茶")
    await asyncio.sleep(2)
    print("茶泡好了")

async def main():
    # 使用 asyncio.gather() 并发执行多个异步任务
    
    await asyncio.gather(boil_water(), make_tea())
    # 安排烧水和泡茶一起进行，等两件事都完成后，收集结果。

# 运行主函数
asyncio.run(main())



 # %%
 
async def search():
    print("开始搜索")
    await asyncio.sleep(5)
    return "搜索结果"


async def main():
    try:
        result = await asyncio.wait_for(
            search(),
            timeout=2
        )

    except asyncio.TimeoutError:
        print("搜索超时了")
        
# 尝试搜索，设置 2 秒超时限制。
# 超时后，产生 asyncio.TimeoutError 异常。
# except 接住这个异常。
# 打印“搜索超时了”。

    else:
        print(result)

await main()