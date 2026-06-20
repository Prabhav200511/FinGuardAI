"""Natural-language fraud explanations via Groq with an offline fallback."""

from __future__ import annotations

import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_TOKENS = 220
TEMPERATURE = 0.2

_SYS_EN = (
    "You are FinGuard AI, a UPI fraud safety assistant for Indian users. "
    "Explain why the supplied transaction appears suspicious in exactly two short sentences. "
    "Use only the supplied risk indicators, avoid ML jargon, do not claim fraud is certain, "
    "and end with one concrete safety action."
)

_SYS_HI = (
    "आप FinGuard AI हैं, भारतीय उपयोगकर्ताओं के लिए UPI धोखाधड़ी सुरक्षा सहायक। "
    "दिए गए जोखिम संकेतों के आधार पर ठीक दो छोटे वाक्यों में सरल हिंदी में समझाएं कि लेनदेन संदिग्ध क्यों है। "
    "तकनीकी शब्दों से बचें, धोखाधड़ी को निश्चित न बताएं और अंत में एक स्पष्ट सुरक्षा कदम बताएं।"
)


def _normalize_language(language: str) -> str:
    return "hindi" if str(language).strip().lower() in {"hi", "hindi", "हिंदी"} else "english"


def _risky_features(pred: dict) -> list[dict]:
    features = [item for item in pred.get("top_features", []) if item.get("increases_risk")]
    return features or pred.get("top_features", [])[:2]


def _build_user_prompt(txn: dict, pred: dict, language: str) -> str:
    language = _normalize_language(language)
    indicators = _risky_features(pred)
    lines = "\n".join(
        f"- {item['label_en']}: {item['display_value']}"
        for item in indicators
    )
    return (
        f"Risk score: {pred.get('risk_score', 0):.0f}/100\n"
        f"Amount: ₹{float(txn.get('amount', 0)):,.0f}\n"
        f"Time: {int(txn.get('hour', 0)):02d}:00\n"
        f"Risk indicators:\n{lines}\n"
        f"Output language: {'simple Hindi' if language == 'hindi' else 'plain English'}"
    )


def _join_reasons(items: list[str], language: str) -> str:
    if not items:
        return "असामान्य गतिविधि" if language == "hindi" else "unusual account activity"
    if len(items) == 1:
        return items[0]
    connector = " और " if language == "hindi" else " and "
    return ", ".join(items[:-1]) + connector + items[-1]


def _offline_explanation(txn: dict, pred: dict, language: str) -> str:
    """Generate a faithful, deterministic explanation without an API key."""
    language = _normalize_language(language)
    reasons = []
    for item in _risky_features(pred):
        feature = item.get("feature")
        value = item.get("display_value", "")
        if language == "hindi":
            templates = {
                "amount": f"राशि {value} सामान्य से अलग है",
                "hour": f"भुगतान {value} बजे हुआ",
                "device_change": "भुगतान नए या बदले हुए डिवाइस से हुआ",
                "geo_distance_km": f"स्थान पिछले लेनदेन से {value} दूर है",
                "velocity_per_hour": f"एक घंटे में {value} लेनदेन हुए",
                "is_new_merchant": "प्राप्तकर्ता नया व्यापारी है",
                "merchant_category": f"व्यापारी श्रेणी {value} असामान्य है",
            }
        else:
            templates = {
                "amount": f"the {value} amount is unusual",
                "hour": f"the payment occurred at {value}",
                "device_change": "it came from a new or changed device",
                "geo_distance_km": f"the location is {value} from the previous transaction",
                "velocity_per_hour": f"there were {value} transactions in one hour",
                "is_new_merchant": "the recipient is a new merchant",
                "merchant_category": f"the {value} merchant category is unusual",
            }
        reasons.append(templates.get(feature, f"{item.get('label_en')}: {value}"))

    joined = _join_reasons(reasons[:3], language)
    if language == "hindi":
        return (
            f"यह लेनदेन संदिग्ध दिखता है क्योंकि {joined}। "
            "यदि आपने भुगतान शुरू नहीं किया है तो UPI PIN न डालें और तुरंत अपने बैंक से संपर्क करें।"
        )
    return (
        f"This transaction looks suspicious because {joined}. "
        "If you did not initiate it, do not enter your UPI PIN and contact your bank immediately."
    )


def _call_groq(txn: dict, pred: dict, language: str) -> str:
    language = _normalize_language(language)
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return _offline_explanation(txn, pred, language)

    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": _SYS_HI if language == "hindi" else _SYS_EN},
                        {"role": "user", "content": _build_user_prompt(txn, pred, language)},
                    ],
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                },
            )
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"].strip()
            return text or _offline_explanation(txn, pred, language)
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return _offline_explanation(txn, pred, language)


def get_explanation(txn: dict, pred: dict, language: str = "english") -> str:
    return _call_groq(txn, pred, language)


async def get_explanation_async(txn: dict, pred: dict, language: str = "english") -> str:
    return await asyncio.to_thread(_call_groq, txn, pred, language)
