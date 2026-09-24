"""
DocumentProcessor 核心逻辑 - 填空练习版
面试重点：文档切块策略 + 引用元数据设计

核心流程：
1. 读取文档（PDF按页/文本直接读）
2. 切块（固定大小 + overlap）
3. 每个块打上引用标签（文件名、页码、字符位置）
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import hashlib


@dataclass
class DocumentChunk:
    """一个文档块，核心是 content + 引用信息"""
    content: str              # 文本内容
    source_file: str          # 来源文件名
    source_type: str          # pdf/txt/web
    page_number: Optional[int] = None   # PDF才有页码
    chunk_index: int = 0      # 第几个块
    start_char: Optional[int] = None    # 在原文的字符位置
    end_char: Optional[int] = None

    def get_citation_info(self) -> Dict[str, Any]:
        """
        【关键点1】返回引用信息，用于后续 RAG 检索后显示来源
        """
        citation = {
            'source': self.source_file,
            'type': self.source_type,
            'chunk_index': self.chunk_index
        }

        # TODO: 填空 - 如果有页码，加到 citation 里
        if ____self.page_number____:
            citation['page'] = _____self.page_number___

        return citation


class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        【关键决策1】chunk_size 和 overlap 怎么设？
        - chunk_size: 一个块多少字符？太大检索不准，太小语义不完整
        - overlap: 块之间重叠多少？避免语义被切断
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _create_chunks_from_text(
        self,
        text: str,
        source_file: str,
        source_type: str,
        page_number: Optional[int] = None
    ) -> List[DocumentChunk]:
        """
        【核心算法】文本切块 - 滑动窗口 + 边界优化
        """
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            # TODO: 填空 - 计算当前块的结束位置（不超过文本长度）
            end = min(____start+self.chunk_size____, len(text))

            # 【关键点2】边界优化：不在句子中间切断
            if end < len(text):
                # 找最后一个句号或换行符
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                boundary = max(last_period, last_newline)

                # 如果找到的边界不是太靠前（），就用它。boundary只是中间变量，用来赋值给end的。如果< 50% chunk_size，也就是说边界太靠前，就不要赋值；靠后的话，end才放到句号或者换行符的后一位
                if boundary > start + self.chunk_size * 0.5:
                    end = boundary + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                # TODO: 填空 - 创建一个 DocumentChunk 对象
                chunk = DocumentChunk(
                    content=_chunk_text_______,
                    source_file=__source_file______,
                    source_type=___source_type_____,
                    page_number=___page_number_____,
                    chunk_index=____chunk_index____,
                    start_char=___start_____,
                    end_char=end - 1
                )
                chunks.append(chunk)
                chunk_index += 1

            # 【关键点3】滑动窗口：下一个块从哪开始？
            # 要有 overlap，但也不能倒退
            # TODO: 填空 - 计算下一个块的起始位置
            start = max(_____self.start+self.chunk_size___ - ___overlap_____, end)

            if start >= len(text):
                break

        return chunks

    def _process_pdf(self, file_path: str) -> List[DocumentChunk]:
        """
        【关键点4】PDF处理策略：按页切还是整体切？
        这里选择：先按页提取文本，每页内部再切块
        好处：页码信息保留，方便引用
        """
        import pymupdf
        chunks = []
        doc = pymupdf.open(file_path)

        # TODO: 填空 - 遍历每一页
        for page_num in range(____doc._page_count___):
            page = doc.load_page(page_num)
            text = page.get_text()

            if not text.strip():
                continue

            # TODO: 填空 - 调用切块函数，注意页码从1开始
            page_chunks = self._create_chunks_from_text(
                text,
                file_path,
                source_type='pdf',
                page_number=___page_num_____
            )
            chunks.extend(page_chunks)

        doc.close()
        return chunks


"""
================== 面试问答准备 ==================

Q1: 为什么要切块？不能直接把整个文档喂给 AI 吗？
A:
- LLM 上下文窗口有限
- 检索时要找最相关的几块，不是整个文档
- 切块后向量化，检索更精准

Q2: chunk_size 设多大合适？
A:
- 看具体场景，一般 500-1500 字符
- 太小：语义不完整，检索召回太多碎片
-太大：不相关内容混在一起，检索不准

Q3: overlap 有什么用？
A:
- 避免关键信息被切在两块中间
- 比如一句话被切断，前半句和后半句分别在两个块里，overlap 能让完整句子出现在某个块里
- end有两种情况，=len(text),=start+chunk_size(这个时候<len(text))，前者肯定不会一句话被切断；后者又分两种情况，boundary处于后一半和前一半，后一半，end被boundary赋值，此时肯定在句号或者换行符的下一位，不会切断；前一半，end==start+chunk_size，可能会位于句子中间，这里的设计取舍是：宁可偶尔切断句子，也不为了找很早的句号而生成一个过短的块。start = max(_____self.start+self.chunk_size___ - ___overlap_____, end)，

Q4: 为什么要存 page_number 和 start_char？
A:
- RAG 检索到这个块后，要告诉用户"这段话来自第X页"
- 就像 NotebookLM 那样，回答后面标注引用来源

Q5: 边界优化是什么意思？
A:
- 不在句子中间硬切，找最近的句号或换行
- 如果句号太靠前（< 50% chunk_size），就算了，避免块太小

Q6: PDF 和 txt 处理有什么不同？
A:
- PDF 能按页提取，每个块能标页码
- txt 没有页码概念，只能标字符位置
"""
