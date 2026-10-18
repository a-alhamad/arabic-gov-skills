# خطة تنفيذ: مجموعة اختبارات أداة الفحص

> **للمنفذ:** المهارة المطلوبة: superpowers:executing-plans أو superpowers:subagent-driven-development، مهمةً مهمة. الخطوات بصيغة مربعات (`- [ ]`) للمتابعة.

**الهدف:** مجموعة اختبارات آلية تثبت سلوك `check_hidden_chars.py` كما توثقه مهارة `arabic-rtl-docs`، وتكشف أي تراجع عند التعديل مستقبلًا.

**البنية:** اختبارات تشغّل الأداة فعليًا عبر سطر الأوامر على ملفات تجريبية تُنشأ داخل كل اختبار، دون محاكاة. لأن الأداة مكتوبة مسبقًا، يُثبَت أن كل اختبار قادر على الفشل بـ"اختبار التعطيل": يُعطَّل السلوك المحمي في نسخة مؤقتة من الأداة، ويجب أن يفشل الاختبار المقابل. أما الأخطاء المكتشفة فتُعالج بالدورة الكاملة: اختبار فاشل أولًا، ثم أقل تعديل يجعله ينجح.

**التقنيات:** Python 3 ومكتبتها القياسية فقط (`unittest`، `zipfile`، `subprocess`، `tempfile`). لا اعتماديات خارجية.

**المواصفة:** `arabic-rtl-docs/SKILL.md` (الأقسام ٢ إلى ٦، وخطوات التحقق، وحدود الأداة).

## القيود العامة
- لا مكتبات خارجية؛ تعمل الاختبارات بأمر واحد: `python3 -m unittest discover -s tests -v`
- ملفات الأداة والاختبارات خالية من أي حرف غير ASCII؛ تُكتب الرموز بصيغة `chr(0x....)`.
- لا يُعدَّل الملف الأصلي أبدًا؛ `--fix` ينتج `<الاسم>_clean.<الامتداد>` بجانبه.
- رموز الخروج: `0` نظيف أو بعد `--fix`، و`1` وجود ما يستوجب المعالجة، و`2` ملف غير مدعوم أو تعذر قراءته.
- العمل على فرع `add-tests`، ولا دمج في `main` قبل اعتماد المستخدم.

## محاور المراجعة
مدخلات لا تذكرها المواصفة، ويتوقع المستخدم أن تُعالج دون انهيار البرنامج:
1. **ملف نصي بترميز Windows-1256** (شائع في الأنظمة الحكومية العربية): المتوقع رسالة واضحة ورمز خروج `2`، لا رسالة خطأ برمجية. الوضع الحالي: انهيار. (المهمة ٥)
2. **ملف غير موجود:** رسالة واضحة ورمز `2`. الوضع الحالي: انهيار. (المهمة ٥)
3. **ملف بامتداد .docx وليس أرشيفًا سليمًا** (تالف أو محمي بكلمة مرور): رسالة واضحة ورمز `2`. الوضع الحالي: انهيار. (المهمة ٥)
4. **اسم ملف عربي يحتوي مسافات:** يعمل الفحص والتنظيف وتنشأ النسخة المنظفة بالاسم الصحيح. (المهمة ٥)
5. **ملف Word بلا خصائص (`docProps/core.xml` غائب):** يعمل الفحص دون خطأ. (المهمة ٤)

---

### المهمة ١: البنية المساندة وقواعد الخروج

**الملفات:**
- إنشاء: `tests/helpers.py`
- إنشاء: `tests/test_cli.py`

**الواجهات:**
- تنتج:
  - `SCRIPT: pathlib.Path` مسار الأداة.
  - `run_cli(path: Path, *args: str) -> subprocess.CompletedProcess` يشغّل الأداة بـ `python3 -I` ويعيد المخرجات نصًا.
  - `make_office(path: Path, parts: dict[str, str]) -> Path` ينشئ أرشيف zip بالأجزاء المعطاة.
  - `tmpdir()` سياق `tempfile.TemporaryDirectory` يعيد `Path`.

- [ ] **الخطوة ١: كتابة الاختبارات**
  - `test_script_source_is_ascii_only`: عدد الحروف التي رمزها أكبر من 127 في ملف الأداة يساوي 0.
  - `test_clean_text_exits_zero`: نص عربي سليم مع `ISSAI 100`، رمز الخروج `0`، والمخرجات تبدأ بـ `Clean`.
  - `test_unsupported_extension_exits_two`: ملف `.doc`، رمز الخروج `2`.
  - `test_fix_never_modifies_original`: محتوى الأصل بعد `--fix` مطابق بايتًا ببايت لما قبله.
