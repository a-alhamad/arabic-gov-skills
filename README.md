# arabic-gov-skills

مهارات لوكلاء الذكاء الاصطناعي تدعم إنتاج المستندات الرسمية العربية في الجهات الحكومية والرقابية.

## المهارات المتاحة

| المهارة | الغرض |
|---|---|
| `arabic-rtl-docs` | ضبط اتجاه RTL في Word وPowerPoint وHTML، وإزالة الرموز المخفية، وعزل المصطلحات الإنجليزية داخل النص العربي |

## التثبيت

```bash
npx skills add a-alhamad/arabic-gov-skills
```

## الاستخدام المباشر لأداة الفحص

```bash
# فحص فقط
python3 arabic-rtl-docs/scripts/check_hidden_chars.py report.docx

# إنتاج نسخة منظفة بجانب الأصل دون المساس به
python3 arabic-rtl-docs/scripts/check_hidden_chars.py report.docx --fix
```

الصيغ المدعومة: `.docx` و`.pptx` و`.xlsx` و`.html` و`.md` و`.txt` و`.xml`.

## مبادئ المستودع
- كل مهارة محددة النطاق، وتنص صراحة على ما لا تفعله.
- لا تعدّل أي أداة الملف الأصلي، وإنما تنتج نسخة منفصلة.
- تُختبر الأدوات قبل إضافتها.
