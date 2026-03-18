"""
سكريبت تجريبي للتحدث مع مدرس الألماني مباشرةً.
يطلب منك مفتاح API إن لم يكن موجوداً في .env

تشغيل:
    python test_live.py
"""

import asyncio
import json
import os
import sys

# ── تحقق من وجود مفتاح API ────────────────────────────────────────────────────
if not os.environ.get("ANTHROPIC_API_KEY"):
    key = input("أدخل ANTHROPIC_API_KEY: ").strip()
    if not key:
        print("❌ لا يمكن المتابعة بدون مفتاح API")
        sys.exit(1)
    os.environ["ANTHROPIC_API_KEY"] = key

# ── استيراد الـ Agent بعد ضبط المفتاح ────────────────────────────────────────
from app.agents.german_teacher.agent import GermanTeacherAgent  # noqa: E402


TASKS = {
    "1": "correct_writing",
    "2": "explain_grammar",
    "3": "free_chat",
}

TASK_LABELS = {
    "correct_writing": "تصحيح كتابة",
    "explain_grammar": "شرح قاعدة",
    "free_chat": "محادثة حرة",
}

LEVELS = ["A1", "A2", "B1", "B2"]


def pick_option(prompt: str, options: list[str]) -> str:
    print(f"\n{prompt}")
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        choice = input("اختيارك: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("اختيار غير صحيح، حاول مجدداً.")


async def run():
    agent = GermanTeacherAgent()

    print("\n" + "=" * 55)
    print("  🇩🇪  مدرس الألماني JYRY AI — وضع التجربة")
    print("=" * 55)

    while True:
        # ── اختيار المهمة ─────────────────────────────────────────
        task = pick_option(
            "اختر نوع المهمة:",
            list(TASK_LABELS.values()),
        )
        task_key = {v: k for k, v in TASK_LABELS.items()}[task]

        # ── اختيار المستوى ────────────────────────────────────────
        level = pick_option("اختر مستوى الطالب:", LEVELS)

        # ── اختيار لغة الشرح ─────────────────────────────────────
        lang = pick_option("لغة الشرح:", ["ar (عربي)", "de (ألماني)", "en (إنجليزي)"])
        lang = lang.split()[0]

        # ── النص ─────────────────────────────────────────────────
        hints = {
            "correct_writing": "اكتب جملة أو فقرة بالألماني لتصحيحها",
            "explain_grammar": "اكتب موضوع القاعدة (مثال: Akkusativ, Perfekt)",
            "free_chat": "اكتب سؤالك أو رسالتك",
        }
        print(f"\n💬 {hints[task_key]}:")
        text = input("> ").strip()
        if not text:
            print("النص فارغ، تخطي.")
            continue

        payload = {"task": task_key, "level": level, "text": text, "language": lang}

        print("\n⏳ جاري الاتصال بـ Claude...")
        try:
            result = await agent.process(payload)
        except Exception as exc:
            print(f"❌ خطأ: {exc}")
            continue

        # ── عرض النتيجة ──────────────────────────────────────────
        print("\n" + "─" * 55)

        if task_key == "correct_writing":
            if result.get("corrected_text"):
                print(f"✏️  النص المصحح:\n  {result['corrected_text']}")
            if result.get("corrections"):
                print("\n📌 التصحيحات:")
                for c in result["corrections"]:
                    print(f"  • {c}")
            if result.get("score"):
                s = result["score"]
                print(
                    f"\n🏅 التقييم: {s['total']}/100"
                    f"  (قواعد {s['grammar']} | مفردات {s['vocabulary']}"
                    f" | تركيب {s['structure']} | وضوح {s['clarity']})"
                )
            if result.get("encouragement"):
                print(f"\n🌟 {result['encouragement']}")

        print(f"\n💡 الشرح:\n{result.get('explanation', '')}")
        print(f"\n🤖 النموذج: {result.get('model_used', '')}")
        print("─" * 55)

        again = input("\nتريد تجربة أخرى؟ (y/n): ").strip().lower()
        if again != "y":
            print("\nإلى اللقاء! Auf Wiedersehen! 👋")
            break


if __name__ == "__main__":
    asyncio.run(run())
