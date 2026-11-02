---
name: free-llm-gateway
description: Use when a script, tool or app needs an LLM API without paid credits - starts a local OpenAI-compatible gateway (LiteLLM) at http://127.0.0.1:4000/v1 over free-tier providers (Gemini, Groq, Cerebras, Mistral, OpenRouter) with automatic fallback on rate limits. Also use when the user mentions running out of API credit, rate limits, OmniRoute, or wants a free model endpoint.
---

# بوابة النماذج المجانية

## النطاق
نقطة اتصال محلية واحدة متوافقة مع OpenAI، تجمع الطبقات المجانية لعدة مزودين، وتتحول تلقائيًا إلى المزود التالي عند تجاوز حد الاستخدام أو حدوث خطأ.

**لا تفعل:**
- لا تستبدل نموذج Claude في Claude Code. الجلسة تعمل باشتراك المستخدم، والبوابة تخدم السكربتات والأدوات التي يكتبها.
- لا تخزن أي مفتاح. تقرأ المفاتيح من متغيرات البيئة فقط.
- لا تستقبل اتصالات من خارج الجهاز. تعمل على `127.0.0.1` فقط.

## المزودون وترتيب التحويل

| الترتيب | المزود | متغير المفتاح | النموذج الافتراضي | مصدر المفتاح المجاني |
|---|---|---|---|---|
| 1 | Gemini | `GEMINI_API_KEY` | `gemini/gemini-2.5-flash` | aistudio.google.com |
| 2 | Groq | `GROQ_API_KEY` | `groq/openai/gpt-oss-120b` | console.groq.com |
| 3 | Cerebras | `CEREBRAS_API_KEY` | `cerebras/gpt-oss-120b` | cloud.cerebras.ai |
| 4 | Mistral | `MISTRAL_API_KEY` | `mistral/mistral-small-latest` | console.mistral.ai |
| 5 | OpenRouter | `OPENROUTER_API_KEY` | `openrouter/meta-llama/llama-3.3-70b-instruct:free` | openrouter.ai |

- Gemini أولًا لأنه الأفضل في العربية بين الطبقات المجانية.
- يُستبعد تلقائيًا كل مزود لا يوجد مفتاحه. مفتاح واحد يكفي للتشغيل.
- لتغيير نموذج مزود: `FREE_GW_<PROVIDER>_MODEL`، مثل `FREE_GW_GEMINI_MODEL=gemini/gemini-2.5-flash-lite`.

## الخطوات

1. التأكد من تثبيت LiteLLM: `command -v litellm || pip install 'litellm[proxy]'`
2. عرض المفاتيح المتاحة: `python3 scripts/gateway.py providers`
3. التشغيل: `python3 scripts/gateway.py start`
4. التحقق بطلب فعلي: `python3 scripts/gateway.py check`
5. الإيقاف: `python3 scripts/gateway.py stop`

المسار نسبي إلى مجلد هذه المهارة. السجل في `~/.free-llm-gateway/proxy.log`.

## الاستخدام من أي أداة

```
Base URL: http://127.0.0.1:4000/v1
API key:  sk-local-free-gateway   (أو قيمة FREE_GW_MASTER_KEY)
Model:    free                    (أو اسم مزود محدد: gemini, groq, ...)
```

```python
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:4000/v1", api_key="sk-local-free-gateway")
client.chat.completions.create(model="free", messages=[{"role": "user", "content": "..."}])
```

## الأعطال الشائعة

| العرض | السبب | الإجراء |
|---|---|---|
| `No provider key found` | لا يوجد أي مفتاح في البيئة | إضافة مفتاح واحد على الأقل |
| `403 Forbidden` يشير إلى عنوان الوكيل المحلي | سياسة الشبكة في البيئة السحابية تحجب المزود | إضافة نطاق المزود إلى Allowed domains في إعدادات البيئة |
| `API key not valid` | المفتاح خاطئ أو ملغى | إصدار مفتاح جديد من لوحة المزود |
| `model not found` | المزود غيّر اسم النموذج | ضبط `FREE_GW_<PROVIDER>_MODEL` بالاسم الحالي |

## نطاقات الشبكة المطلوبة في البيئة السحابية
`generativelanguage.googleapis.com` و`api.groq.com` و`api.cerebras.ai` و`api.mistral.ai` و`openrouter.ai`
