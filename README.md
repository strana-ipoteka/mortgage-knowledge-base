# База знаний отдела ипотеки

Самостоятельный сайт отдела ипотеки, подготовленный для размещения через GitHub Pages.

## Структура

- `index.html` — интерфейс сайта, фирменный стиль, навигация и разделы.
- `faq.json` — полный исходный перенос 73 вопросов и ответов из семи вкладок Google Таблицы. Сайт содержит встроенную копию данных, чтобы работать без дополнительных серверов.

## Источники

- Основная таблица: https://docs.google.com/spreadsheets/d/1bervkdHaLJ3pxrehY4G_qLvVCeVeH1L0IzIS3g5B4Ys/edit
- FAQ: https://docs.google.com/spreadsheets/d/1nhy86r5hGmg4fs37k9_97OYwFzjWPah6B04E_-PoC1s/edit
- Дизайн-референс: https://mikhailshevelev-dotcom.github.io/UOiI/

## Важные ограничения

Информация FAQ взята из рабочих таблиц без независимой юридической и банковской верификации. Перед использованием менеджерами требуется редакторская проверка актуальности. Не публикуйте персональные контакты сотрудников и секретные документы в открытом репозитории. Для актуализации FAQ требуется повторный импорт в `index.html` и `faq.json`.

## Публикация

GitHub → Settings → Pages → Build and deployment → Deploy from a branch → main / (root) → Save.

Адрес после включения Pages: https://strana-ipoteka.github.io/mortgage-knowledge-base/
