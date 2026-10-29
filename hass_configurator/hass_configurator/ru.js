(function () {
  const translations = {
    "HASS Configurator": "Редактор файлов",
    "HASS Configurator - Error": "Редактор файлов — ошибка",
    "Browse Filesystem": "Обзор файлов",
    "File History": "История файлов",
    "Save": "Сохранить",
    "Close": "Закрыть",
    "Search": "Поиск",
    "New tab": "Новая вкладка",
    "Theme: Auto": "Тема: автоматически",
    "Theme: Light": "Тема: светлая",
    "Theme: Dark": "Тема: тёмная",
    "Theme": "Тема",
    "Help": "Справка",
    "Keyboard Shortcuts": "Горячие клавиши",
    "Prompt before save": "Запрашивать подтверждение перед сохранением",
    "Hide details in browser": "Скрывать подробности в браузере",
    "Animated Scroll": "Плавная прокрутка",
    "Behaviour Enabled": "Включить поведение редактора",
    "Display Indent Guides": "Показывать направляющие отступов",
    "Fade Fold Widgets": "Затемнять элементы сворачивания",
    "Font Size": "Размер шрифта",
    "Highlight Active Line": "Подсвечивать текущую строку",
    "Highlight Gutter Line": "Подсвечивать строку в поле номеров",
    "Highlight Selected Word": "Подсвечивать выбранное слово",
    "H Scroll Bar Always Visible": "Всегда показывать горизонтальную прокрутку",
    "Keyboard Handler": "Обработчик клавиатуры",
    "Mode": "Режим",
    "Auto": "Автоматически",
    "New Line Mode": "Символ перевода строки",
    "Read Only": "Только чтение",
    "Scroll Speed": "Скорость прокрутки",
    "Show Fold Widgets": "Показывать элементы сворачивания",
    "Show Gutter": "Показывать поле номеров строк",
    "Show Invisibles": "Показывать невидимые символы",
    "Show Print Margin": "Показывать границу печати",
    "Show Line Numbers": "Показывать номера строк",
    "Save Settings Locally": "Сохранить настройки локально",
    "V Scroll Bar Always Visible": "Всегда показывать вертикальную прокрутку",
    "Wrap Behaviours Enabled": "Включить перенос строк",
    "Wrap Mode": "Режим переноса строк",
    "Wrap Limit": "Ширина переноса",
    "Light Themes": "Светлые темы",
    "Dark Themes": "Тёмные темы",
    "Branch:": "Ветка:",
    "Trigger Platforms": "Платформы триггеров",
    "Add": "Добавить",
    "Numeric state": "Числовое состояние",
    "Trigger": "Триггер",
    "Components": "Интеграции",
    "Material Icons": "Material Icons",
    "Editor Settings": "Настройки редактора",
    "Network status": "Состояние сети",
    "About HASS Configurator": "О редакторе файлов",
    "Observe events": "Просмотр событий",
    "Reload automations": "Перезагрузить автоматизации",
    "Reload scripts": "Перезагрузить скрипты",
    "Reload groups": "Перезагрузить группы",
    "Reload core": "Перезагрузить ядро",
    "Check Home Assistant Configuration": "Проверить конфигурацию Home Assistant",
    "Restart Home Assistant": "Перезапустить Home Assistant",
    "Execute shell command": "Выполнить команду оболочки",
    "Toggle Home Assistant panel": "Показать или скрыть панель Home Assistant",
    "Generate UUID": "Создать UUID",
    "Git": "Git",
    "git init": "Инициализировать Git",
    "git commit": "Создать коммит",
    "git push": "Отправить изменения",
    "git stash": "Временно сохранить изменения",
    "Ace Keyboard Shortcuts": "Горячие клавиши редактора",
    "Line Operations": "Операции со строками",
    "Selection": "Выделение",
    "Multicursor": "Несколько курсоров",
    "Go To": "Переход",
    "Find/Replace": "Поиск и замена",
    "Folding": "Сворачивание кода",
    "Other": "Другое",
    "Windows/Linux": "Windows/Linux",
    "Mac": "Mac",
    "Action": "Действие",
    "Remove line": "Удалить строку",
    "Copy lines down": "Копировать строки вниз",
    "Copy lines up": "Копировать строки вверх",
    "Move lines down": "Переместить строки вниз",
    "Move lines up": "Переместить строки вверх",
    "Remove to line end": "Удалить до конца строки",
    "Remove to linestart": "Удалить до начала строки",
    "Remove word left": "Удалить слово слева",
    "Remove word right": "Удалить слово справа",
    "Split line": "Разделить строку",
    "Select all": "Выделить всё",
    "Select left": "Выделить слева",
    "Select right": "Выделить справа",
    "Select word left": "Выделить слово слева",
    "Select word right": "Выделить слово справа",
    "Select line start": "Выделить до начала строки",
    "Select line end": "Выделить до конца строки",
    "Select to line end": "Выделить до конца строки",
    "Select to line start": "Выделить до начала строки",
    "Select up": "Выделить выше",
    "Select down": "Выделить ниже",
    "Select page up": "Выделить страницу выше",
    "Select page down": "Выделить страницу ниже",
    "Select to start": "Выделить до начала",
    "Select to end": "Выделить до конца",
    "Duplicate selection": "Дублировать выделение",
    "Select to matching bracket": "Выделить до парной скобки",
    "Add multi-cursor above": "Добавить курсор выше",
    "Add multi-cursor below": "Добавить курсор ниже",
    "Add next occurrence to multi-selection": "Добавить следующее совпадение к выделению",
    "Add previous occurrence to multi-selection": "Добавить предыдущее совпадение к выделению",
    "Move multicursor from current line to the line above": "Переместить курсор на строку выше",
    "Move multicursor from current line to the line below": "Переместить курсор на строку ниже",
    "Remove current occurrence from multi-selection and move to next": "Убрать совпадение из выделения и перейти к следующему",
    "Remove current occurrence from multi-selection and move to previous": "Убрать совпадение из выделения и перейти к предыдущему",
    "Select all from multi-selection": "Выделить все совпадения",
    "Go to left": "Перейти влево",
    "Go to right": "Перейти вправо",
    "Go to word left": "Перейти на слово влево",
    "Go to word right": "Перейти на слово вправо",
    "Go line up": "Перейти на строку выше",
    "Go line down": "Перейти на строку ниже",
    "Go to line start": "Перейти в начало строки",
    "Go to line end": "Перейти в конец строки",
    "Go to page up": "Перейти на страницу выше",
    "Go to page down": "Перейти на страницу ниже",
    "Go to start": "Перейти в начало",
    "Go to end": "Перейти в конец",
    "Go to line": "Перейти к строке",
    "Scroll line down": "Прокрутить на строку вниз",
    "Scroll line up": "Прокрутить на строку вверх",
    "Go to matching bracket": "Перейти к парной скобке",
    "Scroll page down": "Прокрутить на страницу вниз",
    "Scroll page up": "Прокрутить на страницу вверх",
    "Find": "Найти",
    "Replace": "Заменить",
    "Find next": "Найти следующее",
    "Find previous": "Найти предыдущее",
    "Fold selection": "Свернуть выделенное",
    "Unfold": "Развернуть",
    "Fold all": "Свернуть всё",
    "Unfold all": "Развернуть всё",
    "Indent": "Добавить отступ",
    "Outdent": "Уменьшить отступ",
    "Undo": "Отменить",
    "Redo": "Повторить",
    "Show the settings menu": "Показать меню настроек",
    "Toggle comment": "Включить или выключить комментарий",
    "Transpose letters": "Поменять буквы местами",
    "Enter full screen": "Перейти в полноэкранный режим",
    "Change to lower case": "Преобразовать в нижний регистр",
    "Change to upper case": "Преобразовать в верхний регистр",
    "Overwrite": "Заменить символ",
    "Macros replay": "Воспроизвести макрос",
    "Macros recording": "Записать макрос",
    "Center selection": "Поместить выделение по центру",
    "Event Observer": "Просмотр событий",
    "Websocket URI": "Адрес WebSocket",
    "API password": "Пароль API",
    "Connect": "Подключиться",
    "Disconnect": "Отключиться",
    "Do you really want to save?": "Сохранить изменения?",
    "No": "Нет",
    "Yes": "Да",
    "Upload File": "Загрузить файл",
    "Please choose a file to upload": "Выберите файл для загрузки",
    "File": "Файл",
    "Cancel": "Отмена",
    "OK": "ОК",
    "Are you sure you want to initialize a repository at the current path?": "Создать репозиторий в текущей папке?",
    "Commit message": "Сообщение коммита",
    "Are you sure you want to push your commited changes to the configured remote / origin?": "Отправить сохранённые изменения в настроенный удалённый репозиторий?",
    "Are you sure you want to stash your changes?": "Временно сохранить изменения?",
    "Close File": "Закрыть файл",
    "Are you sure you want to close the current file? Unsaved changes will be lost.": "Закрыть файл? Несохранённые изменения будут потеряны.",
    "Rename": "Переименовать",
    "Please enter a new name for": "Введите новое имя для",
    "Apply": "Применить",
    "Delete": "Удалить",
    "Are you sure you want to delete": "Удалить",
    "Are you sure you want to add": "Добавить",
    "to the index?": "в индекс Git?",
    "Check configuration": "Проверка конфигурации",
    "Do you want to check the configuration?": "Проверить конфигурацию?",
    "Do you want to reload the automations?": "Перезагрузить автоматизации?",
    "Do you want to reload the scripts?": "Перезагрузить скрипты?",
    "Do you want to reload the groups?": "Перезагрузить группы?",
    "Do you want to reload the core?": "Перезагрузить ядро?",
    "Restart": "Перезапуск",
    "Do you really want to restart Home Assistant?": "Перезапустить Home Assistant?",
    "Remove allowed network / IP": "Удаление разрешённой сети или IP-адреса",
    "Do you really want to remove the network / IP": "Удалить сеть или IP-адрес",
    "from the list of allowed networks?": "из списка разрешённых сетей?",
    "Add allowed network / IP": "Добавление разрешённой сети или IP-адреса",
    "Do you really want to Add the network / IP": "Добавить сеть или IP-адрес",
    "to the list of allowed networks?": "в список разрешённых сетей?",
    "Unban IP": "Разблокировка IP-адреса",
    "Do you really want to unban the IP": "Разблокировать IP-адрес",
    "Ban IP": "Блокировка IP-адреса",
    "Do you really want to ban the IP": "Заблокировать IP-адрес",
    "Command": "Команда",
    "Clear": "Очистить",
    "Execute": "Выполнить",
    "Unsaved Changes": "Несохранённые изменения",
    "You have unsaved changes in the current file. Please save the changes or close the file before opening a new one.": "В текущем файле есть несохранённые изменения. Сохраните их или закройте файл перед открытием нового.",
    "Abort": "Отмена",
    "Close file": "Закрыть файл",
    "Save changes": "Сохранить изменения",
    "New Folder": "Новая папка",
    "New Folder Name": "Имя новой папки",
    "New File": "Новый файл",
    "New File Name": "Имя нового файла",
    "New Branch": "Новая ветка",
    "New Branch Name": "Имя новой ветки",
    "Your address:": "Ваш адрес:",
    "Listening address:": "Адрес прослушивания:",
    "Home Assistant API address:": "Адрес API Home Assistant:",
    "Modifying the following lists is not persistent. To statically control access please use the configuration file.": "Изменения этих списков не сохраняются после перезапуска. Для постоянной настройки доступа измените файл конфигурации.",
    "Add network / IP": "Добавить сеть или IP-адрес",
    "Web-based file editor designed to modify configuration files of": "Веб-редактор для изменения файлов конфигурации",
    "or other textual files. Use at your own risk.": "и других текстовых файлов. Используйте на свой страх и риск.",
    "Published under the MIT license": "Распространяется по лицензии MIT",
    "Developed by:": "Разработчики:",
    "Contact Person": "Контактное лицо",
    "Libraries used:": "Используемые библиотеки:",
    "Ace Editor": "Редактор Ace",
    "Select trigger platform": "Выберите платформу триггера",
    "Calendar": "Календарь",
    "Sentence": "Фраза",
    "Event": "Событие",
    "Geo location": "Геолокация",
    "Home Assistant": "Home Assistant",
    "MQTT": "MQTT",
    "Numeric State": "Числовое состояние",
    "State": "Состояние",
    "Sun": "Солнце",
    "Tag": "Метка",
    "Template": "Шаблон",
    "Time": "Время",
    "Time pattern": "Шаблон времени",
    "Persistent notification": "Постоянное уведомление",
    "Webhook": "Веб-перехватчик",
    "Zone": "Зона",
    "Trigger platforms": "Платформы триггеров",
    "Events": "События",
    "Search entity": "Поиск сущности",
    "Entities": "Сущности",
    "Select condition": "Выберите условие",
    "Conditions": "Условия",
    "Services": "Службы",
    "Configuration seems valid.": "Ошибок в конфигурации не найдено.",
    "Unable to check configuration.": "Не удалось проверить конфигурацию.",
    "Automations reloaded": "Автоматизации перезагружены",
    "Scripts reloaded": "Скрипты перезагружены",
    "Groups reloaded": "Группы перезагружены",
    "Core reloaded": "Ядро перезагружено",
    "Restarting Home Assistant": "Перезапуск Home Assistant",
    "Error:  Please provide a filename": "Ошибка: укажите имя файла",
    "Could not save theme preference": "Не удалось сохранить настройки темы",
    "Ace Settings Saved": "Настройки редактора сохранены",
    "Configuration seems valid": "Ошибок в конфигурации не найдено",
    "Theme:": "Тема:",
    "New File": "Новый файл",
    "New Folder": "Новая папка",
    "Git": "Git"
  };

  const translatedAttributes = [
    "data-tooltip",
    "title",
    "placeholder",
    "aria-label",
  ];

  function isEditorContent(node) {
    const element = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
    return element?.closest(
      "#editor, .ace_editor, .ace_text-input, script, style, textarea, input, [contenteditable='true']",
    );
  }

  function translateText(node) {
    if (isEditorContent(node)) {
      return;
    }

    const original = node.nodeValue;
    const trimmed = original.trim().replace(/\s+/g, " ");
    const translated = translations[trimmed];
    if (translated) {
      const start = original.indexOf(original.trim());
      const end = original.length - (start + original.trim().length);
      node.nodeValue = `${original.slice(0, start)}${translated}${original.slice(original.length - end)}`;
    }
  }

  function translateElement(element) {
    if (
      element.matches(
        "#editor, .ace_editor, .ace_text-input, script, style, textarea, input, [contenteditable='true']",
      )
    ) {
      return;
    }

    for (const attribute of translatedAttributes) {
      const value = element.getAttribute(attribute);
      if (value && translations[value.trim()]) {
        element.setAttribute(attribute, translations[value.trim()]);
      }
    }

    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      translateText(walker.currentNode);
    }
  }

  function translateNode(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      translateText(node);
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      translateElement(node);
    }
  }

  document.documentElement.lang = "ru";
  translateElement(document.body);

  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === "attributes") {
        translateElement(mutation.target);
      } else {
        for (const node of mutation.addedNodes) {
          translateNode(node);
        }
      }
    }
  }).observe(document.body, {
    attributes: true,
    attributeFilter: translatedAttributes,
    childList: true,
    subtree: true,
  });
})();
