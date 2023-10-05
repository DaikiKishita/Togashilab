import time
import nfcpy

def on_startup(targets):
    print("NFCリーダーが起動しました。カードをタッチしてください。")

def on_connect(tag):
    print("NFCタグを検出しました。")
    print("ID:", tag.identifier.encode("hex"))

# NFCリーダーの設定
clf = nfcpy.ContactlessFrontend()
clf.connect(rdwr={'on-startup': on_startup, 'on-connect': on_connect})

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    clf.close()
    print("プログラムを終了します。")