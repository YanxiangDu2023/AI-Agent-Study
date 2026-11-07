import math
import torch
import torch.nn as nn


# ============================================================
# 1. 位置编码：给词向量添加位置信息
# ============================================================

class PositionalEncoding(nn.Module):

    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super().__init__()

        # 这个教学版本采用成对的 sin/cos，因此要求维度为偶数
        assert d_model % 2 == 0, "d_model 必须是偶数"

        self.dropout = nn.Dropout(dropout)

        # 位置编号：(max_len, 1)
        # 例如 [[0], [1], [2], ...]
        position = torch.arange(max_len).unsqueeze(1)

        # 为不同维度准备不同的频率
        div_term = torch.exp(
            torch.arange(0, d_model, 2)
            * (-math.log(10000.0) / d_model)
        )

        # 每个位置都有一个 d_model 维的位置向量
        pe = torch.zeros(max_len, d_model)

        # 偶数维度使用 sin，奇数维度使用 cos
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        # 增加批次维度：(1, max_len, d_model)
        # buffer 会随模型保存和移动，但不会被训练更新
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        # x：(batch_size, seq_len, d_model)
        seq_len = x.size(1)

        if seq_len > self.pe.size(1):
            raise ValueError("输入序列长度超过 max_len")

        # 词向量 + 对应位置的位置向量
        x = x + self.pe[:, :seq_len]

        return self.dropout(x)


# ============================================================
# 2. 多头注意力
# ============================================================

class MultiHeadAttention(nn.Module):

    def __init__(self, d_model, num_heads):
        super().__init__()

        assert d_model % num_heads == 0, \
            "d_model 必须能被 num_heads 整除"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        # 将输入分别转换成 Q、K、V
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)

        # 整合多个头的输出
        self.W_o = nn.Linear(d_model, d_model)

    def split_heads(self, x):
        # 原形状：(batch_size, seq_len, d_model)
        batch_size, seq_len, _ = x.size()

        # 把每个词的向量拆成多个头
        x = x.view(
            batch_size,
            seq_len,
            self.num_heads,
            self.d_k
        )

        # 调整为：(batch_size, num_heads, seq_len, d_k)
        return x.transpose(1, 2)

    def combine_heads(self, x):
        # x：(batch_size, num_heads, seq_len, d_k)
        batch_size, _, seq_len, _ = x.size()

        # 将同一个词的各个头排列到一起
        x = x.transpose(1, 2).contiguous()

        # 拼接回：(batch_size, seq_len, d_model)
        return x.view(batch_size, seq_len, self.d_model)

    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        # Q 与 K 比较，计算各个位置之间的匹配分数
        # 分数形状：
        # (batch_size, num_heads, 查询长度, 被参考序列长度)
        scores = torch.matmul(Q, K.transpose(-2, -1))

        # 除以每个头维度的平方根，控制分数尺度
        scores = scores / math.sqrt(self.d_k)

        if mask is not None:
            # mask=True：允许参考
            # mask=False：禁止参考
            # 每个查询位置至少应保留一个可以参考的位置
            scores = scores.masked_fill(~mask, float("-inf"))

        # 将分数变成权重，每一行的权重总和为 1
        weights = torch.softmax(scores, dim=-1)

        # 按权重混合各个位置的 V
        return torch.matmul(weights, V)

    def forward(self, query, key, value, mask=None):
        # 先生成 Q、K、V，再拆成多个头
        Q = self.split_heads(self.W_q(query))
        K = self.split_heads(self.W_k(key))
        V = self.split_heads(self.W_v(value))

        # 同时计算各个头的注意力
        attn_output = self.scaled_dot_product_attention(
            Q, K, V, mask
        )

        # 合并各个头，并进行最终整合
        combined = self.combine_heads(attn_output)

        return self.W_o(combined)


# ============================================================
# 3. 逐位置前馈网络：分别加工每个词元的向量
# ============================================================

class PositionWiseFeedForward(nn.Module):

    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()

        # 先扩大维度，再缩回原来的维度
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # 同一套参数作用于所有词元位置
        x = self.linear1(x)  # d_model → d_ff
        x = self.relu(x)     # 负数变成 0
        x = self.dropout(x)
        x = self.linear2(x)  # d_ff → d_model

        return x


