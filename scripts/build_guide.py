#!/usr/bin/env python3
"""Assemble the launch guide from the per-stage rule files produced by subagents.

Input:  stages/out_a_nisha.md, out_b_offer.md, out_c_clients.md, out_d_traffic.md,
        out_e_product.md, out_f_errors.md, out_g_cases.md
Output: GID.md (russian: Гайд) — step-by-step guide with citations.
"""
import os
import re

OUT_DIR = "/home/openclaw/.hermes/cache/scratch/tg/stages"
DEST = "/home/openclaw/projects/pdf-limit/GUIDE-ZAPUSK.md"

STAGES = [
    ("Шаг 1. Выбрать нишу и проверить спрос трафиком", "out_a_nisha.md"),
    ("Шаг 2. Собрать оффер, лендинг и цену", "out_b_offer.md"),
    ("Шаг 3. Взять первых клиентов", "out_c_clients.md"),
    ("Шаг 4. Включить платный трафик", "out_d_traffic.md"),
    ("Шаг 5. Собрать продукт минимального объёма", "out_e_product.md"),
    ("Шаг 6. Что считать и когда останавливаться", "out_f_errors.md"),
]

HEADER = """# Гайд: как запустить проект

Собрано из 1 429 постов двух телеграм-каналов: @your_pet_project (648 постов) и @bossofyourboss (781 пост), разобраны 19.10.2026. Из 996 отдельных пунктов базы знаний слиты в {rules} правил: повторы и полудубли схлопнуты, каждая мысль подтверждена номерами постов и цитатой.

Каждое правило: формулировка, цитата из поста с номером, и сколько ещё постов говорят то же самое. Пометка «(пересказ)» означает, что дословной цитаты в базе нет — мысль восстановлена по пересказу агента.

Приложение с цифрами — в конце: {proofs} пруфов по типам продуктов.

"""

FOOTER = """
## Приложение: пруфы с цифрами

{proofs_body}

---
Источник: TG-PETPROJECT-KB.md — полная база с 1 026 пунктами, их статусами сверки и всеми цитатами.
"""

def load(name):
    p = os.path.join(OUT_DIR, name)
    if not os.path.exists(p):
        return None
    return open(p, encoding="utf-8").read().strip()

def count_rules(text):
    return len(re.findall(r"^ПРАВИЛО:", text or "", re.M))

def main():
    parts, total, missing = [], 0, []
    for title, fname in STAGES:
        body = load(fname)
        if body is None:
            missing.append(fname)
            continue
        # единый вид: убираем заголовки агентов, оставляем правила
        body = re.sub(r"^#{1,3} .*$", "", body, flags=re.M).strip()
        body = re.sub(r"\n{3,}", "\n\n", body)
        n = count_rules(body)
        total += n
        parts.append(f"## {title} — {n} правил\n\n{body}\n")
    proofs = load("out_g_cases.md") or "(пруфы не собраны)"
    proofs_n = len(re.findall(r"^ТИП:", proofs, re.M))
    doc = HEADER.format(rules=total, proofs=proofs_n) + "\n".join(parts) + FOOTER.format(proofs_body=proofs)
    open(DEST, "w", encoding="utf-8").write(doc)
    print(f"правил: {total} | пруфов: {proofs_n} | размер: {os.path.getsize(DEST)} байт")
    if missing:
        print("не хватает файлов:", ", ".join(missing))

if __name__ == "__main__":
    main()
