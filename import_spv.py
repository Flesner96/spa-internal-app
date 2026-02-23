import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()



import pandas as pd
from datetime import datetime
from django.utils import timezone
from vouchers.models import Voucher
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.management.base import BaseCommand

User = get_user_model()

FILE_PATH = "spv.xlsx"

def parse_datetime(value):
    if pd.isna(value) or value == "":
        return None
    
    if isinstance(value, pd.Timestamp):
        return timezone.make_aware(value.to_pydatetime())
    
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, "%d.%m.%Y")
            return timezone.make_aware(dt)
        except:
            pass
        
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return timezone.make_aware(dt)
        except:
            pass
    
    return None


def parse_date(value):
    if pd.isna(value) or value == "":
        return None
    
    if isinstance(value, pd.Timestamp):
        return value.date()
    
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%d.%m.%Y").date()
        except:
            pass
        
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except:
            pass
    
    return None


def run():
    df = pd.read_excel(FILE_PATH)
    print("Wczytano:", len(df))

    errors = []
    created = 0

    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                seller = User.objects.get(id=int(row["seller_id"]))

                voucher = Voucher(
                    type=row["type"],
                    receipt_number=str(row["receipt_number"]) if not pd.isna(row["receipt_number"]) else "",
                    code=str(row["code"]),
                    service_name=row["service_name"],
                    client_name=row["client_name"],
                    issue_date=parse_datetime(row["issue_date"]),
                    expiry_date=parse_date(row["expiry_date"]),
                    redeemed_at=parse_datetime(row["redeemed_at"]),
                    seller=seller,
                    status=row["status"],
                    notes=row["notes"] if not pd.isna(row["notes"]) else "",
                )

                voucher.full_clean()
                voucher.save()
                created += 1

            except Exception as e:
                errors.append((index + 2, str(e)))

    if errors:
        print("BŁĘDY:")
        for err in errors:
            print(f"Wiersz {err[0]}: {err[1]}")
    else:
        print(f"SUKCES: Utworzono {created} voucherów.")

run()