"""
RAG Pipeline 核心链路 - 面试填空练习版
=====================================

核心流程（4步）：
1. 文档处理：切块 + 引用信息
2. 向量化：文本 → embedding
3. 向量存储：插入数据库 + 建索引
4. RAG检索：问题 → 检索 → 组装prompt → LLM回答

面试重点：
- 为什么要RAG？（解决LLM知识不足/过时问题）
- 向量检索原理？（余弦相似度）
- Prompt工程？（如何把检索结果喂给LLM）
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np


# ============ Part 1: 文档切块 ============

@dataclass
class DocumentChunk:
    """文档块 = 内容 + 元数据"""
    content: str
    source_file: str
    chunk_index: int
    page_number: Optional[int] = None
    embedding: Optional[List[float]] = None  # 后面会填充


class DocumentProcessor:
    """
    面试要点：
    - chunk_size 太小 → 语义不完整
    - chunk_size 太大 → 检索不精准
    - overlap 作用 → 避免关键信息被切断
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def create_chunks(self, text: str, source_file: str) -> List[DocumentChunk]:
        """
        【核心算法】滑动窗口切块

        TODO 填空：
        1. 计算每个块的起始和结束位置
        2. 注意 overlap 的实现
        3. 生成 DocumentChunk 对象
        """
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            # TODO: 计算结束位置（不超过文本长度）
            end = min(_______, _______)

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk = DocumentChunk(
                    content=_______,
                    source_file=_______,
                    chunk_index=_______
                )
                chunks.append(chunk)
                chunk_index += 1

            # TODO: 计算下一个块的起始位置（考虑overlap）
            # 提示：start 应该向前移动 (chunk_size - overlap)
            start = _______

            if start >= len(text):
                break

        return chunks


# ============ Part 2: 向量化 ============

class EmbeddingGenerator:
    """
    面试要点：
    - embedding 是什么？（文本的数学表示，高维向量）
    - 为什么能做相似度检索？（相似文本的向量接近）
    - 用什么模型？（text-embedding-3-small/large, Sentence-BERT等）
    """

    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self.dimension = 1536  # OpenAI embedding维度

    def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        批量生成embedding

        TODO 填空：
        1. 提取所有chunk的文本内容
        2. 调用API生成embedding
        3. 把embedding填回chunk对象
        """
        
        # 实际项目中调用 OpenAI API，这里模拟
        for chunk in chunks:
            # TODO: 模拟生成embedding（实际应调用API）
            # 提示：np.random.rand() 生成随机向量
            chunk.embedding = np.random.rand(_______).tolist()

        return chunks
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        【关键】用户问题也要向量化，才能和文档块比较

        面试要点：
        - 为什么query也要embedding？（在同一向量空间才能比较相似度）
        """
        # TODO: 生成query的embedding
        return np.random.rand(_______).tolist()



# ============ Part 3: 向量数据库 ============