# ============================================================
# 4. 一个编码器层
# ============================================================

class EncoderLayer(nn.Module):

    def __init__(self, d_model, num_heads, d_ff, dropout):
        super().__init__()

        self.self_attn = MultiHeadAttention(d_model, num_heads)

        self.feed_forward = PositionWiseFeedForward(
            d_model, d_ff, dropout
        )

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(self, x, src_mask):
        # ① 自注意力：输入序列中的词互相参考
        # Q、K、V 的输入都来自 x
        attn_output = self.self_attn(x, x, x, src_mask)

        # 残差连接 + 层归一化
        x = self.norm1(x + self.dropout(attn_output))

        # ② 前馈网络：加工每个位置的向量
        ff_output = self.feed_forward(x)

        # 残差连接 + 层归一化
        x = self.norm2(x + self.dropout(ff_output))

        return x


# ============================================================
# 5. 一个解码器层
# ============================================================

class DecoderLayer(nn.Module):

    def __init__(self, d_model, num_heads, d_ff, dropout):
        super().__init__()

        # 自注意力：参考目标序列中允许看到的前文
        self.self_attn = MultiHeadAttention(d_model, num_heads)

        # 交叉注意力：参考编码器的输出
        # 这是另一个模块，有自己独立的参数
        self.cross_attn = MultiHeadAttention(d_model, num_heads)

        self.feed_forward = PositionWiseFeedForward(
            d_model, d_ff, dropout
        )

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(self, x, encoder_output, src_mask, tgt_mask):
        # ① 带遮罩的自注意力：不能参考未来位置
        attn_output = self.self_attn(x, x, x, tgt_mask)

        x = self.norm1(x + self.dropout(attn_output))

        # ② 交叉注意力
        # Q 来自解码器；K、V 来自编码器
        cross_output = self.cross_attn(
            x,
            encoder_output,
            encoder_output,
            src_mask
        )

        x = self.norm2(x + self.dropout(cross_output))

        # ③ 前馈网络
        ff_output = self.feed_forward(x)

        x = self.norm3(x + self.dropout(ff_output))

        return x


# ============================================================
# 6. 完整 Transformer：把以上组件组合起来
# ============================================================

