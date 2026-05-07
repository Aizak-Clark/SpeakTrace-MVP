import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

AMO_SUBDOMAIN = os.getenv("AMO_SUBDOMAIN", "egorlih")
AMO_TOKEN = os.getenv("AMO_TOKEN")
BASE_URL = f"https://{AMO_SUBDOMAIN}.amocrm.ru/api/v4"

HEADERS = {
    "Authorization": f"Bearer {AMO_TOKEN}",
    "Content-Type": "application/json",
}


def create_contact(name: str) -> int | None:
    if not AMO_TOKEN:
        print("[amoCRM] Ошибка: Переменная AMO_TOKEN пуста!")
        return None

    # Печатаем начало токена для проверки в консоли
    print(f"[DEBUG] Отправка запроса с токеном: {AMO_TOKEN[:15]}...")
    
    payload = [{"name": name}]
    # Убедитесь, что HEADERS определены ПОСЛЕ того, как токен был загружен
    response = httpx.post(f"{BASE_URL}/contacts", json=payload, headers=HEADERS)
    
    # amoCRM возвращает 201 при создании контакта
    if response.status_code in (200, 201):
        return response.json()["_embedded"]["contacts"][0]["id"]
    
    print(f"[amoCRM] Ошибка: {response.status_code} {response.text}")
    return None


def create_lead(title: str, contact_id: int | None = None) -> int | None:
    """Создаёт сделку в amoCRM, опционально привязывает контакт."""
    payload = [{"name": title}]

    if contact_id:
        payload[0]["_embedded"] = {
            "contacts": [{"id": contact_id}]
        }

    response = httpx.post(f"{BASE_URL}/leads/complex", json=payload, headers=HEADERS)

    if response.status_code in (200, 201):
        data = response.json()
        # /leads/complex возвращает список
        return data[0]["id"] if isinstance(data, list) else data["id"]

    print(f"[amoCRM] Ошибка создания сделки: {response.status_code} {response.text}")
    return None