class VectorDatabase:
    """
    面试要点：
    - 向量数据库 vs 传统数据库？（支持向量检索）
    - 相似度计算？（余弦相似度、欧氏距离）
    - 索引类型？（HNSW、IVF等，加速检索）
        embedding 和向量检索
    这是你简历最像“AI 工程”这一层的核心。

    你要问自己：

    模型输出的 embedding 是什么？
    为什么文本可以变成向量？
    为什么 query 也要 embedding？
    为什么要用相似度计算？
    为什么要转成 NumPy 数组？
    """

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.embeddings = []

    def insert(self, chunks: List[DocumentChunk]):
        """
        TODO 填空：
        1. 存储chunks
        EmbeddedChunk类的对象已经存储了向量,chunk,生成向量的模型,但是chunk也需要存储到数据库里面
        把每个文档块 chunk 放进一个列表里
这样后面检索时，能拿到：
内容 chunk.content
来源文件 chunk.source_file
页码 page_number
甚至最终返回给用户的“引用来源”.
        2. 提取embedding到单独数组（便于批量计算相似度）,不是把整个 chunk 都放进 embeddings
而是只把它的向量数字部分拿出来

为什么要分开存？
因为它们的用途不一样：

self.chunks

存文本内容和来源
用来最终返回结果
self.embeddings

只存数字向量
用来做相似度计算、向量检索
        """
        for chunk in chunks:
            self.chunks.append(chunk)
            # TODO: 提取embedding
            self.embeddings.append(___chunk.embedding____)

        # 转成numpy数组便于计算
        self.embeddings = np.array(self.embeddings)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        【核心】向量检索 - 找最相似的k个块

        面试要点：
        - 余弦相似度公式：cos(A,B) = A·B / (|A||B|)
        - 值越大越相似（范围-1到1）

        TODO 填空：
        1. 计算query和所有chunk的相似度
        2. 排序取top_k
        3. 返回结果（包含内容+元数据）
        """
        query_vec = np.array(query_embedding)

        # TODO: 计算余弦相似度
        # 提示：np.dot()点积, np.linalg.norm()求模
        similarities = []
        for emb in self.embeddings:
            # 余弦相似度 = 点积 / (模长1 * 模长2)
            similarity = np.dot(_______, _______) / (
                np.linalg.norm(_______) * np.linalg.norm(_______)
            )
            similarities.append(similarity)

        # TODO: 排序取top_k
        # 提示：np.argsort()返回排序后的索引, [::-1]倒序
        top_indices = np.argsort(similarities)[_______][:_______]

        # TODO: 组装返回结果
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append({
                'content': _______,
                'source_file': _______,
                'page_number': _______,
                'similarity_score': similarities[idx]
            })

        return results


# ============ Part 4: RAG生成器 ============

class RAGGenerator:
    """
    面试要点：
    - RAG流程？（检索 → 组装prompt → LLM生成）
    - 为什么比直接问LLM好？（提供准确的上下文）
    - Prompt设计？（明确告诉LLM基于检索内容回答）
    检索到的 chunk 是怎么选出来的？
    怎么组装 prompt？
    为什么需要先检索、再回答？
    为什么不能直接丢给大模型？
    引用来自哪里，怎么保证可信？
    """

    def __init__(self, vector_db: VectorDatabase, embedding_gen: EmbeddingGenerator):
        self.vector_db = vector_db
        self.embedding_gen = embedding_gen

    def generate_response(self, query: str) -> Dict[str, Any]:
        """
        【完整RAG流程】

        TODO 填空：
        1. 把用户问题向量化
        2. 检索相关chunks
        3. 组装prompt
        4. 调用LLM生成回答
        """
        # Step 1: 问题向量化
        # TODO: 生成query的embedding
        query_embedding = ___generate_query_embedding(query)____

        # Step 2: 检索top-k相关chunks
        # TODO: 调用vector_db.search()
        retrieved_chunks = ___vector_db.search(query_embedding,top_k = 5)____

        # Step 3: 组装prompt
        # TODO: 把检索到的内容拼接成上下文
        context = "\n\n".join([
            f"[来源: {chunk['source_file']}]\n{chunk['____content___']}"
            for chunk in retrieved_chunks
        ])

        prompt = f"""基于以下参考资料回答问题。如果参考资料中没有相关信息，请明确说明。

参考资料：
{_______}

问题：{_______}

