#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Tuple
from .action import Action
import re

PROMPT_TEMPLATE = '''
-----
You are a ChatGPT executive observer expert skilled in identifying problem-solving plans and errors in the execution process. Your goal is to check if the created Execution Plan following the requirements.

# Question or Task
{context}

# Revised Role List
{roles}

# Execution Plan
{plan}

# Steps
1. You should first understand, analyze, and disassemble the human's problem.
2. You should check if the execution plan meets the following requirements:
2.1. The execution plan should be divided into multiple steps to solve the problem step by step. 
2.2. Each step should have at least one expert role to execute. If a step involves multiple expert roles, you need to describe the contributions of each expert role and how they collaborate to produce comprehensive results. 
2.2. The step description should provide as much detail as possible and explain how the steps are related to each other. The step description must also include the expected output of the current step and specify what inputs are required for the next step. Expected output of the current step and required input for the next step must match each other.
2.3. NEVER guess the result of a step.
2.4. Make the plan as detailed as possible to accurately complete the task.
2.5. Indicate the name of the expert role used at the beginning of the step. 
2.6. A language expert role is responsible for summarizing the result information of all steps.
2.7. The final step should always be an independent step 'XXX: Given the above steps taken, please respond to the users original question: XXX' by the language expert role. At the end of your plan, say '<END_OF_PLAN>'
3. Summarize the above inspection results. If there is anything that does not meet the requirements, you MUST re output the details of all expert roles in JSON blob format. If there are any areas that do not meet the requirements, you need to correct the non compliant parts and output the revised execution plan.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# IMPROTANT Attention
1. Make sure the name of the expert role used at the beginning of the step. 
2. If there are no errors for the execution plan, you should output the original execution plan in the section 'Revised Execution Plan'.
3. You must not change any of the expert roles. Make the best use of all the expert roles available.
4. You need to ensure that the following steps are completed to answer questions or complete tasks.
-----
'''

FORMAT_EXAMPLE = '''
---
## Observer
check if the created Execution Plan following the requirements.

## Errors 
you should always think about if there are any errors for created execution plan.

## Revised Execution Plan:
```
1. ROLE 1: STEP 1
2. ROLE 2: STEP 2
```

## Anything UNCLEAR
We need ... how to start.
---
'''

OUTPUT_MAPPING = {
    "Revised Execution Plan": (str, ...),
    "Anything UNCLEAR": (str, ...),
}


class CheckPlans(Action):
    def __init__(self, name="Check Plan", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, context):

        roles = re.findall('## Revised Selected Roles List:([\s\S]*?)##', str(context))[-1]
        agents = re.findall('{[\s\S]*?}', roles)
        if len(agents) <= 0: roles = ''
        roles += re.findall('## Revised Created Roles List:([\s\S]*?)##', str(context))[-1]
        plan = re.findall('## Execution Plan:([\s\S]*?)##', str(context))[-1]
        context = re.findall('## Question or Task:([\s\S]*?)##', str(context))[-1]
        prompt = PROMPT_TEMPLATE.format(context=context, plan=plan, roles=roles, format_example=FORMAT_EXAMPLE)
        return await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

