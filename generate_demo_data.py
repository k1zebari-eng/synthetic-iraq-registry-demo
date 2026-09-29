from __future__ import annotations

import csv
import json
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

OUTPUT_DIR = Path("demo_output")
RECORD_COUNT = 1000
RANDOM_SEED = 20260929

random.seed(RANDOM_SEED)

CITY_DATA = {
    "کوردستان": {
        "هەولێر": ["هەولێر", "شەقڵاوە", "سۆران", "ڕاوندوز", "کۆیە", "چۆمان"],
        "سلێمانی": ["سلێمانی", "ڕانیە", "کەلار", "چەمچەماڵ", "پێنجوێن", "دەربەندیخان"],
        "دهۆک": ["دهۆک", "زاخۆ", "ئامێدی", "ئاکرێ", "سیمێلە", "بارزان"],
        "هەڵەبجە": ["هەڵەبجە", "تاوێڵە"],
    },
    "عێراق": {
        "بغداد": ["بغداد", "ئەبوغورەیب", "مەحمودیە", "تاجی"],
        "نینەوا": ["موسڵ", "تەل ئەفەر", "سەنجار", "قەرەقۆش", "باشیقە"],
        "کەرکووک": ["کەرکووک", "حەویجە", "داقوق", "دبس"],
        "بەسرە": ["بەسرە", "زوبەیر", "ئوم قەسر"],
        "ئەنبار": ["ڕەمادی", "فەلوجە", "حەدیسە", "قائیم"],
        "بابل": ["حیللە", "مسیەب", "قاسم"],
        "دیالە": ["بەقوبە", "خانەقین", "خالیس", "مەندەلی"],
        "نەجەف": ["نەجەف", "کوفە"],
        "کەربەلا": ["کەربەلا"],
        "سەلاحەدین": ["تکریت", "سامەڕا", "بەیجی", "بەلەد"],
        "واسیت": ["کوت", "حەی"],
        "میسان": ["عەمارە"],
        "موسەننا": ["سەماوە"],
        "زی قار": ["ناسیریە", "شەترە"],
        "قادسیە": ["دیوانیە"],
    },
}

FIRST_NAMES = [
    "عەبدوڵڵا", "سەردار", "مەنزڵ", "زینب", "نەسرین", "سەڵاوا", "علی", "حەسەن",
    "ئارام", "دڵدار", "خەلیل", "فەریاد", "کەریمی", "روژان", "ناسر", "بەڕێز",
    "دڵنەو", "هەڵبژاردە", "ئاسیا", "ژیار", "شێرکۆ", "ئەحمەد", "جەلال", "ڕۆژناو"
]
LAST_NAMES = [
    "حسن", "عەلی", "کەریم", "رەزا", "محمود", "ئاسۆ", "نوری", "خاڵ", "ئامان", "دارا",
    "خەڵک", "قادر", "تاهیر", "فەلاح", "یوسف", "حەمد", "شێخ", "قۆچان", "ڕەشید" 
]
JOBS = ["کارمەند", "خوێندکار", "مامۆستا", "پزیشک", "شاغڵ", "فەرمانبەر", "کارگێڕ"]
EDUCATION = ["سەرەتایی", "ناوەندی", "دبلۆم", "بەکالۆریۆس", "کاربەدەستا"]
GENDERS = ["نێر", "مێ"]
STATUS = ["active", "inactive", "test_only"]


def random_birth_date() -> str:
    start = date(1960, 1, 1)
    end = date(2008, 12, 31)
    range_days = (end - start).days
    return (start + timedelta(days=random.randint(0, range_days))).isoformat()


def flatten_cities():
    locations = []
    for region_name, govs in CITY_DATA.items():
        for gov_name, cities in govs.items():
            for city in cities:
                locations.append({
                    "region": region_name,
                    "governorate": gov_name,
                    "city": city,
                })
    return locations


def make_record(index: int, locations):
    location = random.choice(locations)
    person_id = f"TEST-{index:06d}"
    phone = f"+964{random.randint(700000000, 799999999)}"
    return {
        "record_id": f"DEMO-{index:06d}",
        "full_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "national_id": person_id,
        "date_of_birth": random_birth_date(),
        "gender": random.choice(GENDERS),
        "phone": phone,
        "region": location["region"],
        "governorate": location["governorate"],
        "city": location["city"],
        "occupation": random.choice(JOBS),
        "education": random.choice(EDUCATION),
        "status": random.choice(STATUS),
        "synthetic": True,
    }


def save_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_csv(path: Path, records):
    fieldnames = list(records[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def save_sqlite(path: Path, records):
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE registry (
                record_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                national_id TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT NOT NULL,
                region TEXT NOT NULL,
                governorate TEXT NOT NULL,
                city TEXT NOT NULL,
                occupation TEXT NOT NULL,
                education TEXT NOT NULL,
                status TEXT NOT NULL,
                synthetic INTEGER NOT NULL CHECK (synthetic = 1)
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO registry (
                record_id, full_name, national_id, date_of_birth,
                gender, phone, region, governorate, city,
                occupation, education, status, synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    r["record_id"], r["full_name"], r["national_id"], r["date_of_birth"],
                    r["gender"], r["phone"], r["region"], r["governorate"], r["city"],
                    r["occupation"], r["education"], r["status"], 1,
                )
                for r in records
            ],
        )
        conn.commit()
    finally:
        conn.close()


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    locations = flatten_cities()
    records = [make_record(i, locations) for i in range(1, RECORD_COUNT + 1)]

    save_json(OUTPUT_DIR / "iraq_cities.json", {
        "source": "synthetic_demo_data",
        "warning": "This is synthetic-only demo data for testing. No real people are represented.",
        "cities": CITY_DATA,
    })

    save_json(OUTPUT_DIR / "synthetic_registry.json", {
        "source": "synthetic_demo_data",
        "record_count": len(records),
        "warning": "Synthetic and fictional data only. Not real records.",
        "records": records,
    })

    save_csv(OUTPUT_DIR / "synthetic_registry.csv", records)
    save_sqlite(OUTPUT_DIR / "synthetic_registry.db", records)

    print("Files created successfully:")
    print(f"- {OUTPUT_DIR / 'iraq_cities.json'}")
    print(f"- {OUTPUT_DIR / 'synthetic_registry.json'}")
    print(f"- {OUTPUT_DIR / 'synthetic_registry.csv'}")
    print(f"- {OUTPUT_DIR / 'synthetic_registry.db'}")
    print(f"Records created: {len(records)}")
    print("Warning: All dataset values are synthetic and fictional.")


if __name__ == "__main__":
    main()
