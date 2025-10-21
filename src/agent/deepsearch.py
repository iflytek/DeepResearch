# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from typing import *
from dataclasses import dataclass
import re
import json
import traceback
from datetime import datetime

import json_repair

from src.tools import search
from src.llms.llm import llm
from src.prompts.template import apply_prompt_template
from src.utils.print_util import colored_print
import logging

logger = logging.getLogger(__name__)

@dataclass(kw_only=True)
class Judge:
    name: str

@dataclass(kw_only=True)
class Knowledge:
    """Data structure to hold knowledge"""
    insight: str
    snippets: List[str]
    references: List[search.SearchResult]

@dataclass(kw_only=True)
class EvalResult:
    """Data structure to hold evaluation result information"""
    eval_type: str
    reason: str
    pass_label: bool

@dataclass(kw_only=True)
class DeepSearchResult:
    """Data structure to hold deep search result information"""
    query: List[str]
    all_knowledge: List[Knowledge]
    used_knowledge: List[Knowledge]
    re_knowledge: List[Knowledge]
    answer: str
    search_result: Dict[str, List[search.SearchResult]]
    eval_result: List[EvalResult]
    children: 'DeepSearchResult'

class DeepSearch:
    """Deep search workflow"""
    def __init__(self, title:str, chapter:str, sub_chapter: List[str], chapter_outline:str, max_depth:int=2, search_top_n:int=3):
        self._search_client = search.SearchClient()
        self._title = title
        self._chapter = chapter
        self._sub_chapter = sub_chapter
        self._chapter_outline = chapter_outline
        self._max_depth = max_depth
        self._search_top_n = search_top_n
        self._search_query_re = re.compile(r'(?s)<sq>(.*?)</sq>')

    def deep_search(self) -> DeepSearchResult:
        """Deep search for the given query"""
        outline = self._make_outline()
        query = self._gen_search_query(outline)
        judge_results = self._judge_query(outline)
        result = self._deep_search(query, 1, judge_results, outline, '', set())
        result.re_knowledge = self._get_all_used_knowledge(result)
        return result

    def _deep_search(self, query:List[str], depth:int, judge_results:List[Judge], outline:str, pre_answer:str, pre_knowledge: Set[str]) -> DeepSearchResult:
        search_results = self._search_all(query)
        all_search:Dict[str,List[search.SearchResult]] = {}
        for q, search_result in search_results.items():
            for result in search_result:
                if result.url in pre_knowledge:
                    continue
                pre_knowledge.add(result.url)
                all_search.setdefault(q, []).append(result)
        
        deep_search_result = DeepSearchResult(
            query=query,
            search_result=all_search,
            all_knowledge=[],
            used_knowledge=[],
            re_knowledge=[],
            answer='',
            eval_result=[],
            children=None,
        )

        if all_search:
            deep_search_result.all_knowledge = self._extract_all_knowledge(outline, all_search)
        colored_print(f'Learning above webpage', color="purple")
        knowledge, answer = self._gen_answer(outline, deep_search_result.all_knowledge)
        deep_search_result.answer = answer
        deep_search_result.used_knowledge = knowledge

        if depth >= self._max_depth:
            return deep_search_result
        colored_print(f'Learning done', color="purple")
        answer = pre_answer + answer
        eval_list = self._evaluate(outline, answer, judge_results)
        deep_search_result.eval_result = eval_list

        unpass_eval = [eval for eval in eval_list if not eval.pass_label]
        if not unpass_eval:
            return deep_search_result
        for eval in unpass_eval:
            colored_print(eval.reason, color="orange")
        new_query = self._gen_research_query(query, outline, answer, unpass_eval)

        deep_search_result.children = self._deep_search(new_query, depth+1, judge_results, outline, answer, pre_knowledge)
        return deep_search_result

    def _make_outline(self) -> str:
        outline = f'- Writing topic: {self._title}\n'
        outline += f'- Writing requirement: Please focus on the topic "{self._chapter}" of this chapter'
        if self._sub_chapter:
            outline += ' and elaborate from '
            for sub_chapter in self._sub_chapter:
                outline += f'"{sub_chapter}";'
            outline += f'{len(self._sub_chapter)} different aspects.'
        outline += f'\n{self._chapter_outline}\n'
        return outline

    def _gen_search_query(self, outline:str) -> List[str]:
        search_query:List[str] = []
        try:
            text = llm(llm_type='evaluate', messages=apply_prompt_template(
                prompt_name='learning/search_query',
                state={
                    'now': datetime.now().strftime("%a %b %d %Y"),
                    'chapter_outline': outline
                })
            )
            if not text:
                return []
            search_query = self._search_query_re.findall(text)
            return search_query
        except:
            return []

    def _judge_query(self, query:str) -> List[Judge]:
        judge_result:List[Judge] = []
        try:
            text = llm(llm_type='evaluate', messages=apply_prompt_template(
                prompt_name='learning/judge',
                state={
                    'now': datetime.now().strftime("%a %b %d %Y"),
                    'chapter_outline': query
                })
            )
            if not text:
                return []
            judge = json_repair.loads(text)
            for k, v in judge.items():
                if v:
                    judge_result.append(Judge(name=k))

        except Exception as e:
            logger.error(f'Error in judge query: {e}')
            logger.error(traceback.format_exc())

        return judge_result

    def _search_all(self, query:List[str]) -> Dict[str, List[search.SearchResult]]:
        search_result: Dict[str, List[search.SearchResult]] = {}
        for q in query:
            colored_print(f'Searching: {q}', color="purple")
            search_result[q] = self._search_client.search(q, self._search_top_n)
            for result in search_result[q]:
                colored_print(f'{result.title} -- ', color="cyan", end="")
                colored_print(result.url, color="blue", underline=True)
        return search_result

    def _extract_all_knowledge(self, outline:str, search_results:Dict[str,List[search.SearchResult]]) -> List[Knowledge]:
        extract_limit = 32000
        knowledge_results: List[Knowledge] = []
        for search_result in search_results.values():
            content_len = 0
            extract_search: List[search.SearchResult] = []
            for result in search_result:
                if not result.content:
                    continue

                if content_len + len(result.content) > extract_limit:
                    knowledge_results.extend(self._extract_knowledge(outline, extract_search, extract_limit))
                    extract_search = [result]
                    content_len = len(result.content)
                else:
                    extract_search.append(result)
                    content_len += len(result.content)
            if extract_search:
                knowledge_results.extend(self._extract_knowledge(outline, extract_search, extract_limit))
            
        return knowledge_results

    def _extract_knowledge(self, outline:str, search_results:List[search.SearchResult], extract_limit:int) -> List[Knowledge]:
        knowledge_results: List[Knowledge] = []
        if not search_results:
            return knowledge_results

        try:
            search = ''
            for i, result in enumerate(search_results):
                search += f'[document index {i}]\ntitle: {result.title}\ncontent: {result.content}\ndate: {result.date if result.date else "unknown"}\n\n'
            text = llm(llm_type='evaluate', messages=apply_prompt_template(
                prompt_name='learning/extract_knowledge',
                state={
                    'chapter_outline': outline,
                    'search': search[:extract_limit],
                })
            )
            if not text:
                return

            extract_result = json_repair.loads(text)
            for knowledge in extract_result.get('knowledge', []):
                reference:List[search.SearchResult] = []
                for index in knowledge.get('snippets', []):
                    if 0 <= int(index) < len(search_results):
                        reference.append(search_results[int(index)])
                if reference:
                    knowledge_results.append(Knowledge(
                        insight=knowledge.get('insight', ''),
                        snippets=knowledge.get('snippets', []),
                        references=reference,
                    ))

        except Exception as e:
            logger.error(f'extract result error:{e}')
            logger.error(traceback.format_exc())
        
        return knowledge_results

    def _gen_answer(self, outline:str, knowledge:List[Knowledge]) -> tuple[List[Knowledge], str]:
        if not knowledge:
            return [], '<no knowledge>'

        documents:str = ''
        for idx, doc in enumerate(knowledge):
            documents += f'[document id: {idx}]\ninsight: {doc.insight}\n\n'
        try:
            text = llm(llm_type='evaluate', messages=apply_prompt_template(
                prompt_name='learning/draft',
                state={
                    'chapter_outline': outline,
                    'knowledge': documents
                })
            )
            if not text:
                return [], '<no answer>'
            answer_result = json_repair.loads(text)
            answer = answer_result.get('answer', '<no answer>')
            used_knowledge:List[Knowledge] = []
            quote_id = answer_result.get('quote_id', [])
            for idx in json.loads(str(quote_id)) or []:
                id = int(str(idx))
                if 0 <= id < len(knowledge):
                    used_knowledge.append(knowledge[id])

        except Exception as e:
            logger.error(f'evaluate error:{e}')
            logger.error(traceback.format_exc())

        return used_knowledge, answer

    def _evaluate(self, outline:str, answer:str, judge_result:List[Judge]) -> List[EvalResult]:
        eval_results:List[EvalResult] = []
        for judge in judge_result:
            eval_results.append(self._evaluate_one(outline, answer, judge))
        return eval_results

    def _evaluate_one(self, outline:str, answer:str, judge:Judge) -> EvalResult:
        prompt:List = None
        match judge.name:
            case 'completeness':
                prompt = apply_prompt_template(
                    prompt_name='learning/evaluate_completeness',
                    state={
                        'chapter_outline': outline,
                        'draft': answer
                    })
            case 'freshness':
                prompt = apply_prompt_template(
                    prompt_name='learning/evaluate_freshness',
                    state={
                        'now': datetime.now().strftime("%a %b %d %Y"),
                        'chapter_outline': outline,
                        'draft': answer
                    })
            case 'plurality':
                prompt = apply_prompt_template(
                    prompt_name='learning/evaluate_plurality',
                    state={
                        'chapter_outline': outline,
                        'draft': answer
                    })
            case _:
                raise ValueError(f'Unknown judge name: {judge.name}')

        text = llm(llm_type='evaluate', messages=prompt)
        if not text:
            return EvalResult(eval_type=judge.name, pass_label=False, reason='')
        evaluate_result = json_repair.loads(text)
        think = evaluate_result.get('analysis', {}).get('think', '')
        passed = evaluate_result.get('analysis', {}).get('pass', False)
        return EvalResult(eval_type=judge.name, pass_label=passed, reason=think)

    def _gen_research_query(self, query:List[str], outline:str, answer:str, unpass_eval:List[EvalResult]) -> List[str]:
        try:
            text = llm(llm_type='evaluate', messages= apply_prompt_template(
                prompt_name='learning/research_query',
                state={
                    'now': datetime.now().strftime("%a %b %d %Y"),
                    'search_query': f'[{",".join(query)}]',
                    'chapter_outline': outline,
                    'draft': answer,
                    'evaluation': '\n\n'.join([eval.reason for eval in unpass_eval])
                }))
            if not text:
                return []
            research_result = json_repair.loads(text)
        except Exception as e:
            logger.error(f'generate research query error:{e}')
            logger.error(traceback.format_exc())

        return research_result.get('search_query_list', [])

    def _get_all_used_knowledge(self, result: DeepSearchResult) -> List[Knowledge]:
        if result == None:
            return []
        return result.used_knowledge + self._get_all_used_knowledge(result.children)

if __name__ == '__main__':
    deep_searcher = DeepSearch(
        title='The best pc game in 2024',
        chapter='Introduction',
        sub_chapter=['Definition of "best game"', 'How to choose the best game'],
        chapter_outline='- Definition of "best game"\n- How to choose the best game',
        max_depth=3,
        search_top_n=10,
    )
    result = deep_searcher.deep_search()
    print(result.re_knowledge)