class Transformer(nn.Module):

    def __init__(
        self,
        src_vocab_size,   # 输入语言的词汇表大小
        tgt_vocab_size,   # 输出语言的词汇表大小
        d_model=128,      # 词元向量维度
        num_heads=4,      # 注意力头数
        num_layers=2,     # 编码器和解码器各有多少层
        d_ff=512,         # 前馈网络内部维度
        dropout=0.1,
        max_len=5000,
        pad_id=0          # 用于填充序列的编号
    ):
        super().__init__()

        self.d_model = d_model
        self.pad_id = pad_id

        # 词嵌入：将整数编号转换成向量
        # 输入和输出语言分别使用一张词嵌入表
        self.src_embedding = nn.Embedding(
            src_vocab_size, d_model, padding_idx=pad_id
        )
        self.tgt_embedding = nn.Embedding(
            tgt_vocab_size, d_model, padding_idx=pad_id
        )

        self.position = PositionalEncoding(
            d_model, dropout, max_len
        )

        # ModuleList 让 PyTorch 正确管理各层及其参数
        # 每次创建新层，各层之间不共享参数
        self.encoder_layers = nn.ModuleList([
            EncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        self.decoder_layers = nn.ModuleList([
            DecoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        # 把解码器向量转换成目标词汇表中各个词的分数
        self.output_layer = nn.Linear(d_model, tgt_vocab_size)

    def make_masks(self, src, tgt):
        """
        src：(batch_size, src_len)
        tgt：(batch_size, tgt_len)

        这个教学版本使用右侧填充：
        源序列至少有一个有效词元；
        目标序列以非填充的开始标记开头。
        """

        # 输入遮罩：不允许参考 PAD
        # (batch_size, src_len) → (batch_size, 1, 1, src_len)
        src_mask = (src != self.pad_id).unsqueeze(1).unsqueeze(2)

        # 目标序列的填充遮罩
        tgt_padding_mask = (
            (tgt != self.pad_id).unsqueeze(1).unsqueeze(2)
        )

        tgt_len = tgt.size(1)

        # 下三角遮罩：每个位置只能参考自己和前面的位置
        # 例如长度为 3：
        # [[True, False, False],
        #  [True, True,  False],
        #  [True, True,  True ]]
        causal_mask = torch.tril(
            torch.ones(
                tgt_len,
                tgt_len,
                dtype=torch.bool,
                device=tgt.device
            )
        )

        # 同时满足：不是填充位置，也不是未来位置
        tgt_mask = tgt_padding_mask & causal_mask

        return src_mask, tgt_mask

    def forward(self, src, tgt):
        # ① 创建遮罩
        src_mask, tgt_mask = self.make_masks(src, tgt)

        # ② 编码器输入：词嵌入 + 位置编码
        # 乘 sqrt(d_model) 是原始 Transformer 使用的缩放
        encoder_output = self.src_embedding(src)
        encoder_output = encoder_output * math.sqrt(self.d_model)
        encoder_output = self.position(encoder_output)

        # ③ 依次经过多个编码器层
        for layer in self.encoder_layers:
            encoder_output = layer(encoder_output, src_mask)

        # ④ 解码器输入：词嵌入 + 位置编码
        decoder_output = self.tgt_embedding(tgt)
        decoder_output = decoder_output * math.sqrt(self.d_model)
        decoder_output = self.position(decoder_output)

        # ⑤ 依次经过多个解码器层
        # 每一层都可以参考编码器的最终输出
        for layer in self.decoder_layers:
            decoder_output = layer(
                decoder_output,
                encoder_output,
                src_mask,
                tgt_mask
            )

        # ⑥ 输出每个位置对“下一个词”的预测分数
        # 形状：(batch_size, tgt_len, tgt_vocab_size)
        logits = self.output_layer(decoder_output)

        # 返回的是分数 logits，尚未经过 softmax
        return logits


# ============================================================
# 7. 运行示例：演示一次前向计算，不进行训练
# ============================================================

if __name__ == "__main__":
    torch.manual_seed(42)

    # 为了方便理解，手工定义两个小词汇表
    src_vocab = {
        "<pad>": 0,
        "<bos>": 1,  # 句子开始
        "<eos>": 2,  # 句子结束
        "I": 3,
        "love": 4,
        "apples": 5
    }

    tgt_vocab = {
        "<pad>": 0,
        "<bos>": 1,
        "<eos>": 2,
        "我": 3,
        "喜欢": 4,
        "苹果": 5
    }

    # 创建一个小型 Transformer
    model = Transformer(
        src_vocab_size=len(src_vocab),
        tgt_vocab_size=len(tgt_vocab),
        d_model=32,
        num_heads=4,
        num_layers=2,
        d_ff=128,
        dropout=0.1
    )

    # 输入英文：I love apples <eos>
    src = torch.tensor([[3, 4, 5, 2]])

    # 解码器输入：<bos> 我 喜欢 苹果
    tgt_input = torch.tensor([[1, 3, 4, 5]])

    # 训练时对应的正确答案应是：我 喜欢 苹果 <eos>
    # 输入与答案错开一个位置，让模型学习预测下一个词
    tgt_expected = torch.tensor([[3, 4, 5, 2]])

    # 评估模式：关闭 Dropout
    # eval() 不代表模型已经训练好了
    model.eval()

    # 这里只演示计算，不需要记录用于反向传播的梯度
    with torch.no_grad():
        logits = model(src, tgt_input)

        # 将词汇分数转换成概率
        probabilities = torch.softmax(logits, dim=-1)

    print("输入形状：", src.shape)
    print("解码器输入形状：", tgt_input.shape)
    print("输出分数形状：", logits.shape)
    print("输出概率形状：", probabilities.shape)

    # 每个位置对整个词汇表的概率之和应约为 1
    print("每个位置的概率之和：", probabilities.sum(dim=-1))
    
    
    
    #######################
    # Encoder–Decoder Transformer 中编码器的工作过程
    
#     **对，你这次理解是正确的！**你描述的就是我们前面讲的 **Encoder–Decoder Transformer 中编码器的工作过程**。小拼写改一下：是 **FFN** 和 **Transformer**。

# 以输入 `我 喜欢 苹果` 为例：

# 1. **每个 token 变成词向量，再加上位置信息。**
# 2. **经过多层自注意力和 FFN**，每层还包含残差连接和层归一化。
# 3. **自注意力允许每个 token 参考整句中的所有有效 token**，包括自己、前面和后面的 token；填充用的 PAD 通常会被遮住。
# 4. 最后，**每个输入 token 都得到一个融合了上下文信息的新向量**。不同 token 对其他位置的关注程度可能不同。

# 例如：

# | 输入 token | 编码器输出 |
# |---|---|
# | 我 | 融合上下文后的“我”的向量 |
# | 喜欢 | 融合上下文后的“喜欢”的向量 |
# | 苹果 | 融合上下文后的“苹果”的向量 |

# **你最后改成“编码器不负责生成新的 token”，这个说法很准确。**它会生成新的**向量表示**，但不会因此增加新的 **token**：输入 3 个 token，就输出对应的 3 个向量。

# 在这套架构中，**解码器参考编码器的输出和已经生成的内容，再通过输出层预测下一个 token**，逐步生成答案。

# 不过，这是原始的**编码器＋解码器**结构；我们后面要学的 **Decoder-Only** 模型没有这个独立的编码器。


###########################
#########################  Decoder-Only（仅解码器）架构

# **对，这一节讲的是 Decoder-Only（仅解码器）架构。**它和前面完整 Transformer 里的解码器有一点区别。

# 前面的解码器要参考两部分信息：

# - **已经生成的内容**：通过带遮罩的自注意力。
# - **编码器处理后的输入**：通过交叉注意力。

# **Decoder-Only 没有独立的编码器，所以也去掉了与编码器连接的交叉注意力。**提示词和已经生成的回答放在同一个序列里处理。

# 例如，你输入：

# > 中国的首都是

# 它的过程是：

# 1. 把输入 token 变成向量，并引入位置信息。
# 2. 经过多层**带因果遮罩的自注意力和 FFN**，得到上下文向量。
# 3. 用最后一个位置的向量，经过输出层，预测下一个 token。
# 4. 把选出的 token 接到末尾，继续预测。

# 假设后续生成的 token 分别是“北京”和“。”：

# | 当前文本 | 下一步生成 |
# |---|---|
# | 中国的首都是 | 北京 |
# | 中国的首都是北京 | 。 |

# 这里与你刚才理解的编码器最主要的区别是：

# | | 编码器 | Decoder-Only |
# |---|---|---|
# | 每个位置能参考哪里？ | 前面、自己、后面的有效 token | 自己和前面的有效 token |
# | 最终用于什么？ | 提供上下文向量 | 通过输出层预测下一个 token |
# | 是否需要独立编码器？ | 本身就是编码器 | 不需要 |

# **所以，它并不是“不理解，只生成”。它在预测下一个 token 的过程中，也会通过注意力和 FFN 加工、利用输入信息。**只是理解和生成都由同一套网络完成。





# 我们用 **“I love apples” → “我喜欢苹果”**，把前面学的**完整 Encoder–Decoder Transformer** 串起来。

# **① 输入英文，转换成 token 编号**

# 先分词，再查词汇表，把 token 变成编号。例如：

# ```text
# I       love      apples
# ↓       ↓         ↓
# 3       4         5
# ```

# 这些编号只是标识，不代表词的含义。

# **② 编号变成词向量，加入位置信息**

# ```text
# 每个 token 的输入向量 = 词嵌入向量 + 位置编码
# ```

# 此时，每个位置都有一组数字，同时包含词和位置的信息。

# **③ 进入编码器：自注意力**

# 每个位置的向量分别经过三种变换，得到自己的 **Q、K、V**。

# - 用这个位置的 **Q** 与各个位置的 **K** 比较，计算关注权重。
# - 按这些权重混合各个位置的 **V**，得到汇集的信息。

# **编码器中，每个 token 都可以参考整句的有效 token，包括后面的内容。**

# 例如，处理 `love` 时，可以参考 `I`、`love` 和 `apples`。

# **④ 经过残差连接、归一化和 FFN**

# 一个编码器层的过程，对应我们前面的代码是：

# ```text
# 自注意力
# → 加回输入向量（残差连接）
# → 层归一化
# → FFN 加工各个位置的向量
# → 再做残差连接和层归一化
# ```

# 这样重复经过多个编码器层，最终得到：

# | 输入 token | 编码器最终输出 |
# |---|---|
# | I | 融合英文上下文的向量 |
# | love | 融合英文上下文的向量 |
# | apples | 融合英文上下文的向量 |

# **编码器输出的是向量，不是新 token。**这些向量会交给解码器参考。

# ---

# **⑤ 解码器从开始标记出发**

# 翻译刚开始时，还没有生成中文，所以先输入开始标记：

# ```text
# <bos>
# ```

# 它也要经过：

# ```text
# token 编号 → 词嵌入向量 → 加入位置编码
# ```

# **⑥ 解码器先做带遮罩的自注意力**

# 这一步处理**已有的中文前文**。

# 每个位置只能参考**自己和前面的 token**，不能参考后面的 token。

# 刚开始只有 `<bos>`，所以只能参考它自己。之后有了中文：

# ```text
# <bos> 我 喜欢
# ```

# 则：

# | 位置 | 可以参考 |
# |---|---|
# | `<bos>` | `<bos>` |
# | 我 | `<bos>`、我 |
# | 喜欢 | `<bos>`、我、喜欢 |

# 这一步之后，同样做残差连接和层归一化。

# **⑦ 通过交叉注意力，参考英文**

# 这是编码器和解码器连接的地方：

# ```text
# Q：来自解码器当前的向量
# K、V：由编码器的最终输出变换得到
# ```

# 可以理解为：

# > 解码器根据目前的中文前文，去英文的上下文向量中寻找有帮助的信息。

# 例如，准备预测“苹果”时，交叉注意力可以从 `apples` 对应的编码器输出中获取信息。关注哪些位置、关注多少，是训练学到的。

# 交叉注意力之后，再经过：

# ```text
# 残差连接和层归一化
# → FFN
# → 残差连接和层归一化
# ```

# **⑥～⑦ 的这些操作组成一个解码器层，再重复经过多个解码器层。**

# **⑧ 输出层把向量变成下一个 token 的概率**

# 解码器最后输出的仍然是向量。生成时，取**最后一个位置的向量**进行：

# ```text
# 最后位置的向量
# → 输出线性层
# → 词汇表中每个 token 的分数
# → Softmax
# → 每个 token 的概率
# ```

# 然后根据生成策略选出一个 token。例如选出：

# ```text
# 我
# ```

# **⑨ 把新 token 接回输入，继续生成**

# 为了方便演示，假设“我”“喜欢”“苹果”各是一个 token：

# | 解码器已有输入 | 参考的信息 | 下一步选出的 token |
# |---|---|---|
# | `<bos>` | 编码器的英文输出 | 我 |
# | `<bos> 我` | 编码器的英文输出 | 喜欢 |
# | `<bos> 我 喜欢` | 编码器的英文输出 | 苹果 |
# | `<bos> 我 喜欢 苹果` | 编码器的英文输出 | `<eos>` |

# 生成结束标记 `<eos>` 后停止，最后将 token 转回文字：

# > 我喜欢苹果

# **同一句英文通常只需要编码一次，解码器在逐步生成时反复参考这份编码结果。**

# 你刚刚看的 **Decoder-Only** 则把提示词和回答接在同一个序列里，**没有独立编码器，也没有上面第⑦步的交叉注意力**。它通过带遮罩的自注意力处理已有内容，再用输出层不断预测下一个 token。