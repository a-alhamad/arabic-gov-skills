# arabic-gov-skills

مهارات لوكلاء الذكاء الاصطناعي تدعم إنتاج المستندات الرسمية العربية في الجهات الحكومية والرقابية.

## المهارات المتاحة

| المهارة | الغرض |
|---|---|
| `arabic-rtl-docs` | ضبط اتجاه RTL في Word وPowerPoint وHTML، وإزالة الرموز غير المرئية وبقايا تنسيق المحادثة وبيانات التعريف الدالة على أداة التوليد، والإبلاغ عن العلامات المرئية والحروف الشبيهة، وعزل المصطلحات الإنجليزية داخل النص العربي |
| `formal-writing-ar` | أسلوب الكتابة الرسمية والمهنية لكل المستندات: المقترحات والتقارير والخطط وتقارير التقييم والمذكرات ونصوص العروض. يحكم التسلسل والتوثيق ومنع الحشو والاختلاق ودقة السند |
| `formal-memo-ar` | ما يخص المذكرات الداخلية وحدها: الافتتاح المرجعي، وحسم غرض المذكرة، والألقاب. تعمل مع `formal-writing-ar` |

## التثبيت

المستودع سوق إضافات (Plugin Marketplace) يضم إضافة واحدة باسم `arabic-gov-skills` تحتوي المهارات الثلاث.

### في Claude (المحادثة)
1. **Customize** ثم **Plugins** ثم **Add** ثم **Add marketplace**.
2. كتابة `a-alhamad/arabic-gov-skills`.
3. تثبيت الإضافة `arabic-gov-skills` من السوق.

تُحفظ الإضافة في الحساب، وتتاح في المحادثة وفي Claude Code بالحساب نفسه.

### في Claude Code

```bash
/plugin install arabic-gov-skills --marketplace a-alhamad/arabic-gov-skills
```

### البنية

```
.claude-plugin/marketplace.json
plugins/arabic-gov-skills/
  .claude-plugin/plugin.json
  skills/arabic-rtl-docs/
  skills/formal-memo-ar/
  skills/formal-writing-ar/
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

لا تحتاج الاختبارات أي مكتبة خارجية.

```bash
# مجموعة الاختبارات كاملة
python3 -m unittest discover -s tests -v

# إثبات أن الاختبارات قادرة على كشف الأعطال: تُعطَّل الأداة عمدًا 13 مرة، ويجب أن تُكشف كل مرة
python3 tests/mutation_check.py
```

## مبادئ المستودع
- كل مهارة محددة النطاق، وتنص صراحة على ما لا تفعله.
- لا تعدّل أي أداة الملف الأصلي، وإنما تنتج نسخة منفصلة.
- تُختبر الأدوات قبل إضافتها.
