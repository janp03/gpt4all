from fastapi import APIRouter, Depends, Response, Security, status
from pydantic import BaseModel, Field
from typing import List, Dict
import logging
from uuid import uuid4
from api_v1.settings import settings
from gpt4all import GPT4All
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

### This should follow https://github.com/openai/openai-openapi/blob/master/openapi.yaml

class CompletionRequest(BaseModel):
    model: str = Field(..., description='The model to generate a completion from.')
    prompt: str = Field(..., description='The prompt to begin completing from.')
    max_tokens: int = Field(7, description='Max tokens to generate')
    temperature: float = Field(0, description='Model temperature')
    top_p: float = Field(1.0, description='top_p')
    n: int = Field(1, description='')
    stream: bool = Field(False, description='Stream responses')


class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: float
    finish_reason: str

class CompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
class CompletionResponse(BaseModel):
    id: str
    object: str = 'text_completion'
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: CompletionUsage


router = APIRouter(prefix="/completions", tags=["Completion Endpoints"])

@router.post("/", response_model=CompletionResponse)
async def completions(request: CompletionRequest):
    '''
    Completes a GPT4All model response.
    '''

    # global model
    if request.stream:
        raise NotImplementedError("Streaming is not yet implements")

    model = GPT4All(model_name=settings.model, model_path=settings.gpt4all_path)

    output = model.generate(prompt=request.prompt,
                     n_predict = request.max_tokens,
                     top_k = 20,
                     top_p = request.top_p,
                     temp=request.temperature,
                     n_batch = 1024,
                     repeat_penalty = 1.2,
                     repeat_last_n = 10,
                     context_erase = 0)


    return CompletionResponse(
        id=str(uuid4()),
        created=time.time(),
        model=request.model,
        choices=[dict(CompletionChoice(
            text=output,
            index=0,
            logprobs=-1,
            finish_reason='stop'
        ))],
        usage={
            'prompt_tokens': 0, #TODO how to compute this?
            'completion_tokens': 0,
            'total_tokens': 0
        }
    )


