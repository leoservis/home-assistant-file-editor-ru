# File editor — русский

Русская версия приложения File editor для Home Assistant. Это отдельное приложение: оно не заменяет и не изменяет официальный File editor.

## Установка из репозитория Home Assistant

1. В GitHub создайте публичный репозиторий `home-assistant-file-editor-ru` и загрузите в корень файлы этого проекта.
2. В Home Assistant откройте **Настройки → Дополнения → Магазин дополнений**.
3. Через меню с тремя точками выберите **Репозитории**, добавьте адрес:
   `https://github.com/leoservis/home-assistant-file-editor-ru`
4. Найдите **File editor — русский**, установите и запустите приложение.

Home Assistant собирает приложение из `Dockerfile` при установке. Сейчас в манифесте указана архитектура `amd64`.

## Сборка Docker-образа вручную

```sh
docker build -t local/configurator-ru:6.3.0-ru.1 .
```

При выпуске новой версии обновите `version` в `config.yaml`.

## Состав и лицензии

Приложение основано на [Home Assistant app-configurator](https://github.com/home-assistant/app-configurator) версии 6.3.0. В него включён пакет [hass-configurator](https://github.com/danielperna84/hass-configurator) версии 0.7.0. Сохраняйте соответствующие уведомления об авторских правах и лицензии: `LICENSE` и `hass_configurator/LICENSE.txt`.

Перевод интерфейса находится в `hass_configurator/hass_configurator/ru.js`; переводы параметров приложения — в `translations/ru.yaml`.

## Безопасность

Не добавляйте в репозиторий конфигурацию Home Assistant, пароли, токены, закрытые SSH-ключи или личные резервные копии. Для Git-операций по SSH приложение принимает ключи, указанные в настройках самого приложения.
