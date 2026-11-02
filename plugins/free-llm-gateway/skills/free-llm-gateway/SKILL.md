---
name: free-llm-gateway
description: Use when a script, tool or app needs an LLM API without paid credits - starts a local OpenAI-compatible gateway (LiteLLM) at http://127.0.0.1:4000/v1 over free-tier providers (Gemini, Groq, Cerebras, Mistral, Z.ai GLM Flash, OpenRouter) with automatic fallback on rate limits; model "formal" injects the formal-writing-ar style automatically; paid Kimi and GLM-5.3 are opt-in by name only. Also use when the user mentions running out of API credit, rate limits, OmniRoute, or wants a free model endpoint.
---

# بوابة النماذج المجانية

## النطاق
نقطة اتصال محلية واحدة متوافقة مع OpenAI، تجمع الطبقات المجانية لعدة مزودين، وتتحول تلقائيًا إلى المزود التالي عند تجاوز حد الاستخدام أو حدوث خطأ.

**لا تفعل:**
- لا تستبدل نموذج Claude في Claude Code. الجلسة تعمل باشتراك المستخدم، والبوابة تخدم السكربتات والأدوات التي يكتبها.
- لا تخزن أي مفتاح. تقرأ المفاتيح من متغيرات البيئة فقط.
- لا تستقبل اتصالات من خارج الجهاز. تعمل على `127.0.0.1` فقط.
- لا تحوّل أي طلب تلقائيًا إلى مزود مدفوع.

## سرية البيانات
الطبقات المجانية قد تستخدم المدخلات في تحسين النماذج، وبعض المزودين (Z.ai وMoonshot) يعالجون البيانات خارج نطاقك القانوني. **لا تُرسل عبر البوابة أي محتوى سري أو بيانات جهات خاضعة للرقابة.** البوابة للمحتوى العام فقط: المعايير المنشورة والمراجع والمسودات الخالية من البيانات المؤسسية.

## المزودون وترتيب التحويل

| الترتيب | المزود | متغير المفتاح | النموذج الافتراضي | مصدر المفتاح المجاني |
|---|---|---|---|---|
| 1 | Gemini Pro | `GEMINI_API_KEY` | `gemini/gemini-2.5-pro` | aistudio.google.com |
| 2 | Gemini Flash | `GEMINI_API_KEY` (المفتاح نفسه) | `gemini/gemini-2.5-flash` | aistudio.google.com |
| 3 | Groq | `GROQ_API_KEY` | `groq/openai/gpt-oss-120b` | console.groq.com |
| 4 | Cerebras | `CEREBRAS_API_KEY` | `cerebras/gpt-oss-120b` | cloud.cerebras.ai |
| 5 | Mistral | `MISTRAL_API_KEY` | `mistral/mistral-small-latest` | console.mistral.ai |
| 6 | Z.ai | `ZAI_API_KEY` | `zai/glm-4.7-flash` | z.ai |
| 7 | OpenRouter | `OPENROUTER_API_KEY` | `openrouter/meta-llama/llama-3.3-70b-instruct:free` | openrouter.ai |

- الترتيب من الأقوى إلى الأسرع: Gemini Pro أولًا، وهو الأقوى والأفضل في العربية لكن حصته المجانية صغيرة. عند نفادها تنتقل البوابة تلقائيًا إلى Gemini Flash بالمفتاح نفسه، ثم إلى بقية المزودين.
- كل مفتاح يُضاف يدخل السلسلة تلقائيًا دون أي ضبط.
- يُستبعد تلقائيًا كل مزود لا يوجد مفتاحه. مفتاح مجاني واحد يكفي للتشغيل.
- لتوجيه مزود إلى عنوان آخر: `FREE_GW_<PROVIDER>_API_BASE`.

## مزودون مدفوعون (اختياري)
منخفضو التكلفة، ويُستدعون **باسمهم فقط**، ولا يدخلون سلسلة التحويل التلقائي إطلاقًا.

| الاسم | متغير المفتاح | النموذج | التكلفة التقريبية لكل مليون رمز |
|---|---|---|---|
| `kimi` | `MOONSHOT_API_KEY` | `moonshot/kimi-k3.1-pro` | 2 دولار إدخال، 10 دولارات إخراج |
| `glm` | `ZAI_API_KEY` | `zai/glm-5.3` | 1.4 دولار إدخال، 4.4 دولار إخراج |

الأسعار من جدول LiteLLM، وتُراجع في لوحة المزود قبل الاستخدام. يُضبط سقف إنفاق في حساب المزود.
لا تُستخدم «جسور» تحاكي جلسات الويب المجانية لهذه المنصات، لمخالفتها شروط الاستخدام.

## الأسلوب الرسمي التلقائي
النموذج `formal` يضيف نص مهارة `formal-writing-ar` تعليماتٍ ثابتة (System Prompt) لكل طلب، ثم يمر بسلسلة `free` نفسها.
- يُعثر على المهارة تلقائيًا في المستودع أو في الإضافات المثبتة، أو من المسار في `FREE_GW_STYLE_FILE`.
- إن كانت للطلب تعليمات ثابتة أصلًا، يُضاف الأسلوب قبلها دون حذفها.
- يستهلك نحو 3 آلاف رمز إضافي لكل طلب من الحصة المجانية.
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
Model:    free | formal | gemini-pro | gemini | groq | ... | kimi | glm
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
`generativelanguage.googleapis.com` و`api.groq.com` و`api.cerebras.ai` و`api.mistral.ai` و`api.z.ai` و`openrouter.ai`، وللمدفوع: `api.moonshot.ai`
