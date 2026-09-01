---
title: "Полное руководство по установке и автономному запуску конвейера «ДокСинтез»"
date: 2026-08-07T12:00:00+03:00
draft: false
image: "img/blog/installation-guide.webp"
author: "Инженер по внедрению ДокСинтез"
categories: ["Развертывание", "Инструкции", "Автоматизация"]
description: "Пошаговая инструкция по настройке Ollama, импорту GGUF моделей (GLM-OCR, BigBang), виртуального окружения Python и планировщика задач (cron / Task Scheduler) на Windows и Linux."
---

Система **«ДокСинтез»** полностью автономна и не требует подключения к внешним облачным сервисам. В этой статье приведена подробная инструкция по локальному развертыванию конвейера на операционных системах **Linux** и **Windows**, включая установку локального нейросетевого сервера Ollama, импорт специализированных GGUF-моделей с Hugging Face, настройку Python-окружения и запуск ночного регламентного аудита.

![Архитектура локального конвейера и автоматизации](/img/blog/installation-guide.webp)

---

## 1. Установка и подготовка локального сервера Ollama

Локальный сервер Ollama отвечает за локальное исполнение нейросетевых моделей без выхода в сеть.

### На Linux:
```bash
# Установка Ollama в одну команду
curl -fsSL https://ollama.com/install.sh | sh

# Проверка статуса сервиса
systemctl status ollama
```

### На Windows:
1. Скачайте официальный инсталлятор с сайта [ollama.com/download/windows](https://ollama.com/download/windows).
2. Запустите `.exe` установщик и завершите установку.
3. Ollama запустится в фоновом режиме (иконка появится в системном трее) и будет доступна по адресу `http://127.0.0.1:11434`.

---

## 2. Загрузка моделей с Hugging Face и создание Modelfile

Для работы конвейера используются две модели:
1. **GLM-OCR**: Модель высокоточного оптического распознавания текста, штампов и сложных таблиц ([Hugging Face: ggml-org/GLM-OCR-GGUF](https://huggingface.co/ggml-org/GLM-OCR-GGUF)).
2. **BigBang-v1**: Модель семантического анализа, сопоставления номенклатуры и классификации статей ([Hugging Face: mradermacher/BigBang-v1-GGUF](https://huggingface.co/mradermacher/BigBang-v1-GGUF)).

### 2.1. Загрузка GGUF-файлов

Создайте рабочую директорию для моделей и скачайте необходимые квантованные веса:

```bash
mkdir -p ~/models && cd ~/models

# Загрузка GLM-OCR GGUF
wget https://huggingface.co/ggml-org/GLM-OCR-GGUF/resolve/main/glm-ocr-q4_k_m.gguf

# Загрузка BigBang-v1 GGUF
wget https://huggingface.co/mradermacher/BigBang-v1-GGUF/resolve/main/BigBang-v1.Q4_K_M.gguf
```

### 2.2. Импорт моделей в Ollama через Modelfile

Создайте файл манифеста `Modelfile_bigbang`:

```dockerfile
FROM ./BigBang-v1.Q4_K_M.gguf
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER num_ctx 8192
SYSTEM """Вы — строгий финансовый аудитор и эксперт по сопоставлению первичных бухгалтерских документов."""
```

Импортируйте модель в реестр Ollama:

```bash
ollama create bigbang:v1 -f Modelfile_bigbang
```

Аналогично импортируйте модель распознавания:

```dockerfile
FROM ./glm-ocr-q4_k_m.gguf
PARAMETER temperature 0.0
PARAMETER num_ctx 4096
```

```bash
ollama create glm-ocr:v1 -f Modelfile_glm_ocr
```

Проверьте наличие созданных моделей:
```bash
ollama list
```

---

## 3. Настройка окружения Python и установка зависимостей

Конвейер требует Python версии 3.10 или выше.

### Linux / macOS:
```bash
# Переход в директорию проекта
cd /home/grapeonwheels/Documents/CBRE

# Создание виртуального окружения
python3 -m venv .venv

# Активация окружения
source .venv/bin/activate

# Обновление pip и установка библиотек
pip install --upgrade pip
pip install pdfplumber openpyxl pandas requests pillow tabulate
```

### Windows (PowerShell):
```powershell
cd C:\CBRE\DokSintez
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pdfplumber openpyxl pandas requests pillow tabulate
```

---

## 4. Запуск скрипта DokSintez.py

Скрипт поддерживает как запуск со стандартными параметрами (по умолчанию используются локальный хост Ollama `http://127.0.0.1:11434` и модель `bigbang:v1`), так и запуск с кастомными аргументами командной строки:

```bash
# Базовый запуск в виртуальном окружении:
python3 /home/grapeonwheels/Documents/CBRE/DokSintez.py

# Запуск с указанием конкретной модели и пути к данным:
python3 /home/grapeonwheels/Documents/CBRE/DokSintez.py \
  --model "bigbang:v1" \
  --ollama_url "http://127.0.0.1:11434" \
  --data_dir "/home/grapeonwheels/Documents/CBRE/june" \
  --reference "/home/grapeonwheels/Documents/CBRE/Шаблон отчета по подрядчикам.xlsx"
```

### Исполняемый bash-скрипт для ручного запуска (`run_doksintez.sh`):

```bash
#!/bin/bash
source /home/grapeonwheels/Documents/CBRE/.venv/bin/activate
python3 /home/grapeonwheels/Documents/CBRE/DokSintez.py
read -n 1 -s -r -p "Нажмите любую клавишу для продолжения..."
```

---

## 5. Настройка ночного автоматического расписания (Nightly Runs)

Для реализации концепции **«Свежий отчет к завтраку»** обработка входящей первички запускается автоматически каждую ночь.

### 5.1. Настройка через `cron` в Linux

Откройте редактор расписания текущего пользователя:
```bash
crontab -e
```

Добавьте задачу на запуск каждую ночь в 03:00:
```cron
# Запуск конвейера ДокСинтез каждую ночь в 03:00
0 3 * * * /home/grapeonwheels/Documents/CBRE/.venv/bin/python3 /home/grapeonwheels/Documents/CBRE/DokSintez.py >> /home/grapeonwheels/Documents/CBRE/cron_execution.log 2>&1
```

### 5.2. Однократный отложенный запуск через `at` (Linux)
Если требуется запланировать разовый запуск на ближайшую ночь:
```bash
echo "/home/grapeonwheels/Documents/CBRE/.venv/bin/python3 /home/grapeonwheels/Documents/CBRE/DokSintez.py" | at 03:30 tomorrow
```

### 5.3. Настройка в Windows через Планировщик заданий (Task Scheduler)

Создайте файл `nightly_run.bat`:
```cmd
@echo off
cd /d C:\CBRE\DokSintez
call .venv\Scripts\activate.bat
python DokSintez.py >> execution_nightly.log 2>&1
```

1. Нажмите `Win + R`, введите `taskschd.msc` и нажмите Enter.
2. В правом меню выберите **Создать простую задачу...** (Create Basic Task).
3. Укажите имя: `ДокСинтез - Ночной аудит первички`.
4. Триггер: **Ежедневно**, время: `03:00:00`.
5. Действие: **Запустить программу** -> укажите путь к `C:\CBRE\DokSintez\nightly_run.bat`.
6. Готово! Теперь каждое утро к началу рабочего дня руководство и бухгалтерия получают готовый свежий отчет в формате Excel.
