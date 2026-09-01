---
title: "Полное руководство по установке и автономному запуску конвейера «ДокСинтез»"
date: 2026-08-07T12:00:00+03:00
draft: false
image: "img/blog/installation-guide.webp"
author: "Инженер по внедрению ДокСинтез"
categories: ["Развертывание", "Инструкции", "Автоматизация"]
description: "Пошаговая инструкция по настройке Ollama, импорту GGUF моделей (GLM-OCR, BigBang), виртуального окружения Python и планировщика задач (cron / Task Scheduler) на Windows и Linux."
---

Система **«ДокСинтез»** полностью автономна и не требует подключения к внешним облачным сервисам. В этой статье приведено подробное руководство по локальному развертыванию конвейера на операционных системах **Linux** и **Windows**, включая установку локального нейросетевого сервера Ollama, загрузку и импорт специализированных GGUF-моделей с Hugging Face, настройку изолированного Python-окружения и запуск ночного регламентного аудита по расписанию.

---

## 1. Установка и запуск локального сервера Ollama

Локальный сервер Ollama отвечает за аппаратное исполнение нейросетевых моделей на процессоре (с поддержкой AVX2) или графическом ускорителе (NVIDIA / Apple Silicon).

### На Linux:
```bash
# Установка Ollama официальным скриптом
curl -fsSL https://ollama.com/install.sh | sh

# Проверка статуса службы
systemctl status ollama
```