回答："""

        # Step 4: 调用LLM（这里模拟）
        # 实际项目中调用 OpenAI API
        response = f"[模拟回答] 基于{len(retrieved_chunks)}个相关片段..."

        return {
            'response': response,
            'sources': retrieved_chunks,
            'prompt_used': prompt
        }


# ============ 完整示例 ============

def run_rag_pipeline_demo():
    """
    演示完整RAG流程

    面试时可以这样讲解：
    1. "首先我们要把文档切块，因为..."
    2. "然后向量化，这样就能用数学方法检索..."
    3. "检索到相关内容后，组装prompt喂给LLM..."
    """

    # 模拟文档
    document = """
    RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI技术。
    它先从知识库检索相关信息，再把检索结果作为上下文喂给大语言模型。
    这样可以解决LLM知识过时、幻觉等问题。
    """

    # TODO: 补全流程

    # 1. 切块
    processor = DocumentProcessor(chunk_size=100, overlap=20)
    chunks = processor.create_chunks(document, "rag_intro.txt")
    print(f"✅ 切块完成: {len(chunks)}个块")

    # 2. 向量化
    # TODO: 创建embedding生成器
    embedding_gen = EmbeddingGenerator(model_name="baba")
    chunks = embedding_gen.generate_embeddings(chunks)
    print(f"✅ 向量化完成")

    # 3. 存入向量数据库
    # TODO: 创建向量数据库,把生成的向量插入
    vector_db = ____VectorDatabase()___
    vector_db.insert(____chunks___)
    print(f"✅ 存储完成")

    # 4. RAG问答
    # TODO: 创建RAG生成器
    rag = RAGGenerator(____vector_db___, __embedding_gen_____)

    query = "什么是RAG？"
    result = rag.generate_response(query)

    print(f"\n问题: {query}")
    print(f"回答: {result['response']}")
    print(f"引用来源: {len(result['sources'])}个")


"""
================== 面试核心问答 ==================

Q1: 什么是RAG？为什么需要它？
A:
- RAG = Retrieval-Augmented Generation（检索增强生成）
- 问题：LLM知识有限、会过时、有幻觉
- 解决：先从知识库检索相关信息，再让LLM基于检索内容回答
- 优势：回答准确、有依据、可追溯来源

Q2: RAG的完整流程是什么？
A:
1. 文档预处理：切块 → 向量化 → 存入向量数据库
2. 用户提问：问题向量化 → 向量检索 → 找到top-k相关块
3. Prompt组装：把检索内容 + 问题 组装成prompt
4. LLM生成：基于prompt生成回答（带引用）

Q3: 向量检索的原理是什么？
A:
- 文本转成高维向量（embedding）
- 相似文本的向量在空间中距离近
- 用余弦相似度等指标衡量相似程度
- 通过向量索引（如HNSW）快速找到最相似的k个

Q4: Prompt工程在RAG中的作用？
A:
- 明确告诉LLM"基于以下资料回答"
- 提供检索到的上下文
- 要求LLM引用来源、避免编造
- 示例：
  """
  基于以下参考资料回答问题。如果资料中没有相关信息，请说"资料中未提及"。

  参考资料：[检索内容]

  问题：[用户问题]
  """

Q5: 如何评估RAG系统的效果？
A:
- 检索准确率：召回的chunks是否相关（Recall@k）
- 生成质量：回答是否准确、是否基于检索内容
- 引用准确性：citation是否指向正确来源
- 端到端指标：用户满意度、任务完成率

Q6: RAG vs 微调（Fine-tuning）？
A:
- RAG：不改模型，动态检索外部知识，易更新
- 微调：改模型参数，知识固化在模型里，更新成本高
- 选择：RAG适合频繁变化的知识，微调适合特定领域风格

Q7: 这个项目中的技术栈？
A:
- 文档处理：PyMuPDF (PDF), LangChain (切块)
- Embedding：OpenAI text-embedding-3-small
- 向量数据库：Milvus Lite（本地轻量级）
- LLM：OpenAI GPT-4o-mini
- 前端：Streamlit

Q8: 遇到过什么坑？
A:
- chunk_size太小导致回答碎片化 → 调整到1000字符
- 没overlap导致关键句被切断 → 加200字符overlap
- 检索top-k太少答不全 → 从3提升到5
- prompt不明确导致LLM不引用 → 优化prompt模板
"""
