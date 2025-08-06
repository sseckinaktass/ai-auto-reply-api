from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from transformers import pipeline
import json

app = FastAPI() #fastAPI sınıfından obje oluşturduk
classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli") #niyet tespiti için kullandığımız model. türkçe çalışıyor.

# JSON dosyasını okuma, with ile işimiz bitince otomatik close yapıyor.
with open('users.json', 'r') as f:
    data = json.load(f)
    users = data['users']

# istek için BaseModel 
class AutoReplyRequest(BaseModel):
    email: str
    text: str
    date: str

def detect_intent_analysis(text):
    text = text.lower()
    labels = ["teklif", "bilgilendirme", "teşekkür", "toplantı"]
    result = classifier(text, candidate_labels=labels)
    highest_score_index = result['scores'].index(max(result['scores']))
    return result['labels'][highest_score_index]

def find_user(email): # emaile göre .json dosyasında arama yapıyoruz.
    for user in users:
        if user['email'] == email:
            return user
    return None

def is_user_on_leave(user, today): #çalışan izinli mi? belirttiğimiz tarih izin aralğında ise True döndürür.
    if not user['is_on_leave'] or not user['leave_dates']:
        return False 
    start_date = datetime.strptime(user['leave_dates']['start'], '%Y-%m-%d').date()
    end_date = datetime.strptime(user['leave_dates']['end'], '%Y-%m-%d').date()
    return start_date <= today <= end_date

def detect_thank_you(mail_text): #eğer mesajımız teşekkür ifadesi belirtiyorsa fonksiyon True döndürür.
    if detect_intent_analysis(mail_text) == "teşekkür":
        return True
    else:
        return False  


def detect_offer_request(mail_text): #eğer mesajımız teklif ifadesi belirtiyorsa fonksiyon True döndürür.
    if detect_intent_analysis(mail_text) == "teklif" or detect_intent_analysis(mail_text) == "toplantı":
        return True
    else:
        return False

def get_available_slots(user, requested_date): 
    calendar = user.get('calendar', []) #calendar yoksa hata vermemsi için boş liste döndürecek.
    busy_slots = []

    for day in calendar: #istenilen güne göre o gün olan meşgul saatler alınır.
        if day['date'] == requested_date:
            busy_slots = day['busy_slots']
            break

    working_hours = [("09:00", "18:00")]
    available_slots = []

    for work_start, work_end in working_hours:
        current_start = datetime.strptime(work_start, '%H:%M')
        work_end_dt = datetime.strptime(work_end, '%H:%M')
        busy_slots_dt = [tuple(map(lambda x: datetime.strptime(x, '%H:%M'), slot.split('-'))) for slot in busy_slots] #meşgul olan saatlerin arasındaki - karekterini al çıkan saatleri tuple veri listesine al

        for busy_start, busy_end in sorted(busy_slots_dt):
            if current_start < busy_start: #eğer istediğimiz saat meşgul zamanından erken ise arada boş bir vakit vardır.
                available_slots.append(f"{current_start.strftime('%H:%M')}-{busy_start.strftime('%H:%M')}") #boş vakiti ekler
            current_start = max(current_start, busy_end) #bir sonraki zaman aralığına bakmak için current_startı güncelledik
        
        if current_start < work_end_dt:
            available_slots.append(f"{current_start.strftime('%H:%M')}-{work_end_dt.strftime('%H:%M')}")

    return available_slots

@app.get("/") # ana sayfaya get isteği atınca bu decorator fonksiyon çalışır
def home():
    return {"message": "hello world."}

@app.post("/auto-reply") # /auto-reply'a post methodu ile email, text ve date verilerini attığımız decotator fonksiyon
def auto_reply(request: AutoReplyRequest):
    user = find_user(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    today = datetime.strptime(request.date, '%Y-%m-%d').date()
    if is_user_on_leave(user, today): #istenilen günde izinli ise izinli olduğu tarihleri yazdır. varsa notu yazdır.
        reply = f"{user['name']} kullanıcısı {user['leave_dates']['start']} ve {user['leave_dates']['end']} tarihleri arasında izindedir."
        if user['leave_note']:
            reply += f" Not: {user['leave_note']}"
        return {"reply": reply}

    if detect_thank_you(request.text): #alınan text teşekkür bildiriyor ise bu fonksiyon döner.
        return {"reply": "Rica ederim iyi günler diliyorum."}

    if detect_offer_request(request.text): #alınan text teklif belirtiyorsa bu fonksiyon döner. teklif için uygun zamanları döndürür.
        available_slots = get_available_slots(user, request.date)
        if available_slots:
            reply = f"{request.date} tarihinde uygun saat aralıkları: {', '.join(available_slots)}. Size uygun bir zamanı bildirmenizi rica ederim." #saatleri virgül ve bir boşluk bırakarak tek bir string haline getirir.
        else:
            reply = f"{request.date} tarihinde uygun bir saat bulunmamaktadır."
        return {"reply": reply}

    return {"reply": "Mesajınız alınmıştır. En kısa sürede geri dönüş yapılacaktır."}