- [ ] **الخطوة ٢:** تشغيل `python3 -m unittest tests.test_cli -v`. المتوقع: نجاح الأربعة.
- [ ] **الخطوة ٣: اختبار التعطيل:** إدراج حرف `chr(0x200F)` في تعليق داخل نسخة مؤقتة من الأداة، والتأكد من فشل `test_script_source_is_ascii_only` (يُنفَّذ ضمن المهمة ٦).
- [ ] **الخطوة ٤: إيداع** `test: add CLI harness and exit-code tests`

### المهمة ٢: الرموز غير المرئية

**الملفات:** إنشاء `tests/test_invisible.py`
**الواجهات:** تستهلك `run_cli` و`tmpdir` من المهمة ١.

- [ ] **الخطوة ١: كتابة الاختبارات** (كل اختبار يكتب ملف `.txt` ويشغّل `--fix` ويقرأ `_clean.txt`)
  - `test_removes_zero_width_and_directional`: `chr(0x200B)` و`chr(0x200F)` و`chr(0x202E)` و`chr(0x2066)` و`chr(0xFEFF)` غائبة من الناتج.
  - `test_removes_tag_characters`: `chr(0xE0041)` غائب.
  - `test_replaces_nbsp_and_curly_quotes`: `chr(0x00A0)` يصبح مسافة، و`chr(0x201C)` و`chr(0x201D)` يصبحان `"`.
  - `test_keeps_zwnj_and_reports_it`: `chr(0x200C)` باقٍ، والتقرير يتضمن `U+200C`.
  - `test_report_mode_exits_one_on_invisible`: رمز الخروج `1` دون `--fix`.
- [ ] **الخطوة ٢:** `python3 -m unittest tests.test_invisible -v`. المتوقع: نجاح الخمسة.
- [ ] **الخطوة ٣: إيداع** `test: cover invisible-character layer`

### المهمة ٣: العلامات المرئية والحروف الشبيهة وبقايا Markdown

**الملفات:** إنشاء `tests/test_text_layers.py`
**الواجهات:** تستهلك `run_cli` و`tmpdir`.

- [ ] **الخطوة ١: كتابة الاختبارات**
  - `test_em_dash_reported_not_removed`: `chr(0x2014)` باقٍ بعد `--fix`، والتقرير يذكر `EM DASH`.
  - `test_presentation_form_normalized`: `chr(0xFEFB)` يصبح `chr(0x0644)+chr(0x0627)`.
  - `test_farsi_yeh_reported_not_changed`: `chr(0x06CC)` باقٍ، والتقرير يذكر `FARSI YEH`.
  - `test_mixed_script_word_reported`: `"ISS" + chr(0x0410) + "I"` يرد في التقرير.
  - `test_txt_markdown_stripped`: نص بسطر `## عنوان` وسطر `- بند` و`**غامق**` وسطر `---`؛ الناتج خالٍ من `#` و`**` وبادئة `- ` وسطر الفاصل.
  - `test_single_asterisk_kept`: `الحاشية* سليمة` تبقى كما هي.
  - `test_md_file_markdown_untouched`: ملف `.md` بالمحتوى نفسه يبقى تنسيقه بعد `--fix`.
- [ ] **الخطوة ٢:** `python3 -m unittest tests.test_text_layers -v`. المتوقع: نجاح السبعة.
- [ ] **الخطوة ٣: إيداع** `test: cover visible, lookalike and markdown layers`

### المهمة ٤: ملفات Office وHTML وبيانات التعريف

**الملفات:** إنشاء `tests/test_office_html.py`
**الواجهات:** تستهلك `make_office` و`run_cli` و`tmpdir`.

- [ ] **الخطوة ١: كتابة الاختبارات** (الأرشيف يُبنى من أجزاء XML نصية دون مكتبة Word)
  - `test_docx_bold_markers_removed_from_document`: `word/document.xml` يحتوي `<w:t>**ملخص**</w:t>`؛ بعد `--fix` يصبح `<w:t>ملخص</w:t>`.
  - `test_docx_font_names_untouched`: `word/fontTable.xml` يحتوي اسم خط بحرف `chr(0xFF2D)`؛ يبقى بعد `--fix` ولا يرد في التقرير.
  - `test_generator_creator_cleared`: `<dc:creator>python-docx</dc:creator>` يصبح فارغًا.
  - `test_real_author_preserved`: `<dc:creator>آلاء الحمد</dc:creator>` يبقى كما هو.
  - `test_docx_without_docprops_works`: أرشيف بلا `docProps/`؛ رمز الخروج `0`. (محور المراجعة ٥)
  - `test_html_generator_meta_removed`: وسم `<meta name="generator" content="X">` غائب من الناتج.
  - `test_md_mentioning_meta_not_flagged`: ملف `.md` يذكر الوسم نصًا؛ رمز الخروج `0`.
