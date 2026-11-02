# arabic-gov-skills

مهارات لوكلاء الذكاء الاصطناعي تدعم إنتاج المستندات الرسمية العربية في الجهات الحكومية والرقابية.

## المهارات المتاحة

مهارات الإضافة `arabic-gov-skills`:

| المهارة | الغرض |
|---|---|
| `arabic-rtl-docs` | ضبط اتجاه RTL في Word وPowerPoint وHTML، وإزالة الرموز غير المرئية وبقايا تنسيق المحادثة وبيانات التعريف الدالة على أداة التوليد، والإبلاغ عن العلامات المرئية والحروف الشبيهة، وعزل المصطلحات الإنجليزية داخل النص العربي |
| `formal-writing-ar` | أسلوب الكتابة الرسمية والمهنية لكل المستندات: المقترحات والتقارير والخطط وتقارير التقييم والمذكرات ونصوص العروض. يحكم التسلسل والتوثيق ومنع الحشو والاختلاق ودقة السند |
| `arabic-design-workflow` | ينظّم مهارات التصميم والتخطيط والمراجعة لكل مخرَج بصري: العروض، والملصقات، وصفحات HTML، والواجهات، ولوحات المؤشرات، وتصاميم Canva، تحت ضوابط RTL وعدم وضع نص داخل الصور |
| `document-pattern-analysis` | تفكيك مستند أو عرض نموذجي إلى بنيته ووظيفة أقسامه ومسار حجته وأسلوبه، واستخلاص قالب وقائمة مراجعة لإعادة الاستخدام دون نسخ النص |
| `formal-memo-ar` | ما يخص المذكرات الداخلية وحدها: الافتتاح المرجعي، وحسم غرض المذكرة، والألقاب. تعمل مع `formal-writing-ar` |

## الإضافات الأخرى

| الإضافة | المهارة | الغرض |
|---|---|---|
| `gov-templates` | `presentation-templates` | قوالب PowerPoint جاهزة لأدلة الموظفين والتهيئة والامتثال وتقييم التدريب ومخططات القرار |
| `free-llm-gateway` | `free-llm-gateway` | بوابة محلية متوافقة مع OpenAI على `http://127.0.0.1:4000/v1` تجمع الطبقات المجانية لمزودي Gemini وGroq وCerebras وMistral وOpenRouter، مع تحويل تلقائي عند تجاوز الحد |

## التثبيت

المستودع سوق إضافات (Plugin Marketplace) يضم ثلاث إضافات مستقلة. تُثبَّت كل إضافة مرة واحدة على مستوى الحساب، فتتاح في كل المشاريع.

### في Claude (المحادثة)
1. **Customize** ثم **Plugins** ثم **Add** ثم **Add marketplace**.
2. كتابة `a-alhamad/arabic-gov-skills`.
3. تثبيت الإضافات المطلوبة من السوق.

### في Claude Code

```bash
/plugin marketplace add a-alhamad/arabic-gov-skills
```

```bash
/plugin install arabic-gov-skills@a-alhamad-skills
```

```bash
/plugin install gov-templates@a-alhamad-skills
```

```bash
/plugin install free-llm-gateway@a-alhamad-skills
```

### في بيئات Claude Code السحابية
في إعدادات البيئة:
1. **Setup script**: إضافة السطر التالي لتثبيت مكونات البوابة المجانية:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/a-alhamad/arabic-gov-skills/main/setup/cloud-setup.sh | bash
   ```
2. **Network secrets**: إضافة مفتاح مزود مجاني واحد على الأقل، مثل `GEMINI_API_KEY`.
3. **Network access**: إضافة نطاقات المزودين إلى Allowed domains. القائمة في مهارة `free-llm-gateway`.

### البنية

```
.claude-plugin/marketplace.json
plugins/
  arabic-gov-skills/      مهارات الكتابة والتنظيف والتصميم
  gov-templates/          قوالب العروض في skills/presentation-templates/assets/
  free-llm-gateway/       البوابة المجانية: skills/free-llm-gateway/scripts/gateway.py
setup/cloud-setup.sh      سكربت إعداد البيئة السحابية، ولا يحتوي أي مفتاح
tests/
```

## الاستخدام المباشر لأداة الفحص

```bash
# فحص فقط
python3 plugins/arabic-gov-skills/skills/arabic-rtl-docs/scripts/check_hidden_chars.py report.docx

# إنتاج نسخة منظفة بجانب الأصل دون المساس به
python3 plugins/arabic-gov-skills/skills/arabic-rtl-docs/scripts/check_hidden_chars.py report.docx --fix
```

الصيغ المدعومة: `.docx` و`.pptx` و`.xlsx` و`.html` و`.md` و`.txt` و`.xml`.

## تشغيل الاختبارات

لا تحتاج الاختبارات أي مكتبة خارجية، ولا تحتاج LiteLLM.

```bash
# مجموعة الاختبارات كاملة
python3 -m unittest discover -s tests -v

# إثبات أن الاختبارات قادرة على كشف الأعطال: تُعطَّل الأداة عمدًا 15 مرة، ويجب أن تُكشف كل مرة
python3 tests/mutation_check.py
```

## محتوى من أطراف أخرى
قائمة الحد الأدنى لجودة التصميم مقتبسة بتصرف من مستودع impeccable بترخيص Apache 2.0. التفاصيل ونص الترخيص في `THIRD_PARTY_NOTICES.md`.

## مبادئ المستودع
- عند كل تعديل على إضافة يُرفع رقم الإصدار في ملف `.claude-plugin/plugin.json` الخاص بها، وإلا لا يصل التعديل إلى الإضافة المثبتة.
- لا يُحفظ أي مفتاح أو بيانات مؤسسية في المستودع، فهو عام. المفاتيح تُقرأ من متغيرات البيئة فقط.
- كل مهارة محددة النطاق، وتنص صراحة على ما لا تفعله.
- لا تعدّل أي أداة الملف الأصلي، وإنما تنتج نسخة منفصلة.
- تُختبر الأدوات قبل إضافتها.