### На Windows:
1. Скачайте инсталлятор с официального сайта [ollama.com/download/windows](https://ollama.com/download/windows).
2. Запустите инсталлятор и завершите установку.
3. Ollama автоматически запустится в системном трее и будет слушать локальный порт `http://127.0.0.1:11434`.

---

## 2. Загрузка моделей с Hugging Face и создание Modelfile

Для работы гибридного конвейера используются две квантованные модели:
1. **GLM-OCR**: Модель оптического распознавания текста и извлечения сложных табличных структур ([Hugging Face: ggml-org/GLM-OCR-GGUF](https://huggingface.co/ggml-org/GLM-OCR-GGUF)).
2. **BigBang-v1**: Модель семантического анализа, сопоставления номенклатуры и финансовой классификации ([Hugging Face: mradermacher/BigBang-v1-GGUF](https://huggingface.co/mradermacher/BigBang-v1-GGUF)).

### 2.1. Загрузка весов GGUF

Создайте каталог для хранения моделей и загрузите необходимые файлы:

#### Linux:
```bash
mkdir -p ~/models && cd ~/models

# Загрузка весов GLM-OCR
wget https://huggingface.co/ggml-org/GLM-OCR-GGUF/resolve/main/glm-ocr-q4_k_m.gguf

# Загрузка весов BigBang-v1
wget https://huggingface.co/mradermacher/BigBang-v1-GGUF/resolve/main/BigBang-v1.Q4_K_M.gguf
```

#### Windows (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path C:\Models
Set-Location C:\Models

# Загрузка GLM-OCR
Invoke-WebRequest -Uri "https://huggingface.co/ggml-org/GLM-OCR-GGUF/resolve/main/glm-ocr-q4_k_m.gguf" -OutFile "glm-ocr-q4_k_m.gguf"

# Загрузка BigBang-v1
Invoke-WebRequest -Uri "https://huggingface.co/mradermacher/BigBang-v1-GGUF/resolve/main/BigBang-v1.Q4_K_M.gguf" -OutFile "BigBang-v1.Q4_K_M.gguf"
```

### 2.2. Создание Modelfile и регистрация моделей в Ollama

Создайте файл `Modelfile_bigbang`:

```dockerfile
FROM ./BigBang-v1.Q4_K_M.gguf
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER num_ctx 8192
SYSTEM """Вы — строгий финансовый аудитор и эксперт по сопоставлению первичных бухгалтерских документов."""
```

Импортируйте модель семантического сопоставления:
```bash
ollama create bigbang:v1 -f Modelfile_bigbang
```

Создайте файл `Modelfile_glm_ocr`:

```dockerfile
FROM ./glm-ocr-q4_k_m.gguf
PARAMETER temperature 0.0
PARAMETER num_ctx 4096
```

Импортируйте модель оптического распознавания:
```bash
ollama create glm-ocr:v1 -f Modelfile_glm_ocr
```

Проверьте корректность регистрации моделей:
```bash
ollama list
```

---

## 3. Настройка окружения Python и установка зависимостей

Для работы скрипта требуется Python версии 3.10 или выше.

### Linux:
```bash
# Переход в рабочий каталог проекта
cd /opt/doksintez

# Создание изолированного виртуального окружения
python3 -m venv .venv

# Активация окружения
source .venv/bin/activate

# Установка библиотек
pip install --upgrade pip
pip install pdfplumber openpyxl pandas requests pillow tabulate
```

### Windows (PowerShell):
```powershell
# Переход в рабочий каталог проекта
Set-Location C:\DokSintez

# Создание виртуального окружения
python -m venv .venv

# Активация окружения
.\.venv\Scripts\Activate.ps1

# Установка библиотек
pip install --upgrade pip
pip install pdfplumber openpyxl pandas requests pillow tabulate
```

---

## 4. Запуск конвейера DokSintez.py

Скрипт готов к работе как с параметрами по умолчанию, так и с настраиваемыми аргументами командной строки:

### Запуск на Linux:
```bash
# Базовый запуск:
/opt/doksintez/.venv/bin/python3 /opt/doksintez/DokSintez.py

# Запуск с указанием кастомных каталогов и модели:
/opt/doksintez/.venv/bin/python3 /opt/doksintez/DokSintez.py \
  --model "bigbang:v1" \
  --ollama_url "http://127.0.0.1:11434" \
  --data_dir "/opt/doksintez/incoming_docs" \
  --reference "/opt/doksintez/Шаблон_отчета_по_подрядчикам.xlsx"
```

### Исполняемый bash-скрипт (`run_doksintez.sh`):
```bash
#!/bin/bash
source /opt/doksintez/.venv/bin/activate
python3 /opt/doksintez/DokSintez.py
read -n 1 -s -r -p "Нажмите любую клавишу для продолжения..."
```

### Запуск на Windows (PowerShell / CMD):
```powershell
# Базовый запуск:
C:\DokSintez\.venv\Scripts\python.exe C:\DokSintez\DokSintez.py

# Запуск с кастомными аргументами:
C:\DokSintez\.venv\Scripts\python.exe C:\DokSintez\DokSintez.py --model "bigbang:v1" --ollama_url "http://127.0.0.1:11434" --data_dir "C:\DokSintez\incoming_docs" --reference "C:\DokSintez\Шаблон_отчета_по_подрядчикам.xlsx"
```

### Исполняемый батник для Windows (`run_doksintez.bat`):
```cmd
@echo off
cd /d C:\DokSintez
call .venv\Scripts\activate.bat
python DokSintez.py
pause
```

---

## 5. Настройка ночного автоматического расписания (Nightly Runs)

Для реализации концепции **«Свежий отчет к завтраку»** обработка поступивших за день документов выполняется автоматически каждую ночь.

### 5.1. Настройка на Linux через `cron`

Откройте планировщик текущего пользователя:
```bash
crontab -e
```

Добавьте задание на запуск каждую ночь в 03:00:
```cron
# Запуск конвейера ДокСинтез каждую ночь в 03:00
0 3 * * * /opt/doksintez/.venv/bin/python3 /opt/doksintez/DokSintez.py >> /opt/doksintez/cron_execution.log 2>&1
```

### 5.2. Разовый отложенный запуск на Linux через `at`
```bash
echo "/opt/doksintez/.venv/bin/python3 /opt/doksintez/DokSintez.py" | at 03:30 tomorrow
```

### 5.3. Настройка на Windows через Планировщик заданий (Task Scheduler)

Создайте файл `nightly_audit.bat`:
```cmd
@echo off
cd /d C:\DokSintez
call .venv\Scripts\activate.bat
python DokSintez.py >> execution_nightly.log 2>&1
```

1. Нажмите сочетание клавиш `Win + R`, введите `taskschd.msc` и нажмите Enter.
2. В правой панели выберите **Создать простую задачу...** (Create Basic Task).
3. Задайте имя: `ДокСинтез - Ночной аудит первички`.
4. В качестве триггера укажите: **Ежедневно** в `03:00:00`.
5. Действие: **Запустить программу** -> выберите `C:\DokSintez\nightly_audit.bat`.
6. Сохраните задачу. Каждое утро к началу рабочего дня руководство и финансовый отдел получают актуальный верифицированный отчет в формате Excel.