- [ ] **الخطوة ٢:** `python3 -m unittest tests.test_office_html -v`. المتوقع: نجاح السبعة.
- [ ] **الخطوة ٣: إيداع** `test: cover office parts, metadata and html`

### المهمة ٥: المدخلات غير المتوقعة (إصلاح بالدورة الكاملة)

**الملفات:**
- إنشاء: `tests/test_bad_inputs.py`
- تعديل: `arabic-rtl-docs/scripts/check_hidden_chars.py` في الدالة `main()`

**الواجهات:** تستهلك `run_cli` و`make_office` و`tmpdir`.

- [ ] **الخطوة ١: كتابة الاختبارات الفاشلة**
  - `test_non_utf8_text_exits_two_with_message`: ملف `.txt` مرمز بـ `cp1256`؛ رمز الخروج `2`، والمخرجات تتضمن `UTF-8`، ولا تتضمن `Traceback`.
  - `test_missing_file_exits_two_with_message`: مسار غير موجود؛ رمز `2`، والمخرجات تتضمن `not found`، ولا `Traceback`.
  - `test_corrupt_docx_exits_two_with_message`: ملف `.docx` محتواه نص عادي؛ رمز `2`، والمخرجات تتضمن `not a valid`، ولا `Traceback`.
  - `test_arabic_filename_with_spaces`: ملف `تقرير الرقابة.txt`؛ `--fix` ينشئ `تقرير الرقابة_clean.txt`.
- [ ] **الخطوة ٢:** تشغيل `python3 -m unittest tests.test_bad_inputs -v`. المتوقع: فشل الثلاثة الأولى بسبب `Traceback`، ونجاح الرابع.
- [ ] **الخطوة ٣: التنفيذ:** في `main()`، التحقق من وجود الملف قبل القراءة، والتقاط `UnicodeDecodeError` و`zipfile.BadZipFile` وطباعة رسالة سطر واحد ثم إعادة `2`. الرسائل: `File not found: <path>`، و`File is not UTF-8 encoded: save it as UTF-8 and retry`، و`File is not a valid .docx/.pptx/.xlsx archive (corrupt or password-protected)`.
- [ ] **الخطوة ٤:** تشغيل المجموعة كاملة. المتوقع: نجاح الجميع.
- [ ] **الخطوة ٥: إيداع** `fix: report unreadable inputs clearly instead of crashing`

### المهمة ٦: إثبات قدرة الاختبارات على الفشل، والتوثيق

**الملفات:**
- إنشاء: `tests/mutation_check.py`
- تعديل: `README.md` (قسم جديد: تشغيل الاختبارات)

**الواجهات:** تستهلك وحدات الاختبار من المهام ١ إلى ٥.

- [ ] **الخطوة ١: كتابة سكربت التعطيل:** قائمة تعطيلات، كل منها `(وصف، نص أصلي، نص بديل)`؛ لكل تعطيل: نسخة مؤقتة من المستودع، تطبيق التعطيل على الأداة، تشغيل المجموعة، وتسجيل "مكتشف" إذا فشل اختبار واحد على الأقل. ينتهي برمز `1` إن بقي أي تعطيل غير مكتشف. التعطيلات:
  1. حذف `0x200B` من `REMOVE`.
  2. حذف `(0xE0000, 0xE007F, "TAG CHARACTER")` من `REMOVE_RANGES`.
  3. جعل `clean()` يحذف `review` بدل إبقائه.
  4. حذف `0x2014` من `VISIBLE` وإضافته إلى `REMOVE`.
  5. إلغاء التوحيد في `clean()` (إعادة الحرف كما هو).
  6. إلغاء شرط `text_part` في `clean()`.
  7. حذف `MD_BULLET.sub` من `md_clean_plain`.
  8. تطبيق `md_scan_plain` على ملفات `.md`.
  9. إلغاء `clean_meta`.
  10. إلغاء شرط `is_html` لفحص وسم المولّد.
  11. إدراج `chr(0x200F)` حرفيًا في تعليق.
  12. كتابة الناتج فوق الملف الأصلي بدل `_clean`.
- [ ] **الخطوة ٢:** تشغيل `python3 tests/mutation_check.py`. المتوقع: `12/12 mutations detected` ورمز `0`.
- [ ] **الخطوة ٣:** إضافة قسم "تشغيل الاختبارات" إلى `README.md` بالأمرين، وفحصه بالأداة نفسها (النتيجة `Clean`).
- [ ] **الخطوة ٤: إيداع** `test: add mutation check proving tests can fail; document test commands`
- [ ] **الخطوة ٥:** دفع الفرع، وعرض النتائج على المستخدم للاعتماد قبل الدمج.
