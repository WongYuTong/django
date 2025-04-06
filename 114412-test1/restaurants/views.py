from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
import os

client = OpenAI(api_key="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")  # 建議用 os.getenv() 取金鑰會更安全

def gpt_test(request):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "write a haiku about AI"}
        ]
    )
    reply = completion.choices[0].message.content
    return JsonResponse({"reply": reply})
# Create your views here.
